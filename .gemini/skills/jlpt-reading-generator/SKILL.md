---
name: jlpt-tim-thong-tin
description: >
  Generate JLPT 情報検索 (tìm thông tin / information retrieval) reading passages as beautifully
  styled HTML files, capture screenshots, produce clean HTML, and output CSV training data.
  Skill này bao gồm TOÀN BỘ luồng: gen → QC loop (6 tiêu chí) → sửa → chụp ảnh.
  Gen từng bài một, kiểm tra đến khi đạt chất lượng mới chuyển sang bài tiếp theo.
  Use this skill whenever the user wants to: generate tìm thông tin content, create 情報検索 passages,
  batch-generate HTML reading materials, produce AI fine-tuning data for JLPT N1-N5,
  kiểm tra chất lượng, quality check, review bài, QC.
---

# JLPT 情報検索 — Workflow

> **⚠️ CẢNH BÁO DÀNH CHO GEMINI:**
> Gemini có 3 xu hướng lỗi nghiêm trọng:
> 1. **Gen khó hơn level** — bài N4 nhưng dùng từ vựng/ngữ pháp N2-N3 → đọc `rules/vocabulary.md`
> 2. **Dùng ngoặc thay ruby** — `漢字(かんじ)` thay vì `<ruby>漢字<rt>かんじ</rt></ruby>` → REJECT
> 3. **Thiếu `<rt>` trong `<ruby>`** — `<ruby>漢字</ruby>` mà không có `<rt>` → REJECT

> **Nguyên tắc cốt lõi:**
> 1. **Gen từng bài một** — không batch rồi QC sau
> 2. **QC loop** — check 6 TC → FAIL → sửa → check lại → lặp đến khi PASS
> 3. **Screenshot cuối cùng** — CHỈ sau khi PASS tất cả 6 TC
> 4. **1 FAIL = REJECT** — không có ngoại lệ

## Cấu trúc file

| File | Nội dung | Đọc khi |
|------|----------|---------|
| `SKILL.md` (file này) | Workflow BƯỚC 0→7 | Luôn đọc đầu tiên |
| `rules/content.md` | R1 chủ đề + R2 layout + R7 formats + R8 visual | BƯỚC 1 (gen HTML) |
| `rules/vocabulary.md` | R3 từ vựng/ngữ pháp + R4 furigana | BƯỚC 1 + BƯỚC 2 |
| `rules/questions.md` | R5 câu hỏi + R6 đáp án/bẫy | BƯỚC 3 (gen Q&A) |
| `rules/technical.md` | R9 HTML template + R10 clean HTML + R11 CSV + QC scripts | BƯỚC 1 + BƯỚC 3 + BƯỚC 4 |
| `scripts/screenshot.py` | Script chụp ảnh (KHÔNG tự viết code) | BƯỚC 6 |
| `scripts/process_html.py` | Script xử lý HTML → CSV | BƯỚC 3 |

## Outputs Per Passage

1. **Styled HTML** → `assets/html/tim_thong_tin/{LEVEL}_{uuid}.html`
2. **Screenshot PNG** → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
3. **Clean HTML** → CSV column `text_read`

---

# WORKFLOW

## BƯỚC 0: CHUẨN BỊ (1 lần cho batch)

