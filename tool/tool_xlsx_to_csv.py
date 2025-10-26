import os
import pandas as pd


def convert_xlsx_to_csv(source_dir, target_dir):
    """
    将指定目录下的所有xlsx文件转换为csv文件并保存到目标目录
    """
    # 创建目标目录如果不存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 遍历源目录中的所有文件
    for filename in os.listdir(source_dir):
        if filename.endswith('.xlsx'):
            # 构建完整的文件路径
            xlsx_path = os.path.join(source_dir, filename)

            # 读取xlsx文件
            try:
                # 读取第一个工作表
                df = pd.read_excel(xlsx_path)

                # 生成目标csv文件名
                csv_filename = filename.replace('.xlsx', '.csv')
                csv_path = os.path.join(target_dir, csv_filename)

                # 保存为csv文件
                df.to_csv(csv_path, index=False, encoding='utf-8')

                print(f"已转换: {filename} -> {csv_filename}")
            except Exception as e:
                print(f"转换 {filename} 时出错: {str(e)}")


# 使用示例

source_directory = r"D:\BaiduSyncdisk\7-花牛大叔\6-卷王-题材细分"
# source_directory = r"D:\BaiduSyncdisk\7-花牛大叔\6-卷王-题材细分\1-0-100"
# source_directory = r"D:\03-code\pycharm\stock\flaskJuanwang_es\data\6-卷王-题材细分"
# source_directory = r"D:\03-code\pycharm\stock\flaskJuanwang_es\data\6-卷王-题材细分\1-0-100"
# target_directory = r"./data/csv"
target_directory = r"D:\03-code\pycharm\stock\flaskJuanwang_es\data\csv"

# 执行转换
convert_xlsx_to_csv(source_directory, target_directory)
