---
name: jlpt-tim-thong-tin
description: >
  Generate JLPT 情報検索 (tìm thông tin / information retrieval) reading passages as beautifully
  styled HTML files, capture screenshots, produce clean HTML, and output CSV training data.
  This skill is specifically for the "tìm thông tin" question type — documents like flyers, notices,
  schedules, comparison articles, medicine sheets, and application forms.
  Use this skill whenever the user wants to: generate tìm thông tin content, create 情報検索 passages,
  batch-generate HTML reading materials for JLPT information retrieval, or produce AI fine-tuning
  data for the tìm thông tin section of JLPT N1-N5.
  Also trigger when the user mentions: gen bài tìm thông tin, tạo nội dung tìm thông tin,
  generate information search passages, or create JLPT reading HTML with screenshots.
---

# JLPT 情報検索 / Tìm Thông Tin — Passage Generator

This skill generates JLPT-style "information retrieval" (情報検索 / tìm thông tin) reading passages. These are the document-based questions on real JLPT exams where test-takers must extract specific information from materials like flyers, notices, schedules, comparison articles, medicine sheets, and application forms.

This skill covers only the "tìm thông tin" type. Other reading types (đoạn văn ngắn, đoạn văn dài, đọc hiểu tổng hợp, etc.) are outside its scope.

## Outputs Per Passage

For each passage, three artifacts are produced:

1. **Styled HTML** → `assets/html/tim_thong_tin/{LEVEL}_{uuid}.html`
   Full standalone page: Tailwind CSS, Noto Sans JP, tables, bordered boxes, pill labels, furigana via `<ruby>/<rt>`.
   Example: `assets/html/tim_thong_tin/N3_a1b2c3d4.html`

2. **Screenshot PNG** → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
   Captured from the HTML via Playwright. Local path is stored in CSV column `general_image`.
   Example: `assets/img/tim_thong_tin/N3_a1b2c3d4.png`

3. **Clean HTML** → CSV column `text_read`
   Body content only, all attributes/classes stripped, whitespace collapsed, no style/script/rt text.
   Example: `<div><h1>Title</h1><table><tr><td>...</td></tr></table></div>`

**No combined/aggregate HTML files** — only individual files per passage.

## Character Counting (Critical)

JLPT counts ALL visible characters (字), not just Japanese. Use this exact method:

```python
from html.parser import HTMLParser
import re

class BodyTextExtractor(HTMLParser):
    """Extracts visible text from HTML body, skipping <rt>, <style>, <script>."""
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
    text = ''.join(ext.texts)
    return len(re.sub(r'[ \t\n\r\u3000]', '', text))
```

Rules:
- Count from the **full HTML file**, not the clean version
- Skip `<rt>` (furigana), `<style>`, `<script>` content
- Remove all whitespace: space, tab, newline, full-width space (　)
- Numbers, punctuation, Latin chars ALL count — "字" means every visible character

Alternatively, run the bundled script:
```bash
python3 <skill-path>/scripts/process_html.py --count-only --file <html-file>
```

## Target Character Counts

Based on 61 approved reference samples in `input/html/`:

| Level | Files | Min | Max | Avg | Target Range |
|-------|-------|-----|-----|-----|-------------|
| N1    | 13*   | 499 | 799 | 694 | 500–800     |
| N2    | 12    | 478 | 767 | 697 | 480–770     |
| N3    | 15    | 342 | 747 | 618 | 340–750     |
| N4    | 10    | 306 | 491 | 419 | 300–500     |
| N5    | 10    | 137 | 285 | 210 | 130–290     |

*N1: n1_10.html is empty (0 bytes), excluded.

Aim within the target range (based on actual sample min–max). After generating, always verify with `count_body_chars()` and adjust if outside range.

## Vocabulary & Grammar Constraints

- **50%+ vocabulary from the target JLPT level**
- **Never use vocabulary above the target level** (N2 content must not have N1-only words)
- N4/N5: simple sentence patterns, everyday topics
- N1/N2: compound sentences, formal/business register
- N3: bridge level — conversational with some formal elements

## Furigana Density

### Core Rule — Furigana Only for Above-Level Words

Furigana (`<ruby>/<rt>`) is **only** added for words/kanji that **exceed** the passage's target JLPT level. Words at or below the target level are written without furigana — the learner is expected to know them.

**Key principle**: A well-written passage should contain very few above-level words. Most vocabulary and kanji should be within the target level. Only when a word unavoidably exceeds the level (e.g., a place name with difficult kanji, a topic-specific term) should furigana be added.

