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
   Example: `assets/html/tim_thong_tin/N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5.html`

2. **Screenshot PNG** → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
   Captured from the HTML via Playwright. Local path is stored in CSV column `general_image`.
   Example: `assets/img/tim_thong_tin/N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5.png`

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

### Dữ liệu tham khảo từ 61 mẫu gốc

| Level | Files | Min | Max | Avg |
|-------|-------|-----|-----|-----|
| N1    | 13*   | 499 | 799 | 694 |
| N2    | 12    | 478 | 767 | 697 |
| N3    | 15    | 342 | 747 | 618 |
| N4    | 10    | 306 | 491 | 419 |
| N5    | 10    | 137 | 285 | 210 |

### Target Range (BẮT BUỘC tuân thủ)

Dựa trên feedback biên tập viên (bài gen thường ít ký tự hơn tiêu chuẩn), Target Range đã được điều chỉnh lên vùng **Avg → Max** của dữ liệu mẫu:

| Level | Target Range | Hard Reject (< Min) |
|-------|-------------|---------------------|
| N1    | **700–800** | < 700 → gen lại |
| N2    | **700–770** | < 700 → gen lại |
| N3    | **600–750** | < 600 → gen lại |
| N4    | **400–500** | < 400 → gen lại |
| N5    | **250–290** | < 250 → gen lại |

After generating, always verify with `count_body_chars()`. Nếu dưới Target Range, bổ sung nội dung (thêm điều kiện, ghi chú, lưu ý chi tiết) thay vì chấp nhận bài ngắn.

> **🚫 HARD REJECT — Ngưỡng tối thiểu tuyệt đối (không có ngoại lệ)**
>
> Nếu `count_body_chars()` **thấp hơn Min** của Target Range, bài **PHẢI gen lại từ đầu**. Không chấp nhận bài nào dưới minimum.
> Không chấp nhận, không chỉnh sửa nhỏ — gen lại hoàn toàn.
>
> Quy trình: Gen HTML → count chars → nếu < Hard Reject → **xóa và gen lại** → count lại → lặp cho đến khi đạt.

## Vocabulary & Grammar Constraints

- **50%+ vocabulary from the target JLPT level**
- **Never use vocabulary above the target level** (N2 content must not have N1-only words)
- N4/N5: simple sentence patterns, everyday topics
- N1/N2: compound sentences, formal/business register
- N3: bridge level — conversational with some formal elements

## Furigana Density

> **⚠️ BẮT BUỘC: PHẢI DÙNG THẺ `<ruby>` VÀ `<rt>` CHO FURIGANA ⚠️**
>
> Khi cần furigana, **BẮT BUỘC** sử dụng thẻ HTML `<ruby>` và `<rt>`. Đây là cách duy nhất được chấp nhận.
>
> **Đúng**: `<ruby>拠点<rt>きょてん</rt></ruby>` → hiển thị furigana phía trên kanji
>
> **QUAN TRỌNG**: Phải có **CẢ HAI** thẻ `<ruby>` và `<rt>`. Chỉ có `<ruby>` mà không có `<rt>` thì furigana **KHÔNG hiển thị** và vô nghĩa.
>
> **SAI — KHÔNG BAO GIỜ làm như sau**:
> - ❌ `<ruby>拠点</ruby>` — thiếu `<rt>`, furigana không hiển thị, VÔ NGHĨA
> - ❌ `拠点(きょてん)` — dùng ngoặc thay vì ruby tag
> - ❌ `拠点【きょてん】` — dùng brackets thay vì ruby tag
> - ❌ Viết reading bên cạnh kanji bằng bất kỳ cách nào khác ngoài `<ruby>/<rt>`
> - ❌ Bỏ qua furigana hoàn toàn khi từ vượt level
>
> Nếu HTML output không chứa thẻ `<ruby>` và `<rt>`, bài viết **KHÔNG HỢP LỆ** và phải viết lại.

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
| N5 | 0–1 words | 0–2 ruby tags |
| N4 | 0–2 words | 0–4 ruby tags |
| N3 | 0–3 words | 0–6 ruby tags |
| N2 | 0–2 words | 0–4 ruby tags |
| N1 | 0–1 words | 0–2 ruby tags |

