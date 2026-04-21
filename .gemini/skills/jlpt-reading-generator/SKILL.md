---
name: jlpt-tim-thong-tin
description: >
  Generate JLPT 情報検索 (tìm thông tin / information retrieval) reading passages as beautifully
  styled HTML files, capture screenshots, produce clean HTML, and output CSV training data.
  Skill này bao gồm TOÀN BỘ luồng: gen → QC loop (6 tiêu chí) → sửa → chụp ảnh.
  Gen từng bài một, kiểm tra đến khi đạt chất lượng mới chuyển sang bài tiếp theo.
  This skill is specifically for the "tìm thông tin" question type — documents like flyers, notices,
  schedules, comparison articles, medicine sheets, and application forms.
  Use this skill whenever the user wants to: generate tìm thông tin content, create 情報検索 passages,
  batch-generate HTML reading materials for JLPT information retrieval, or produce AI fine-tuning
  data for the tìm thông tin section of JLPT N1-N5.
  Also trigger when the user mentions: gen bài tìm thông tin, tạo nội dung tìm thông tin,
  generate information search passages, create JLPT reading HTML with screenshots,
  kiểm tra chất lượng, quality check, review bài, QC.
---

# JLPT 情報検索 / Tìm Thông Tin — Generator & Quality Check (Unified)

Skill này bao gồm **TOÀN BỘ luồng end-to-end**: từ gen nội dung → kiểm tra chất lượng (6 tiêu chí) → sửa lỗi → chụp ảnh. Mỗi bài được gen và QC **từng bài một** — không chuyển sang bài tiếp theo cho đến khi bài hiện tại PASS tất cả 6 tiêu chí.

> **Nguyên tắc cốt lõi:**
> 1. **Gen từng bài một** — không batch 5 bài rồi QC sau
> 2. **QC loop** — check 6 TC → nếu FAIL → sửa → check lại → lặp đến khi PASS
> 3. **Screenshot cuối cùng** — CHỈ chụp ảnh sau khi bài PASS tất cả 6 TC
> 4. **1 FAIL = REJECT** — không có "gần đạt", không có ngoại lệ

---

## Outputs Per Passage

For each passage, three artifacts are produced:

1. **Styled HTML** → `assets/html/tim_thong_tin/{LEVEL}_{uuid}.html`
   Full standalone page: Tailwind CSS, Noto Sans JP, tables, bordered boxes, pill labels, furigana via `<ruby>/<rt>`.

2. **Screenshot PNG** → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
   Captured from the HTML via Playwright. Local path is stored in CSV column `general_image`.

3. **Clean HTML** → CSV column `text_read`
   Body content only, all attributes/classes stripped, whitespace collapsed, no style/script/rt text.

**No combined/aggregate HTML files** — only individual files per passage.

---

# ═══════════════════════════════════════════════════
# PHẦN 1: CÁC QUY TẮC (RULES — định nghĩa 1 lần duy nhất)
# ═══════════════════════════════════════════════════

## R1. Character Counting

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

### Target Character Counts (BẮT BUỘC)

| Level | Target Range | Hard Reject (< Min) |
|-------|-------------|---------------------|
| N1    | **700–800** | < 700 → gen lại |
| N2    | **700–770** | < 700 → gen lại |
| N3    | **600–750** | < 600 → gen lại |
| N4    | **400–500** | < 400 → gen lại |
| N5    | **250–290** | < 250 → gen lại |

> **🚫 HARD REJECT**: Dưới minimum → gen lại hoàn toàn, không chỉnh sửa nhỏ.

---

## R2. Vocabulary & Grammar Constraints (RẤT QUAN TRỌNG — Gemini thường gen khó hơn level)

> **⚠️ LƯU Ý ĐẶC BIỆT CHO GEMINI**: Gemini có xu hướng gen nội dung KHÓ HƠN so với level yêu cầu.
> Ví dụ: gen bài N4 nhưng dùng từ vựng/ngữ pháp N2-N3, hoặc nhồi thuật ngữ chuyên ngành vào N2/N1.
> Nội dung PHẢI phản ánh đúng độ khó của level — người học level đó phải đọc hiểu được.

### Hướng dẫn chi tiết per level (Gemini reference)

| Level | Từ vựng & Kanji | Ngữ pháp | Chủ đề | Ví dụ câu |
|-------|----------------|----------|--------|-----------|
| N5 | Hiragana nhiều, kanji N5 cơ bản (日月人円時) | ～です, ～ます, ～てください, ～があります | Mua sắm, giờ mở cửa, bảng giá | おみせは あさ 9じから よる 8じまでです。 |
| N4 | Kanji N5+N4, ít hiragana hơn | ～ことができます, ～なければなりません, ～てもいいです | Sự kiện, lớp học, quy tắc | 小学生以下のお子様は無料で参加できます。 |
| N3 | Kanji N5-N3 | ～について, ～による, ～場合は, ～ために | Dịch vụ, tuyển dụng, du lịch | 応募の場合は、履歴書を郵送してください。 |
| N2 | Kanji N5-N2 | ～に伴い, ～に基づき, ～を踏まえて, ～に限り | So sánh, hướng dẫn, quy trình | 本サービスは会員登録に基づき提供されます。 |
| N1 | Kanji đầy đủ N5-N1 | ～いかんによらず, ～をもって, ～に先立ち, 敬語 | Y tế, pháp luật, tài chính | 理由のいかんによらず、返金には応じかねます。 |