### Compound Word Rule (Critical — Matches Real JLPT Exams)

When a word contains kanji above the learner's level, **always write the full kanji form** with furigana over the entire word. **NEVER** split a word into partial kanji + partial hiragana (the "Ab" form). This matches real JLPT exam formatting.

**The rule**: For any above-level word, choose one of two forms:
1. **Full kanji + furigana** (preferred when kanji is educational): `<ruby>週間<rt>しゅうかん</rt></ruby>`
2. **Full hiragana** (preferred at lower levels): `しゅうかん`

**NEVER use the "Ab" mixed form** — it does not appear in real JLPT exams or natural Japanese writing:
- ❌ `週かん` — WRONG: nobody writes this way
- ❌ `届きます` with furigana only on 届 — WRONG for a word that is entirely above-level
- ❌ `友だち` — WRONG at N5 (write `ともだち` in full hiragana)

**Examples of correct handling**:

| Word | Level of word | In N5 passage | In N4 passage | In N3 passage |
|------|-------------|--------------|--------------|--------------|
| 週間 (しゅうかん) | N4 | ✅ `しゅうかん` (full hiragana) or ✅ `<ruby>週間<rt>しゅうかん</rt></ruby>` (full kanji+furi) | ✅ `週間` (no furigana — N4 word in N4) | ✅ `週間` (no furigana) |
| 届く (とどく) | N3 | ✅ `とどく` (full hiragana) | ✅ `<ruby>届<rt>とど</rt></ruby>く` (kanji+furi, く is okurigana) or ✅ `とどく` | ✅ `届く` (no furigana — N3 word in N3) |
| 拠点 (きょてん) | N1 | ✅ avoid entirely | ✅ avoid or `<ruby>拠点<rt>きょてん</rt></ruby>` | ✅ `<ruby>拠点<rt>きょてん</rt></ruby>` |
| 友達 (ともだち) | N5 (hiragana form) | ✅ `ともだち` (full hiragana — N5 learner knows this word in hiragana only) | ✅ `友達` (N4 learner may know kanji) | ✅ `友達` |

**Okurigana exception**: When a word has kanji stem + hiragana okurigana (e.g., 届**く**, 届**け**る), the furigana covers only the kanji part, and the okurigana stands alone. This is NOT the "Ab" mixed form — it's standard Japanese orthography:
- ✅ `<ruby>届<rt>とど</rt></ruby>く` — correct (kanji stem + okurigana)
- ❌ `<ruby>届く<rt>とどく</rt></ruby>` — wrong (furigana should not cover okurigana)

### Policy Per Level

| Level | Words at or below level | Words above level (should be rare!) |
|-------|------------------------|--------------------------------------|
| N5 | **No furigana.** Write in hiragana if the learner only knows the word in hiragana (e.g. きょう, ともだち). Write kanji without furigana if the kanji is within N5 (日, 月, 人, 大, 小, etc.). | Write full hiragana (preferred) or full kanji + furigana. NEVER partial. Minimize such words. |
| N4 | **No furigana.** N5+N4 kanji are written bare. Words only known in hiragana at N4 stay in hiragana. | Write full kanji + furigana or full hiragana. Keep to a minimum. |
| N3 | **No furigana.** N5+N4+N3 kanji are expected. Common kana-only words stay in kana (きれい, たくさん). | Write full kanji + furigana. Very few such cases. |
| N2 | **No furigana.** N5–N2 kanji are expected. | Write full kanji + furigana for N1 words. Absolute minimum. |
| N1 | **No furigana.** All standard kanji are expected. | Furigana only for rare/specialized readings even N1 learners may not know. |

### How Many Above-Level Words?

In practice, a good passage should have **very few** above-level words:

| Level | Target above-level words | Ruby tags expected |
|-------|--------------------------|-------------------|
| N5 | 0–2 words | 0–5 ruby tags |
| N4 | 0–3 words | 0–8 ruby tags |
| N3 | 0–5 words | 0–12 ruby tags |
| N2 | 0–3 words | 0–8 ruby tags |
| N1 | 0–2 words | 0–5 ruby tags |

If you find yourself adding many furigana, **rewrite using simpler vocabulary** rather than adding more ruby tags.

### Summary Examples