> **⚠️ NGUYÊN TẮC VÀNG: THAY TỪ, KHÔNG RẮC FURIGANA**
>
> Biên tập viên JLPT nhận xét: bài gen thường "rắc furigana không phù hợp từ". Furigana gây 2 vấn đề:
> 1. **Lệch dòng** — dòng có ruby cao hơn dòng thường, phá vỡ layout đều đặn
> 2. **Không tự nhiên** — đề thi JLPT thật rất ít furigana; nhiều furigana = không giống đề thật
>
> **Ưu tiên theo thứ tự:**
> 1. 🥇 **Thay bằng từ cùng level** — ví dụ: thay 届く (N3) bằng 来る (N5) trong bài N5
> 2. 🥈 **Viết full hiragana** (cho N5/N4) — ví dụ: おおもり thay vì <ruby>大盛<rt>おおもり</rt></ruby>
> 3. 🥉 **Dùng furigana** — CHỈ khi từ không thể thay thế VÀ không thể viết hiragana (ví dụ: tên riêng, thuật ngữ chuyên ngành)
>
> Nếu bài có hơn **3 cặp `<ruby>/<rt>`**, hãy xem lại và thay từ đơn giản hơn.

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
- **Content boxes**: rounded border + floating label (`position: relative` on box + `position: absolute; top: -12px` on label) — **BẮT BUỘC** box phải có `padding-top` đủ lớn (≥ 20px) để label không che text bên trong, và `margin-top` đủ lớn (≥ 16px) để label không che text bên trên box
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
        /* === A4 PAGE LAYOUT === */
        /* A4 at 96dpi: 794×1123px. Container mô phỏng tờ A4 trắng trên nền xám. */
        body {
            font-family: 'Noto Sans JP', sans-serif;
            background-color: #e5e7eb;
            color: #000;
            line-height: 2;
            word-break: keep-all;      /* KHÔNG tách giữa từ CJK */
            line-break: strict;        /* Quy tắc ngắt dòng tiếng Nhật nghiêm ngặt nhất */
            overflow-wrap: break-word;  /* Fallback: chỉ ngắt khi từ dài hơn container */
            margin: 0;
            padding: 30px;
        }
        .container {
            width: 794px;              /* A4 width at 96dpi */
            min-height: 1123px;        /* A4 height at 96dpi — tối thiểu 1 trang */
            margin: 0 auto;
            background: white;
            padding: 50px 56px;        /* ~18-20mm margins giống A4 thật */
            border: 1px solid #d1d5db;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            box-sizing: border-box;
        }
        /* Đảm bảo table/flex không tràn ra ngoài A4 */
        table { width: 100%; table-layout: fixed; }
        td, th { overflow-wrap: break-word; }
        .container > * { max-width: 100%; }
        ruby {
            ruby-align: center;
            ruby-position: over;       /* ← furigana luôn ở TRÊN, không đẩy text xuống */
            vertical-align: baseline;  /* ← giữ text gốc đúng baseline, không bị thấp xuống */
        }
        ruby rt {
            font-size: 0.55em;
            color: #333;
            letter-spacing: 0.02em;
            line-height: 1;            /* ← rt không chiếm thêm chiều cao */
            vertical-align: top;
        }
        /* document-specific styles here */
    </style>
</head>
<body>
<div class="container">
    <!-- content -->
