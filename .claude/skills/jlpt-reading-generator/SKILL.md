---
name: jlpt-tim-thong-tin
description: >
  Generate JLPT 情報検索 (tìm thông tin / information retrieval) reading passages as beautifully
  styled HTML files, capture screenshots, produce clean HTML, and output CSV training data.
  Skill này bao gồm TOÀN BỘ luồng: gen → QC loop (checklist PASS/FAIL) → sửa → chụp ảnh.
  Gen từng bài một, kiểm tra đến khi đạt chất lượng mới chuyển sang bài tiếp theo.
  Use this skill whenever the user wants to: generate tìm thông tin content, create 情報検索 passages,
  batch-generate HTML reading materials, produce AI fine-tuning data for JLPT N1-N5,
  kiểm tra chất lượng, quality check, review bài, QC.
---

# JLPT 情報検索 — Workflow

> **Nguyên tắc cốt lõi:**
> 1. **Gen từng bài một** — không batch rồi QC sau
> 2. **Agent tự QC** — đọc lại bài + câu hỏi, tự đánh giá từng mục, log PASS/FAIL
> 3. **1 FAIL = chưa xong** — sửa → QC lại → lặp đến khi ALL PASS
> 4. **Screenshot cuối cùng** — CHỈ sau khi PASS tất cả

## Cấu trúc file

| File | Nội dung | Đọc khi |
|------|----------|---------|
| `SKILL.md` (file này) | Workflow + QC Checklist | Luôn đọc đầu tiên |
| `rules/content.md` | R1 chủ đề + R2 layout + R7 formats + R8 visual | Gen HTML |
| `rules/vocabulary.md` | R3 từ vựng/ngữ pháp + R4 furigana | Gen HTML + QC |
| `rules/questions.md` | R5 câu hỏi + R6 đáp án/bẫy | Gen Q&A + QC |
| `rules/technical.md` | R9 HTML template + R10 clean HTML + R11 CSV | Gen HTML + CSV |
| `scripts/screenshot.py` | Chụp ảnh (KHÔNG tự viết code) | Sau khi PASS checklist |
| `scripts/process_html.py` | Xử lý HTML → CSV | Gen CSV |

## Outputs Per Passage

1. **Styled HTML** → `assets/html/tim_thong_tin/{LEVEL}_{uuid}.html`
2. **Screenshot PNG** → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
3. **Clean HTML** → CSV column `text_read`

---

# WORKFLOW

## BƯỚC 0: CHUẨN BỊ (1 lần cho batch)

1. **Đọc rules**: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md`
2. Scan `sheets/` xem format đã dùng → chọn format chưa/ít dùng
3. Lập kế hoạch: mỗi bài gán format + visual + chủ đề (không trùng)
4. Read references: 1-2 HTML mẫu `input/html/` + 1 QA mẫu `input/htm_content_qa/` + `input/rule_gen_tim_thong_tin.md`

---

## BƯỚC 1→5: LẶP CHO TỪNG BÀI

### BƯỚC 1: GEN HTML + CÂU HỎI
> Đọc: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md` + `rules/questions.md`

1. Gen `_id` = `{LEVEL}_{uuid.uuid4().hex}`
2. Gen HTML theo rules → save `assets/html/tim_thong_tin/{id}.html`
3. Gen câu hỏi + đáp án theo `rules/questions.md`
4. Chạy process_html.py để tạo CSV + screenshot:
   ```bash
   python3 .claude/skills/jlpt-reading-generator/scripts/process_html.py \
     --file assets/html/tim_thong_tin/{LEVEL}_{uuid}.html \
     --img-dir assets/img/tim_thong_tin \
     --csv sheets/{LEVEL}.csv
   ```
5. Điền câu hỏi, đáp án, explanation vào CSV

---

### BƯỚC 2: ⛔ QC — AGENT TỰ ĐÁNH GIÁ CHECKLIST

