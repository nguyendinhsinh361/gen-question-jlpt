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

> **⚠️ NGUYÊN TẮC VÀNG: Độ khó đến từ CẤU TRÚC THÔNG TIN, không phải từ vựng khó ⚠️**
>
> Bài JLPT khó vì phải cross-reference nhiều điều kiện, đọc bảng phức tạp, tìm ngoại lệ —
> KHÔNG phải vì nhồi nhét thuật ngữ chuyên ngành. Một bài N1 hay dùng từ vựng bình thường
> nhưng cấu trúc thông tin dày đặc, nhiều điều kiện chồng chéo, ghi chú nhỏ dễ bỏ sót.

- **80%+ từ vựng thuộc level mục tiêu hoặc thấp hơn** (ví dụ: bài N2 → ≥80% từ N2/N3/N4/N5)
- **Thuật ngữ chuyên ngành chỉ dùng khi THỰC SỰ CẦN THIẾT** cho ngữ cảnh (tên thuốc trong bài medicine_info, tên khóa học trong bài class_enrollment). KHÔNG thêm thuật ngữ chỉ để "tăng độ khó"
- **KHÔNG BAO GIỜ dùng từ vượt level mà không có furigana** — nếu bắt buộc dùng → phải có `<ruby>/<rt>`
- N4/N5: simple sentence patterns, everyday topics
- N1/N2: compound sentences, formal/business register — **nhưng từ vựng vẫn phải quen thuộc với người học level đó**
- N3: bridge level — conversational with some formal elements

### Nguồn tạo độ khó ĐÚNG CÁCH (theo level)

| Level | Nguồn khó ĐÚNG ✅ | Nguồn khó SAI ❌ |
|-------|-------------------|-----------------|
| N5 | Thông tin rải ở nhiều vị trí trong bài | Dùng kanji khó, từ N3+ |
| N4 | 2 điều kiện cần kết hợp, ghi chú nhỏ | Ngữ pháp N2, từ vựng formal |
| N3 | Bảng nhiều cột + điều kiện phụ trong văn xuôi | Thuật ngữ chuyên ngành N1 |
| N2 | Cross-reference bảng + văn xuôi, nhiều ngoại lệ | Nhồi thuật ngữ pháp lý/y tế |
| N1 | 3+ điều kiện chồng chéo, footnote, ngoại lệ ẩn | Từ hiếm không ai dùng, keigo cực đoan |

> **Ví dụ N2 SAI**: Bài về gym nhưng dùng "施設利用規約に基づく減免措置" — quá formal, thực tế không ai viết tờ rơi gym như vậy.
> **Ví dụ N2 ĐÚNG**: Bài về gym dùng "会員の方は月額500円引き。ただし、学生証の提示が必要です。" — từ vựng bình thường, khó vì phải cross-reference điều kiện giảm giá.

## Furigana Density

### Core Rule — Furigana Only for Above-Level Words

Furigana (`<ruby>/<rt>`) is **only** added for words/kanji that **exceed** the passage's target JLPT level. Words at or below the target level are written without furigana — the learner is expected to know them.

**Key principle**: ≥80% từ vựng phải thuộc level mục tiêu hoặc thấp hơn. Từ vượt level chỉ xuất hiện khi ngữ cảnh BẮT BUỘC (tên thuốc, tên dịch vụ, thuật ngữ không thể thay thế). Khi dùng từ vượt level → **giữ nguyên kanji + thêm furigana**. KHÔNG thêm thuật ngữ chuyên ngành chỉ để tăng độ khó — độ khó phải đến từ cấu trúc thông tin phức tạp.

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
| N3 | **No furigana.** N5+N4+N3 kanji are expected. Common kana-only words stay in kana (きれい, たくさん). | Write full kanji + furigana. Nội dung N3 thường có từ N2/N1 chuyên ngành → **nên dùng furigana thoải mái** cho những từ này. |
| N2 | **No furigana.** N5–N2 kanji are expected. | Write full kanji + furigana cho từ N1 và từ chuyên ngành. Nội dung N2 formal → tự nhiên có nhiều từ cần furigana. |
| N1 | **No furigana.** All standard kanji are expected. | Write full kanji + furigana cho từ chuyên ngành, thuật ngữ hiếm, tên riêng có kanji khó. Nội dung N1 (y tế, pháp luật, tài chính) thường có từ cần furigana. |