</div>
</body>
</html>
```

## Layout & Line-Break Rules (Critical — Editor Feedback)

### Quy tắc A4 (BẮT BUỘC)

Mỗi bài phải trông như **1 tờ A4** khi capture screenshot. Đây là yêu cầu bắt buộc.

- **Container = A4**: `width: 794px`, `min-height: 1123px` (A4 at 96dpi = 210×297mm)
- **Viewport Playwright = 854px** (794 + 60px body padding)
- **Nội dung phải nằm gọn trong A4** — không tràn, không bị cắt
- **Table**: luôn dùng `table-layout: fixed; width: 100%` để cột không bị đẩy ra ngoài
- **Flex/grid 2 cột**: đảm bảo tổng width ≤ 100% container, thêm `gap` hợp lý
- **Nếu nội dung dài hơn 1 trang**: OK — `full_page: True` sẽ capture hết, nhưng nên cố gắng giữ trong 1 trang

**Checklist A4 khi review screenshot:**
- ✅ Nền xám, tờ giấy trắng ở giữa với shadow nhẹ
- ✅ Nội dung có margin đều 4 bên (~50px = ~18mm)
- ✅ Table/box không bị cắt, không sát mép phải
- ❌ Nội dung tràn ra ngoài tờ giấy trắng
- ❌ Box bên phải bị sát mép container

### Quy tắc ngắt dòng — Flow Text (RẤT QUAN TRỌNG)

> **⚠️ NGHIÊM CẤM: Không dùng `<br>` để ngắt dòng sau mỗi câu ⚠️**
>
> Đề thi JLPT thật **KHÔNG BAO GIỜ** ngắt dòng sau mỗi câu. Text chảy liên tục (flow text),
> tự động wrap khi đến mép container. Mỗi câu KHÔNG được nằm trên 1 dòng riêng.
>
> Đây là lỗi nghiêm trọng nhất về layout — bài nào vi phạm phải **viết lại HTML**.

**Nguyên tắc**: Văn bản tiếng Nhật trong cùng 1 đoạn (paragraph) phải nằm trong **1 thẻ `<p>`** duy nhất, KHÔNG có `<br>` bên trong. Trình duyệt sẽ tự động wrap text khi đến mép container — đây là hành vi đúng và giống đề JLPT thật.

**❌ SAI — mỗi câu 1 dòng (KHÔNG GIỐNG ĐỀ JLPT THẬT):**
```html
自転車は「自転車専用」と書いてある道だけを通ってください。<br>
歩いている人がいる道や、花の近くの道では乗らないでください。<br>
また、道を逆向きに走ることはできません。
```

**✅ ĐÚNG — text chảy liên tục trong 1 thẻ `<p>`, tự wrap:**
```html
<p>自転車は「自転車専用」と書いてある道だけを通ってください。歩いている人がいる道や、花の近くの道では乗らないでください。また、道を逆向きに走ることはできません。</p>
```

**Khi nào MỚI được ngắt dòng / tách paragraph:**

| Được ngắt | Cách ngắt | Ví dụ |
|-----------|-----------|-------|
| Chuyển sang section/mục mới | `</p>` rồi heading mới | Hết mục 1 → sang mục 2 |
| Sau heading | Heading + `<p>` mới | `<h2>2. スピードと安全</h2><p>...` |
| List items / bullet points | `<li>` hoặc `・` trong table | Danh sách điều kiện, quy định |
| Thông tin dạng key-value | Table hoặc grid | Ngày, giờ, địa chỉ, số điện thoại |
| Chuyển ý hoàn toàn khác | `<p>` mới | Đoạn giới thiệu → đoạn quy định |

| KHÔNG được ngắt | Lý do |
|-----------------|-------|
| Giữa 2 câu cùng đoạn | Đề JLPT thật không ngắt — text flow liên tục |
| Sau mỗi dấu 。 | 。 không phải lý do để `<br>` |
| Để "trông đẹp" / dễ đọc | Layout phải giống đề thi, không phải dễ đọc cho dev |

**Ví dụ hoàn chỉnh — regulation_notice (N4):**

```html
<!-- ❌ SAI -->
<p>公園の中ではスピードを出さないでください。</p>
<p>特に子供やお年寄りがいる場所では、ゆっくり走ってください。</p>
<p>夜は必ずライトをつけてください。</p>
<p>二人で一つの自転車に乗ることは禁止です。</p>

