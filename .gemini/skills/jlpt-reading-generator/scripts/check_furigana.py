#!/usr/bin/env python3
"""
check_furigana.py — Kiểm tra kanji thiếu furigana trong bài JLPT 情報検索

Scan HTML file, extract tất cả kanji, tra level từng ký tự trong kanji_jlpt_sensei.csv,
báo cáo kanji vượt level mà không có <ruby><rt> tag.

Usage:
    python3 check_furigana.py --html <path> --level N5 --kanji-csv input/kanji_jlpt_sensei.csv

Exit code:
    0 = OK (không có kanji thiếu furigana)
    1 = FAIL (có kanji thiếu furigana)
    2 = Error (file không tồn tại, tham số sai...)
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# ── Kanji Unicode range ──────────────────────────────────────────────
def is_kanji(ch: str) -> bool:
    """CJK Unified Ideographs + Extension A (covers JLPT kanji)."""
    cp = ord(ch)
    return (0x4E00 <= cp <= 0x9FFF) or (0x3400 <= cp <= 0x4DBF)

# ── Level comparison ─────────────────────────────────────────────────
LEVEL_RANK = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}

def level_exceeds(kanji_level: str, target_level: str) -> bool:
    """True nếu kanji_level khó hơn target_level (N1 > N2 > ... > N5)."""
    return LEVEL_RANK.get(kanji_level, 0) < LEVEL_RANK.get(target_level, 0)

# ── Load kanji CSV ───────────────────────────────────────────────────
def load_kanji_csv(csv_path: str) -> dict:
    """Return dict {kanji_char: level_str}."""
    mapping = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mapping[row["kanji"]] = row["jlpt"]
    return mapping

# ── Extract ruby kanji (already have furigana) ───────────────────────
def extract_ruby_kanji(html: str) -> set:
    """Return set of kanji chars that are inside <ruby>...<rt>...</rt></ruby>."""
    # Match <ruby>CONTENT<rt>READING</rt></ruby>
    ruby_pattern = re.compile(r"<ruby>(.*?)<rt>.*?</rt></ruby>", re.DOTALL)
    kanji_set = set()
    for m in ruby_pattern.finditer(html):
        content = m.group(1)
        for ch in content:
            if is_kanji(ch):
                kanji_set.add(ch)
    return kanji_set

# ── Extract visible kanji without ruby ───────────────────────────────
def extract_bare_kanji(html: str) -> dict:
    """
    Return dict {kanji_char: [context_words]} for kanji visible in body
    that are NOT inside <ruby> tags.
    """
    # Remove everything inside <ruby>...</ruby>
    no_ruby = re.sub(r"<ruby>.*?</ruby>", "□", html, flags=re.DOTALL)

    # Extract body content only (between <body> and </body>)
    body_match = re.search(r"<body[^>]*>(.*?)</body>", no_ruby, re.DOTALL)
    if not body_match:
        return {}
    body = body_match.group(1)

    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", body)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Find kanji and their context (surrounding word)
    kanji_contexts = {}
    for i, ch in enumerate(text):
        if is_kanji(ch):
            # Extract surrounding word (consecutive kanji + kana)
            start = i
            while start > 0 and (is_kanji(text[start - 1]) or _is_kana(text[start - 1])):
                start -= 1
            end = i + 1
            while end < len(text) and (is_kanji(text[end]) or _is_kana(text[end])):
                end += 1
            word = text[start:end].strip()

            if ch not in kanji_contexts:
                kanji_contexts[ch] = set()
            if word and len(word) <= 10:
                kanji_contexts[ch].add(word)

    return kanji_contexts

def _is_kana(ch: str) -> bool:
    cp = ord(ch)
    return (0x3040 <= cp <= 0x309F) or (0x30A0 <= cp <= 0x30FF)

# ── Main check ───────────────────────────────────────────────────────
def check_furigana(html_path: str, target_level: str, kanji_csv_path: str) -> list:
    """
    Check all kanji in HTML against target level.
    Return list of dicts with problem kanji.
    """
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    kanji_map = load_kanji_csv(kanji_csv_path)
    ruby_kanji = extract_ruby_kanji(html)
    bare_kanji = extract_bare_kanji(html)

    problems = []
    for ch, contexts in sorted(bare_kanji.items()):
        if ch in ruby_kanji:
            # This kanji appears both with and without ruby — still a problem
            # (some occurrences lack furigana)
            pass

        kanji_lv = kanji_map.get(ch, None)

        if kanji_lv is None:
            # Not in JLPT list → treat as above level
            problems.append({
                "kanji": ch,
                "level": "N/A",
                "target": target_level,
                "contexts": sorted(contexts),
                "reason": "Không có trong kanji_jlpt_sensei.csv → mặc định cần furigana",
            })
        elif level_exceeds(kanji_lv, target_level):
            problems.append({
                "kanji": ch,
                "level": kanji_lv,
                "target": target_level,
                "contexts": sorted(contexts),
                "reason": f"{kanji_lv} > {target_level}",
            })

    return problems

# ── CLI ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Kiểm tra kanji thiếu furigana trong bài JLPT"
    )
    parser.add_argument("--html", required=True, help="Path to HTML file")
    parser.add_argument("--level", required=True, choices=["N1", "N2", "N3", "N4", "N5"],
                        help="Target JLPT level")
    parser.add_argument("--kanji-csv", default="input/kanji_jlpt_sensei.csv",
                        help="Path to kanji_jlpt_sensei.csv (default: input/kanji_jlpt_sensei.csv)")
    args = parser.parse_args()

    if not Path(args.html).exists():
        print(f"❌ File không tồn tại: {args.html}", file=sys.stderr)
        sys.exit(2)
    if not Path(args.kanji_csv).exists():
        print(f"❌ Kanji CSV không tồn tại: {args.kanji_csv}", file=sys.stderr)
        sys.exit(2)

    problems = check_furigana(args.html, args.level, args.kanji_csv)

    # Report
    print(f"🔍 Furigana check: {args.html} (Level: {args.level})")
    print("=" * 70)

    if not problems:
        print("✅ PASS — Không có kanji vượt level thiếu furigana")
        sys.exit(0)
    else:
        print(f"❌ FAIL — {len(problems)} kanji vượt level thiếu furigana:\n")
        print("{:<6} {:<8} {:<10} {}".format("Kanji", "Level", "Lý do", "Ngữ cảnh"))
        print("-" * 70)
        for p in problems:
            ctx = ", ".join(p["contexts"][:3]) if p["contexts"] else "—"
            print("{:<6} {:<8} {:<10} {}".format(
                p["kanji"], p["level"], p["reason"], ctx
            ))

        print(f"\n⛔ Sửa: thêm <ruby><rt> cho {len(problems)} kanji trên, hoặc viết hiragana.")
        print("   Ưu tiên N5/N4: viết hiragana nếu có thể. Furigana chỉ khi không thể thay.")
        sys.exit(1)

if __name__ == "__main__":
    main()