### How Many Above-Level Words?

| Level | Target above-level words | Ruby tags expected | Ghi chú |
|-------|--------------------------|-------------------|---------|
| N5 | 0–1 words | 0–2 ruby tags | Ưu tiên viết hiragana thay kanji |
| N4 | 0–2 words | 0–4 ruby tags | Hiragana hoặc kanji + furigana |
| N3 | 3–6 words | 5–12 ruby tags | Chỉ furigana cho từ thực sự vượt N3 và cần thiết cho ngữ cảnh |
| N2 | 3–5 words | 5–10 ruby tags | Furigana cho từ N1 xuất hiện tự nhiên — KHÔNG nhồi thuật ngữ |
| N1 | 2–4 words | 3–8 ruby tags | Furigana cho thuật ngữ chuyên ngành không thể thay thế (tên thuốc, tên luật...) |

> **NGUYÊN TẮC FURIGANA THEO LEVEL**
>
> **N5/N4**: Hạn chế furigana. Ưu tiên thay bằng từ cùng level hoặc viết full hiragana.
> - 🥇 **Thay bằng từ cùng level** — ví dụ: thay 届く (N3) bằng 来る (N5) trong bài N5
> - 🥈 **Viết full hiragana** — ví dụ: おおもり thay vì <ruby>大盛<rt>おおもり</rt></ruby>
> - 🥉 **Dùng furigana** — chỉ khi không thể thay thế
>
> **N3/N2/N1**: Dùng furigana cho từ vượt level khi ngữ cảnh BẮT BUỘC (tên thuốc, tên dịch vụ, thuật ngữ không thể thay thế). **KHÔNG nhồi thuật ngữ chuyên ngành** chỉ để bài trông "khó hơn". Nếu có thể diễn đạt bằng từ đúng level → dùng từ đúng level. Ví dụ: dùng "申し込み" (N3) thay vì "出願手続き" (N1) khi cả hai đều phù hợp ngữ cảnh.
>
> **Lưu ý chung**: Furigana chỉ cho từ VƯỢT level. Từ đúng level hoặc dưới level → KHÔNG furigana.

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

### BẮT BUỘC: Furigana Verification sau khi gen (KHÔNG ĐƯỢC BỎ QUA)

Furigana hay bị bỏ sót vì AI gen xong không quay lại kiểm tra. **Bước này BẮT BUỘC sau mỗi bài gen:**

**Quy trình 3 bước:**

1. **Scan toàn bộ kanji** trong HTML đã gen → liệt kê tất cả từ có kanji
2. **Check từng từ**: từ này thuộc level nào? Nếu vượt level bài → phải có `<ruby>+<rt>`. Nếu đang viết trần (không furigana) → **LỖI, phải sửa**
3. **Đếm ruby tags** → so sánh với bảng density. N3: 5–12, N2: 5–10, N1: 3–8. Nếu = 0 hoặc quá ít → **khả năng cao bị sót, review lại**

**Dấu hiệu bị sót furigana (phải kiểm tra):**
- Bài N3/N2/N1 có **0 ruby tags** → gần như chắc chắn sót
- Bài có từ chuyên ngành (医療, 保険, 契約, 免責...) mà không có furigana nào
- Bài dùng kanji N1 (如何, 伴, 踏, 控除, 還付...) trong bài N3 mà viết trần

**Danh sách từ thường vượt level — HAY BỊ QUÊN furigana:**