<!-- ✅ ĐÚNG — cùng 1 section thì gộp 1 <p> -->
<p>公園の中ではスピードを出さないでください。特に子供やお年寄りがいる場所では、ゆっくり走ってください。夜は必ずライトをつけてください。二人で一つの自転車に乗ることは禁止です。</p>
```

### Cấm tách từ giữa dòng (RẤT QUAN TRỌNG)

> **⚠️ KHÔNG ĐƯỢC tách giữa 1 từ tiếng Nhật khi xuống dòng ⚠️**
>
> Giống như trong tiếng Việt không được viết "CH" cuối dòng rồi "ÀO" đầu dòng tiếp (tách từ "CHÀO"),
> tiếng Nhật **KHÔNG ĐƯỢC** tách giữa 1 từ khi wrap dòng.
>
> - ❌ 「いたしま」cuối dòng →「す」đầu dòng tiếp (tách từ いたします)
> - ❌ 「くださ」cuối dòng →「い」đầu dòng tiếp (tách từ ください)
> - ❌ 「変更につ」cuối dòng →「いて」đầu dòng tiếp (tách cụm について)
> - ✅ Cả từ「いたします」nằm trọn trên 1 dòng, hoặc wrap nguyên từ sang dòng mới

**CSS đã xử lý** bằng `word-break: keep-all` + `line-break: strict`. Tuy nhiên, CSS chỉ xử lý được khi trình duyệt nhận diện đúng ranh giới từ. Nếu screenshot vẫn cho thấy từ bị tách, hãy:
1. Wrap cụm từ quan trọng trong `<span style="display:inline-block">...</span>` để ngăn tách
2. Hoặc điều chỉnh nội dung (thêm/bớt vài ký tự) để dòng wrap ở vị trí tự nhiên

### Cấm che khuất chữ tiếng Nhật (RẤT QUAN TRỌNG)

> **⚠️ NGHIÊM CẤM: Chữ tiếng Nhật KHÔNG ĐƯỢC bị che bởi bất kỳ element nào ⚠️**
>
> Mọi ký tự tiếng Nhật trên trang phải **hiển thị rõ ràng 100%**, không bị đè, che, chồng lấp
> bởi bất kỳ element trang trí nào (label, badge, box border, step marker, heading background, v.v.).
>
> Đây là lỗi nghiêm trọng — bài nào có chữ bị che phải **sửa lại HTML** ngay lập tức.

**Nguyên nhân phổ biến nhất**: Floating label dùng `position: absolute` đè lên text ở dòng trước hoặc text bên trong box.

**Quy tắc bắt buộc khi dùng floating label / badge / step marker:**

1. **Box chứa label phải có `position: relative`** — để label absolute định vị theo box, không theo page
2. **`margin-top` đủ lớn trên box** (≥ 16px) — tạo khoảng trống phía trên để label không che text dòng trước
3. **`padding-top` đủ lớn bên trong box** (≥ 24px) — đẩy nội dung bên trong xuống, tránh label che dòng đầu tiên
4. **Label phải có `background-color`** — để text bên dưới label không "xuyên qua" thấy mờ mờ
5. **Kiểm tra cả 2 hướng**: label không che text PHÍA TRÊN box VÀ text BÊN TRONG box

**❌ SAI — label che mất dòng text phía trên:**
```html
<p>以下の手順および注意事項をご確認の上、お申し込みください。</p>
<!-- Label STEP 1 đè lên dòng text trên vì box không có margin-top -->
<div style="position: relative; border: 2px solid #4CAF50; border-radius: 8px; padding: 16px;">
    <span style="position: absolute; top: -12px; left: 16px; background: #4CAF50; color: white; padding: 2px 12px; font-weight: bold;">STEP 1</span>
    <h3>オンライン申し込み</h3>
    ...
</div>
```

**✅ ĐÚNG — có margin-top + padding-top đủ lớn:**
```html
<p>以下の手順および注意事項をご確認の上、お申し込みください。</p>
<!-- margin-top: 24px tạo khoảng trống, padding-top: 28px đẩy nội dung xuống -->
<div style="position: relative; border: 2px solid #4CAF50; border-radius: 8px; padding: 28px 16px 16px 16px; margin-top: 24px;">
    <span style="position: absolute; top: -12px; left: 16px; background: #4CAF50; color: white; padding: 2px 12px; font-weight: bold; border-radius: 4px;">STEP 1</span>
    <h3>オンライン申し込み</h3>
    ...