**N5 passage** — 友達 is known only in hiragana at N5:
- ✅ `ともだちと いっしょに きてください。` (full hiragana)
- ❌ `友だちと いっしょに 来てください。` (WRONG — "Ab" mixed form 友だち, and 来 needs context)
- ❌ `<ruby>友達<rt>ともだち</rt></ruby>` (WRONG — this is a level-appropriate word, no furigana needed; just write hiragana)

**N4 passage** — 届く is N3-level (above N4):
- ✅ `<ruby>届<rt>とど</rt></ruby>く` (full kanji + furigana on stem, okurigana く stands alone)
- ✅ `とどく` (full hiragana — also acceptable)
- ❌ Writing 届 without furigana in an N4 passage (wrong — above level)
- Better yet: rewrite to avoid the above-level word entirely.

**N3 passage** — 届く is N3-level (same level):
- ✅ `届く` (no furigana — learner knows this)
- ❌ `<ruby>届<rt>とど</rt></ruby>く` (wrong — same-level word, no furigana)

**N3 passage** — 拠点 is N1-level (above N3):
- ✅ `<ruby>拠点<rt>きょてん</rt></ruby>` (full kanji + furigana over entire compound)
- ❌ `拠てん` (WRONG — "Ab" mixed form, never do this)
- ❌ `拠点` without furigana (wrong — N1 word in N3 passage needs furigana)

## Document Formats (from 61 reference samples)

Each passage must be assigned a `format` label from the catalog below. When generating multiple passages, **distribute formats diversely** — avoid repeating the same format within one batch. Use the per-level distribution table to pick formats appropriate for the target level.

### Format Catalog (15 formats)

| Format Label | Description | Example Topics |
|---|---|---|
| `price_comparison_table` | Side-by-side comparison of plans/products/services with pricing columns | Credit card plans, hotel rooms, moving service plans, course fees |
| `event_announcement` | Date/time/place/fee for a single event with participation rules | Job fair, beach cleanup, speech contest, cherry blossom party |
| `facility_guide` | Information about using a facility: hours, fees, rules, sections | Library, pool, zoo, community garden, museum |
| `class_enrollment` | Course/lesson offerings with schedule, fee, capacity, and signup method | Guitar lessons, cooking class, PC class, Japanese class, ski school |
| `service_guide` | How a service works: steps, conditions, pricing tiers, contact | Buy-back service, cleaning service, kimono rental, consultation service |
| `schedule_timetable` | Grid/table showing times by day/session, often with ○/× availability | Train timetable, sports club schedule, employment event schedule |
| `recruitment_notice` | Calling for applicants/volunteers/monitors with eligibility conditions | Newspaper monitors, festival volunteers, flea market sellers |
| `store_flyer` | Promotional sale with product names, prices, and sale period | Supermarket sale, bakery sale, weekly specials with starbursts |
| `menu_guide` | Restaurant/cafeteria menu with set meals, prices, drink options | Curry restaurant, university cafeteria, lunch sets, buffet |
| `travel_listing` | Tour/trip options with destinations, dates, transport, and prices | Summer travel packages, day-trip bus tours, ski travel |
| `medicine_info` | Drug name, dosage, timing, cautions in structured table format | Prescription sheet from clinic/pharmacy |
| `regulation_notice` | Rule changes or instructions for daily procedures (garbage, handwashing) | Garbage sorting rules, recycling notice, handwashing steps |
| `comparison_article` | Prose-style A/B/C/D comparison of options with sectioned text | Housing types comparison, service comparison with decision flow |
| `member_notification` | Letter/notice addressed to members/cardholders with policy details | Credit card member notice, ticket exchange policy, subscription renewal |
| `access_guide` | Route/directions with transport options, times, and costs | Campus access map, route diagram with train/bus connections |

### Per-Level Format Distribution (from 61 reference samples)

