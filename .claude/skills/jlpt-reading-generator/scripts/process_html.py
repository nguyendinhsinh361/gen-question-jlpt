#!/usr/bin/env python3
"""
Process generated JLPT HTML files:
- Count visible body characters (JLPT standard)
- Extract clean HTML (no attributes/classes/whitespace)
- Capture screenshots via Playwright
- Update CSV with results

Usage:
    python process_html.py --html-dir assets/html/tim_thong_tin --img-dir assets/img/tim_thong_tin --csv sheets/samples_v5.csv
    python process_html.py --file assets/html/tim_thong_tin/n1_4.html  # process single file
"""

import argparse
import asyncio
import csv
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


# ── Character Counting ──────────────────────────────────────────────

class BodyTextExtractor(HTMLParser):
    """Extracts visible text from HTML body, skipping <rt>, <style>, <script>."""
    def __init__(self):
        super().__init__()
        self.texts = []
        self.skip_depth = 0
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.in_body = True
        if tag in ('rt', 'style', 'script'):
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in ('rt', 'style', 'script'):
            self.skip_depth -= 1

    def handle_data(self, d):
        if self.in_body and self.skip_depth == 0:
            self.texts.append(d)


def count_body_chars(html_string):
    """Count all visible characters in HTML body, excluding whitespace.
    This is the JLPT standard — counts JP, Latin, numbers, punctuation, everything."""
    ext = BodyTextExtractor()
    ext.feed(html_string)
    text = ''.join(ext.texts)
    return len(re.sub(r'[ \t\n\r\u3000]', '', text))


# ── Clean HTML Extraction ───────────────────────────────────────────

class CleanHTMLExtractor(HTMLParser):
    """Extract body HTML with all attributes, classes, styles stripped.
    Skips rt/style/script content entirely."""
    def __init__(self):
        super().__init__()
        self.result = []
        self.skip_depth = 0
        self.in_body = False
        self.body_done = False

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.in_body = True
            return
        if not self.in_body or self.body_done:
            return
        if tag in ('style', 'script'):
            self.skip_depth += 1
            return
        if self.skip_depth > 0:
            return
        self.result.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if tag == 'body':
            self.body_done = True
            return
        if not self.in_body or self.body_done:
            return
        if tag in ('style', 'script'):
            self.skip_depth -= 1
            return
        if self.skip_depth > 0:
            return
        self.result.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.in_body or self.body_done or self.skip_depth > 0:
            return
        self.result.append(data)


def clean_html(full_html):
    """Extract clean body HTML: no attributes, no classes, collapsed whitespace."""
    ext = CleanHTMLExtractor()
    ext.feed(full_html)
    raw = ''.join(ext.result)
    raw = re.sub(r'\s+', ' ', raw)
    raw = re.sub(r'\s*<', '<', raw)
    raw = re.sub(r'>\s*', '>', raw)
    raw = re.sub(r'<(\w+)></\1>', '', raw)  # remove empty tags
    return raw.strip()


# ── Screenshot Capture ──────────────────────────────────────────────

async def capture_screenshots(html_files, img_dir):
    """Capture screenshots cropped tight to content — no whitespace/gray borders."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Installing playwright...")
        os.system("pip install playwright --break-system-packages -q")
        os.system("python3 -m playwright install chromium")
        from playwright.async_api import async_playwright

    os.makedirs(img_dir, exist_ok=True)
    results = {}

    JS_MEASURE = """
        (() => {
            const c = document.querySelector('.container');
            if (!c) return null;
            const cRect = c.getBoundingClientRect();
            let maxBottom = cRect.top;
            for (const ch of c.children) {
                const r = ch.getBoundingClientRect();
                if (r.bottom > maxBottom) maxBottom = r.bottom;
            }
            return {
                x: Math.round(cRect.left),
                y: Math.round(cRect.top),
                width: Math.round(cRect.width),
                height: Math.ceil(maxBottom - cRect.top) + 8
            };
        })()
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for html_path in html_files:
            name = Path(html_path).stem
            img_path = os.path.join(img_dir, f"{name}.png")

            try:
                if not os.path.exists(html_path):
                    print(f"  ❌ File not found: {html_path}", file=sys.stderr)
                    continue

                page = await browser.new_page(viewport={"width": 700, "height": 800})
                print(f"  📄 Loading: {name}.html")
                await page.goto(f"file://{os.path.abspath(html_path)}", wait_until="networkidle")
                await page.wait_for_timeout(1500)
                # Force white background
                await page.evaluate("""
                    document.documentElement.style.cssText += 'background:#fff!important;';
                    document.body.style.cssText += 'background:#fff!important;';
                """)
                # Measure content height
                clip = await page.evaluate(JS_MEASURE)
                if clip is None:
                    print(f"  ❌ No .container element in {name}.html", file=sys.stderr)
                    await page.close()
                    continue

                print(f"  📐 Measure: {clip['width']}x{clip['height']}px")
                # Resize viewport to fit content (avoid clipping long pages)
                await page.set_viewport_size({"width": 700, "height": clip["height"] + 20})
                await page.wait_for_timeout(300)
                # Re-measure after resize
                clip = await page.evaluate(JS_MEASURE)
                await page.screenshot(path=img_path, clip=clip)
                await page.close()

                results[html_path] = img_path
                size_kb = os.path.getsize(img_path) // 1024
                print(f"  ✅ {name}.png — {clip['width']}x{clip['height']}px ({size_kb}KB)")
            except Exception as e:
                print(f"  ❌ Error capturing {name}.html: {e}", file=sys.stderr)

        await browser.close()

    return results