> **⚠️ NGUYÊN TẮC VÀNG: Độ khó đến từ CẤU TRÚC THÔNG TIN, không phải từ vựng khó ⚠️**
>
> Bài JLPT khó vì phải cross-reference nhiều điều kiện, đọc bảng phức tạp, tìm ngoại lệ —
> KHÔNG phải vì nhồi nhét thuật ngữ chuyên ngành.

- **80%+ từ vựng thuộc level mục tiêu hoặc thấp hơn**
- **Từ vượt level → ưu tiên level gần nhất**: bài N3 cần từ vượt level → dùng từ N2 trước, KHÔNG nhảy thẳng lên N1
- **HẠN CHẾ thuật ngữ chuyên ngành** — chỉ dùng khi ngữ cảnh BẮT BUỘC
- **KHÔNG BAO GIỜ dùng từ vượt level mà không có furigana**
- **N4/N5: KHÔNG dùng kanji vượt level** — các kanji như 当, 届, 締, 割, 欄 là N3+ và KHÔNG được xuất hiện trong bài N4/N5 (kể cả có furigana). Viết hiragana thay thế
- N4/N5: simple sentence patterns, everyday topics
- N1/N2: compound sentences, formal/business register — **nhưng từ vựng vẫn phải quen thuộc**
- N3: bridge level — conversational with some formal elements

> **Quy tắc chọn từ vượt level:**
> - N5 cần từ vượt → N4 (KHÔNG N3+)
> - N4 cần từ vượt → N3 (KHÔNG N2+)
> - N3 cần từ vượt → N2 (KHÔNG N1 trừ khi không thể thay)
> - N2 cần từ vượt → N1 thông dụng (KHÔNG thuật ngữ hiếm)
> - N1 → dùng N1 đầy đủ, thuật ngữ chỉ khi ngữ cảnh yêu cầu

### Nguồn tạo độ khó ĐÚNG CÁCH

| Level | Nguồn khó ĐÚNG ✅ | Nguồn khó SAI ❌ |
|-------|-------------------|-----------------|
| N5 | Thông tin rải ở nhiều vị trí trong bài | Dùng kanji khó, từ N3+ |
| N4 | 2 điều kiện cần kết hợp, ghi chú nhỏ | Ngữ pháp N2, từ vựng formal |
| N3 | Bảng nhiều cột + điều kiện phụ trong văn xuôi | Thuật ngữ chuyên ngành N1 |
| N2 | Cross-reference bảng + văn xuôi, nhiều ngoại lệ | Nhồi thuật ngữ pháp lý/y tế |
| N1 | 3+ điều kiện chồng chéo, footnote, ngoại lệ ẩn | Từ hiếm không ai dùng, keigo cực đoan |

### Ngữ pháp phù hợp level

| Level | Ngữ pháp mong đợi |
|-------|--------------------|
| N5 | ～です/ます, ～てください, ～ことができます |
| N4 | ～たら, ～ても, ～なければならない, ～ようにしてください |
| N3 | ～場合, ～ことになっている, ～に限り, ～とする |
| N2 | ～において, ～に伴い, ～を踏まえ, ～次第 |
| N1 | ～をもって, ～に基づき, ～を経て, formal keigo |

- ❌ Bài N5 dùng ～において → REJECT
- ❌ Bài N4 dùng ～を踏まえ → REJECT

---

## R3. Furigana Rules

> **⚠️ BẮT BUỘC: PHẢI DÙNG THẺ `<ruby>` VÀ `<rt>` CHO FURIGANA ⚠️**
>
> Khi cần furigana, **BẮT BUỘC** sử dụng thẻ HTML `<ruby>` và `<rt>`. Đây là cách duy nhất được chấp nhận.
>
> **Đúng**: `<ruby>拠点<rt>きょてん</rt></ruby>` → hiển thị furigana phía trên kanji
>
> **QUAN TRỌNG**: Phải có **CẢ HAI** thẻ `<ruby>` và `<rt>`. Chỉ có `<ruby>` mà không có `<rt>` thì furigana **KHÔNG hiển thị**.
>
> **SAI — KHÔNG BAO GIỜ làm như sau (phát hiện → GEN LẠI ngay)**:
> - ❌ `<ruby>拠点</ruby>` — thiếu `<rt>`, VÔ NGHĨA → **GEN LẠI**
> - ❌ `拠点(きょてん)` — dùng ngoặc đơn → **GEN LẠI**
> - ❌ `拠点【きょてん】` — dùng brackets → **GEN LẠI**
> - ❌ `集荷（しゅうか）` — dùng ngoặc kép → **GEN LẠI**
> - ❌ Bỏ qua furigana hoàn toàn khi từ vượt level
>
> **🚫 HARD REJECT — Nếu phát hiện furigana dạng ngoặc `()` hoặc `【】` → bài PHẢI gen lại từ đầu.**
> Gemini có xu hướng dùng dạng ngoặc `漢字(かんじ)` thay vì `<ruby>漢字<rt>かんじ</rt></ruby>`.
> Đây là lỗi nghiêm trọng — dạng ngoặc KHÔNG được chấp nhận.

