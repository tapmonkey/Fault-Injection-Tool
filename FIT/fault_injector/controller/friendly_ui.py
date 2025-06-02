import os
import sys
import random
# 设置项目根路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from ctypes import cdll, c_char_p, c_int
from prompt_toolkit import prompt
from rich.console import Console
from controller.config_loader import save_custom
from logger.live_monitor import monitor_dmesg



console = Console()

# 加载注入器库
lib_path = os.path.join(PROJECT_ROOT, 'injector/libinjector.so')
if not os.path.exists(lib_path):
    console.print(f"[red] 注入器库未找到: {lib_path}")
    sys.exit(1)

lib = cdll.LoadLibrary(lib_path)
lib.inject_function.argtypes = [c_char_p, c_int, c_int, c_int, c_int, c_int]

targets = {
    "1": ("pagealloc", "内存页分配 (模拟内存不足)"),
    "2": ("slab", "SLAB 分配器 (kmalloc 失败)"),
    "3": ("futex", "Futex 同步机制 (锁异常)"),
    "4": ("io_timeout", "输入输出超时"),
    "5": ("make_request", "磁盘 I/O 模拟失败"),
    "6": ("function", "指定函数 (注入错误返回)")
}

def step_select_target():
    console.rule(" 选择注入目标")
    for k, (code, desc) in targets.items():
        console.print(f"[{k}] {desc}")
    selected = prompt(" 输入编号以选择目标: ").strip()
    return targets.get(selected, (None, None))

def step_get_parameters():
    console.rule(" 设置注入参数")
    def ask(msg, default):
        val = prompt(f"{msg} 默认[{default}]: ").strip()
        return int(val) if val else default
    prob = ask("注入概率（0-100）", 10)
    interval = ask("注入间隔（每 N 次触发一次）", 100)
    times = ask("最大注入次数（0为无限）", 10)
    verbose = ask("是否启用日志（0=否, 1=是）", 1)
    pid_str = prompt("限制某个进程 PID（留空表示全部）: ").strip()
    pid = int(pid_str) if pid_str else 0
    return prob, interval, times, verbose, pid

def generate_random_parameters():
    prob = random.randint(5, 50)
    interval = random.choice([10, 50, 100])
    times = random.randint(1, 20)
    verbose = 1
    pid = 0
    return prob, interval, times, verbose, pid

def run_injection(target, prob, interval, times, verbose, pid):
    if target == "function":
        func = prompt("请输入注入的内核函数名: ")
        lib.inject_function(func.encode('utf-8'), prob, interval, times, verbose, pid)
    else:
        func_name = f"inject_{target}"
        if hasattr(lib, func_name):
            getattr(lib, func_name)(prob, interval, times, verbose, pid)
        else:
            console.print("[red] 不支持的注入目标")

def friendly_ui():
    console.print("[bold green]Linux Kernel Fault Injection 测试平台")

    while True:
        console.rule(" 选择注入模式")
        console.print("[1] 手动选择目标")
        console.print("[2] 随机注入一个目标")
        console.print("[3] 遍历所有目标")
        console.print("[0] 退出系统")
        mode = prompt(" 选择模式 [默认1]: ").strip() or "1"

        if mode == "0":
            console.print("[bold red]退出系统。")
            break

        if mode == "2":
            key = random.choice(list(targets.keys()))
            target, description = targets[key]
            console.print(f"[cyan] 随机注入目标: {description}")

            console.print("\n[bold yellow]参数选择：")
            console.print("[1] 使用默认参数")
            console.print("[2] 使用随机参数")
            param_mode = prompt(" 选择参数模式 [默认1]: ").strip() or "1"

            if param_mode == "2":
                prob, interval, times, verbose, pid = generate_random_parameters()
            else:
                prob, interval, times, verbose, pid = step_get_parameters()

            console.rule(" 注入配置")
            console.print(f"类型: {description}")
            console.print(f"概率: {prob}%, 间隔: {interval}, 次数: {times}, 日志: {verbose}, PID: {pid or '全部'}")

            run_injection(target, prob, interval, times, verbose, pid)
            monitor_dmesg(duration=30)

        elif mode == "3":
            console.print("[cyan] 遍历注入所有目标...")

            console.print("\n[bold yellow]参数选择：")
            console.print("[1] 每个注入手动设置参数")
            console.print("[2] 为每个目标使用随机参数")
            param_mode = prompt(" 选择参数模式 [默认1]: ").strip() or "1"

            for key, (target, description) in targets.items():
                console.rule(f"[{target}] {description}")
                if param_mode == "2":
                    prob, interval, times, verbose, pid = generate_random_parameters()
                else:
                    prob, interval, times, verbose, pid = step_get_parameters()

                run_injection(target, prob, interval, times, verbose, pid)
                monitor_dmesg(duration=15)

            continue

        else:
            target, description = step_select_target()
            if not target:
                console.print("[red]无效选择，返回主菜单。")
                continue

            prob, interval, times, verbose, pid = step_get_parameters()

            console.rule(" 注入配置")
            console.print(f"类型: {description}")
            console.print(f"概率: {prob}%, 间隔: {interval}, 次数: {times}, 日志: {verbose}, PID: {pid or '全部'}")

            run_injection(target, prob, interval, times, verbose, pid)
            monitor_dmesg(duration=30)

        save_name = prompt(" 是否保存为预设配置？输入名称或留空跳过: ").strip()
        if save_name:
            preset = {
                "target": target,
                "probability": prob,
                "interval": interval,
                "times": times,
                "verbose": verbose,
                "task_filter": pid
            }
            save_custom(save_name, preset)

        console.print("\n[cyan]返回主菜单...\n")

if __name__ == "__main__":
    friendly_ui()