# ── CSV Operations ──────────────────────────────────────────────────

CSV_FIELDNAMES = [
    '_id', 'level', 'tag', 'jp_char_count', 'kind', 'general_audio', 'general_image',
    'text_read', 'text_read_vn', 'text_read_en',
    'question_label_1', 'question_1', 'question_image_1', 'answer_1', 'correct_answer_1', 'explain_vn_1', 'explain_en_1',
    'question_label_2', 'question_2', 'question_image_2', 'answer_2', 'correct_answer_2', 'explain_vn_2', 'explain_en_2',
    'question_label_3', 'question_3', 'question_image_3', 'answer_3', 'correct_answer_3', 'explain_vn_3', 'explain_en_3',
    'question_label_4', 'question_4', 'question_image_4', 'answer_4', 'correct_answer_4', 'explain_vn_4', 'explain_en_4',
    'question_label_5', 'question_5', 'question_image_5', 'answer_5', 'correct_answer_5', 'explain_vn_5', 'explain_en_5',
]


def parse_filename(filename):
    """Extract level and id from filename like N5_uuid.html → ('N5', 'N5_uuid')"""
    stem = Path(filename).stem
    match = re.match(r'([nN]\d)_([0-9a-fA-F]+)', stem)
    if match:
        level = match.group(1).upper()
        return level, stem
    return None, stem


def build_csv_row(html_path, img_path, tag=''):
    """Build a CSV row dict from an HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        full_html = f.read()

    level, name = parse_filename(html_path)
    char_count = count_body_chars(full_html)
    cleaned = clean_html(full_html)

    # Make paths relative
    img_rel = img_path
    if os.path.isabs(img_path):
        # Try to make relative to CWD
        try:
            img_rel = os.path.relpath(img_path)
        except ValueError:
            img_rel = img_path

    row = {field: '' for field in CSV_FIELDNAMES}
    row.update({
        '_id': name,  # e.g. N5_c1da8a43ccaa4701b9f228b7f75ae5f1
        'level': level or '',
        'tag': tag,
        'jp_char_count': str(char_count),
        'kind': 'tìm thông tin',
        'general_image': img_rel,
        'text_read': cleaned,
    })
    return row


def append_to_csv(csv_path, rows):
    """Append rows to existing CSV or create new one."""
    existing_rows = []

    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)

    # Skip rows whose _id already exists in CSV (avoid duplicates)
    existing_ids = {r['_id'] for r in existing_rows if r.get('_id')}
    new_rows = [r for r in rows if r.get('_id') not in existing_ids]

    if len(new_rows) < len(rows):
        skipped = len(rows) - len(new_rows)
        print(f"  Skipped {skipped} duplicate row(s)")

    all_rows = existing_rows + new_rows

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"  CSV: {len(rows)} rows added → {csv_path} (total: {len(all_rows)})")


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Process JLPT HTML files')
    parser.add_argument('--html-dir', help='Directory with HTML files')
    parser.add_argument('--img-dir', default='assets/img/tim_thong_tin', help='Output directory for screenshots')
    parser.add_argument('--csv', default='sheets/samples_v5.csv', help='CSV file path')
    parser.add_argument('--file', help='Process a single HTML file')
    parser.add_argument('--no-screenshot', action='store_true', help='Skip screenshot capture')
    parser.add_argument('--count-only', action='store_true', help='Only count characters')
    args = parser.parse_args()

    # Collect HTML files
    if args.file:
        html_files = [args.file]
    elif args.html_dir:
        html_files = sorted(
            [os.path.join(args.html_dir, f) for f in os.listdir(args.html_dir) if f.endswith('.html')],
        )
    else:
        print("Provide --html-dir or --file")
        sys.exit(1)

    print(f"Processing {len(html_files)} file(s)...\n")

    # Count characters
    for f in html_files:
        with open(f, 'r', encoding='utf-8') as fh:
            html = fh.read()
        chars = count_body_chars(html)
        level, name = parse_filename(f)
        print(f"  {name}: {chars} chars ({level})")

    if args.count_only:
        return

    # Capture screenshots
    if not args.no_screenshot:
        print("\nCapturing screenshots...")
        screenshot_map = asyncio.run(capture_screenshots(html_files, args.img_dir))
    else:
        screenshot_map = {f: os.path.join(args.img_dir, Path(f).stem + '.png') for f in html_files}

    # Build CSV rows
    print("\nBuilding CSV rows...")
    rows = []
    for html_path in html_files:
        img_path = screenshot_map.get(html_path, '')
        row = build_csv_row(html_path, img_path)
        rows.append(row)

    append_to_csv(args.csv, rows)
    print("\nDone!")


if __name__ == '__main__':
    main()