### Core Rule — Furigana ONLY for Above-Level Words (KHÔNG rắc toàn bộ)

> **🚫 LỖI PHỔ BIẾN NHẤT: AI rắc furigana lên HẦU HẾT mọi kanji — kể cả từ đúng level và dưới level.**
> Đây là SAI NGHIÊM TRỌNG. Nếu 80% từ vựng thuộc level mục tiêu → 80% kanji KHÔNG CẦN furigana.
> **Chỉ ~20% từ vượt level mới cần furigana.** Bài N3 có 111 ruby tags = SAI. Bài N3 nên có ~10-20 ruby tags.

Furigana (`<ruby>/<rt>`) is **ONLY** added for words/kanji that **exceed** the passage's target JLPT level. Words **at or below** the target level are written **WITHOUT furigana** — người học ở level đó được kỳ vọng đã biết những từ này.

> **Quy tắc: TẤT CẢ từ vượt level → phải có furigana. Từ đúng/dưới level → KHÔNG furigana.**

### Ước tính ruby count hợp lý (QUAN TRỌNG)

Vì 80%+ từ vựng đúng level → chỉ ~20% từ vượt level → ruby count phải THẤP:

| Level | Ruby count hợp lý | Nếu vượt mức này → kiểm tra lại |
|-------|-------------------|----------------------------------|
| N5 | **0–3** | > 5 → đang furigana từ đúng level |
| N4 | **0–5** | > 8 → đang furigana từ đúng level |
| N3 | **5–15** | > 20 → đang furigana từ đúng level |
| N2 | **5–15** | > 20 → đang furigana từ đúng level |
| N1 | **3–10** | > 15 → đang furigana từ đúng level |

### Ví dụ cụ thể — N3 passage

**❌ SAI — furigana toàn bộ (111 ruby tags!):**
```
<ruby>最近<rt>さいきん</rt></ruby>は、<ruby>仕事<rt>しごと</rt></ruby>や<ruby>生活<rt>せいかつ</rt></ruby>で...
<ruby>教室<rt>きょうしつ</rt></ruby>は...15<ruby>名<rt>めい</rt></ruby>までの<ruby>少人数<rt>しょうにんずう</rt></ruby>...
```
→ 最近(N3), 仕事(N4), 生活(N3), 教室(N3), 名(N4) đều đúng level → KHÔNG cần furigana

**✅ ĐÚNG — chỉ furigana từ vượt N3 (~12 ruby tags):**
```
最近は、仕事や生活で...
教室は...15名までの<ruby>少人数<rt>しょうにんずう</rt></ruby>...
<ruby>経験豊富<rt>けいけんほうふ</rt></ruby>な<ruby>講師<rt>こうし</rt></ruby>が<ruby>丁寧<rt>ていねい</rt></ruby>にお教えします。
```
→ 少人数(N2), 経験豊富(N2), 講師(N2), 丁寧(N2) vượt N3 → CẦN furigana
→ 最近, 仕事, 生活, 教室, 名 đúng level → viết trần

### Danh sách từ KHÔNG cần furigana (AI hay nhầm)

| Level | Từ KHÔNG cần furigana (đúng level hoặc dưới) |
|-------|----------------------------------------------|
| N5 | 日, 月, 人, 円, 大, 小, 時, 年, 何, 前, 後, 店, 上, 下, 中, 外 |
| N4 | 場所, 仕事, 電話, 大丈夫, 手紙, 先生, 買う, 使う, 教える, 名前, 方, 時間, 市, 町, 村, 写真, 必要 |
| N3 | 最近, 生活, 機会, 質問, 内容, 基本, 簡単, 教室, 文書, 作成, 地域, 説明, 練習, 経験, 予約, 申し込み |
| N2 | 受付, 締切, 割引, 対象, 詳細, 申込, 制度, 条件, 届出, 規定, 設備, 施設, 担当, 了承, 開催 |
| N1 | Hầu hết kanji thông thường — chỉ furigana cho thuật ngữ chuyên ngành hiếm |

### Compound Word Rule (Matches Real JLPT Exams)

For any above-level word, choose one of two forms:
1. **Full kanji + furigana** (preferred): `<ruby>週間<rt>しゅうかん</rt></ruby>`
2. **Full hiragana**: `しゅうかん`

**NEVER use the "Ab" mixed form** — it does not appear in real JLPT exams:
- ❌ `週かん` — WRONG
- ❌ `友だち` — WRONG at N5 (write `ともだち`)

**Okurigana exception**: kanji stem + hiragana okurigana is standard:
- ✅ `<ruby>届<rt>とど</rt></ruby>く` — correct
- ❌ `<ruby>届く<rt>とどく</rt></ruby>` — wrong (furigana should not cover okurigana)

### Policy Per Level

| Level | Words at or below level | Words above level |
|-------|------------------------|--------------------------------------|
| N5 | **No furigana.** Write hiragana if learner only knows word in hiragana. | Write full hiragana (preferred) or full kanji + furigana. NEVER partial. |
| N4 | **No furigana.** N5+N4 kanji written bare. | Write full kanji + furigana or full hiragana. |
| N3 | **No furigana.** N5+N4+N3 kanji expected. | Write full kanji + furigana. |
| N2 | **No furigana.** N5–N2 kanji expected. | Write full kanji + furigana cho từ N1 và từ chuyên ngành. |
| N1 | **No furigana.** All standard kanji expected. | Write full kanji + furigana cho thuật ngữ chuyên ngành, tên riêng khó. |

