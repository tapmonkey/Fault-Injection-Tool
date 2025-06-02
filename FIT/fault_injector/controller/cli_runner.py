import os
import sys
from ctypes import cdll, c_char_p, c_int

# 设置路径以便跨目录导入
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from logger.collector import collect_logs
from logger.reporter import generate_report
from logger.verifier import check_injection_effect
from controller.config_loader import load_presets, save_custom

# 全局变量：用于保存当前注入配置
current_cfg = {}

def menu():
    print("\n=== Linux Kernel Fault Injector ===")
    print("1. Inject: Manual")
    print("2. Inject: From Preset")
    print("3. Save current as preset")
    print("4. Collect logs and generate report")
    print("5. Verify injection effectiveness")
    print("0. Exit")
    return input("Select option: ")

def get_params():
    try:
        prob = int(input("Set probability (0–100): "))
        interval = int(input("Set interval (every N triggers): "))
        times = int(input("Set max injection count: "))
        verbose = int(input("Verbose mode (0 = off, 1 = on): "))
        pid = input("Restrict to PID (blank = all): ")
        pid = int(pid) if pid.strip() else 0
        return prob, interval, times, verbose, pid
    except ValueError:
        print(" Invalid input. Please enter integers.")
        return get_params()

def main():
    lib_path = os.path.join(PROJECT_ROOT, 'injector/libinjector.so')
    if not os.path.exists(lib_path):
        print(f" Library not found: {lib_path}")
        sys.exit(1)

    lib = cdll.LoadLibrary(lib_path)

    # 设置 C 函数参数类型
    lib.inject_function.argtypes = [c_char_p, c_int, c_int, c_int, c_int, c_int]

    while True:
        choice = menu()

        if choice == '0':
            print(" Exiting...")
            break

        elif choice == '1':  # 手动注入
            prob, interval, times, verbose, pid = get_params()
            target = input("Target (e.g. pagealloc / slab / function): ").strip()
            current_cfg.update({
                "probability": prob,
                "interval": interval,
                "times": times,
                "verbose": verbose,
                "task_filter": pid,
                "target": target
            })

            if target == "function":
                func = input("Function name (in kernel): ")
                lib.inject_function(func.encode('utf-8'), prob, interval, times, verbose, pid)
            else:
                func_name = f"inject_{target}"
                if hasattr(lib, func_name):
                    getattr(lib, func_name)(prob, interval, times, verbose, pid)
                else:
                    print(" Unsupported injection target.")

        elif choice == '2':  # 从预设注入
            presets = load_presets()
            if not presets:
                print(" No presets available.")
                continue
            print("Available presets:")
            for name in presets:
                print(f"  - {name}")
            sel = input("Enter preset name: ").strip()
            if sel in presets:
                cfg = presets[sel]
                target = cfg["target"]
                if target == "function":
                    func = input("Function name (in kernel): ")
                    lib.inject_function(func.encode('utf-8'),
                                        cfg['probability'], cfg['interval'],
                                        cfg['times'], cfg['verbose'], cfg['task_filter'])
                else:
                    getattr(lib, f"inject_{target}")(
                        cfg['probability'], cfg['interval'], cfg['times'],
                        cfg['verbose'], cfg['task_filter']
                    )
                current_cfg.update(cfg)
            else:
                print(" Preset not found.")

        elif choice == '3':  # 保存当前配置为预设
            if not current_cfg:
                print(" No active configuration to save.")
                continue
            name = input("Preset name to save as: ").strip()
            if name:
                save_custom(name, current_cfg)
            else:
                print(" Invalid name.")

        elif choice == '4':  # 生成日志和报告
            logs = collect_logs()
            generate_report(logs)

        elif choice == '5':  # 验证注入效果
            check_injection_effect()

        else:
            print(" Invalid selection.")

if __name__ == "__main__":
    main()

