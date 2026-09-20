# -*- coding: utf-8 -*-
import os, re, glob, subprocess, sys
from PIL import Image
import markdown

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, "CP 1 - Offensive - HTB 3d01bdecf154808297fcc448639ffe32.md")
COMP = os.path.join(BASE, "compressed")
os.makedirs(COMP, exist_ok=True)

# ---- 1. Compress images ----
def compress(png_path, out_path, max_w=1100, quality=80):
    im = Image.open(png_path)
    if im.width > max_w:
        h = int(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.LANCZOS)
    if im.mode == 'RGBA':
        bg = Image.new('RGB', im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[3] if im.mode == 'RGBA' else None)
        im = bg
    elif im.mode != 'RGB':
        im = im.convert('RGB')
    im.save(out_path, 'JPEG', quality=quality, optimize=True)

total_in = total_out = 0
for f in sorted(glob.glob(os.path.join(BASE, "*.png"))):
    name = os.path.splitext(os.path.basename(f))[0] + '.jpg'
    out = os.path.join(COMP, name)
    compress(f, out)
    total_in += os.path.getsize(f)
    total_out += os.path.getsize(out)
print(f"images: {total_in//1024}KB -> {total_out//1024}KB")

# ---- 2. Read markdown ----
text = open(MD, encoding='utf-8').read()

# split cover (title + integrantes) from body
lines = text.split('\n')
# find first body heading
body_start = None
for i, l in enumerate(lines):
    if l.startswith('### '):
        body_start = i
        break
cover_lines = lines[:body_start]
body_lines = lines[body_start:]

cover_md = '\n'.join(cover_lines).strip()
body_md = '\n'.join(body_lines).strip()

md_conv = markdown.Markdown(extensions=['fenced_code', 'sane_lists', 'tables'])
body_html = md_conv.convert(body_md)
# point images at compressed folder (and .jpg extension)
body_html = re.sub(r'src="(image[^"]*)\.png"', r'src="compressed/\1.jpg"', body_html)

# ---- 3. Build cover ----
# cover_md looks like:
#   # CP 1 - Offensive - HTB
#   ---
#   - **Integrantes:**
#       - Ana Luiza Azevedo Morais
#           - **RM:** 565771
#   ...
title = "CP 1 - Offensive - HTB"
m = re.search(r'^#\s+(.+)$', cover_md, re.M)
if m:
    title = m.group(1).strip()

members = []
for mm in re.finditer(r'-\s+([A-Za-zÀ-ú .]+?)\s*\n\s*-\s+\*{0,2}RM:\*{0,2}\s*(\d+)', cover_md):
    members.append((mm.group(1).strip(), mm.group(2).strip()))

members_html = ''.join(
    f'<div class="member"><span class="mname">{n}</span><span class="mrm">RM {r}</span></div>'
    for n, r in members
)

# ---- 4. HTML template ----
html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  @page {{
    size: A4;
    margin: 16mm 15mm 18mm 15mm;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', 'Calibri', system-ui, sans-serif;
    color: #20242a;
    line-height: 1.55;
    font-size: 11pt;
    margin: 0;
  }}

  /* cover */
  .cover {{
    text-align: center;
    padding-top: 55mm;
    page-break-after: always;
  }}
  .cover .kicker {{
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 10pt;
    color: #7a8290;
    margin-bottom: 10mm;
  }}
  .cover h1 {{
    font-size: 26pt;
    margin: 0 0 6mm;
    color: #11151c;
    line-height: 1.15;
  }}
  .cover .sub {{
    color: #5a6370;
    font-size: 12pt;
    margin-bottom: 18mm;
  }}
  .members {{
    display: inline-block;
    text-align: left;
    border-top: 1px solid #e3e6ea;
    padding-top: 8mm;
    margin-top: 4mm;
  }}
  .member {{
    display: flex;
    justify-content: space-between;
    gap: 12mm;
    padding: 1.6mm 0;
    font-size: 11.5pt;
  }}
  .mname {{ color: #20242a; font-weight: 600; }}
  .mrm {{ color: #7a8290; font-family: Consolas, monospace; }}

  /* body */
  h3 {{
    color: #11151c;
    font-size: 14pt;
    margin: 22px 0 8px;
    padding-bottom: 4px;
    border-bottom: 2px solid #e8ebef;
    page-break-after: avoid;
  }}
  p {{ margin: 6px 0; }}
  strong {{ color: #11151c; }}
  hr {{ border: none; border-top: 1px solid #eceff2; margin: 20px 0; }}
  ul {{ margin: 6px 0; padding-left: 22px; }}
  li {{ margin: 3px 0; }}

  pre {{
    background: #0e141b;
    color: #d8dee6;
    padding: 10px 13px;
    border-radius: 6px;
    font-family: Consolas, 'Courier New', monospace;
    font-size: 9.5pt;
    line-height: 1.45;
    overflow: hidden;
    white-space: pre-wrap;
    word-wrap: break-word;
    page-break-inside: avoid;
    margin: 8px 0;
  }}
  pre code {{
    font-family: inherit;
    color: inherit;
    background: none;
    padding: 0;
  }}
  code {{
    font-family: Consolas, monospace;
    background: #f0f2f5;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9.5pt;
  }}

  img {{
    display: block;
    max-width: 100%;
    height: auto;
    margin: 10px auto;
    border: 1px solid #dfe3e8;
    border-radius: 5px;
    page-break-inside: avoid;
  }}
</style>
</head>
<body>
<div class="cover">
  <div class="kicker">FIAP &middot; Defesa Cibern&eacute;tica &middot; Offensive Security</div>
  <h1>{title}</h1>
  <div class="sub">CheckPoint 1, relat&oacute;rio t&eacute;cnico</div>
  <div class="members">{members_html}</div>
</div>
{body_html}
</body>
</html>
"""

html_path = os.path.join(BASE, "report.html")
open(html_path, 'w', encoding='utf-8').write(html)
print("HTML written:", html_path)

# ---- 5. Render PDF via headless Chrome ----
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
pdf_out = os.path.join(BASE, "..", "..", "CP 1 - Offensive - HTB - limpo.pdf")
pdf_out = os.path.abspath(pdf_out)
url = "file:///" + html_path.replace("\\", "/")

cmd = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--virtual-time-budget=8000",
    f"--print-to-pdf={pdf_out}",
    url,
]
r = subprocess.run(cmd, capture_output=True, text=True)
print("chrome rc:", r.returncode)
if r.returncode != 0:
    print("STDERR:", r.stderr[:2000])
else:
    print("PDF written:", pdf_out, os.path.getsize(pdf_out) // 1024, "KB")