| Format | N1 | N2 | N3 | N4 | N5 | Total |
|---|---|---|---|---|---|---|
| `price_comparison_table` | n1_3, n1_7, n1_13 | — | n3_11 | n4_7 | — | 5 |
| `event_announcement` | n1_4 | n2_2, n2_8 | n3_9, n3_10 | n4_2, n4_5, n4_9, n4_10 | n5_6 | 10 |
| `facility_guide` | n1_5, n1_9 | n2_3, n2_6 | n3_5 | — | — | 5 |
| `class_enrollment` | — | n2_7 | n3_1, n3_3, n3_7, n3_12, n3_13, n3_15 | n4_4 | n5_10 | 9 |
| `service_guide` | n1_2, n1_12 | n2_11, n2_12 | n3_8, n3_14 | n4_6 | — | 7 |
| `schedule_timetable` | n1_8, n1_11 | n2_4 | — | — | n5_9 | 4 |
| `recruitment_notice` | n1_6 | — | n3_6 | — | — | 2 |
| `store_flyer` | — | — | — | — | n5_1, n5_2, n5_4, n5_7 | 4 |
| `menu_guide` | — | n2_5 | n3_4 | n4_8 | — | 3 |
| `travel_listing` | — | — | n3_2 | — | n5_5 | 2 |
| `medicine_info` | n1_1 | — | — | — | — | 1 |
| `regulation_notice` | — | — | — | n4_1, n4_3 | n5_3 | 3 |
| `comparison_article` | — | n2_1, n2_9, n2_10 | — | — | — | 3 |
| `member_notification` | n1_14 | — | — | — | — | 1 |
| `access_guide` | — | — | — | — | n5_8 | 1 |

### Level-Appropriate Format Selection

When generating passages, choose formats that match the level's complexity:

- **N5**: `store_flyer`, `event_announcement`, `regulation_notice`, `schedule_timetable`, `travel_listing`, `access_guide` — simple layouts, few conditions, minimal text
- **N4**: `event_announcement`, `class_enrollment`, `regulation_notice`, `menu_guide`, `price_comparison_table`, `service_guide` — simple tables, short rules, daily life topics
- **N3**: `class_enrollment`, `service_guide`, `event_announcement`, `facility_guide`, `travel_listing`, `price_comparison_table`, `recruitment_notice`, `menu_guide` — moderate tables, multiple conditions, discount rules
- **N2**: `facility_guide`, `service_guide`, `comparison_article`, `event_announcement`, `class_enrollment`, `schedule_timetable`, `menu_guide` — complex tables, flowcharts, multi-section layouts
- **N1**: `price_comparison_table`, `service_guide`, `facility_guide`, `schedule_timetable`, `medicine_info`, `recruitment_notice`, `member_notification`, `event_announcement` — dense data tables, cross-referencing multiple conditions, formal register

## Visual Elements Toolkit

Mix and match from this catalog (see `references/design-patterns.md` for detailed CSS):

- **Tables**: bordered, gray header row
- **Pill labels**: `border-radius: 9999px` (とき, ところ, etc.)
- **【】sections**: bracket headers
- **Content boxes**: rounded border + floating label (`position: absolute; top: -12px`)
- **Info grid**: CSS grid — label column + value column
- **Bullet markers**: ◆, ◎, ※, ＊, ☆, ✓
- **Black banner**: dark bg, white text, slight rotation for emphasis
- **Dashed contact box**: `border: 2px dashed`
- **Award grid**: 3-column layout
- **Footer**: `border-top` separator with contact details

## HTML Template Skeleton