</div>
```

**Checklist chống che khuất:**
- ✅ Mọi `position: absolute` label đều nằm trong parent có `position: relative`
- ✅ Box có floating label luôn có `margin-top ≥ 16px`
- ✅ Box có floating label luôn có `padding-top ≥ 24px`
- ✅ Label/badge luôn có `background-color` solid (không transparent)
- ✅ Không có text nào bị che khi zoom 100% trên screenshot
- ❌ Label đè lên dòng text phía trên
- ❌ Label che mất chữ đầu tiên bên trong box
- ❌ Border hoặc background của element này chồng lên text của element khác

### CSS text bắt buộc (đã tích hợp trong template)

1. **`word-break: keep-all`** — Ngăn trình duyệt ngắt giữa ký tự CJK. Mặc định tiếng Nhật cho phép ngắt giữa bất kỳ 2 ký tự nào — property này chặn hành vi đó.

2. **`line-break: strict`** — Áp dụng quy tắc ngắt dòng tiếng Nhật **nghiêm ngặt nhất**. Cấm ngắt trước dấu nhỏ (っ、ゃ、ょ), cấm ngắt sau dấu mở ngoặc, v.v.

3. **`overflow-wrap: break-word`** — Fallback: chỉ cho phép ngắt khi 1 từ dài hơn container.

4. **`line-height: 2`** — Khoảng cách dòng đủ rộng để dòng có `<ruby>/<rt>` không bị cao hơn dòng thường.

5. **`ruby { ruby-position: over; vertical-align: baseline; }`** — Fix lỗi từ có furigana bị thấp xuống so với baseline.

6. **`ruby rt { font-size: 0.55em; line-height: 1; }`** — Furigana nhỏ, không chiếm thêm chiều cao.

### Kiểm tra layout khi review screenshot

Khi review screenshot, kiểm tra:
- ❌ **Chữ bị che khuất** bởi label, badge, step marker, hoặc bất kỳ element trang trí nào
- ❌ Mỗi câu nằm trên 1 dòng riêng (dấu hiệu: tất cả dòng ngắn, mép phải ragged không đều)
- ❌ `<br>` được dùng bên trong paragraph
- ❌ Từ bị tách giữa 2 dòng
- ❌ Dòng có furigana cao hơn hoặc thấp hơn dòng thường
- ✅ **Mọi chữ tiếng Nhật đều đọc được rõ ràng**, không bị đè/che bởi element nào
- ✅ Text chảy liên tục, tự wrap khi đến mép container — dòng dài đầy đủ chiều rộng
- ✅ Chỉ ngắt dòng khi chuyển section/heading/list
- ✅ Tất cả dòng cùng chiều cao, baseline đều

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
        # Viewport = A4 container (794px) + body padding (60px) = 854px
        page = await browser.new_page(viewport={"width": 854, "height": 1200})
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
| `_id` | `{LEVEL}_{uuid}` — e.g. `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5`, `N5_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6`. Generate UUID with `uuid.uuid4().hex` (full 32-char hex) |
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

- **Pattern**: `{LEVEL}_{uuid}.html` / `.png` — e.g. `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5.html`
- **Level prefix is UPPERCASE**: `N1`, `N2`, `N3`, `N4`, `N5`
- **UUID**: 32-character hex from `uuid.uuid4().hex` (Python) — full UUID, KHÔNG cắt
- **_id in CSV** = same value = filename without extension: `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5`
- No need to check existing files for sequential numbering — UUID ensures uniqueness

```python
import uuid
def gen_id(level: str) -> str:
    """Generate unique ID for a passage. E.g. 'N3' → 'N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5'"""
    return f"{level}_{uuid.uuid4().hex}"
```

## Generation Workflow

1. **Generate IDs** → create `{LEVEL}_{uuid}` for each passage using `uuid.uuid4().hex` (full 32-char)
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