| Trong bài N3 (cần furigana) | Trong bài N2 (cần furigana) | Trong bài N1 (cần furigana) |
|------------------------------|-----------------------------|-----------------------------|
| <ruby>締切<rt>しめきり</rt></ruby> (N2) | <ruby>概要<rt>がいよう</rt></ruby> (N1) | <ruby>遵守<rt>じゅんしゅ</rt></ruby> (ngoài JLPT) |
| <ruby>受付<rt>うけつけ</rt></ruby> (N2) | <ruby>控除<rt>こうじょ</rt></ruby> (N1) | <ruby>瑕疵<rt>かし</rt></ruby> (ngoài JLPT) |
| <ruby>割引<rt>わりびき</rt></ruby> (N2) | <ruby>還付<rt>かんぷ</rt></ruby> (N1) | <ruby>斡旋<rt>あっせん</rt></ruby> (ngoài JLPT) |
| <ruby>申込<rt>もうしこみ</rt></ruby> (N2) | <ruby>免責<rt>めんせき</rt></ruby> (N1) | <ruby>拠点<rt>きょてん</rt></ruby> (N1 hiếm) |
| <ruby>対象<rt>たいしょう</rt></ruby> (N2) | <ruby>規約<rt>きやく</rt></ruby> (N1) | <ruby>稀<rt>まれ</rt></ruby> (ngoài JLPT) |
| <ruby>詳細<rt>しょうさい</rt></ruby> (N2) | <ruby>併用<rt>へいよう</rt></ruby> (N1) | <ruby>滞納<rt>たいのう</rt></ruby> (ngoài JLPT) |
| <ruby>持参<rt>じさん</rt></ruby> (N2) | <ruby>添付<rt>てんぷ</rt></ruby> (N1) | <ruby>譲渡<rt>じょうと</rt></ruby> (ngoài JLPT) |
| <ruby>掲載<rt>けいさい</rt></ruby> (N1) | <ruby>履歴<rt>りれき</rt></ruby> (N1) | <ruby>充填<rt>じゅうてん</rt></ruby> (ngoài JLPT) |

> **⚠️ Quy tắc vàng: Gen xong → Scan kanji → Check level → Thêm furigana thiếu → Đếm ruby tags**
> Nếu bỏ qua bước này, furigana SẼ bị sót. Đây là lỗi phổ biến nhất khi gen.

## Document Formats (from 61 reference samples)

Each passage must be assigned a `format` label from the catalog below.

> **⚠️ VẤN ĐỀ THƯỜNG GẶP: Format không đa dạng ⚠️**
>
> Claude hay lặp lại một số format quen thuộc (event_announcement, class_enrollment, service_guide) mà bỏ qua các format khác.
> **Quy tắc cứng:**
> 1. **KHÔNG lặp format** trong cùng batch — mỗi bài PHẢI dùng format khác nhau
> 2. **Ưu tiên format ít dùng** — kiểm tra `assets/html/tim_thong_tin/` xem format nào đã có nhiều → chọn format chưa có hoặc ít nhất
> 3. **Visual elements phải khác nhau** — ngay cả khi format khác nhau, 2 bài KHÔNG được trông giống nhau. Mỗi bài phải dùng tổ hợp visual elements khác nhau (bảng vs pill labels vs 【】sections vs info grid vs dashed box...)
> 4. **Chủ đề phải khác nhau** — 2 bài cùng format "event_announcement" nhưng khác batch: 1 về lễ hội mùa hè, 1 về job fair — OK. Nhưng 2 bài cùng về "lớp học" → KHÔNG OK

**BẮT BUỘC: Trước khi gen batch, liệt kê format + visual elements cho TỪNG bài:**
```
Bài 1: format=store_flyer, visual=[bảng giá, banner đỏ, dashed contact box]
Bài 2: format=facility_guide, visual=[info grid, 【】sections, pill labels]
Bài 3: format=schedule_timetable, visual=[bảng ○/×, footer liên hệ]
...
```
Nếu 2 bài có cùng tổ hợp visual → đổi 1 bài.

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

When generating passages, choose formats that match the level's complexity. **Mỗi level có nhiều format — PHẢI dùng hết, KHÔNG chỉ chọn 2-3 format quen thuộc:**

- **N5** (6 formats — dùng luân phiên): `store_flyer`, `event_announcement`, `regulation_notice`, `schedule_timetable`, `travel_listing`, `access_guide`
  - ❌ Hay bị lặp: chỉ gen store_flyer và event_announcement → thiếu đa dạng
  - ✅ Phải gen cả: regulation_notice (bảng phân loại rác), schedule_timetable (lịch xe bus), access_guide (bản đồ đường đi)
- **N4** (6 formats): `event_announcement`, `class_enrollment`, `regulation_notice`, `menu_guide`, `price_comparison_table`, `service_guide`
  - ❌ Hay bị lặp: chỉ gen event_announcement và class_enrollment
  - ✅ Phải gen cả: menu_guide (thực đơn), price_comparison_table (so sánh giá), regulation_notice (quy tắc)
