# run_tools.py
import subprocess
import sys
import os


def run_script(script_path):
    """
    运行指定的Python脚本
    """
    try:
        print(f"正在运行: {script_path}")
        result = subprocess.run([sys.executable, script_path],
                                capture_output=True,
                                text=True,
                                encoding='utf-8')

        if result.returncode == 0:
            print(f"✓ {os.path.basename(script_path)} 运行成功")
            if result.stdout:
                print(f"输出:\n{result.stdout}")
        else:
            print(f"✗ {os.path.basename(script_path)} 运行失败")
            if result.stderr:
                print(f"错误:\n{result.stderr}")
        return result.returncode == 0

    except Exception as e:
        print(f"运行 {script_path} 时发生异常: {e}")
        return False


def main():
    """
    主函数：依次运行xlsx转csv工具和csv导入ES工具
    """
    # 定义脚本路径
    xlsx_to_csv_script = r"D:\03-code\pycharm\stock\flaskJuanwang_es\tool\tool_xlsx_to_csv2.py"
    csv_to_es_script = r"D:\03-code\pycharm\stock\flaskJuanwang_es\tool\tool_csv_to_es2.py"

    # 检查脚本文件是否存在
    if not os.path.exists(xlsx_to_csv_script):
        print(f"错误: 找不到文件 {xlsx_to_csv_script}")
        return False

    if not os.path.exists(csv_to_es_script):
        print(f"错误: 找不到文件 {csv_to_es_script}")
        return False

    print("开始运行数据处理工具...")
    print("=" * 50)

    # 第一步：运行xlsx转csv工具
    print("步骤1: 转换xlsx文件为csv文件")
    if not run_script(xlsx_to_csv_script):
        print("xlsx转csv步骤失败，终止执行")
        return False

    print("\n" + "=" * 50)

    # 第二步：运行csv导入ES工具
    print("步骤2: 将csv数据导入Elasticsearch")
    if not run_script(csv_to_es_script):
        print("csv导入ES步骤失败")
        return False

    print("\n" + "=" * 50)
    print("✓ 所有步骤已完成")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行过程中发生未预期的错误: {e}")
        sys.exit(1)
