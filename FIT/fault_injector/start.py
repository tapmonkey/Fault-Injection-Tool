#!/usr/bin/env python3

import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTROLLER_PATH = os.path.join(PROJECT_ROOT, "controller")

def main():
    print("\n=== Linux Kernel Fault Injector 启动器 ===")
    print("请选择模式：")
    print("[1] 友好 UI 模式（适合交互使用）")
    print("[2] 命令行菜单模式（适合批量/高级使用）")
    print("[0] 退出")

    choice = input("输入编号 [默认1]: ").strip() or "1"

    if choice == "0":
        print("退出启动器。")
        return

    elif choice == "1":
        subprocess.run(["python3", os.path.join(CONTROLLER_PATH, "friendly_ui.py")])

    elif choice == "2":
        subprocess.run(["python3", os.path.join(CONTROLLER_PATH, "cli_runner.py")])

    else:
        print("无效选择，请重新运行。")

if __name__ == "__main__":
    main()