- **N3** (8 formats): `class_enrollment`, `service_guide`, `event_announcement`, `facility_guide`, `travel_listing`, `price_comparison_table`, `recruitment_notice`, `menu_guide`
  - ❌ Hay bị lặp: chỉ gen class_enrollment và service_guide
  - ✅ Phải gen cả: recruitment_notice (tuyển dụng), travel_listing (tour), facility_guide (thư viện/hồ bơi)
- **N2** (7 formats): `facility_guide`, `service_guide`, `comparison_article`, `event_announcement`, `class_enrollment`, `schedule_timetable`, `menu_guide`
  - ❌ Hay bị lặp: chỉ gen service_guide và facility_guide
  - ✅ Phải gen cả: comparison_article (so sánh văn xuôi A/B/C), schedule_timetable (lịch hội thảo)
- **N1** (8 formats): `price_comparison_table`, `service_guide`, `facility_guide`, `schedule_timetable`, `medicine_info`, `recruitment_notice`, `member_notification`, `event_announcement`
  - ❌ Hay bị lặp: chỉ gen service_guide và price_comparison_table
  - ✅ Phải gen cả: medicine_info (phiếu thuốc), member_notification (thông báo hội viên), recruitment_notice (tuyển dụng)

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
        /* === COMPACT LAYOUT — tối ưu cho mobile app === */
        body {
            font-family: 'Noto Sans JP', sans-serif;
            background-color: #ffffff;
            color: #000;
            line-height: 2;
            word-break: keep-all;      /* KHÔNG tách giữa từ CJK */
            line-break: strict;        /* Quy tắc ngắt dòng tiếng Nhật nghiêm ngặt nhất */
            overflow-wrap: break-word;  /* Fallback: chỉ ngắt khi từ dài hơn container */
            margin: 0;
            padding: 0;                /* Body padding = 0, vì crop bằng container.screenshot() */
        }
        .container {
            width: 700px;
            margin: 0 auto;
            background: white;
            padding: 12px 16px;        /* Lề sát nội dung — tối ưu hiển thị trên app */
            box-sizing: border-box;
        }
        /* Đảm bảo table/flex không tràn ra ngoài container */
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

### Layout Compact — Tối ưu cho mobile app (BẮT BUỘC)

**KHÔNG dùng A4.** Layout compact, crop sát nội dung, lề nhỏ để ảnh to hơn trên app.

- **Container = 700px**, `padding: 12px 16px`, nền trắng, **KHÔNG `min-height`**
- **Viewport Playwright = 700px** (body padding = 0, crop bằng `container.screenshot()`)
- **Capture bằng `container.screenshot()`** — crop sát container, KHÔNG `full_page`
- **Table**: luôn dùng `table-layout: fixed; width: 100%` để cột không bị đẩy ra ngoài
- **Flex/grid 2 cột**: đảm bảo tổng width ≤ 100% container, thêm `gap` hợp lý

**Checklist layout khi review screenshot:**
- ✅ Nền trắng, lề nhỏ sát nội dung
- ✅ Ảnh crop sát dòng text cuối cùng
- ✅ Table/box không bị cắt, không sát mép phải
- ❌ Nền xám, shadow — đã bỏ
- ❌ Khoảng trắng lớn phía dưới nội dung

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
> bởi bất kỳ element nào — bao gồm cả label, badge, step marker, heading background,
> **hình vẽ, icon, emoji, SVG, ảnh nền, và mọi element trang trí khác**.
>
> Đây là lỗi nghiêm trọng — bài nào có chữ bị che phải **sửa lại HTML** ngay lập tức.

#### Trường hợp 1: Floating label đè lên text

**Nguyên nhân**: Floating label dùng `position: absolute` đè lên text ở dòng trước hoặc text bên trong box.

**Quy tắc bắt buộc khi dùng floating label / badge / step marker:**

