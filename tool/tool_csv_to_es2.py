import os
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
import logging
import hashlib
import re  # 新增导入
from concurrent.futures import ProcessPoolExecutor, as_completed

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_text(text):
    """
    清洗文本数据，移除 Emoji 等特殊字符，保留中文、英文、数字和常用标点
    解决 Windows 控制台 GBK 编码无法处理特殊字符的问题
    """
    if not isinstance(text, str):
        return text

    # 保留范围：中文、英文、数字、常用标点符号、空格
    # 移除 Emoji、特殊符号等多字节字符
    cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\.\-\(\)\s，。？！、；：""''…—_/\[\]]', '', text)
    return cleaned.strip()




class CSVToElasticsearchImporter:
    def __init__(self):
        # Elasticsearch 连接配置
        self.es = Elasticsearch(
            hosts=[{
                'host': '10.0.0.215',
                'port': 9200,
                'scheme': 'http'
            }]
        )
        self.index_name = "stockinfo"
        self.csv_directory = r"D:\03-code\pycharm\stock\flaskJuanwang_es\data\csv"

    def delete_index_if_exists(self):
        """删除现有的索引（如果存在）"""
        if self.es.indices.exists(index=self.index_name):
            try:
                self.es.indices.delete(index=self.index_name)
                logger.info(f"已删除旧索引：{self.index_name}")
            except Exception as e:
                logger.error(f"删除索引失败：{e}")
                return False
        else:
            logger.info(f"索引 {self.index_name} 不存在，无需删除")
        return True

    def create_index_if_not_exists(self):
        """创建索引（如果不存在）"""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "序号": {"type": "integer"},
                        "题干": {"type": "text"},
                        "选项 A": {"type": "text"},
                        "选项 B": {"type": "text"},
                        "选项 C": {"type": "text"},
                        "选项 D": {"type": "text"},
                        "选项 E": {"type": "text"},
                        "选项 F": {"type": "text"},
                        "选项 G": {"type": "text"},
                        "选项 H": {"type": "text"},
                        "解析": {"type": "text"},
                        "分数": {"type": "keyword"},
                        "答案": {"type": "text"},
                        "标签": {"type": "text"},
                        "file_hash": {"type": "keyword"},
                        "unique_id": {"type": "keyword"}
                    }
                }
            }
            try:
                self.es.indices.create(index=self.index_name, body=mapping)
                logger.info(f"索引 {self.index_name} 创建成功")
            except Exception as e:
                logger.error(f"创建索引失败：{e}")
                return False
        else:
            logger.info(f"索引 {self.index_name} 已存在")
        return True

    def read_csv_files(self):
        """读取目录中的所有 CSV 文件"""
        csv_files = []
        if not os.path.exists(self.csv_directory):
            logger.error(f"目录 {self.csv_directory} 不存在")
            return csv_files

        for file in os.listdir(self.csv_directory):
            if file.endswith('.csv') and not file.startswith('~$'):
                csv_files.append(os.path.join(self.csv_directory, file))

        logger.info(f"找到 {len(csv_files)} 个 CSV 文件")
        return csv_files

    def generate_unique_id(self, row_data, file_hash):
        """生成基于行数据和文件 hash 的唯一 ID"""
        data_str = ''.join([f"{k}:{v}" for k, v in sorted(row_data.items()) if k not in ['file_hash', 'unique_id']])
        unique_string = f"{file_hash}_{data_str}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()



    def process_csv_to_bulk(self, file_path):
        """
        【优化版】将 CSV 文件处理成 bulk 操作格式
        核心优化：移除了每行查询 ES 的逻辑，直接生成动作列表。
        因为上层逻辑已经删除了旧索引，所以所有数据都是新的，直接写入即可。
        """
        actions = []
        file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()[:10]

        try:
            # 使用 pandas 读取 CSV
            # 如果速度仍不够，可考虑添加 usecols 只读取需要的列
            df = pd.read_csv(file_path, encoding='utf-8')

            # 预处理列名，去除空格（与之前逻辑保持一致）
            df.columns = [col.replace(' ', '') for col in df.columns]

            for index, row in df.iterrows():
                doc = {}
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        doc[col] = None
                    else:
                        if col == "序号":
                            try:
                                doc[col] = int(value)
                            except:
                                doc[col] = str(value)
                        else:
                            # doc[col] = str(value)
                            # 新增：清洗文本数据，移除 Emoji 等特殊字符
                            doc[col] = clean_text(str(value))

                doc['file_hash'] = file_hash
                unique_id = self.generate_unique_id(doc, file_hash)
                doc['unique_id'] = unique_id

                # 构建 bulk action
                # 直接使用 unique_id 作为 _id，ES 会自动覆盖（虽然这里索引是新的，不会冲突）
                action = {
                    "_index": self.index_name,
                    "_id": unique_id,
                    "_source": doc
                }
                actions.append(action)

        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错：{e}")

        logger.info(f"文件 {os.path.basename(file_path)} 准备完成，共 {len(actions)} 条记录")
        return actions

    def import_all_csv(self):
        """导入所有 CSV 文件到 Elasticsearch"""
        if not self.delete_index_if_exists():
            logger.error("无法删除旧索引，程序退出")
            return False

        if not self.create_index_if_not_exists():
            logger.error("无法创建索引，程序退出")
            return False

        csv_files = self.read_csv_files()
        if not csv_files:
            logger.warning("没有找到 CSV 文件")
            return False

        total_imported = 0
        total_failed = 0

        # 优化：逐个文件处理，但每个文件内部使用高效的 bulk
        for file_path in csv_files:
            logger.info(f"正在处理文件：{os.path.basename(file_path)}")

            actions = self.process_csv_to_bulk(file_path)
            if not actions:
                continue

            try:
                # 使用 bulk helpers 进行批量导入
                # 移除了 request_timeout，因为它已在 ES 客户端初始化时设置
                success, failed = bulk(
                    self.es,
                    actions,
                    chunk_size=2000,
                    raise_on_error=False
                )
                total_imported += success
                total_failed += len(failed) if failed else 0

                logger.info(f"文件 {os.path.basename(file_path)} 导入完成：成功 {success} 条")
                if failed:
                    logger.warning(f"文件 {os.path.basename(file_path)} 失败 {len(failed)} 条")

            except Exception as e:
                logger.error(f"导入文件 {os.path.basename(file_path)} 时出错：{e}")

        logger.info(f"=== 导入全部完成 ===\n总共成功：{total_imported} 条\n总共失败：{total_failed} 条")
        return True


def main():
    importer = CSVToElasticsearchImporter()
    success = importer.import_all_csv()
    if success:
        logger.info("所有 CSV 文件导入完成")
    else:
        logger.error("导入过程中出现错误")


if __name__ == "__main__":
    main()