### N5/N4 Furigana Priority

> **N5/N4**: Hạn chế furigana. Ưu tiên:
> - 🥇 **Thay bằng từ cùng level** — ví dụ: thay 届く (N3) bằng 来る (N5)
> - 🥈 **Viết full hiragana** — ví dụ: おおもり
> - 🥉 **Dùng furigana** — chỉ khi không thể thay thế
>
> **N3/N2/N1**: Dùng furigana cho từ vượt level khi ngữ cảnh BẮT BUỘC. KHÔNG nhồi thuật ngữ.

### Format Furigana — Chỉ `<ruby>+<rt>`

- ✅ `<ruby>漢字<rt>かんじ</rt></ruby>` — ĐÚNG duy nhất
- ❌ `漢字(かんじ)` — REJECT
- ❌ `漢字【かんじ】` — REJECT
- ❌ `拠てん` — REJECT (dạng "Ab")

### Danh sách từ thường vượt level — HAY BỊ QUÊN furigana

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

---

## R4. Document Formats (15 formats from 61 reference samples)

> **Quy tắc cứng:**
> 1. **KHÔNG lặp format** trong cùng batch — mỗi bài PHẢI dùng format khác nhau
> 2. **Ưu tiên format ít dùng** — kiểm tra `assets/html/tim_thong_tin/` xem format nào đã có nhiều
> 3. **Visual elements phải khác nhau** — 2 bài KHÔNG được trông giống nhau
> 4. **Chủ đề phải khác nhau**

### Format Catalog

| Format Label | Description | Example Topics |
|---|---|---|
| `price_comparison_table` | Side-by-side comparison of plans/products/services | Credit card plans, hotel rooms, moving plans |
| `event_announcement` | Date/time/place/fee for a single event | Job fair, beach cleanup, speech contest |
| `facility_guide` | Information about using a facility: hours, fees, rules | Library, pool, zoo, museum |
| `class_enrollment` | Course offerings with schedule, fee, capacity | Guitar lessons, cooking class, PC class |
| `service_guide` | How a service works: steps, conditions, pricing | Buy-back service, cleaning, kimono rental |
| `schedule_timetable` | Grid showing times by day/session, often ○/× | Train timetable, sports club schedule |
| `recruitment_notice` | Calling for applicants/volunteers with conditions | Newspaper monitors, festival volunteers |
| `store_flyer` | Promotional sale with products, prices, period | Supermarket sale, bakery, weekly specials |
| `menu_guide` | Restaurant menu with set meals, prices, options | Curry restaurant, university cafeteria |
| `travel_listing` | Tour options with destinations, dates, prices | Summer packages, day-trip bus tours |
| `medicine_info` | Drug name, dosage, timing, cautions | Prescription sheet from clinic/pharmacy |
| `regulation_notice` | Rule changes or instructions for procedures | Garbage sorting, recycling notice |
| `comparison_article` | Prose-style A/B/C/D comparison | Housing types, service comparison |
| `member_notification` | Letter to members with policy details | Credit card notice, subscription renewal |
| `access_guide` | Route/directions with transport options | Campus access map, route diagram |

### Level-Appropriate Formats

- **N5** (6 formats): `store_flyer`, `event_announcement`, `regulation_notice`, `schedule_timetable`, `travel_listing`, `access_guide`
- **N4** (6 formats): `event_announcement`, `class_enrollment`, `regulation_notice`, `menu_guide`, `price_comparison_table`, `service_guide`
- **N3** (8 formats): `class_enrollment`, `service_guide`, `event_announcement`, `facility_guide`, `travel_listing`, `price_comparison_table`, `recruitment_notice`, `menu_guide`
- **N2** (7 formats): `facility_guide`, `service_guide`, `comparison_article`, `event_announcement`, `class_enrollment`, `schedule_timetable`, `menu_guide`
- **N1** (8 formats): `price_comparison_table`, `service_guide`, `facility_guide`, `schedule_timetable`, `medicine_info`, `recruitment_notice`, `member_notification`, `event_announcement`

---

## R5. Visual Elements Toolkit

Mix and match from this catalog:
- **Tables**: bordered, gray header row
- **Pill labels**: `border-radius: 9999px` (とき, ところ, etc.)
- **【】sections**: bracket headers
- **Content boxes**: rounded border + floating label (`position: relative` + `position: absolute; top: -12px`) — box phải có `padding-top ≥ 24px` và `margin-top ≥ 16px`
- **Info grid**: CSS grid — label column + value column
- **Bullet markers**: ◆, ◎, ※, ＊, ☆, ✓
- **Black banner**: dark bg, white text
- **Dashed contact box**: `border: 2px dashed`
- **Footer**: `border-top` separator with contact details

---

## R6. HTML Template Skeleton

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
            background-color: #ffffff;
            color: #000;
            line-height: 2;
            word-break: keep-all;
            line-break: strict;
            overflow-wrap: break-word;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 700px;
            margin: 0;
            background: white;
            padding: 12px 16px;
            box-sizing: border-box;
        }
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