1. **Box chứa label phải có `position: relative`** — để label absolute định vị theo box, không theo page
2. **`margin-top` đủ lớn trên box** (≥ 16px) — tạo khoảng trống phía trên để label không che text dòng trước
3. **`padding-top` đủ lớn bên trong box** (≥ 24px) — đẩy nội dung bên trong xuống, tránh label che dòng đầu tiên
4. **Label phải có `background-color`** — để text bên dưới label không "xuyên qua" thấy mờ mờ
5. **Kiểm tra cả 2 hướng**: label không che text PHÍA TRÊN box VÀ text BÊN TRONG box

**❌ SAI — label che mất dòng text phía trên:**
```html
<p>以下の手順および注意事項をご確認の上、お申し込みください。</p>
<div style="position: relative; border: 2px solid #4CAF50; border-radius: 8px; padding: 16px;">
    <span style="position: absolute; top: -12px; left: 16px; background: #4CAF50; color: white; padding: 2px 12px; font-weight: bold;">STEP 1</span>
    <h3>オンライン申し込み</h3>
</div>
```

**✅ ĐÚNG — có margin-top + padding-top đủ lớn:**
```html
<p>以下の手順および注意事項をご確認の上、お申し込みください。</p>
<div style="position: relative; border: 2px solid #4CAF50; border-radius: 8px; padding: 28px 16px 16px 16px; margin-top: 24px;">
    <span style="position: absolute; top: -12px; left: 16px; background: #4CAF50; color: white; padding: 2px 12px; font-weight: bold; border-radius: 4px;">STEP 1</span>
    <h3>オンライン申し込み</h3>
</div>
```

#### Trường hợp 2: Hình vẽ / icon / emoji đè lên text (RẤT PHỔ BIẾN)

**Nguyên nhân**: Icon lớn (★, ⭐, 🌟, SVG ngôi sao, hình trang trí) được đặt chồng lên hoặc cạnh text,
khiến chữ bên dưới/bên cạnh bị che một phần hoặc toàn bộ.

**NGUYÊN TẮC VÀNG: Nếu không thể hiển thị cả hình VÀ chữ rõ ràng 100% → BỎ HÌNH, GIỮ CHỮ.**

**Quy tắc bắt buộc:**

1. **KHÔNG BAO GIỜ đặt hình/icon chồng lên vùng có text** — dù dùng `position: absolute`, `z-index`, hay `background-image`
2. **Nếu hình và chữ cùng nằm trong 1 box**: phải tách rõ ràng — hình 1 vùng, chữ 1 vùng, KHÔNG overlap
3. **Nếu không đủ chỗ cho cả hình và chữ**: ưu tiên chữ, bỏ hình hoặc thu nhỏ hình
4. **Icon trang trí nhỏ** (≤ 1em): OK nếu nằm inline trước/sau text, nhưng KHÔNG đè lên text
5. **Thay thế bằng cách khác**: Dùng border, background-color, hoặc emoji nhỏ inline thay vì hình lớn overlay

**❌ SAI — ngôi sao lớn đè lên text ngày tháng:**
```html
<!-- ★ font-size: 80px đè lên "20日(火)" bên trong cùng box -->
<div style="position: relative; border: 3px solid red; width: 120px; height: 100px;">
    <span style="font-size: 80px; color: gold; position: absolute; top: -10px; left: 5px;">★</span>
    <span style="position: absolute; bottom: 5px; left: 10px;">20日(火)</span>
</div>
```

**✅ ĐÚNG — text nằm DƯỚI hình, tách biệt rõ ràng:**
```html
<!-- Hình và chữ tách riêng, không chồng lấp -->
<div style="border: 3px solid red; text-align: center; padding: 8px;">
    <div style="font-size: 40px; color: gold; line-height: 1;">★</div>
    <div style="font-weight: bold; margin-top: 4px;">20日(火)</div>
</div>
```

**✅ ĐÚNG — dùng background-color thay vì hình lớn:**
```html
<!-- Không dùng icon lớn, dùng background nổi bật thay thế -->
<div style="background: #FFF3CD; border: 3px solid red; text-align: center; padding: 12px; border-radius: 8px;">
    <div style="font-weight: bold; font-size: 1.1em;">🔥 20日(火)</div>
    <div>特売日</div>
</div>
```

**✅ ĐÚNG — icon nhỏ inline, không che chữ:**
```html
<p>★ 20日(火) — たまご 100円</p>
```

