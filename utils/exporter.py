from pathlib import Path
import html

def export_markdown(report_md: str, output_path: Path) -> Path:
    """匯出 Markdown 格式報告"""
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    return output_path

def export_html(report_md: str, title: str = "結業問卷綜合診斷報告書", output_path: Path = None) -> str:
    """將 Markdown 報告轉換為排版精美的可列印 HTML 格式"""
    try:
        import markdown
        html_body = markdown.markdown(report_md, extensions=['tables', 'fenced_code'])
    except ImportError:
        # 簡易 Markdown 解析 (表格、標題、引用、加粗)
        html_body = simple_md_to_html(report_md)

    full_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <title>{html.escape(title)}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
    
    body {{
      font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.7;
      color: #1e293b;
      background-color: #f8fafc;
      margin: 0;
      padding: 40px 20px;
    }}
    .report-container {{
      max-width: 860px;
      margin: 0 auto;
      background: #ffffff;
      padding: 50px 60px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
      border: 1px solid #e2e8f0;
    }}
    h1 {{
      font-size: 1.8rem;
      color: #0f172a;
      border-bottom: 3px solid #6366f1;
      padding-bottom: 12px;
      margin-bottom: 20px;
    }}
    h2 {{
      font-size: 1.35rem;
      color: #1e293b;
      margin-top: 36px;
      margin-bottom: 14px;
      border-left: 4px solid #6366f1;
      padding-left: 12px;
    }}
    h3 {{
      font-size: 1.1rem;
      color: #334155;
      margin-top: 22px;
      margin-bottom: 10px;
    }}
    p, li {{
      font-size: 0.96rem;
      color: #334155;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 0.92rem;
    }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 10px 14px;
      text-align: left;
    }}
    th {{
      background-color: #f1f5f9;
      font-weight: 600;
      color: #0f172a;
    }}
    tr:nth-child(even) {{
      background-color: #f8fafc;
    }}
    blockquote {{
      margin: 16px 0;
      padding: 12px 18px;
      background-color: #f5f3ff;
      border-left: 4px solid #818cf8;
      border-radius: 0 8px 8px 0;
      color: #4338ca;
      font-style: italic;
    }}
    .print-btn {{
      position: fixed;
      bottom: 30px;
      right: 30px;
      background: #6366f1;
      color: #fff;
      border: none;
      padding: 12px 24px;
      border-radius: 30px;
      font-size: 1rem;
      font-weight: 600;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
      cursor: pointer;
    }}
    .print-btn:hover {{
      background: #4f46e5;
    }}
    @media print {{
      body {{
        background: #fff;
        padding: 0;
      }}
      .report-container {{
        box-shadow: none;
        border: none;
        padding: 0;
        max-width: 100%;
      }}
      .print-btn {{
        display: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="report-container">
    {html_body}
  </div>
  <button class="print-btn" onclick="window.print()">🖨️ 列印 / 另存為 PDF</button>
</body>
</html>"""

    if output_path:
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_html)

    return full_html

def simple_md_to_html(md: str) -> str:
    """輕量 Markdown 轉換器"""
    lines = md.split("\n")
    html_lines = []
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("> *「") or stripped.startswith("> "):
            clean_quote = stripped.replace("> ", "").replace("*", "")
            html_lines.append(f"<blockquote>{clean_quote}</blockquote>")
        elif stripped.startswith("|"):
            if "---" in stripped:
                continue
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            tag = "th" if not in_table else "td"
            if not in_table:
                html_lines.append("<table><thead><tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr></thead><tbody>")
                in_table = True
            else:
                html_lines.append("<tr>" + "".join(f"<td>{c}</td>" for c in cols) + "</tr>")
        elif stripped.startswith("* ") or stripped.startswith("- "):
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif stripped == "---":
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;'>")
        elif stripped:
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append(f"<p>{stripped}</p>")
        else:
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False

    if in_table:
        html_lines.append("</tbody></table>")
        
    return "\n".join(html_lines)