1. **Đọc rules**: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md` (HTML template)
2. Scan `sheets/` xem format đã dùng → chọn format chưa/ít dùng
3. Lập kế hoạch: mỗi bài gán format + visual + chủ đề (không trùng)
4. Read references: 1-2 HTML mẫu `input/html/` + 1 QA mẫu `input/htm_content_qa/` + `input/rule_gen_tim_thong_tin.md`

---

## BƯỚC 1→7: LẶP CHO TỪNG BÀI

### BƯỚC 1: GEN HTML
> Đọc: `rules/content.md` (chủ đề, format, layout) + `rules/vocabulary.md` (từ vựng, furigana) + `rules/technical.md` (HTML template)

1. Gen `_id` = `{LEVEL}_{uuid.uuid4().hex}`
2. Gen HTML theo rules
3. `count_body_chars()` → < Hard Reject → gen lại (xem bảng char count trong `rules/content.md`)
4. Save HTML → `assets/html/tim_thong_tin/{id}.html`

### BƯỚC 2: FURIGANA VERIFICATION (⛔ BLOCKING)
> Đọc: `rules/vocabulary.md` R4

> **⚠️ GEMINI: Sau khi gen HTML, BẮT BUỘC kiểm tra:**
> 1. Có bất kỳ furigana nào dùng ngoặc `()` hoặc `【】` không? → gen lại
> 2. Có `<ruby>` nào thiếu `<rt>` không? → sửa ngay
> 3. Có furigana cho từ đúng level không? → xóa bớt

1. Scan kanji → check level từng từ
2. Key terms đúng level → KHÔNG furigana
3. Context words vượt level → PHẢI có `<ruby>+<rt>`
4. Đếm ruby count → vượt ngưỡng → đang furigana thừa, xóa bớt

### BƯỚC 3: GEN CÂU HỎI + ĐÁP ÁN
> Đọc: `rules/questions.md` (câu hỏi, đáp án, bẫy)

1. Gen theo rules (tình huống, cross-reference, 4 loại bẫy)
2. Kiểm tra: thông tin trả lời phân tán ≥2 vị trí?
3. Kiểm tra: đáp án tương đương độ dài? Thì động từ nhất quán?
4. Extract clean HTML → fill CSV (xem `rules/technical.md` R10, R11)

### BƯỚC 4: ⛔ QC PHẦN A — HTML (TC1-TC5)

| TC | Tiêu chí | FAIL nếu |
|----|----------|----------|
| TC1 | Ký tự | Ngoài ngưỡng chấp nhận |
| TC2 | Chủ đề & Format | Chủ đề sai level, nội dung phi logic, thiếu dữ liệu tra cứu, thông tin tập trung 1 chỗ |
| TC3 | Layout | `。<br>`, container sai, thiếu bảng biểu/ký hiệu |
| TC4 | Từ vựng & NP | Key terms vượt level, ngữ pháp sai level, thuật ngữ ở vị trí nổi bật không giải thích |
| TC5 | Furigana | Sót furigana context words, thừa furigana key terms, ruby count vượt ngưỡng, format sai (ngoặc/thiếu rt) |

### BƯỚC 5: ⛔ QC PHẦN B — CÂU HỎI (TC6)

> **⛔ AI HAY BỎ QUÊN. Check TC1-TC5 xong CHƯA PHẢI LÀ XONG.**

| TC | Tiêu chí | FAIL nếu |
|----|----------|----------|
| TC6a | Tình huống | Q thiếu nhân vật tên thật + profile + điều kiện |
| TC6b | Cross-reference | Đáp án tìm được trong 1 câu/1 chỗ duy nhất (không cần scan) |
| TC6c | Kiểu hỏi | Q1 = Q2 cùng kiểu |
| TC6d | Đáp án đúng | Copy nguyên văn (N3+), không paraphrase |
| TC6e | Distractor | Bịa thông tin, sai hiển nhiên, thiếu bẫy chất lượng |
| TC6f | Test che bài | Che bài, nhìn 4 đáp án → đoán được |
| TC6g | Hình thức | correct_answer ≠ integer; đáp án không đều độ dài; thì không nhất quán |

> **CHECKPOINT**: "Tôi đã đọc question + answer từ CSV chưa?" Chưa = QC chưa xong.

### BƯỚC 5b: SỬA → QUAY LẠI BƯỚC 4

| FAIL | Hành động |
|------|-----------|
| TC1/TC2/TC4 | Gen lại toàn bộ HTML |
| TC3 | Sửa HTML (bỏ `<br>`, fix CSS) |
| TC5 | Sửa ruby tags |
| TC6 | Sửa câu hỏi/đáp án → cập nhật CSV |

**Lặp BƯỚC 4→5→5b cho đến khi tất cả TC1-TC6 PASS.**

---

### BƯỚC 6: CHỤP ẢNH (CHỈ SAU KHI PASS)

**Chạy script có sẵn — KHÔNG tự viết code Playwright:**
```bash
python3 .gemini/skills/jlpt-reading-generator/scripts/screenshot.py \
  --html assets/html/tim_thong_tin/{LEVEL}_{uuid}.html \
  --png  assets/img/tim_thong_tin/{LEVEL}_{uuid}.png
```

---

### BƯỚC 6b: ⛔ KIỂM TRA ẢNH — RETRY LOOP (BẮT BUỘC)

> **⛔ KHÔNG ĐƯỢC bỏ qua bước này. KHÔNG ĐƯỢC chuyển sang bài tiếp theo khi ảnh chưa đạt.**

**Quy trình bắt buộc sau mỗi lần chụp:**

1. **Mở file PNG** vừa save và xem bằng mắt (dùng tool đọc ảnh)
2. **Kiểm tra 5 tiêu chí** bên dưới
3. **Nếu bất kỳ tiêu chí nào FAIL** → thực hiện hành động sửa → **chạy lại script** → **quay lại bước 1**
4. **Chỉ khi tất cả 5 tiêu chí PASS** → chuyển sang BƯỚC 7

| # | Kiểm tra | FAIL nếu | Hành động sửa |
|---|----------|----------|----------------|
| 1 | **Crop sát** | Thừa khoảng trắng/viền xám bất kỳ cạnh nào | Thêm vào HTML: `html,body{background:#fff!important;margin:0!important;padding:0!important}` rồi chạy lại script |
| 2 | **Đủ nội dung** | Bị cắt cụt — thiếu phần cuối bài | Chạy lại script (script tự resize viewport) |
| 3 | **Chữ rõ ràng** | Chữ bị mờ, bị che, bị tràn | Sửa CSS (font-size, overflow, width) rồi chạy lại script |
| 4 | **Furigana hiển thị** | Ruby text không hiện hoặc bị lệch | Sửa `<ruby><rt>` tags rồi chạy lại script |
| 5 | **Bảng biểu nguyên vẹn** | Bảng bị vỡ layout, cột bị tràn | Sửa CSS bảng (table-layout, width) rồi chạy lại script |

**Lệnh chạy lại script (copy-paste):**
```bash
python3 .gemini/skills/jlpt-reading-generator/scripts/screenshot.py \
  --html assets/html/tim_thong_tin/{LEVEL}_{uuid}.html \
  --png  assets/img/tim_thong_tin/{LEVEL}_{uuid}.png
```

> **⚠️ GEMINI: Mỗi lần sửa xong HTML → PHẢI chạy lại lệnh trên → PHẢI mở lại ảnh kiểm tra.**
> **Vòng lặp: sửa → chạy script → xem ảnh → kiểm tra → nếu FAIL thì lặp lại. Tối đa 5 lần.**
> **Nếu sau 5 lần vẫn FAIL → báo lỗi cho user, KHÔNG bỏ qua.**

---

### BƯỚC 7: LẶP LẠI → bài tiếp theo

---

## Reference Samples

- Passage HTML (61 files): `input/html/` — N1(14), N2(12), N3(15), N4(10), N5(10)
- QA references (20 files): `input/htm_content_qa/` — 4 per level
- Teacher rules: `input/rule_gen_tim_thong_tin.md`