## R7. Layout & Line-Break Rules

### Flow Text (RẤT QUAN TRỌNG)

> **NGHIÊM CẤM: Không dùng `<br>` để ngắt dòng sau mỗi câu.**
> Đề thi JLPT thật KHÔNG BAO GIỜ ngắt dòng sau mỗi câu. Text chảy liên tục (flow text).

- Văn bản cùng 1 đoạn → 1 thẻ `<p>` duy nhất, KHÔNG có `<br>` bên trong
- ❌ `。<br>` → REJECT
- ✅ Text chảy liên tục, tự wrap khi đến mép container

**Khi nào MỚI được ngắt**: chuyển section, sau heading, list items, key-value, chuyển ý hoàn toàn.

### Layout Compact (BẮT BUỘC)

- **Container = 700px**, `margin: 0`, `padding: 12px 16px`, KHÔNG `min-height`, KHÔNG `margin: 0 auto`
- **Viewport Playwright = 700px** — PHẢI bằng container width
- **Capture bằng `container.screenshot()`** — KHÔNG `page.screenshot()`
- **Table**: `table-layout: fixed; width: 100%`

### Cấm che khuất chữ tiếng Nhật

> **NGHIÊM CẤM: Chữ tiếng Nhật KHÔNG ĐƯỢC bị che bởi bất kỳ element nào.**

- Floating label → box phải có `margin-top ≥ 16px` và `padding-top ≥ 24px`, label phải có `background-color` solid
- Icon/emoji lớn → KHÔNG đặt chồng lên text. Nếu không đủ chỗ → bỏ hình, giữ chữ
- **NGUYÊN TẮC VÀNG: Nếu không thể hiển thị cả hình VÀ chữ rõ ràng 100% → BỎ HÌNH, GIỮ CHỮ.**

### Cấm tách từ giữa dòng

CSS `word-break: keep-all` + `line-break: strict` đã xử lý. Nếu screenshot vẫn thấy từ bị tách → wrap cụm từ trong `<span style="display:inline-block">` hoặc điều chỉnh nội dung.

---

## R8. Question Generation Rules

### Question Count Per Level

| Level | Questions per passage |
|-------|----------------------|
| N1-N4 | 2 questions (Q1, Q2) |
| N5    | 1 question (Q1 only) |

### BẮT BUỘC: Câu hỏi TÌNH HUỐNG (シチュエーション問題)

> **MỌI câu hỏi (Q1 VÀ Q2) phải là TÌNH HUỐNG**: nhân vật có **tên thật** + profile + điều kiện cá nhân → hỏi nên chọn/làm gì.
>
> **KHÔNG dùng tên chung chung** Aさん, Bさん, 人A, 人B. Phải dùng **tên thật**:
> - Tên Nhật: 田中さん, 佐藤さん, 山田さん, 鈴木さん, 高橋さん, 中村さん...
> - Tên nước ngoài: リンさん, キムさん, チャンさん, マリアさん, アリさん...
>
> ❌ "教室は何曜日ですか" — quá đơn giản, không tình huống
> ❌ "～について正しいものはどれか" — thiếu nhân vật, thiếu tình huống → **REJECT**
> ✅ "田中さんは水曜と金曜が休みで、基礎から学びたい。どのコースが合いますか。"

> **⚠️ LỖI PHỔ BIẾN NHẤT: Q1 có tình huống nhưng Q2 thì không.**
> **CẢ Q1 VÀ Q2 đều PHẢI có nhân vật + tình huống. Q2 dùng nhân vật khác Q1. Không có ngoại lệ.**

### 8 Kiểu câu hỏi — Q1 và Q2 PHẢI khác kiểu

| # | Kiểu tình huống | Ví dụ | Level |
|---|----------------|-------|-------|
| 1 | **Chọn phương án phù hợp** | 田中さんは～条件がある。どれが合いますか。 | All |
| 2 | **Kiểm tra tư cách/điều kiện** | 山本さんは～歳、～経験。応募できるのはどれですか。 | N3-N1 |
| 3 | **Xác định thủ tục/trình tự** | リンさんが申し込む場合、最初に何をしますか。 | N3-N1 |
| 4 | **Tính toán chi phí/thời gian** | 佐藤さんが3か月利用する場合、合計いくらですか。 | N4-N1 |
| 5 | **Xác định đúng/sai về nội dung** | このお知らせの内容と合っているのはどれですか。 | All |
| 6 | **Tìm ngoại lệ/điều kiện đặc biệt** | 高橋さんの場合、通常と違う点は何ですか。 | N2-N1 |
| 7 | **So sánh và chọn** | 鈴木さんの条件に最も近いのはAとBのどちらですか。 | N3-N1 |
| 8 | **Hành động khi có vấn đề** | キムさんは～の状況になった。どうすればいいですか。 | N4-N1 |

### Answer Quality Rules

**Đáp án đúng:**
- PHẢI có căn cứ trong bài đọc (cross-reference được)
- PHẢI **paraphrase** — KHÔNG copy nguyên văn từ bài

