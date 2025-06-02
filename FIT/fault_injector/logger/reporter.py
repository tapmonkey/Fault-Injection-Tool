# logger/reporter.py
import os
from jinja2 import Template
from datetime import datetime

def generate_report(logs, output_file="reports/report.html"):
    html_template = Template("""
    <html><head><title>Fault Injection Report</title></head>
    <body>
    <h1>Linux Kernel Fault Injection Report</h1>
    <p>Generated at: {{ timestamp }}</p>
    <h2>Logs:</h2>
    <pre>{{ logs }}</pre>
    </body></html>
    """)
    rendered = html_template.render(timestamp=datetime.now().isoformat(), logs="\n".join(logs))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(rendered)
    print(f" Report written to {output_file}")