> **ĐÂY LÀ BƯỚC QUAN TRỌNG NHẤT. KHÔNG ĐƯỢC BỎ QUA.**
>
> Agent phải **đọc lại** file HTML vừa gen + câu hỏi/đáp án trong CSV,
> rồi **tự đánh giá từng mục** bên dưới. Log kết quả theo format:
>
> ```
> QC: {_id}  |  Level: {LEVEL}
> ────────────────────────────────
> [ 1] ✅ PASS — Char count (275 chars, range 230-280)
> [ 2] ❌ FAIL — Flow text (found 2x 。<br>)
> [ 3] ✅ PASS — Container CSS
> ...
> ────────────────────────────────
> ⚠️ 1 FAIL → sửa rồi QC lại
> ```
>
> **⛔ KHÔNG ĐƯỢC tự PASS mà không đọc lại nội dung. Phải confirm từng mục.**

---

### BƯỚC 3: ⛔ CHECKLIST — TẤT CẢ PHẢI PASS

> **Quy tắc: 1 FAIL = chưa xong. Sửa → QC lại từ đầu → lặp đến khi ALL PASS.**

#### PHẦN A: HTML

Agent đọc lại file HTML và kiểm tra:

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 1 | **Char count** | Đếm ký tự visible trong body (bỏ whitespace, bỏ `<rt>`) | Trong ngưỡng: N5 230-280, N4 370-430, N3 560-640, N2/N1 660-740 |
| 2 | **Flow text** | Tìm `。<br>` trong HTML | Không có `。<br>` nào |
| 3 | **Container CSS** | Xem CSS trong HTML | Không có `margin:0 auto`, không `min-height` |
| 4 | **`.container`** | Xem HTML structure | Có `<div class="container">` bọc nội dung |
| 5 | **White background** | Xem CSS | Có `background:#fff` |
| 6 | **Furigana format** | Tìm ngoặc `漢字(かんじ)` hoặc `漢字【かんじ】` | Không có — tất cả furigana dùng `<ruby><rt>` |
| 7 | **Ruby có `<rt>`** | Xem mọi `<ruby>...</ruby>` | Tất cả đều có `<rt>` bên trong |
| 8 | **Ruby count** | Đếm số `<ruby>` | Trong ngưỡng: N5 0-5, N4 0-8, N3 5-20, N2 5-20, N1 3-15 |
| 9 | **Table layout** | Xem CSS nếu có `<table>` | Có `table-layout:fixed` (bỏ qua nếu không có table) |
| 10 | **Symbols** | Tìm ○×△※★◆◎【】 | Có ít nhất 1 symbol trong nội dung |

#### PHẦN B: NỘI DUNG & TỪ VỰNG

Agent đọc nội dung bài viết và đánh giá:

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 11 | **Chủ đề đúng level** | Đọc nội dung, đối chiếu `rules/content.md` R1 | Chủ đề phù hợp level (N5: đời sống cơ bản, N1: chuyên ngành) |
| 12 | **Nội dung logic** | Đọc toàn bài | Thông tin nhất quán, không mâu thuẫn, số liệu hợp lý |
| 13 | **Đủ dữ liệu tra cứu** | Đọc toàn bài | Có bảng/danh sách/lịch... để người đọc tra cứu |
| 14 | **Thông tin phân tán** | Xem thông tin liên quan đến đáp án | Nằm ở ≥2 vị trí khác nhau (không tập trung 1 chỗ) |
| 15 | **Từ vựng đúng level** | Đọc từng từ, đối chiếu `rules/vocabulary.md` R3 | Key terms ≤ level, không dùng ngữ pháp vượt level |
| 16 | **Furigana đúng từ** | Xem các `<ruby>` tags | Context words vượt level → CÓ furigana. Key terms đúng level → KHÔNG furigana |

#### PHẦN C: CÂU HỎI & ĐÁP ÁN

