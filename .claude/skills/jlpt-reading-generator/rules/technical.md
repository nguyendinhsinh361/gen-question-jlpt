# Rules: HTML Template, Clean HTML, CSV Schema (R9, R10, R11)

## R9. HTML Template

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Title]</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
        html, body { background: #fff !important; margin: 0 !important; padding: 0 !important; }
        body { font-family: 'Noto Sans JP', sans-serif; color: #000; line-height: 2; word-break: keep-all; line-break: strict; overflow-wrap: break-word; }
        .container { width: 700px; margin: 0; background: #fff; padding: 6px 8px; box-sizing: border-box; }
        table { width: 100%; table-layout: fixed; }
        td, th { overflow-wrap: break-word; }
        .container > * { max-width: 100%; }
        ruby { ruby-align: center; ruby-position: over; vertical-align: baseline; }
        ruby rt { font-size: 0.55em; color: #333; letter-spacing: 0.02em; line-height: 1; vertical-align: top; }
    </style>
</head>
<body>
<div class="container">
    <!-- content -->
</div>
</body>
</html>
```

---

## R10. Clean HTML & Screenshot

### Clean HTML (`text_read`)

```python
class CleanHTMLExtractor(HTMLParser):
    SKIP_TAGS = ('style', 'script')   # ruby, rt được GIỮ NGUYÊN
    def __init__(self):
        super().__init__()
        self.result, self.skip_depth = [], 0
        self.in_body, self.body_done = False, False
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.in_body = True; return
        if not self.in_body or self.body_done: return
        if tag in self.SKIP_TAGS: self.skip_depth += 1; return
        if self.skip_depth > 0: return
        self.result.append(f'<{tag}>')
    def handle_endtag(self, tag):
        if tag == 'body': self.body_done = True; return
        if not self.in_body or self.body_done: return
        if tag in self.SKIP_TAGS: self.skip_depth -= 1; return
        if self.skip_depth > 0: return
        self.result.append(f'</{tag}>')
    def handle_data(self, data):
        if not self.in_body or self.body_done or self.skip_depth > 0: return
        self.result.append(data)

def clean_html(full_html):
    ext = CleanHTMLExtractor()
    ext.feed(full_html)
    raw = ''.join(ext.result)
    raw = re.sub(r'\s+', ' ', raw)
    raw = re.sub(r'\s*<', '<', raw)
    raw = re.sub(r'>\s*', '>', raw)
    raw = re.sub(r'<(\w+)></\1>', '', raw)
    return raw.strip()
```

### Character count (`count_body_chars()`)

```python
from html.parser import HTMLParser
import re

class BodyTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts, self.skip_depth, self.in_body = [], 0, False
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.in_body = True
        if tag in ('rt', 'style', 'script'): self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag in ('rt', 'style', 'script'): self.skip_depth -= 1
    def handle_data(self, d):
        if self.in_body and self.skip_depth == 0: self.texts.append(d)

def count_body_chars(html_string):
    ext = BodyTextExtractor()
    ext.feed(html_string)
    return len(re.sub(r'[ \t\n\r\u3000]', '', ''.join(ext.texts)))
```

### Screenshot

> **⛔ NGHIÊM CẤM tự viết code Playwright screenshot. Chạy script có sẵn.**

```bash
# Chụp 1 file:
python3 .claude/skills/jlpt-reading-generator/scripts/screenshot.py \
  --html assets/html/tim_thong_tin/{LEVEL}_{uuid}.html \
  --png  assets/img/tim_thong_tin/{LEVEL}_{uuid}.png

# Chụp cả thư mục:
python3 .claude/skills/jlpt-reading-generator/scripts/screenshot.py \
  --html-dir assets/html/tim_thong_tin/ \
  --png-dir  assets/img/tim_thong_tin/
```

---

## R11. CSV Schema & File Naming

45 columns matching `input/question_sheet.csv`:

| Column | Value |
|--------|-------|
| `_id` | `{LEVEL}_{uuid.uuid4().hex}` |
| `level` | N1-N5 |
| `tag` | Format label |
| `jp_char_count` | `count_body_chars()` |
| `kind` | `tìm thông tin` |
| `general_image` | `assets/img/tim_thong_tin/{id}.png` |
| `text_read` | Clean HTML (giữ ruby/rt) |
| `question_label_{i}` | `question_information_search` |
| `question_{i}` | Question text |
| `answer_{i}` | 4 options `\n` separated, KHÔNG số thứ tự |
| `correct_answer_{i}` | Integer `1`-`4` (KHÔNG `2.0`) |
| `explain_vn_{i}` / `explain_en_{i}` | Explanations |

---

## QC Automation Scripts

```python
import re
from pathlib import Path

def check_html(html_path: str, level: str) -> dict:
    """Kiểm tra tự động các tiêu chí đo được."""
    html = Path(html_path).read_text(encoding='utf-8')
    results = {}
    
    # TC1: Character count (min AND max)
    char_count = count_body_chars(html)
    char_range = {
        "N1": (660, 740), "N2": (660, 740), "N3": (560, 640),
        "N4": (370, 430), "N5": (230, 280)
    }
    lo, hi = char_range[level]
    results["TC1_chars"] = {
        "count": char_count, "range": f"{lo}-{hi}",
        "pass": lo <= char_count <= hi
    }
    
    # TC3a: Flow text
    br_in_prose = len(re.findall(r'。\s*<br\s*/?>', html))
    results["TC3_flow_text"] = {"br_in_prose": br_in_prose, "pass": br_in_prose == 0}
    
    # TC3b: Container CSS
    has_margin_auto = bool(re.search(r'margin:\s*0\s+auto', html))
    has_min_height = bool(re.search(r'min-height', html))
    results["TC3_container"] = {"pass": not has_margin_auto and not has_min_height}
    
    # TC5a: Ruby count
    ruby_count = len(re.findall(r'<ruby>', html))
    results["TC5_ruby_count"] = {"count": ruby_count}
    
    # TC5b: Wrong furigana format (check parentheses)
    paren_furigana = re.findall(r'[\u4e00-\u9fff]+[（(][ぁ-ん]+[）)]', html)
    bracket_furigana = re.findall(r'[\u4e00-\u9fff]+【[ぁ-ん]+】', html)
    results["TC5_furigana_format"] = {
        "paren_found": paren_furigana,
        "bracket_found": bracket_furigana,
        "pass": len(paren_furigana) == 0 and len(bracket_furigana) == 0
    }
    
    # TC5c: Ruby without rt (check each <ruby>...</ruby> block has <rt> inside)
    ruby_blocks = re.findall(r'<ruby>(.*?)</ruby>', html, re.DOTALL)
    ruby_without_rt = [b for b in ruby_blocks if '<rt>' not in b]
    results["TC5_ruby_has_rt"] = {
        "missing_rt": ruby_without_rt,
        "pass": len(ruby_without_rt) == 0
    }
    
    return results
```

---

## Bundled Scripts

```bash
# Đếm ký tự:
python3 .claude/skills/jlpt-reading-generator/scripts/process_html.py --count-only --file <html-file>

# Chụp ảnh + tạo CSV (all-in-one):
python3 .claude/skills/jlpt-reading-generator/scripts/process_html.py \
  --file <html-file> \
  --img-dir assets/img/tim_thong_tin \
  --csv sheets/<file>.csv
```
