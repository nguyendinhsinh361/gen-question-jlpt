#!/usr/bin/env python3
"""
check_furigana.py — Kiểm tra kanji thiếu VÀ thừa furigana trong bài JLPT 情報検索

Scan HTML file, extract tất cả kanji, tra level từng ký tự trong kanji_jlpt_sensei.csv:
  - THIẾU: kanji vượt level mà không có <ruby><rt> tag → FAIL
  - THỪA: ruby word mà TẤT CẢ kanji ≤ level (không cần furigana) → FAIL

Usage:
    python3 check_furigana.py --html <path> --level N5 --kanji-csv input/kanji_jlpt_sensei.csv

Exit code:
    0 = OK (không có kanji thiếu hoặc thừa furigana)
    1 = FAIL (có kanji thiếu hoặc thừa furigana)
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
    ruby_pattern = re.compile(r"<ruby>(.*?)<rt>.*?</rt></ruby>", re.DOTALL)
    kanji_set = set()
    for m in ruby_pattern.finditer(html):
        content = m.group(1)
        for ch in content:
            if is_kanji(ch):
                kanji_set.add(ch)
    return kanji_set

def extract_ruby_words(html: str) -> list:
    """Return list of (content, reading) tuples from <ruby>CONTENT<rt>READING</rt></ruby>."""
    ruby_pattern = re.compile(r"<ruby>(.*?)<rt>(.*?)</rt></ruby>", re.DOTALL)
    results = []
    for m in ruby_pattern.finditer(html):
        content = m.group(1).strip()
        reading = m.group(2).strip()
        results.append((content, reading))
    return results

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

# ── Check MISSING furigana ──────────────────────────────────────────
def check_missing(html: str, target_level: str, kanji_map: dict) -> list:
    """Kanji vượt level mà KHÔNG có ruby → thiếu furigana."""
    bare_kanji = extract_bare_kanji(html)

    problems = []
    for ch, contexts in sorted(bare_kanji.items()):
        kanji_lv = kanji_map.get(ch, None)

        if kanji_lv is None:
            problems.append({
                "kanji": ch,
                "level": "N/A",
                "target": target_level,
                "contexts": sorted(contexts),
                "reason": "Không có trong CSV → mặc định cần furigana",
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

# ── Check EXCESS furigana ───────────────────────────────────────────
def check_excess(html: str, target_level: str, kanji_map: dict) -> list:
    """
    Ruby words mà TẤT CẢ kanji bên trong đều ≤ level → furigana thừa.
    Rule: nếu BẤT KỲ kanji trong từ > level → cả từ cần ruby (OK).
          nếu TẤT CẢ kanji ≤ level → ruby là thừa (FAIL).
    """
    ruby_words = extract_ruby_words(html)
    excess = []
    seen = set()

    for content, reading in ruby_words:
        kanji_in_word = [ch for ch in content if is_kanji(ch)]
        if not kanji_in_word:
            continue

        # Check if ANY kanji in this word exceeds level
        needs_ruby = False
        for ch in kanji_in_word:
            kanji_lv = kanji_map.get(ch, None)
            if kanji_lv is None:
                # Not in JLPT list → treat as above level → ruby OK
                needs_ruby = True
                break
            elif level_exceeds(kanji_lv, target_level):
                needs_ruby = True
                break

        if not needs_ruby:
            key = f"{content}({reading})"
            if key not in seen:
                seen.add(key)
                kanji_info = []
                for ch in kanji_in_word:
                    lv = kanji_map.get(ch, "?")
                    kanji_info.append(f"{ch}={lv}")
                excess.append({
                    "word": content,
                    "reading": reading,
                    "kanji_levels": ", ".join(kanji_info),
                    "target": target_level,
                })

    return excess

# ── CLI ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Kiểm tra kanji thiếu VÀ thừa furigana trong bài JLPT"
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

    with open(args.html, "r", encoding="utf-8") as f:
        html = f.read()

    kanji_map = load_kanji_csv(args.kanji_csv)
    missing = check_missing(html, args.level, kanji_map)
    excess = check_excess(html, args.level, kanji_map)

    # Report
    print(f"🔍 Furigana check: {args.html} (Level: {args.level})")
    print("=" * 70)

    has_error = False

    if missing:
        has_error = True
        print(f"\n❌ THIẾU FURIGANA — {len(missing)} kanji vượt level không có ruby:\n")
        print("{:<6} {:<8} {:<10} {}".format("Kanji", "Level", "Lý do", "Ngữ cảnh"))
        print("-" * 70)
        for p in missing:
            ctx = ", ".join(p["contexts"][:3]) if p["contexts"] else "—"
            print("{:<6} {:<8} {:<10} {}".format(
                p["kanji"], p["level"], p["reason"], ctx
            ))
        print(f"\n⛔ Sửa: thêm <ruby><rt> cho {len(missing)} kanji trên, hoặc viết hiragana.")

    if excess:
        has_error = True
        print(f"\n❌ THỪA FURIGANA — {len(excess)} từ có ruby nhưng tất cả kanji ≤ {args.level}:\n")
        print("{:<12} {:<12} {:<20} {}".format("Từ", "Reading", "Kanji levels", "Target"))
        print("-" * 70)
        for e in excess:
            print("{:<12} {:<12} {:<20} {}".format(
                e["word"], e["reading"], e["kanji_levels"], e["target"]
            ))
        print(f"\n⛔ Sửa: bỏ <ruby><rt> cho {len(excess)} từ trên — kanji đều ≤ {args.level}, không cần furigana.")

    if not has_error:
        print("✅ PASS — Không có kanji thiếu hoặc thừa furigana")
        sys.exit(0)
    else:
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