Agent đọc câu hỏi + 4 đáp án từ CSV và đánh giá:

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 17 | **Q1 tình huống** | Đọc câu hỏi 1 | Có nhân vật tên thật (không phải Aさん) + profile + điều kiện cụ thể |
| 18 | **Q1 cross-reference** | Thử trả lời Q1 | Phải scan ≥2 vị trí trong bài mới tìm được đáp án |
| 19 | **A1 format** | Xem 4 đáp án | Đúng 4 options, đều độ dài (ratio < 2.5), thì động từ nhất quán |
| 20 | **A1 correct_answer** | Xem giá trị correct_answer_1 | Integer 1-4 |
| 21 | **A1 đáp án đúng** | Đọc đáp án đúng + so bài | Paraphrase (N3+), không copy nguyên văn từ bài |
| 22 | **A1 distractors** | Đọc 3 đáp án sai | Có ≥2 loại bẫy: detail swap / condition miss / partial match / plausible wrong |
| 23 | **Test che bài** | Che bài, nhìn 4 đáp án | KHÔNG đoán được đáp án đúng chỉ từ đáp án |
| 24 | **Q2 exists (N1-N4)** | Xem CSV | Có câu hỏi 2 + 4 đáp án + correct_answer (bỏ qua nếu N5) |
| 25 | **Q2 ≠ Q1 kiểu** | So sánh Q1 và Q2 | Q1 và Q2 khác kiểu hỏi (ví dụ: Q1 hỏi thời gian, Q2 hỏi điều kiện) |
| 26 | **Explanations** | Xem CSV | Có explain_vn_1 và explain_en_1 (không trống) |

#### PHẦN D: ẢNH

Agent mở file PNG và xem:

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 27 | **Screenshot tồn tại** | Xem file PNG | File tồn tại, không rỗng |
| 28 | **Crop sát** | Nhìn ảnh | Không thừa khoảng trắng/viền xám bất kỳ cạnh nào |
| 29 | **Đủ nội dung** | Nhìn ảnh | Không bị cắt cụt — hiển thị đầy đủ bài |
| 30 | **Chữ rõ ràng** | Nhìn ảnh | Chữ không mờ, không bị che, không tràn |
| 31 | **Furigana hiển thị** | Nhìn ảnh | Ruby text hiện đúng vị trí, không lệch |
| 32 | **Bảng biểu nguyên vẹn** | Nhìn ảnh | Bảng không vỡ layout, cột không tràn |

---

### BƯỚC 4: SỬA & LẶP LẠI

| Nếu FAIL | Hành động | Sau đó |
|-----------|-----------|--------|
| #1, #11, #12, #13, #15 | Gen lại toàn bộ HTML | Quay lại BƯỚC 2 |
| #2, #3, #4, #5, #9, #10 | Sửa HTML/CSS | Quay lại BƯỚC 2 |
| #6, #7, #8, #16 | Sửa ruby tags | Quay lại BƯỚC 2 |
| #14 | Sửa bố cục bài (phân tán thông tin) | Quay lại BƯỚC 2 |
| #17-#26 | Sửa câu hỏi/đáp án trong CSV | Quay lại BƯỚC 2 |
| #27-#32 | Sửa HTML/CSS → chạy lại screenshot | Quay lại BƯỚC 2 |

**Lệnh chạy lại screenshot:**
```bash
python3 .claude/skills/jlpt-reading-generator/scripts/screenshot.py \
  --html assets/html/tim_thong_tin/{LEVEL}_{uuid}.html \
  --png  assets/img/tim_thong_tin/{LEVEL}_{uuid}.png
```

> **Vòng lặp: sửa → quay lại BƯỚC 2 (QC lại TẤT CẢ) → nếu còn FAIL thì lặp lại.**
> **Tối đa 5 vòng. Sau 5 vòng vẫn FAIL → báo lỗi cho user, KHÔNG bỏ qua.**

---

### BƯỚC 5: ✅ HOÀN THÀNH → BÀI TIẾP THEO

Chỉ khi **TẤT CẢ 32 checks PASS** → log:
```
🎉 ALL PASSED (32/32) — {_id} hoàn thành
```
→ Chuyển sang bài tiếp theo (quay lại BƯỚC 1).

---

## Reference Samples

- Passage HTML (61 files): `input/html/` — N1(14), N2(12), N3(15), N4(10), N5(10)
- QA references (20 files): `input/htm_content_qa/` — 4 per level
- Teacher rules: `input/rule_gen_tim_thong_tin.md`
