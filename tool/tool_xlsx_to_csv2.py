import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed


def convert_single_file(args):
    """
    单个文件的转换逻辑，用于多进程调用
    """
    xlsx_path, target_dir = args
    filename = os.path.basename(xlsx_path)

    # 跳过临时文件
    if filename.startswith('~$'):
        return None

    try:
        # 读取第一个工作表
        # engine='openpyxl' 通常对 .xlsx 更高效
        df = pd.read_excel(xlsx_path, engine='openpyxl')

        # 去除表头中的空格
        df.columns = [col.replace(' ', '') for col in df.columns]

        # 生成目标 csv 文件名
        csv_filename = filename.replace('.xlsx', '.csv')
        csv_path = os.path.join(target_dir, csv_filename)

        # 保存为 csv 文件
        # index=False 避免写入行索引，encoding='utf-8' 保证兼容性
        df.to_csv(csv_path, index=False, encoding='utf-8')

        return f"已转换：{filename} -> {csv_filename}"
    except Exception as e:
        return f"转换 {filename} 时出错：{str(e)}"


def convert_xlsx_to_csv_parallel(source_dirs, target_dir):
    """
    并行转换多个目录下的 xlsx 文件
    """
    # 创建目标目录
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 收集所有需要处理的任务
    tasks = []
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            print(f"警告：源目录不存在 - {source_dir}")
            continue

        for filename in os.listdir(source_dir):
            if filename.endswith('.xlsx') and not filename.startswith('~$'):
                xlsx_path = os.path.join(source_dir, filename)
                tasks.append((xlsx_path, target_dir))

    print(f"共发现 {len(tasks)} 个文件待转换，开始并行处理...")

    success_count = 0
    error_count = 0

    # 使用进程池并行执行
    # max_workers 默认为 CPU 核心数，可根据实际情况调整
    with ProcessPoolExecutor() as executor:
        # 提交所有任务
        future_to_file = {executor.submit(convert_single_file, task): task[0] for task in tasks}

        for future in as_completed(future_to_file):
            result = future.result()
            if result:
                if result.startswith("已转换"):
                    print(result)
                    success_count += 1
                else:
                    print(result)
                    error_count += 1

    print(f"\n处理完成：成功 {success_count} 个，失败 {error_count} 个")


if __name__ == "__main__":
    # 定义源目录列表
    source_directories = [
        r"E:\BaiduSyncdisk\7-花牛大叔\6-卷王-题材细分\1-0-100",
        r"E:\BaiduSyncdisk\7-花牛大叔\6-卷王-题材细分"
    ]
    target_directory = r"D:\03-code\pycharm\stock\flaskJuanwang_es\data\csv"

    convert_xlsx_to_csv_parallel(source_directories, target_directory)
