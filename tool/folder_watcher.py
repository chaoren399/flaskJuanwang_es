import os
import time
import subprocess

# ================= 配置区域 =================
# 监控的目录
SOURCE_DIRECTORY = r"E:\BaiduSyncdisk\7-花牛大叔\6-卷王-题材细分\1-0-100"
SOURCE_DIRECTORY2 = r"E:\BaiduSyncdisk\7-花牛大叔\6-卷王-题材细分"

# 要触发执行的动作脚本
ACTION_SCRIPT = r"run_all_tool.py"

# 检查间隔 (秒)，根据需要调整，太短会占用CPU，太长会有延迟
CHECK_INTERVAL = 2


# ==========================================

def get_folder_mod_time(folder_path):
    """获取文件夹的最后修改时间"""
    try:
        # os.path.getmtime 也可以获取，但 os.stat 更通用
        return os.stat(folder_path).st_mtime
    except Exception as e:
        print(f"无法访问目录 {folder_path}: {e}")
        return 0


def run_action_script():
    """执行指定的 Python 脚本"""
    try:
        print(f"检测到文件夹修改，正在执行: {ACTION_SCRIPT} ...")

        # 使用 subprocess.Popen 启动脚本，不阻塞主监控程序
        # shell=True 允许在 shell 中执行，确保路径解析正确
        process = subprocess.Popen(
            ['python', ACTION_SCRIPT],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 等待脚本执行完成（可选，如果不希望等待，可以去掉 communicate）
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("动作执行完成。")
        else:
            print(f"动作执行出错: {stderr.decode().strip()}")

    except Exception as e:
        print(f"执行脚本时发生错误: {e}")


def main():
    print("🚀 监控程序已启动...")
    print(f"监控目录1: {SOURCE_DIRECTORY}")
    print(f"监控目录2: {SOURCE_DIRECTORY2}")

    # 初始化时记录当前时间
    last_time_1 = get_folder_mod_time(SOURCE_DIRECTORY)
    last_time_2 = get_folder_mod_time(SOURCE_DIRECTORY2)

    try:
        while True:
            time.sleep(CHECK_INTERVAL)

            current_time_1 = get_folder_mod_time(SOURCE_DIRECTORY)
            current_time_2 = get_folder_mod_time(SOURCE_DIRECTORY2)

            # 检查目录1是否有变化
            if current_time_1 != last_time_1:
                print(f"[{time.ctime()}] 目录1发生变化，触发动作。")
                run_action_script()
                last_time_1 = current_time_1  # 更新时间戳，防止重复触发

            # 检查目录2是否有变化
            if current_time_2 != last_time_2:
                print(f"[{time.ctime()}] 目录2发生变化，触发动作。")
                run_action_script()
                last_time_2 = current_time_2  # 更新时间戳，防止重复触发

    except KeyboardInterrupt:
        print("\n🛑 监控程序已停止。")


if __name__ == "__main__":
    main()