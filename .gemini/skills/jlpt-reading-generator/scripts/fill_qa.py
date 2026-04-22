#!/usr/bin/env python3
"""
Fill Q&A data into CSV safely — handles commas, newlines, quoting automatically.
Agent MUST use this script instead of editing CSV by hand.

Usage:
    python3 fill_qa.py --csv sheets/N5.csv --row-id N5_abc123 \
        --q1 "Question text here" \
        --a1 "Option 1
    Option 2
    Option 3
    Option 4" \
        --ca1 2 \
        --evn1 "Explanation VN..." \
        --een1 "Explanation EN..."

    # For N1-N4 (2 questions):
    python3 fill_qa.py --csv sheets/N1.csv --row-id N1_abc123 \
        --q1 "..." --a1 "..." --ca1 2 --evn1 "..." --een1 "..." \
        --q2 "..." --a2 "..." --ca2 3 --evn2 "..." --een2 "..."
"""
import argparse, csv, os, sys
from pathlib import Path

CSV_FIELDNAMES = [
    '_id', 'level', 'tag', 'jp_char_count', 'kind', 'general_audio', 'general_image',
    'text_read', 'text_read_vn', 'text_read_en',
    'question_label_1', 'question_1', 'question_image_1', 'answer_1', 'correct_answer_1', 'explain_vn_1', 'explain_en_1',
    'question_label_2', 'question_2', 'question_image_2', 'answer_2', 'correct_answer_2', 'explain_vn_2', 'explain_en_2',
    'question_label_3', 'question_3', 'question_image_3', 'answer_3', 'correct_answer_3', 'explain_vn_3', 'explain_en_3',
    'question_label_4', 'question_4', 'question_image_4', 'answer_4', 'correct_answer_4', 'explain_vn_4', 'explain_en_4',
    'question_label_5', 'question_5', 'question_image_5', 'answer_5', 'correct_answer_5', 'explain_vn_5', 'explain_en_5',
]


def main():
    parser = argparse.ArgumentParser(description="Fill Q&A data into CSV safely")
    parser.add_argument("--csv", required=True, help="CSV file path")
    parser.add_argument("--row-id", required=True, help="_id of the row to update")
    # Q1
    parser.add_argument("--q1", help="Question 1 text")
    parser.add_argument("--a1", help="Answer 1 options (4 lines, newline-separated)")
    parser.add_argument("--ca1", help="Correct answer 1 (integer 1-4)")
    parser.add_argument("--evn1", help="Explanation VN for Q1")
    parser.add_argument("--een1", help="Explanation EN for Q1")
    # Q2
    parser.add_argument("--q2", help="Question 2 text")
    parser.add_argument("--a2", help="Answer 2 options (4 lines, newline-separated)")
    parser.add_argument("--ca2", help="Correct answer 2 (integer 1-4)")
    parser.add_argument("--evn2", help="Explanation VN for Q2")
    parser.add_argument("--een2", help="Explanation EN for Q2")
    args = parser.parse_args()

    csv_path = args.csv
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Read existing CSV
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    # Find the target row
    target = None
    for row in rows:
        if row.get('_id') == args.row_id:
            target = row
            break

    if target is None:
        print(f"❌ Row _id={args.row_id} not found in {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Validate answers format
    updated = []
    for i, (q, a, ca, evn, een) in enumerate([
        (args.q1, args.a1, args.ca1, args.evn1, args.een1),
        (args.q2, args.a2, args.ca2, args.evn2, args.een2),
    ], start=1):
        if q is None and a is None:
            continue

        # Validate answer options
        if a:
            opts = [x.strip() for x in a.strip().split('\n') if x.strip()]
            if len(opts) != 4:
                print(f"❌ answer_{i} must have exactly 4 options (got {len(opts)})", file=sys.stderr)
                print(f"   Options found: {opts}", file=sys.stderr)
                sys.exit(1)
            a_clean = '\n'.join(opts)
        else:
            a_clean = None

        # Validate correct_answer
        if ca and ca not in ('1', '2', '3', '4'):
            print(f"❌ correct_answer_{i} must be 1-4 (got '{ca}')", file=sys.stderr)
            sys.exit(1)

        # Fill fields
        if q is not None:
            target[f'question_{i}'] = q
            target[f'question_label_{i}'] = 'question_information_search'
        if a_clean is not None:
            target[f'answer_{i}'] = a_clean
        if ca is not None:
            target[f'correct_answer_{i}'] = ca
        if evn is not None:
            target[f'explain_vn_{i}'] = evn
        if een is not None:
            target[f'explain_en_{i}'] = een
        updated.append(f'Q{i}')

    # Write back CSV with proper quoting
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Updated {', '.join(updated)} for {args.row_id} in {csv_path}")

    # Show summary
    for qi in updated:
        idx = qi[1]
        print(f"\n  {qi}:")
        print(f"    question_{idx}: {target.get(f'question_{idx}','')[:60]}...")
        a_val = target.get(f'answer_{idx}', '')
        opts = a_val.split('\n') if a_val else []
        for j, opt in enumerate(opts, 1):
            marker = " ✓" if str(j) == target.get(f'correct_answer_{idx}') else ""
            print(f"    ({j}) {opt}{marker}")
        print(f"    correct_answer_{idx}: {target.get(f'correct_answer_{idx}','')}")
        evn = target.get(f'explain_vn_{idx}', '')
        print(f"    explain_vn_{idx}: {evn[:60]}..." if len(evn) > 60 else f"    explain_vn_{idx}: {evn}")


if __name__ == '__main__':
    main()
