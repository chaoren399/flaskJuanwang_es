# run_tools.py
import subprocess
import sys
import os
import time  # 引入 time 模块


def run_script(script_path):
    """
    运行指定的Python脚本并记录耗时
    """
    try:
        print(f"正在运行：{script_path}")
        start_time = time.time()  # 记录开始时间

        result = subprocess.run([sys.executable, script_path],
                                capture_output=True,
                                text=True,
                                encoding='gbk',  # 修复中文输出乱码问题
                                errors='replace')  # 增加容错

        end_time = time.time()  # 记录结束时间
        duration = end_time - start_time

        if result.returncode == 0:
            print(f"✓ {os.path.basename(script_path)} 运行成功")
            print(f"⏱️  耗时：{duration:.2f} 秒")
            if result.stdout:
                # 可选：如果 stdout 内容太多，可以选择不打印或只打印最后几行
                # print(f"输出:\n{result.stdout}")
                pass
        else:
            print(f"✗ {os.path.basename(script_path)} 运行失败")
            print(f"⏱️  耗时：{duration:.2f} 秒")
            if result.stderr:
                print(f"错误:\n{result.stderr}")
        return result.returncode == 0

    except Exception as e:
        print(f"运行 {script_path} 时发生异常：{e}")
        return False


def main():
    """
    主函数：依次运行 xlsx 转 csv 工具和 csv 导入 ES 工具
    """
    # 定义脚本路径
    xlsx_to_csv_script = r"D:\03-code\pycharm\stock\flaskJuanwang_es\tool\tool_xlsx_to_csv2.py"
    csv_to_es_script = r"D:\03-code\pycharm\stock\flaskJuanwang_es\tool\tool_csv_to_es2.py"

    # 检查脚本文件是否存在
    if not os.path.exists(xlsx_to_csv_script):
        print(f"错误：找不到文件 {xlsx_to_csv_script}")
        return False

    if not os.path.exists(csv_to_es_script):
        print(f"错误：找不到文件 {csv_to_es_script}")
        return False

    total_start_time = time.time()  # 记录总程序开始时间
    print("开始运行数据处理工具...")
    print("=" * 50)

    # 第一步：运行 xlsx 转 csv 工具
    print("步骤 1: 转换 xlsx 文件为 csv 文件")
    step1_success = run_script(xlsx_to_csv_script)

    if not step1_success:
        print("xlsx 转 csv 步骤失败，终止执行")
        return False

    print("\n" + "=" * 50)

    # 第二步：运行 csv 导入 ES 工具
    print("步骤 2: 将 csv 数据导入 Elasticsearch")
    step2_success = run_script(csv_to_es_script)

    if not step2_success:
        print("csv 导入 ES 步骤失败")
        return False

    print("\n" + "=" * 50)

    total_end_time = time.time()  # 记录总程序结束时间
    total_duration = total_end_time - total_start_time

    print("✓ 所有步骤已完成")
    print(f"🚀 总耗时：{total_duration:.2f} 秒 ({total_duration / 60:.2f} 分钟)")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行过程中发生未预期的错误：{e}")
        sys.exit(1)
