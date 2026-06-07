import os
from datetime import date as _date
from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def render_report(leads: list[dict], output_dir: str = "output", date_str: str = None) -> str:
    if date_str is None:
        date_str = _date.today().isoformat()

    sorted_leads = sorted(leads, key=lambda x: x["score"], reverse=True)
    sources = len({l["source"] for l in leads}) if leads else 0

    env = Environment(loader=FileSystemLoader(_TEMPLATE_DIR), autoescape=True)
    html = env.get_template("report.html").render(
        leads=sorted_leads,
        date=date_str,
        sources=sources,
    )

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"leads-{date_str}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return path