#### Checklist chống che khuất (PHẢI kiểm tra trên screenshot)

**Floating label:**
- ✅ Mọi `position: absolute` label đều nằm trong parent có `position: relative`
- ✅ Box có floating label luôn có `margin-top ≥ 16px` và `padding-top ≥ 24px`
- ✅ Label/badge luôn có `background-color` solid (không transparent)

**Hình vẽ / icon / emoji:**
- ✅ Mọi hình trang trí KHÔNG chồng lấp lên bất kỳ vùng text nào
- ✅ Hình và chữ trong cùng box được tách riêng vùng (trên/dưới hoặc trái/phải)
- ✅ Nếu không đủ chỗ → bỏ hình, giữ chữ
- ❌ Icon/emoji lớn (font-size > 2em) đặt absolute đè lên text
- ❌ SVG hoặc hình nền che mất chữ bên dưới
- ❌ Text nằm bên trong hình vẽ nhưng không đọc được rõ

**Tổng quát:**
- ✅ **Mọi chữ tiếng Nhật đều đọc được 100% rõ ràng trên screenshot**
- ❌ Bất kỳ ký tự nào bị che dù chỉ 1 phần

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
        # Viewport = container width (700px), body padding = 0
        page = await browser.new_page(viewport={"width": 700, "height": 1200})
        await page.goto(f"file://{html_path}", wait_until="networkidle")
        await page.wait_for_timeout(1500)  # wait for font loading
        container = page.locator('.container')
        await container.screenshot(path=img_path)
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

### Question Patterns by Level — BẮT BUỘC là câu hỏi TÌNH HUỐNG

> **Câu hỏi dạng "tìm thông tin" PHẢI là câu hỏi TÌNH HUỐNG (シチュエーション問題).**
> Mỗi câu hỏi phải đưa ra tình huống giả định: nhân vật có **tên thật** + điều kiện cá nhân → hỏi nên chọn/làm gì.
>
> **KHÔNG dùng tên chung chung** như Aさん, Bさん, 人A, 人B. Phải dùng **tên người Nhật hoặc tên nước ngoài tự nhiên**:
> - Tên Nhật: 田中さん, 佐藤さん, 山田さん, 鈴木さん, 高橋さん, 中村さん, 小林さん, 渡辺さん...
> - Tên nước ngoài (cho bài có người nước ngoài): リンさん, キムさん, チャンさん, マリアさん, アリさん...
> - Tên sự vật/địa điểm cũng nên cụ thể: "さくら教室" thay vì "教室A", "みどり公園" thay vì "公園B"
>
> ❌ KHÔNG hỏi thông tin thô: "教室は何曜日ですか" — quá đơn giản
> ❌ KHÔNG dùng tên chung: "Aさんは..." — không gần gũi, không tự nhiên
> ✅ Hỏi tình huống: "田中さんは水曜と金曜が休みで、基礎から学びたい。どのコースが合いますか。"

Study `input/htm_content_qa/` for exact patterns:

**N1** (n1_qa_1~4): Complex scenario — cross-reference 3+ điều kiện.
- Q1: 山本さん có profile cụ thể (tuổi, kinh nghiệm, bằng cấp) → đáp ứng tiêu chuẩn nào?
- Q2: 佐々木さん trong tình huống → thủ tục theo trình tự nào?
- 4 đáp án, formal, distractor sai 1 điều kiện khó nhận ra

**N2** (n2_qa_1~4): Practical scenario — cross-reference 2-3 điều kiện.
- Q1: 高橋さん có yêu cầu cụ thể → nên chọn gì?
- Q2: リンさん muốn đăng ký → phải làm gì?
- 4 đáp án, semi-formal, distractor lẫn thông tin giữa sections

**N3** (n3_qa_1~4): Daily-life scenario — cross-reference 2 điều kiện.
- Q1: 中村さん trong tình huống → cần chuẩn bị gì?
- Q2: キムさん muốn đăng ký → điền form thế nào?
- 4 đáp án, nửa formal, distractor đúng 1 điều kiện sai 1

**N4** (n4_qa_1~4): Simple scenario — check 1-2 điều kiện.
- Q1: 鈴木さん muốn tham gia → có thể không?
- Q2: マリアさん trong tình huống → câu nào đúng?
- 4 đáp án, simple Japanese, distractor sai 1 chi tiết

