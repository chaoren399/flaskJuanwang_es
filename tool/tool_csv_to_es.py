import os
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CSVToElasticsearchImporter:
    def __init__(self):
        # Elasticsearch连接配置
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
                logger.info(f"已删除旧索引: {self.index_name}")
            except Exception as e:
                logger.error(f"删除索引失败: {e}")
                return False
        else:
            logger.info(f"索引 {self.index_name} 不存在，无需删除")
        return True

    def create_index_if_not_exists(self):
        """创建索引（如果不存在）"""
        if not self.es.indices.exists(index=self.index_name):
            # 创建索引映射
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
                        "标签": {"type": "keyword"},
                        "file_hash": {"type": "keyword"},  # 添加文件hash字段
                        "unique_id": {"type": "keyword"}  # 添加唯一ID字段
                    }
                }
            }

            try:
                self.es.indices.create(index=self.index_name, body=mapping)
                logger.info(f"索引 {self.index_name} 创建成功")
            except Exception as e:
                logger.error(f"创建索引失败: {e}")
                return False
        else:
            logger.info(f"索引 {self.index_name} 已存在")
        return True

    def read_csv_files(self):
        """读取目录中的所有CSV文件"""
        csv_files = []
        if not os.path.exists(self.csv_directory):
            logger.error(f"目录 {self.csv_directory} 不存在")
            return csv_files

        for file in os.listdir(self.csv_directory):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(self.csv_directory, file))

        logger.info(f"找到 {len(csv_files)} 个CSV文件")
        return csv_files

    def generate_unique_id(self, row_data, file_hash):
        """生成基于行数据和文件hash的唯一ID"""
        # 将行数据转换为字符串并排序以确保一致性
        data_str = ''.join([f"{k}:{v}" for k, v in sorted(row_data.items()) if k not in ['file_hash', 'unique_id']])
        unique_string = f"{file_hash}_{data_str}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

    def process_csv_to_bulk(self, file_path):
        """将CSV文件处理成bulk操作格式"""
        actions = []

        # 生成文件hash以标识不同的文件
        file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()[:10]

        try:
            # 使用pandas读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8')

            # 处理每一行数据
            for index, row in df.iterrows():
                # 将NaN值替换为None，确保数据类型正确
                doc = {}
                for col in df.columns:
                    value = row[col]
                    # 处理NaN和空值
                    if pd.isna(value):
                        doc[col] = None
                    else:
                        # 尝试转换数字类型
                        if col == "序号":
                            try:
                                doc[col] = int(value)
                            except:
                                doc[col] = value
                        else:
                            doc[col] = str(value)

                # 添加文件hash和唯一ID
                doc['file_hash'] = file_hash

                # 生成唯一ID
                unique_id = self.generate_unique_id(doc, file_hash)
                doc['unique_id'] = unique_id

                # 检查文档是否已存在
                exists_query = {
                    "query": {
                        "term": {
                            "unique_id.keyword": unique_id
                        }
                    }
                }

                search_result = self.es.search(index=self.index_name, body=exists_query)

                # 如果文档不存在，则添加到导入列表
                if search_result['hits']['total']['value'] == 0:
                    action = {
                        "_index": self.index_name,
                        "_id": unique_id,  # 使用唯一ID作为文档ID
                        "_source": doc
                    }
                    actions.append(action)
                else:
                    logger.debug(f"文档已存在，跳过导入: {unique_id}")

        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {e}")

        logger.info(f"文件 {os.path.basename(file_path)} 处理完成，新增 {len(actions)} 条记录")
        return actions

    def import_all_csv(self):
        """导入所有CSV文件到Elasticsearch"""
        # 删除旧索引
        if not self.delete_index_if_exists():
            logger.error("无法删除旧索引，程序退出")
            return False

        # 创建新索引
        if not self.create_index_if_not_exists():
            logger.error("无法创建索引，程序退出")
            return False

        # 获取所有CSV文件
        csv_files = self.read_csv_files()

        if not csv_files:
            logger.warning("没有找到CSV文件")
            return False

        total_imported = 0
        total_failed = 0

        # 处理每个CSV文件
        for file_path in csv_files:
            logger.info(f"正在处理文件: {os.path.basename(file_path)}")

            # 转换为bulk操作格式
            actions = self.process_csv_to_bulk(file_path)

            if not actions:
                logger.warning(f"文件 {os.path.basename(file_path)} 没有新数据需要导入")
                continue

            try:
                # 批量导入数据
                success, failed = bulk(self.es, actions, chunk_size=1000, request_timeout=60)
                total_imported += success
                total_failed += len(failed) if failed else 0
                logger.info(f"文件 {os.path.basename(file_path)} 导入完成: 成功{success}条记录")

                if failed:
                    logger.warning(f"文件 {os.path.basename(file_path)} 导入失败: {len(failed)} 条记录")

            except Exception as e:
                logger.error(f"导入文件 {os.path.basename(file_path)} 时出错: {e}")

        logger.info(f"导入完成 - 总共成功导入 {total_imported} 条记录，失败 {total_failed} 条记录")
        return True

    # def import_all_csv(self):
    #     """导入所有CSV文件到Elasticsearch"""
    #     # 创建索引
    #     if not self.create_index_if_not_exists():
    #         logger.error("无法创建索引，程序退出")
    #         return False
    #
    #     # 获取所有CSV文件
    #     csv_files = self.read_csv_files()
    #
    #     if not csv_files:
    #         logger.warning("没有找到CSV文件")
    #         return False
    #
    #     total_imported = 0
    #     total_failed = 0
    #
    #     # 处理每个CSV文件
    #     for file_path in csv_files:
    #         logger.info(f"正在处理文件: {os.path.basename(file_path)}")
    #
    #         # 转换为bulk操作格式
    #         actions = self.process_csv_to_bulk(file_path)
    #
    #         if not actions:
    #             logger.warning(f"文件 {os.path.basename(file_path)} 没有新数据需要导入")
    #             continue
    #
    #         try:
    #             # 批量导入数据
    #             success, failed = bulk(self.es, actions, chunk_size=1000, request_timeout=60)
    #             total_imported += success
    #             total_failed += len(failed) if failed else 0
    #             logger.info(f"文件 {os.path.basename(file_path)} 导入完成: 成功{success}条记录")
    #
    #             if failed:
    #                 logger.warning(f"文件 {os.path.basename(file_path)} 导入失败: {len(failed)} 条记录")
    #
    #         except Exception as e:
    #             logger.error(f"导入文件 {os.path.basename(file_path)} 时出错: {e}")
    #
    #     logger.info(f"导入完成 - 总共成功导入 {total_imported} 条记录，失败 {total_failed} 条记录")
    #     return True




def main():
    importer = CSVToElasticsearchImporter()
    success = importer.import_all_csv()
    if success:
        logger.info("所有CSV文件导入完成")
    else:
        logger.error("导入过程中出现错误")


if __name__ == "__main__":
    main()