**Đáp án sai (distractor):**
- PHẢI chứa thông tin **CÓ trong bài** nhưng áp dụng sai (sai điều kiện, sai đối tượng)
- PHẢI cần suy nghĩ mới loại được
- ❌ Bịa thông tin không có trong bài → REJECT
- ❌ Sai hiển nhiên → REJECT
- ❌ 3 đáp án tích cực + 1 phủ định rõ ràng → REJECT

**Test nhanh**: Che bài đọc, chỉ nhìn 4 đáp án → nếu đoán được đáp án đúng → câu hỏi THẤT BẠI.

### Answer Format in CSV

- `answer_{i}`: 4 options separated by `\n`, **KHÔNG có số thứ tự**: `ĐA1\nĐA2\nĐA3\nĐA4`
- `correct_answer_{i}`: integer string `1`, `2`, `3`, `4` — **KHÔNG** `2.0`
- `question_label_{i}`: Always `question_information_search`
- `question_image_{i}`: luôn để trống

---

## R9. Clean HTML Extraction

```python
class CleanHTMLExtractor(HTMLParser):
    SKIP_TAGS = ('style', 'script')   # skip tag AND content (không hiển thị)
    # ruby và rt được GIỮ NGUYÊN — furigana cần có trong clean HTML
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

---

## R10. Screenshot Capture

```python
async def capture_screenshot(html_path, img_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 700, "height": 1200})
        await page.goto(f"file://{html_path}", wait_until="networkidle")
        await page.wait_for_timeout(1500)  # wait for font loading
        container = page.locator('.container')
        await container.screenshot(path=img_path)
        await page.close()
        await browser.close()
```

Install: `pip install playwright --break-system-packages && python3 -m playwright install chromium`

---

## R11. CSV Schema

45 columns matching `input/question_sheet.csv`:

| Column | Value |
|--------|-------|
| `_id` | `{LEVEL}_{uuid}` — e.g. `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5` |
| `level` | N1, N2, N3, N4, N5 |
| `tag` | Format label (e.g. `class_enrollment`) |
| `jp_char_count` | Result of `count_body_chars()` |
| `kind` | Always `tìm thông tin` |
| `general_image` | `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png` |
| `text_read` | Clean HTML |
| `question_label_{i}` | Always `question_information_search` |
| `question_{i}` | Question text in Japanese |
| `answer_{i}` | 4 options `\n` separated, KHÔNG số thứ tự |
| `correct_answer_{i}` | Integer 1–4 |
| `explain_vn_{i}` | Vietnamese explanation |
| `explain_en_{i}` | English explanation |

N1-N4: fill Q1+Q2. N5: fill Q1 only.

### File Naming

`{LEVEL}_{uuid}` — UUID from `uuid.uuid4().hex` (32-char hex), level UPPERCASE.

```python
import uuid
def gen_id(level: str) -> str:
    return f"{level}_{uuid.uuid4().hex}"