**N5** (n5_qa_1~4): Basic scenario — **only 1 question**, 1 điều kiện.
- 田中さん muốn mua/đi → chọn gì? ngày nào?
- 4 đáp án, very basic Japanese

### Đa dạng hóa câu hỏi — NGHIÊM CẤM lặp kiểu hỏi

> **⚠️ Câu hỏi phải ĐA DẠNG về kiểu tình huống, góc nhìn, và cách hỏi.**
> KHÔNG lặp lại cùng một pattern "Xさんは～したい。どれがいいですか" cho mọi câu.

**8 kiểu câu hỏi tình huống — xoay vòng sử dụng:**

| # | Kiểu tình huống | Ví dụ | Level phù hợp |
|---|----------------|-------|---------------|
| 1 | **Chọn phương án phù hợp** | 田中さんは～で、～条件がある。どれが合いますか。 | All |
| 2 | **Kiểm tra tư cách/điều kiện** | 山本さんは～歳、～経験。応募できるのはどれですか。 | N3-N1 |
| 3 | **Xác định thủ tục/trình tự** | リンさんが申し込む場合、最初に何をしますか。 | N3-N1 |
| 4 | **Tính toán chi phí/thời gian** | 佐藤さんが3か月利用する場合、合計でいくらかかりますか。 | N4-N1 |
| 5 | **Xác định đúng/sai về nội dung** | このお知らせの内容と合っているのはどれですか。 | All |
| 6 | **Tìm ngoại lệ/điều kiện đặc biệt** | 高橋さんの場合、通常と違う点は何ですか。 | N2-N1 |
| 7 | **So sánh và chọn** | 鈴木さんの条件に最も近いのはAとBのどちらですか。なぜですか。 | N3-N1 |
| 8 | **Hành động khi có vấn đề** | キムさんは～の状況になった。どうすればいいですか。 | N4-N1 |

**Quy tắc đa dạng:**
- Q1 và Q2 trong cùng bài PHẢI dùng **kiểu khác nhau** (ví dụ: Q1 = kiểu 1, Q2 = kiểu 3)
- Trong batch 5 bài cùng level, KHÔNG lặp cùng kiểu quá **2 lần**
- Mỗi câu hỏi phải có **profile nhân vật cụ thể** — không chỉ "muốn X" mà còn có tuổi, nghề, hoàn cảnh, ngân sách, lịch trình...

### Answer Format in CSV

Each answer column (`answer_{i}`) contains all 4 options separated by `\n`, **KHÔNG có số thứ tự**:
```
Option A text\nOption B text\nOption C text\nOption D text
```

**KHÔNG viết** `1. ...`, `2. ...` — chỉ lưu nội dung đáp án, không prefix số.

`correct_answer_{i}` is the option number: `1`, `2`, `3`, or `4`.

### Question Quality Rules

1. **BẮT BUỘC là câu hỏi TÌNH HUỐNG** — Nhân vật có **tên thật** (田中さん, リンさん... KHÔNG dùng Aさん/Bさん) + điều kiện cá nhân → hỏi nên chọn/làm gì. KHÔNG hỏi thông tin thô.
2. **Information retrieval, not inference** — Đáp án tìm được bằng cross-reference thông tin trong bài. Không suy luận.
3. **Wrong answers must be plausible** — Distractor đúng 1 phần, sai 1 điều kiện. Level cao → distractor tinh vi hơn.
4. **Cross-reference multiple conditions** — Kiểm tra 2+ điều kiện đồng thời.
5. **Each question tests a different aspect** — Q1 và Q2 test khía cạnh khác nhau.
6. **Furigana in questions** — Cùng quy tắc với bài đọc. Chỉ dùng `<ruby>/<rt>`.
7. **No question images** — `question_image_{i}` luôn để trống.

### 🚫 HARD REJECT — Nội dung & Câu hỏi (gen lại nếu vi phạm)

> Ngoài Hard Reject về số ký tự, các trường hợp sau cũng BẮT BUỘC gen lại toàn bộ:

**A. Nội dung bài đọc không logic → GEN LẠI**

