import subprocess
import time
from collections import deque
from rich.console import Console
from rich.live import Live
from rich.table import Table

console = Console()

FAIL_KEYWORDS = [
    "failslab", "fail_page_alloc", "fail_futex",
    "fail_function", "fail_make_request", "fail_io_timeout"
]

def get_dmesg_lines():
    try:
        output = subprocess.check_output(["dmesg"], text=True)
        return output.splitlines()
    except Exception as e:
        console.print(f"[red]无法读取 dmesg: {e}")
        return []

def filter_lines(lines):
    return [line for line in lines if any(k in line for k in FAIL_KEYWORDS)]

def build_table(logs):
    table = Table(title="实时故障注入日志监控 (增强 polling)", show_lines=True)
    table.add_column("日志内容", style="white")
    for line in list(logs)[-10:]:
        table.add_row(line)
    return table

def monitor_dmesg(duration=30, interval=2):
    console.print("[bold green]开始监控注入行为...\n")

    logs = deque(maxlen=100)
    last_seen_count = 0

    try:
        with Live(console=console, refresh_per_second=2) as live:
            for _ in range(duration // interval):
                all_lines = get_dmesg_lines()
                new_part = all_lines[last_seen_count:]
                last_seen_count = len(all_lines)

                new_logs = filter_lines(new_part)
                logs.extend(new_logs)

                live.update(build_table(logs))
                time.sleep(interval)
    except KeyboardInterrupt:
        console.print("[yellow] 手动中断监控")
    finally:
        console.print("[green] 监控完成")

if __name__ == "__main__":
    monitor_dmesg(30)