```

---

# ═══════════════════════════════════════════════════
# PHẦN 2: LUỒNG THỰC HIỆN (WORKFLOW — end-to-end)
# ═══════════════════════════════════════════════════

> **⛔ NGUYÊN TẮC: Gen từng bài → QC loop → PASS → Screenshot → Bài tiếp theo**
> KHÔNG gen 5 bài rồi QC sau. Mỗi bài phải PASS trước khi chuyển sang bài tiếp.

## BƯỚC 0: CHUẨN BỊ (1 lần cho cả batch)

1. **Scan format đã dùng** → `ls assets/html/tim_thong_tin/` + đọc CSV cột `tag` → thống kê format nào đã có nhiều
2. **Lập kế hoạch** cho TOÀN BATCH:
   ```
   Bài 1: level=N3, format=facility_guide, visual=[info grid, 【】sections, pill labels], chủ đề=thư viện
   Bài 2: level=N2, format=comparison_article, visual=[prose sections, bordered box], chủ đề=nhà ở
   ...
   ```
   - Mỗi bài format khác nhau, visual khác nhau, chủ đề khác nhau
3. **Read references** → 1-2 HTML mẫu từ `input/html/` + 1 QA mẫu từ `input/htm_content_qa/` cho level cần gen

---

## BƯỚC 1–6: LẶP CHO TỪNG BÀI (repeat per passage)

### BƯỚC 1: GEN HTML

1. Generate `{LEVEL}_{uuid}` ID
2. Gen HTML theo format + visual đã lên kế hoạch, tuân thủ R1-R7
3. Count chars bằng `count_body_chars()` → nếu < minimum → gen lại ngay
4. Save HTML → `assets/html/tim_thong_tin/{id}.html`

### BƯỚC 2: FURIGANA VERIFICATION (⛔ BLOCKING)

> **Không qua được bước này → KHÔNG ĐƯỢC tiếp tục.**

1. **Scan toàn bộ kanji** trong HTML vừa gen → liệt kê tất cả từ có kanji
2. **Check từng từ**: thuộc level nào? Nếu vượt level → phải có `<ruby>+<rt>`. Nếu viết trần → **sửa ngay**
3. Confirm: không còn từ vượt level nào thiếu furigana

### BƯỚC 3: GEN CÂU HỎI + ĐÁP ÁN

1. Gen questions theo R8 (tình huống, tên thật, profile, Q1≠Q2 kiểu hỏi)
2. Gen 4 đáp án (đáp án đúng paraphrase, đáp án sai có căn cứ trong bài)
3. Gen explanations (VN + EN)
4. Extract clean HTML → `text_read`
5. Fill CSV row → append to CSV

### BƯỚC 4: ⛔ QUALITY CHECK — PHẦN A: HTML (TC1-TC5)

Kiểm tra 5 tiêu chí HTML. **1 FAIL = phải sửa.**

| TC | Tiêu chí | Kiểm tra | FAIL nếu |
|----|----------|----------|----------|
| TC1 | Ký tự | `count_body_chars()` ≥ minimum? | < minimum (N1:700, N2:700, N3:600, N4:400, N5:250) |
| TC2 | Chủ đề & Format | Chủ đề phù hợp level? Nội dung logic? (giá hợp lý, thời gian không mâu thuẫn) | Chủ đề sai level, nội dung phi logic |
| TC3 | Layout | Flow text? (tìm `。<br>` → FAIL). Container 700px, margin:0? Table fixed? | `<br>` trong văn xuôi, container sai |
| TC4 | Từ vựng & NP | ≥80% từ đúng level? Từ vượt level dùng level gần nhất? N4/N5 không kanji N3+? Ngữ pháp phù hợp? | <80%, kanji vượt level ở N4/N5, ngữ pháp sai level |
| TC5 | Furigana | (a) Mọi từ vượt level có `<ruby>+<rt>`? (b) Không furigana cho từ đúng/dưới level? (c) Đếm ruby count: N5≤3, N4≤5, N3≤15, N2≤15, N1≤10 — vượt = đang furigana thừa? | Sót furigana, thừa furigana (furigana từ đúng level), format sai |

### BƯỚC 5: ⛔ QUALITY CHECK — PHẦN B: CÂU HỎI & ĐÁP ÁN (TC6)

> **⛔ AI HAY BỎ QUÊN BƯỚC NÀY. Check TC1-TC5 xong CHƯA PHẢI LÀ XONG.**
> **QC chưa check TC6 = QC CHƯA HOÀN THÀNH. KHÔNG được kết luận khi chưa check TC6.**

Đọc lại `question_{i}`, `answer_{i}`, `correct_answer_{i}` từ CSV vừa ghi:

| TC | Tiêu chí | FAIL nếu |
|----|----------|----------|
| TC6a | Tình huống | Q1 hoặc Q2 thiếu nhân vật tên thật + profile + điều kiện. "～について正しいものはどれか" = FAIL. "Aさん" = FAIL |
| TC6b | Kiểu hỏi | Q1 và Q2 dùng cùng kiểu (8 kiểu) |
| TC6c | Đáp án đúng | Copy nguyên văn từ bài (không paraphrase) |
| TC6d | Đáp án sai | Bịa thông tin không có trong bài. Sai hiển nhiên |
| TC6e | Test che bài | Che bài, nhìn 4 đáp án → đoán được đáp án đúng |
| TC6f | Format | `correct_answer` không phải integer ("2.0" thay vì "2") |

> **CHECKPOINT**: "Tôi đã đọc question_1, question_2, answer_1, answer_2 từ CSV chưa?"
> Nếu chưa đọc = QC chưa hoàn thành, KHÔNG được kết luận.

### BƯỚC 5b: SỬA BÀI FAIL → QUAY LẠI BƯỚC 4

Nếu bất kỳ TC nào FAIL:

| TC FAIL | Hành động |
|---------|-----------|
| TC1 (chars thiếu) | Gen lại toàn bộ HTML |
| TC2 (topic/logic sai) | Gen lại toàn bộ HTML |
| TC3 (layout) | Sửa HTML (bỏ `<br>`, fix CSS) |
| TC4 (vocab sai) | Gen lại toàn bộ HTML |
| TC5 (furigana) | Thêm/sửa ruby tags trong HTML |
| TC6 (question) | Sửa câu hỏi/đáp án → cập nhật CSV |

→ **Sau khi sửa → quay lại BƯỚC 4 chạy lại QC (CẢ PHẦN A + PHẦN B) → lặp đến khi PASS tất cả 6 TC**

### BƯỚC 6: CHỤP ẢNH (CHỈ SAU KHI QC PASS)

> **⛔ Đây là bước CUỐI CÙNG. Không sửa HTML sau khi chụp.**

Chỉ khi bài đã PASS tất cả 6 TC:
1. Chụp `container.screenshot()` (KHÔNG `page.screenshot()`)
2. viewport=700, crop sát nội dung
3. Save → `assets/img/tim_thong_tin/{id}.png`

### Output QC Report cho bài vừa PASS

```
╔══════════════════════════════════════════════════════════════════════════╗
║  QC REPORT — {_id}  (Level: {level})                                    ║
╠═══════════════ PHẦN A: HTML ════════════════════════════════════════════╣
║ TC1  Ký tự         │ {count} chars (min {min})          │ ✅ PASS      ║
║ TC2  Chủ đề/Format │ {chủ đề} — phù hợp {level}        │ ✅ PASS      ║
║ TC3  Layout         │ Flow text OK, container OK         │ ✅ PASS      ║
║ TC4  Từ vựng/NP    │ ~{%}% đúng level                   │ ✅ PASS      ║
║ TC5  Furigana       │ {count} ruby, format OK            │ ✅ PASS      ║
╠═══════════════ PHẦN B: CÂU HỎI & ĐÁP ÁN ══════════════════════════════╣
║ TC6a Tình huống     │ Q1: {tên}さん ✅  Q2: {tên}さん ✅  │ ✅ PASS      ║
║ TC6b Kiểu hỏi      │ Q1={kiểu}, Q2={kiểu}              │ ✅ PASS      ║
║ TC6c Đáp án đúng    │ Paraphrase ✅                       │ ✅ PASS      ║
║ TC6d Distractor     │ Có căn cứ trong bài ✅              │ ✅ PASS      ║
║ TC6e Test che bài   │ Không đoán được ✅                  │ ✅ PASS      ║
║ TC6f Format         │ correct_answer = integer ✅         │ ✅ PASS      ║
╠══════════════════════════════════════════════════════════════════════════╣
║ KẾT LUẬN: ✅ PASS — Screenshot captured                                ║
╚══════════════════════════════════════════════════════════════════════════╝
```

> **Nếu bảng chỉ có PHẦN A mà thiếu PHẦN B → QC CHƯA HOÀN THÀNH.**

---

## BƯỚC 7: LẶP LẠI

Quay lại BƯỚC 1 cho bài tiếp theo trong kế hoạch. Tiếp tục đến hết số lượng yêu cầu.

---

## KẾT THÚC: Tổng kết batch

```
TỔNG KẾT BATCH: {N} bài
├── ✅ PASS: {n} bài ({%}%)
├── Iterations: bài {id} sửa {x} lần, bài {id} sửa {y} lần
└── Files: {n} HTML, {n} PNG, CSV updated
```

---

# ═══════════════════════════════════════════════════
# PHẦN 3: TÀI LIỆU THAM KHẢO
# ═══════════════════════════════════════════════════

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

| Level | Files | Questions | IDs |
|-------|-------|-----------|-----|
| N1 | 4 | 2 per file | n1_qa_1~4 |
| N2 | 4 | 2 per file | n2_qa_1~4 |
| N3 | 4 | 2 per file | n3_qa_1~4 |
| N4 | 4 | 2 per file | n4_qa_1~4 |
| N5 | 4 | 1 per file | n5_qa_1~4 |

Before generating, read 2–3 passage references AND 1 QA reference for the target level.

## Bundled Scripts

### process_html.py

```bash
# Count chars only
python3 <skill>/scripts/process_html.py --count-only --file <html-file>

