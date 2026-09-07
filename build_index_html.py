"""
build_index_html.py
Generates the resilient, standalone index.html with live API connectivity
and embedded real-world fallback snapshot data for seamless Vercel deployment.
"""

import json
import re
from econometrics import (
    calculate_econometric_indicators,
    compute_lead_time_curve,
    read_index_history,
    read_fares,
)
from scrapy_runner import read_scrapy_status

def generate():
    # Read base template
    with open("templates/index.html", "r", encoding="utf-8") as f:
        template = f.read()

    fares = read_fares()
    fares_sorted = sorted(fares, key=lambda x: x.get("timestamp", ""), reverse=True)[:150]
    history = read_index_history()
    summary = calculate_econometric_indicators()
    lead_time = compute_lead_time_curve()
    scrapy_status = read_scrapy_status()

    # Inject fallback globals at start of head
    fallback_script = f"""  <script>
    window.FALLBACK_SUMMARY = {json.dumps(summary)};
    window.FALLBACK_TRENDS = {json.dumps(history)};
    window.FALLBACK_LEAD_TIME = {json.dumps(lead_time)};
    window.FALLBACK_FARES = {json.dumps(fares_sorted)};
    window.FALLBACK_SCRAPY_STATUS = {json.dumps(scrapy_status)};
  </script>"""

    # Strip existing fallback script block if present
    res = re.sub(r'  <script>\s*window\.FALLBACK_SUMMARY\s*=[\s\S]*?</script>', '', template)
    res = res.replace("<head>", "<head>\n" + fallback_script)

    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(res)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(res)

    print("Successfully built clean index.html and templates/index.html!")

if __name__ == "__main__":
    generate()
