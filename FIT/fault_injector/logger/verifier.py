import subprocess

def check_injection_effect(keywords=None):
    if keywords is None:
        keywords = ["fail_", "injected", "slab", "page", "request", "futex"]

    result = subprocess.run(["dmesg", "-T"], capture_output=True, text=True)
    logs = result.stdout.splitlines()
    hits = [line for line in logs if any(k in line for k in keywords)]

    print("\n Injection Effect Summary:")
    for line in hits[-10:]:
        print("", line)

    return hits

