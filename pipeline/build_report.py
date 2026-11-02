"""Build distributable files for a report version: HTML, A4 PDF, and per-page PNG images.

  python -m pipeline.build_report v1.0            # both languages
  python -m pipeline.build_report v1.1 --lang zh --images

Requires: pandoc, Python Playwright with Chromium, and a CJK font (fonts-noto-cjk on Ubuntu).
PNG pages need poppler-utils (pdftoppm). No author names are added: reports are credited to the project.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

from pipeline.common import REPORTS, load_yaml

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
html { font-size: 10.5pt; }
body { font-family: "Noto Serif", "Noto Serif CJK SC", "Source Han Serif SC", serif; line-height: 1.55; color: #1b1b1b; max-width: 100%; }
:lang(zh) body, body:lang(zh) { font-family: "Noto Sans CJK SC", "Source Han Sans SC", "Noto Serif CJK SC", sans-serif; }
h1 { font-size: 22pt; line-height: 1.2; margin: 0 0 4mm; }
h2 { font-size: 15pt; margin: 8mm 0 2mm; border-bottom: 0.4pt solid #bbb; padding-bottom: 1mm; break-after: avoid; }
h3 { font-size: 12pt; margin: 5mm 0 1.5mm; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
a { color: #1f5fa8; text-decoration: none; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 3mm 0; break-inside: auto; }
th, td { border: 0.4pt solid #c8c8c8; padding: 1.2mm 1.6mm; vertical-align: top; }
th { background: #f1f1ef; }
tr { break-inside: avoid; }
img { max-width: 100%; display: block; margin: 3mm auto; break-inside: avoid; }
.meta { color: #555; font-size: 9pt; margin-bottom: 5mm; }
"""


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def build(version: str, lang: str, images: bool) -> list[pathlib.Path]:
    d = REPORTS / version
    meta = load_yaml(d / "meta.yaml")
    md = d / meta["files"][lang]
    out_dir = d / "pdf"
    out_dir.mkdir(exist_ok=True)
    css = d / "pdf" / "_report.css"
    css.write_text(CSS, encoding="utf-8")
    html = d / f"report_{lang}.html"
    title = md.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    run(["pandoc", str(md), "-f", "gfm", "-t", "html5", "--standalone", "--embed-resources",
         "--metadata", f"title={title}", "--metadata", f"lang={'zh-CN' if lang == 'zh' else 'en'}",
         "--css", str(css), "--resource-path", str(d), "-V", "title-block=false", "-o", str(html)])
    # pandoc adds a title block from metadata; the markdown already starts with "# title", so hide pandoc's.
    text = html.read_text(encoding="utf-8").replace('<header id="title-block-header">', '<header id="title-block-header" style="display:none">')
    html.write_text(text, encoding="utf-8")
    pdf = out_dir / f"report_{lang}.pdf"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.goto(html.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(pdf), format="A4", print_background=True, display_header_footer=True,
                 header_template="<span></span>",
                 footer_template=f'<div style="font-size:7pt;color:#777;width:100%;text-align:center;">{version} · '
                                 '<span class="pageNumber"></span>/<span class="totalPages"></span></div>',
                 margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        b.close()
    made = [html, pdf]
    if images:
        img_dir = out_dir / f"pages_{lang}"
        if img_dir.exists():
            shutil.rmtree(img_dir)
        img_dir.mkdir()
        run(["pdftoppm", "-r", "150", "-png", str(pdf), str(img_dir / f"report_{lang}")])
        made.append(img_dir)
    css.unlink()
    return made


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("version")
    ap.add_argument("--lang", choices=["en", "zh", "all"], default="all")
    ap.add_argument("--images", action="store_true")
    a = ap.parse_args(argv)
    langs = ["en", "zh"] if a.lang == "all" else [a.lang]
    for lang in langs:
        for f in build(a.version, lang, a.images):
            print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