Bài đọc phải mô phỏng tài liệu thực tế. Nếu nội dung có bất kỳ điểm nào phi logic, mâu thuẫn, hoặc không thực tế → gen lại.

- ❌ Giá quá vô lý (cốc cà phê 50,000円, vé xe bus 1円)
- ❌ Thời gian mâu thuẫn (đăng ký trước ngày 5 nhưng sự kiện ngày 3)
- ❌ Điều kiện tự mâu thuẫn (miễn phí cho tất cả nhưng phải trả 500円)
- ❌ Thông tin không thực tế (bể bơi mở 24/7, bệnh viện nhận trẻ dưới 0 tuổi)
- ❌ Nội dung không phù hợp ngữ cảnh (tờ rơi siêu thị viết như hợp đồng pháp lý)
- ✅ Giá hợp lý, thời gian hợp lý, điều kiện nhất quán, đọc như tài liệu thật

**B. Đáp án đúng — phải paraphrase từ bài đọc → GEN LẠI nếu không đạt**

- ✅ Đáp án đúng PHẢI có căn cứ rõ ràng trong bài đọc (cross-reference được)
- ✅ Đáp án đúng nên **paraphrase** (diễn đạt lại) thông tin trong bài — KHÔNG copy nguyên văn
- ❌ Đáp án đúng copy nguyên câu từ bài đọc → học sinh chỉ cần tìm câu giống nhất, không cần hiểu
- ❌ Đáp án đúng chứa thông tin không có trong bài → suy luận, không phải tìm thông tin

> Ví dụ: Bài viết "月曜日と水曜日は休館です" → đáp án đúng nên viết "火曜日に利用できる" (paraphrase, cần suy nghĩ), KHÔNG nên viết "月曜日と水曜日は休みです" (copy gần nguyên văn, quá dễ nhận ra)

**C. Đáp án sai (distractor) — phải cần suy nghĩ mới loại được → GEN LẠI nếu không đạt**

- ✅ Distractor PHẢI chứa thông tin **có trong bài đọc** nhưng áp dụng sai (sai điều kiện, sai đối tượng, sai thời gian)
- ✅ Distractor phải hợp lý đến mức học sinh **phải đọc kỹ và so sánh** mới loại được
- ❌ Distractor chứa thông tin hoàn toàn KHÔNG có trong bài → loại ngay, không cần đọc bài
- ❌ Distractor sai hiển nhiên (giá khác xa, ngày không tồn tại) → loại ngay
- ❌ Distractor dùng từ ngữ tiêu cực/phủ định rõ ràng trong khi 3 đáp án còn lại tích cực → đoán được

> **Test nhanh**: Che bài đọc, chỉ nhìn 4 đáp án → nếu đoán được đáp án đúng → câu hỏi THẤT BẠI, gen lại.
> Học sinh phải BẮT BUỘC đọc bài mới trả lời được — đó mới là câu hỏi tìm thông tin tốt.

**D. Kiểm tra chéo đáp án — PHẢI thực hiện sau khi gen**

Sau khi gen xong câu hỏi + 4 đáp án:
1. Đọc lại bài gốc → xác nhận đáp án đúng thực sự đúng (có căn cứ trong bài)
2. Đọc lại bài gốc → xác nhận 3 distractor thực sự SAI (không có trường hợp 2 đáp án cùng đúng)
3. Che bài đọc → nhìn 4 đáp án → nếu đoán được → sửa distractor
4. Kiểm tra distractor có thông tin trong bài không → nếu distractor bịa thông tin → sửa lại

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
| `answer_{i}` | 4 options separated by `\n` — **KHÔNG có số thứ tự**: `ĐA1\nĐA2\nĐA3\nĐA4` |
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
2. **Kiểm tra format đã có** → `ls assets/html/tim_thong_tin/` rồi đọc CSV để xem format (cột `tag`) nào đã gen nhiều → ưu tiên format ít/chưa có
3. **Lập kế hoạch format + visual** → liệt kê format + tổ hợp visual elements cho TỪNG bài TRƯỚC khi gen. Không được 2 bài cùng format trong batch. Không được 2 bài trông giống nhau về layout.
4. **Read 1–2 reference samples** from `input/html/` that match the chosen formats for the target level
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