# Full pipeline: count + screenshot + CSV update
python3 <skill>/scripts/process_html.py --file <html-file> --img-dir assets/img/tim_thong_tin --csv sheets/samples_v5.csv

# Process all files in a directory
python3 <skill>/scripts/process_html.py --html-dir assets/html/tim_thong_tin --img-dir assets/img/tim_thong_tin --csv sheets/samples_v5.csv
```

## QC Automation Scripts

```python
import re
from pathlib import Path

def check_html(html_path: str, level: str) -> dict:
    """Kiểm tra tự động các tiêu chí đo được."""
    html = Path(html_path).read_text(encoding='utf-8')
    results = {}
    
    # TC1: Character count
    char_count = count_body_chars(html)
    min_chars = {"N1": 700, "N2": 700, "N3": 600, "N4": 400, "N5": 250}
    results["TC1_chars"] = {
        "count": char_count, "min": min_chars[level],
        "pass": char_count >= min_chars[level]
    }
    
    # TC3a: Flow text
    br_in_prose = len(re.findall(r'。\s*<br\s*/?>', html))
    results["TC3_flow_text"] = {"br_in_prose": br_in_prose, "pass": br_in_prose == 0}
    
    # TC3b: Container CSS
    has_margin_auto = bool(re.search(r'margin:\s*0\s+auto', html))
    has_min_height = bool(re.search(r'min-height', html))
    results["TC3_container"] = {"pass": not has_margin_auto and not has_min_height}
    
    # TC5a: Ruby count (tham khảo)
    ruby_count = len(re.findall(r'<ruby>', html))
    results["TC5_ruby_count"] = {"count": ruby_count}
    
    # TC5b: Wrong furigana format
    paren_furigana = re.findall(r'[\u4e00-\u9fff]+[（(][ぁ-ん]+[）)]', html)
    bracket_furigana = re.findall(r'[\u4e00-\u9fff]+【[ぁ-ん]+】', html)
    results["TC5_furigana_format"] = {
        "pass": len(paren_furigana) == 0 and len(bracket_furigana) == 0
    }
    
    return results

def check_csv_row(row: dict, level: str) -> dict:
    """Kiểm tra tự động CSV."""
    results = {}
    for i in ["1", "2"]:
        key = f"correct_answer_{i}"
        if key in row and row[key]:
            val = str(row[key]).strip()
            results[f"TC6_correct_answer_{i}"] = {"value": val, "pass": val in ["1","2","3","4"]}
        key = f"question_{i}"
        if key in row and row[key]:
            has_name = "さん" in row[key]
            has_generic = any(x in row[key] for x in ["Aさん", "Bさん", "人A", "人B"])
            results[f"TC6_scenario_q{i}"] = {"pass": has_name and not has_generic}
    return results
```
