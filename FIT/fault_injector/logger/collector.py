# logger/collector.py
import subprocess

def collect_logs(output_file="inject.log"):
    print("Collecting fault injection logs via dmesg...")
    try:
        result = subprocess.run(["dmesg", "-T"], capture_output=True, text=True)
        logs = result.stdout.splitlines()
        keywords = ["fail_slab", "fail_page_alloc", "fail_futex", "fail_function", "fail_make_request", "fail_sunrpc"]
        matched = [line for line in logs if any(k in line for k in keywords)]
        with open(output_file, "w") as f:
            f.write("\n".join(matched))
        print(f" Log saved to {output_file}")
        return matched
    except Exception as e:
        print(" Failed to collect logs:", e)
        return []