Every generated file follows this structure:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Document title in Japanese]</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
        body {
            font-family: 'Noto Sans JP', sans-serif;
            background-color: #f3f4f6;
            color: #000;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 2rem auto;
            background: white;
            padding: 3rem;
            border: 1px solid #d1d5db;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        ruby rt { font-size: 0.6em; color: #333; }
        /* document-specific styles here */
    </style>
</head>
<body class="p-4 md:p-8">
<div class="container">
    <!-- content -->
</div>
</body>
</html>
```

## Clean HTML Extraction

Strip all attributes, classes, and whitespace for the `text_read` CSV column. Use the bundled `process_html.py` or this logic:

```python
class CleanHTMLExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result, self.skip_depth = [], 0
        self.in_body, self.body_done = False, False
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.in_body = True; return
        if not self.in_body or self.body_done: return
        if tag in ('style', 'script', 'rt'): self.skip_depth += 1; return
        if self.skip_depth > 0: return
        self.result.append(f'<{tag}>')
    def handle_endtag(self, tag):
        if tag == 'body': self.body_done = True; return
        if not self.in_body or self.body_done: return
        if tag in ('style', 'script', 'rt'): self.skip_depth -= 1; return
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

## Screenshot Capture

Use Playwright with headless Chromium:

```python
async def capture_screenshot(html_path, img_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1000, "height": 800})
        await page.goto(f"file://{html_path}", wait_until="networkidle")
        await page.wait_for_timeout(1500)  # wait for font loading
        await page.screenshot(path=img_path, full_page=True)
        await page.close()
        await browser.close()
```

Install if needed: `pip install playwright --break-system-packages && python3 -m playwright install chromium`

## Question Generation

Each passage must include JLPT-style multiple-choice questions. Reference samples in `input/htm_content_qa/` (20 files, 4 per level) demonstrate proper question patterns.

### Question Count Per Level (from `input/question_format.json`)

| Level | question_parent | question_child | Total Questions |
|-------|----------------|----------------|----------------|
| N1 | 1 | 2 | 2 questions per passage |
| N2 | 1 | 2 | 2 questions per passage |
| N3 | 1 | 2 | 2 questions per passage |
| N4 | 1 | 2 | 2 questions per passage |
| N5 | 1 | 1 | 1 question per passage |

### Question Label (from `input/mission.json`)

For all questions in "tìm thông tin" passages, use:
```
question_label = "question_information_search"
```

### Question Patterns by Level

Study `input/htm_content_qa/` for exact patterns. Key observations:

**N1** (n1_qa_1~4): Complex scenario-based questions.
- Q1: "Who/what meets the eligibility criteria?" — table with candidates, test-taker must cross-reference multiple conditions
- Q2: "What must person X do to apply?" — procedural questions requiring synthesis of multiple rules
- 4 answer options each, formal Japanese register, dense information

**N2** (n2_qa_1~4): Practical scenario questions.
- Q1: "Who can participate?" or "Where should person X go?" — cross-referencing conditions in a table/schedule
- Q2: "What is correct about the application method?" — testing understanding of procedures
- 4 answer options each, semi-formal register

**N3** (n3_qa_1~4): Practical daily-life questions.
- Q1: "What must participants bring?" or "What does the notice say?" — direct information extraction
- Q2: "How should person X fill in the postcard/form?" — application of rules, sometimes with table-based answer options
- 4 answer options each, mix of formal and conversational

**N4** (n4_qa_1~4): Simple information lookup.
- Q1: "Who can participate?" — straightforward eligibility checking
- Q2: "Which statement is correct?" — fact-checking against the document
- 4 answer options each, simple Japanese

**N5** (n5_qa_1~4): Basic information retrieval — **only 1 question**.
- "When is the cheapest day to buy X and Y together?" or "Where should you go?"
- Very simple question with concrete answer from a flyer/list
- 4 answer options, very basic Japanese

### Answer Format in CSV

Each answer column (`answer_{i}`) contains all 4 options separated by `\n`:
```
1. Option A text\n2. Option B text\n3. Option C text\n4. Option D text
```

`correct_answer_{i}` is the option number: `1`, `2`, `3`, or `4`.

### Question Quality Rules

1. **Information retrieval, not inference** — Answers must be findable directly in the document by cross-referencing facts. No opinion or inference needed.
2. **Wrong answers must be plausible** — Each distractor should be partially correct or address a real detail from the document, but fail on one condition.
3. **Cross-reference multiple conditions** — Good questions require checking 2+ conditions simultaneously (age + residence, date + product, eligibility + procedure).
4. **Each question tests a different aspect** — Q1 and Q2 should not test the same information.
5. **Furigana in questions** — Same rule as passage: only add furigana for words above the target level. Questions should use level-appropriate vocabulary, so furigana should be rare.
6. **No question images** — `question_image_{i}` is always empty for tìm thông tin.

## CSV Schema

45 columns matching `input/question_sheet.csv`:

| Column | Value for this skill |
|--------|---------------------|
| `_id` | `{LEVEL}_{uuid}` — e.g. `N3_a1b2c3d4`, `N5_e5f6g7h8`. Generate UUID with `uuid.uuid4().hex[:8]` |
| `level` | N1, N2, N3, N4, N5 |
| `tag` | Format label from the Format Catalog (e.g. `class_enrollment`, `store_flyer`, `facility_guide`) |
| `jp_char_count` | Result of `count_body_chars()` |
| `kind` | Always `tìm thông tin` |
| `general_image` | `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png` — same ID as `_id` |
| `text_read` | Clean HTML (no attributes, collapsed whitespace) |
| `question_label_{i}` | Always `question_information_search` |
| `question_{i}` | Question text in Japanese (furigana only for above-level words) |
| `answer_{i}` | 4 options separated by `\n`: `1. ...\n2. ...\n3. ...\n4. ...` |
| `correct_answer_{i}` | Number 1–4 |
| `explain_vn_{i}` | Vietnamese explanation of why the answer is correct |
| `explain_en_{i}` | English explanation of why the answer is correct |

N1-N4: fill `question_1` through `question_2` (2 questions). N5: fill only `question_1` (1 question). Remaining question columns left empty.

## File Naming & _id Convention

All files and the CSV `_id` column use the same ID: `{LEVEL}_{uuid}`

- **Pattern**: `{LEVEL}_{uuid}.html` / `.png` — e.g. `N3_a1b2c3d4.html`, `N5_e5f6g7h8.png`
- **Level prefix is UPPERCASE**: `N1`, `N2`, `N3`, `N4`, `N5`
- **UUID**: 8-character hex from `uuid.uuid4().hex[:8]` (Python) or equivalent
- **_id in CSV** = same value = filename without extension: `N3_a1b2c3d4`
- No need to check existing files for sequential numbering — UUID ensures uniqueness

```python
import uuid
def gen_id(level: str) -> str:
    """Generate unique ID for a passage. E.g. 'N3' → 'N3_a1b2c3d4'"""
    return f"{level}_{uuid.uuid4().hex[:8]}"
```

## Generation Workflow

1. **Generate IDs** → create `{LEVEL}_{uuid}` for each passage using `uuid.uuid4().hex[:8]`
2. **Select formats** → pick diverse format labels from the Format Catalog (see "Per-Level Format Distribution"). No two passages in the same batch should share a format unless the batch exceeds 15.
3. **Read 1–2 reference samples** from `input/html/` that match the chosen formats for the target level
4. **Read 1 QA reference** from `input/htm_content_qa/` for the target level (to calibrate question style)
5. **Generate HTML** → each passage follows its assigned format's layout patterns and visual elements
6. **Count characters** → verify within ±10% tolerance, adjust if needed
7. **Save HTML** → `assets/html/tim_thong_tin/`
8. **Capture screenshots** → `assets/img/tim_thong_tin/`
9. **Extract clean HTML** → build CSV rows
10. **Generate questions** → create questions, answer options, correct answers, and explanations per the rules above
11. **Fill CSV columns** → `tag` = format label, `general_image` = local PNG path, `question_label_{i}`, `question_{i}`, `answer_{i}`, `correct_answer_{i}`, `explain_vn_{i}`, `explain_en_{i}`
12. **Append to CSV** (or create new if starting fresh)
13. **Verify** all character counts, question counts, format diversity, and file integrity

## Reference Samples

### Passage references (61 files): `input/html/`

| Level | Files | Sample IDs |
|-------|-------|-----------|
| N1 | 14 | n1_1 to n1_14 (n1_10 is empty) |
| N2 | 12 | n2_1 to n2_12 |
| N3 | 15 | n3_1 to n3_15 |
| N4 | 10 | n4_1 to n4_10 |
| N5 | 10 | n5_1 to n5_10 |

### Question/Answer references (20 files): `input/htm_content_qa/`

Each file contains a reading passage + questions + 4 answer options + correct answer marked.

| Level | Files | Question Count | IDs |
|-------|-------|---------------|-----|
| N1 | 4 | 2 per file | n1_qa_1, n1_qa_2, n1_qa_3, n1_qu_4 |
| N2 | 4 | 2 per file | n2_qa_1, n2_qa_2, n2_qa_3, n2_qa_4 |
| N3 | 4 | 2 per file | n3_qa_1, n3_qa_2, n3_qa_3, n3_qa_4 |
| N4 | 4 | 2 per file | n4_qa_1, n4_qa_2, n4_qa_3, n4_qa_4 |
| N5 | 4 | 1 per file | n5_qa_1, n5_qa_2, n5_qa_3, n5_qa_4 |

Before generating, read 2–3 passage references AND 1 QA reference for the target level to calibrate style, length, visual complexity, and question patterns. For detailed per-file analysis (document types, char counts, design elements, ruby counts), see `references/design-patterns.md`. For question pattern analysis, see `references/question-patterns.md`.

## Bundled Scripts

### process_html.py — Count, screenshot, clean HTML

`scripts/process_html.py` automates the post-generation pipeline:

```bash
# Count chars only
python3 <skill>/scripts/process_html.py --count-only --file <html-file>

# Full pipeline: count + screenshot + CSV update
python3 <skill>/scripts/process_html.py --file <html-file> --img-dir assets/img/tim_thong_tin --csv sheets/samples_v5.csv

# Process all files in a directory
python3 <skill>/scripts/process_html.py --html-dir assets/html/tim_thong_tin --img-dir assets/img/tim_thong_tin --csv sheets/samples_v5.csv
```

