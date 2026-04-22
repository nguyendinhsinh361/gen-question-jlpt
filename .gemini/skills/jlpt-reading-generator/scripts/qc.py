#!/usr/bin/env python3
"""
QC checklist — chạy tất cả check tự động, log PASS/FAIL từng mục.
Usage:
    python3 qc.py --html <file> --level N5
    python3 qc.py --html <file> --level N5 --csv sheets/N5.csv --row-id N5_abc123
"""
import argparse, csv, os, re, sys
from html.parser import HTMLParser
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────

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

def count_body_chars(html):
    ext = BodyTextExtractor()
    ext.feed(html)
    return len(re.sub(r'[ \t\n\r\u3000]', '', ''.join(ext.texts)))


CHAR_RANGE = {
    "N1": (660, 740), "N2": (660, 740), "N3": (560, 640),
    "N4": (370, 430), "N5": (230, 280),
}

RUBY_RANGE = {
    "N1": (3, 15), "N2": (5, 20), "N3": (5, 20),
    "N4": (0, 8), "N5": (0, 5),
}


# ── Checks ───────────────────────────────────────────────────────────

def check_all(html_path, level, csv_path=None, row_id=None):
    html = Path(html_path).read_text(encoding='utf-8')
    results = []
    all_pass = True

    def log(num, name, passed, detail=""):
        nonlocal all_pass
        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_pass = False
        msg = f"  [{num:>2}] {status} — {name}"
        if detail:
            msg += f"  ({detail})"
        print(msg)
        results.append({"num": num, "name": name, "pass": passed, "detail": detail})

    print(f"\n{'='*60}")
    print(f"  QC: {os.path.basename(html_path)}  |  Level: {level}")
    print(f"{'='*60}")

    # ── PHẦN A: HTML ─────────────────────────────────────────────

    print(f"\n  ── PHẦN A: HTML ──")

    # 1. Char count
    count = count_body_chars(html)
    lo, hi = CHAR_RANGE[level]
    log(1, "Char count", lo <= count <= hi, f"{count} chars, range {lo}-{hi}")

    # 2. Flow text — no 。<br>
    br_count = len(re.findall(r'。\s*<br\s*/?>', html))
    log(2, "Flow text (no 。<br>)", br_count == 0, f"found {br_count}" if br_count else "")

    # 3. Container CSS — no margin:auto, no min-height
    has_auto = bool(re.search(r'margin:\s*0\s+auto', html))
    has_minh = bool(re.search(r'min-height', html))
    issues = []
    if has_auto: issues.append("margin:auto")
    if has_minh: issues.append("min-height")
    log(3, "Container CSS", not has_auto and not has_minh,
        ", ".join(issues) if issues else "")

    # 4. Has .container element
    has_container = bool(re.search(r'class="[^"]*container[^"]*"', html))
    log(4, ".container element", has_container, "" if has_container else "missing .container div")

    # 5. White background in CSS
    has_bg = bool(re.search(r'background\s*:\s*#fff', html))
    log(5, "White background CSS", has_bg, "" if has_bg else "missing background:#fff")

    # 6. Furigana format — no parentheses
    paren = re.findall(r'[\u4e00-\u9fff]+[（(][ぁ-ん]+[）)]', html)
    bracket = re.findall(r'[\u4e00-\u9fff]+【[ぁ-ん]+】', html)
    bad = paren + bracket
    log(6, "Furigana format (no parentheses)", len(bad) == 0,
        f"found: {bad[:3]}" if bad else "")

    # 7. Ruby has <rt>
    ruby_blocks = re.findall(r'<ruby>(.*?)</ruby>', html, re.DOTALL)
    missing_rt = [b.strip() for b in ruby_blocks if '<rt>' not in b]
    log(7, "Ruby has <rt>", len(missing_rt) == 0,
        f"missing rt in: {missing_rt[:3]}" if missing_rt else "")

    # 8. Ruby count in range
    ruby_count = len(re.findall(r'<ruby>', html))
    rlo, rhi = RUBY_RANGE[level]
    log(8, "Ruby count", rlo <= ruby_count <= rhi,
        f"{ruby_count} rubies, range {rlo}-{rhi}")

    # 9. Table layout
    tables = re.findall(r'<table', html)
    has_fixed = bool(re.search(r'table-layout\s*:\s*fixed', html))
    if tables:
        log(9, "Table layout fixed", has_fixed,
            f"{len(tables)} table(s)" + ("" if has_fixed else ", missing table-layout:fixed"))
    else:
        log(9, "Table layout fixed", True, "no tables (skip)")

    # 10. Has Japanese content symbols
    symbols = re.findall(r'[○×△※★◆◎【】]', html)
    log(10, "Japanese symbols (○×△※【】)", len(symbols) > 0,
        f"found {len(symbols)}" if symbols else "none found — consider adding")

    # ── PHẦN B: CÂU HỎI (from CSV) ─────────────────────────────

    if csv_path and row_id and os.path.exists(csv_path):
        print(f"\n  ── PHẦN B: CÂU HỎI (CSV) ──")

        row = None
        with open(csv_path, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r.get('_id') == row_id:
                    row = r
                    break

        if not row:
            log(11, "CSV row found", False, f"_id={row_id} not in {csv_path}")
        else:
            log(11, "CSV row found", True, f"_id={row_id}")

            # 12. Q1 exists
            q1 = row.get('question_1', '').strip()
            log(12, "Q1 exists", len(q1) > 0, f"{len(q1)} chars" if q1 else "empty")

            # 13. Q1 has named character (not Aさん/Bさん)
            has_name_q1 = bool(re.search(r'[\u4e00-\u9fff\u30a0-\u30ff]{2,}さん', q1)) if q1 else False
            has_ab = bool(re.search(r'[A-Zａ-ｚ]さん', q1)) if q1 else False
            log(13, "Q1 named character", has_name_q1 and not has_ab,
                "has real name" if has_name_q1 and not has_ab else "missing or uses A/Bさん")

            # 14. A1 has 4 options
            a1 = row.get('answer_1', '').strip()
            opts1 = [x.strip() for x in a1.split('\n') if x.strip()] if a1 else []
            log(14, "A1 has 4 options", len(opts1) == 4, f"{len(opts1)} options")

            # 15. correct_answer_1 is integer 1-4
            ca1 = row.get('correct_answer_1', '').strip()
            is_int = ca1 in ('1', '2', '3', '4')
            log(15, "correct_answer_1 valid", is_int, f"value={ca1}")

            # 16. Options roughly equal length
            if len(opts1) == 4:
                lens = [len(o) for o in opts1]
                ratio = max(lens) / max(min(lens), 1)
                log(16, "A1 options equal length", ratio < 2.5,
                    f"lengths={lens}, ratio={ratio:.1f}")
            else:
                log(16, "A1 options equal length", False, "need 4 options first")

            # Q2 (N1-N4 only)
            if level != "N5":
                q2 = row.get('question_2', '').strip()
                log(17, "Q2 exists", len(q2) > 0, f"{len(q2)} chars" if q2 else "empty")

                a2 = row.get('answer_2', '').strip()
                opts2 = [x.strip() for x in a2.split('\n') if x.strip()] if a2 else []
                log(18, "A2 has 4 options", len(opts2) == 4, f"{len(opts2)} options")

                ca2 = row.get('correct_answer_2', '').strip()
                log(19, "correct_answer_2 valid", ca2 in ('1', '2', '3', '4'), f"value={ca2}")

            # 20. Explanations exist
            exp_vn = row.get('explain_vn_1', '').strip()
            exp_en = row.get('explain_en_1', '').strip()
            log(20, "Explanations exist", len(exp_vn) > 0 and len(exp_en) > 0,
                f"vn={len(exp_vn)}ch, en={len(exp_en)}ch")

    # ── PHẦN C: ẢNH ─────────────────────────────────────────────

    stem = Path(html_path).stem
    img_candidates = [
        f"assets/img/tim_thong_tin/{stem}.png",
        os.path.join(os.path.dirname(html_path), '..', '..', 'img', 'tim_thong_tin', f"{stem}.png"),
    ]
    img_path = None
    for p in img_candidates:
        if os.path.exists(p):
            img_path = p
            break

    if img_path:
        print(f"\n  ── PHẦN C: ẢNH ──")
        size_kb = os.path.getsize(img_path) // 1024
        log(21, "Screenshot exists", True, f"{img_path} ({size_kb}KB)")

        # Basic size check — image shouldn't be too wide (>750) or too small
        try:
            # Try reading image dimensions without PIL
            with open(img_path, 'rb') as f:
                data = f.read(32)
                if data[:8] == b'\x89PNG\r\n\x1a\n':
                    w = int.from_bytes(data[16:20], 'big')
                    h = int.from_bytes(data[20:24], 'big')
                    log(22, "Image dimensions", 680 <= w <= 720,
                        f"{w}x{h}px" + ("" if 680 <= w <= 720 else f" — expected ~700px wide"))
                else:
                    log(22, "Image dimensions", False, "not a valid PNG")
        except Exception as e:
            log(22, "Image dimensions", False, str(e))
    else:
        print(f"\n  ── PHẦN C: ẢNH ──")
        log(21, "Screenshot exists", False, "not found — run screenshot.py first")

    # ── SUMMARY ──────────────────────────────────────────────────

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    print(f"\n{'='*60}")
    if all_pass:
        print(f"  🎉 ALL PASSED ({passed}/{total})")
    else:
        failed = [r for r in results if not r["pass"]]
        print(f"  ⚠️  {len(failed)} FAILED / {total} total")
        for r in failed:
            print(f"     [{r['num']:>2}] {r['name']}: {r['detail']}")
    print(f"{'='*60}\n")

    return all_pass


def main():
    parser = argparse.ArgumentParser(description="QC checklist — PASS/FAIL cho từng mục")
    parser.add_argument("--html", required=True, help="HTML file to check")
    parser.add_argument("--level", required=True, choices=["N1","N2","N3","N4","N5"])
    parser.add_argument("--csv", help="CSV file to check questions")
    parser.add_argument("--row-id", help="_id of the row in CSV")
    args = parser.parse_args()

    if not os.path.exists(args.html):
        print(f"❌ File not found: {args.html}", file=sys.stderr)
        sys.exit(1)

    all_pass = check_all(args.html, args.level, args.csv, args.row_id)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
