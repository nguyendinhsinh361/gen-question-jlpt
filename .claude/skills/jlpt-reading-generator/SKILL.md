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
| `scripts/process_html.py` | Xử lý HTML → CSV (tạo row) | Gen CSV |
| `scripts/fill_qa.py` | Điền Q&A vào CSV (quote an toàn) | Sau khi gen Q&A |

## Outputs Per Passage

1. **Styled HTML** → `assets/html/tim_thong_tin/{LEVEL}_{uuid}.html`
2. **Screenshot PNG** → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
3. **Clean HTML** → CSV column `text_read`

---

# WORKFLOW

## BƯỚC 0: CHUẨN BỊ (1 lần cho batch)

1. **Đọc rules**: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md`
2. **Đọc `input/jlpt_kanji.csv`** — dùng để tra level từng kanji khi quyết định furigana
3. Scan `sheets/` xem format đã dùng → chọn format chưa/ít dùng
4. Lập kế hoạch: mỗi bài gán format + visual + chủ đề (không trùng)
5. Read references: 1-2 HTML mẫu `input/html/` + 1 QA mẫu `input/htm_content_qa/` + `input/rule_doc_hieu.md`

---

## BƯỚC 1→5: LẶP CHO TỪNG BÀI

### BƯỚC 1: GEN HTML + CÂU HỎI
> Đọc: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md` + `rules/questions.md`

1. Gen `_id` = `{LEVEL}_{uuid.uuid4().hex}`
2. Chọn format tag từ R7 (`rules/content.md`) — xem danh sách 15 formats. Scan `sheets/` để chọn format chưa/ít dùng.
3. Gen HTML theo rules → save `assets/html/tim_thong_tin/{id}.html`
4. Gen câu hỏi + đáp án theo `rules/questions.md`
5. Chạy process_html.py để tạo CSV + screenshot (⚠️ **BẮT BUỘC truyền `--tag` và `--replace`**):
   ```bash
   python3 .claude/skills/jlpt-reading-generator/scripts/process_html.py \
     --file assets/html/tim_thong_tin/{LEVEL}_{uuid}.html \
     --img-dir assets/img/tim_thong_tin \
     --csv sheets/{LEVEL}.csv \
     --tag {format_tag} \
     --replace
   ```
6. Điền câu hỏi, đáp án, explanation vào CSV bằng **fill_qa.py**:
   > **⛔ KHÔNG ĐƯỢC sửa CSV bằng tay. Commas trong nội dung (ví dụ 100,000円) sẽ làm vỡ cột.**
   > **LUÔN dùng script fill_qa.py — script tự quote đúng.**
   ```bash
   python3 .claude/skills/jlpt-reading-generator/scripts/fill_qa.py \
     --csv sheets/{LEVEL}.csv --row-id {LEVEL}_{uuid} \
     --q1 "Câu hỏi 1..." \
     --a1 "Đáp án 1
   Đáp án 2
   Đáp án 3
   Đáp án 4" \
     --ca1 2 \
     --evn1 "Explanation VN..." \
     --een1 "Explanation EN..."
   ```
   Với N1-N4 (2 câu hỏi), thêm `--q2`, `--a2`, `--ca2`, `--evn2`, `--een2`.

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
| 3 | **Container CSS + word-break** | Xem CSS trong HTML | Không có `margin:0 auto`, không `min-height`. `word-break: auto-phrase` + `text-align: justify` (KHÔNG `keep-all`, KHÔNG `normal`) |
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
| 14 | **Thông tin phân tán** | Xem thông tin liên quan đến đáp án | Nằm ở ≥3 vị trí khác nhau (bảng + lưu ý + đoạn văn...) |
| 15 | **Từ vựng đúng level** | Đọc từng từ, đối chiếu `rules/vocabulary.md` R3 | Key terms ≤ level, không dùng ngữ pháp vượt level |
| 16 | **⛔ Furigana đúng từ (tra CSV)** | Liệt kê TẤT CẢ từ kanji trong bài → tra TỪNG ký tự trong `input/jlpt_kanji.csv` → ghi: `từ(ký tự=level)` → kết luận cần/không cần furigana. **PHẢI log bảng tra này.** Ví dụ: `全部(全=N3,部=N4) → bài N5 → CẦN furigana ✓` | Mọi từ có kanji > level đều có `<ruby><rt>`. Không thừa. Không thiếu. KHÔNG đoán — phải tra CSV |

#### PHẦN C: CÂU HỎI & ĐÁP ÁN

Agent đọc câu hỏi + 4 đáp án từ CSV và đánh giá:

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 17 | **Q1 tình huống** | Đọc câu hỏi 1 | Nhân vật tên thật + profile + **≥3 điều kiện ràng buộc** đồng thời |
| 18 | **Q1 cross-reference** | Thử trả lời Q1 | Phải scan **≥3 vị trí** trong bài mới tìm được đáp án |
| 19 | **A1 format** | Xem 4 đáp án | Đúng 4 options, đều độ dài (ratio < 2.0), thì động từ nhất quán |
| 20 | **A1 correct_answer** | Xem giá trị correct_answer_1 | Integer 1-4. Vị trí ≠ correct_answer_2 (nếu có Q2). Scan batch: không lặp cùng vị trí ≥3 lần liên tiếp |
| 21 | **A1 paraphrase** | So đáp án đúng với bài gốc | KHÔNG trùng cụm ≥4 từ liên tiếp (N3+) hoặc ≥6 từ (N4/N5) |
| 22 | **A1 đủ 4 loại bẫy** | Đọc 3 đáp án sai, xác định loại bẫy | Đủ: ① condition miss ② calculation trap ③ detail swap ④ partial match |
| 23 | **A1 distractor khó loại** | Với mỗi đáp án sai: có dùng info thật? Cần quay lại bài mới loại? | Không có đáp án nào loại được trong <3 giây bằng common sense |
| 24 | **Test che bài** | Che bài, nhìn 4 đáp án | Cả 4 đều hợp lý như nhau, KHÔNG đoán được đáp án đúng |
| 25 | **Q2 exists (N1-N4)** | Xem CSV | Có câu hỏi 2 + 4 đáp án + correct_answer (bỏ qua nếu N5) |
| 26 | **Q2 ≠ Q1 kiểu** | So sánh Q1 và Q2 | Q1 và Q2 khác kiểu hỏi (ví dụ: Q1 hỏi thời gian, Q2 hỏi điều kiện) |
| 27 | **Explanations đầy đủ** | Đọc explain_vn_1 + explain_en_1 | Giải thích đủ 3 phần (xem format bên dưới) |
| 28 | **⛔ CSV data completeness** | Đọc CSV row, kiểm tra TỪNG field bắt buộc | TẤT CẢ fields PHẢI có dữ liệu (không empty): `_id`, `level`, `tag`, `jp_char_count`, `text_read`, `general_image`, `question_label_1`, `question_1`, `answer_1` (đủ 4 options), `correct_answer_1`, `explain_vn_1`, `explain_en_1`. Với N1-N4: thêm tất cả `_2` fields. Thiếu BẤT KỲ field nào = FAIL |

> **⛔ CHECK #27 — FORMAT EXPLANATION BẮT BUỘC**
>
> Explanation không chỉ "có nội dung" — nó phải **chứng minh** câu hỏi + đáp án đúng logic.
> Agent viết explain_vn_1 và explain_en_1 theo đúng 3 phần sau:
>
> **Phần 1 — Đáp án đúng:** Giải thích TẠI SAO đáp án đúng là đúng. Trích dẫn cụ thể vị trí trong bài
> (ví dụ: "Theo bảng 【クラスと料金】..." hoặc "Phần 【予約について】 ghi rằng...").
> Phải cross-reference ≥2 thông tin từ bài.
>
> **Phần 2 — Đáp án sai:** Giải thích TẠI SAO từng đáp án sai là sai. Nêu rõ loại bẫy
> (detail swap / condition miss / partial match / plausible wrong) và chỉ ra thông tin nào trong bài
> khiến đáp án đó sai.
>
> **Phần 3 — Tóm tắt:** 1 câu ngắn tóm lại logic tìm đáp án.
>
> **Ví dụ explain_vn_1:**
> ```
> ĐÁP ÁN ĐÚNG (2): 10時
> Theo bảng【クラスと料金】, ngày Thứ Bảy có lớp 週末ヨガ lúc 14:00～15:30.
> Phần【わりびき】ghi: đi cùng bạn được giảm 500円/người → 2,500 - 500 = 2,000円.
> Vậy đáp án đúng là 2,000円.
>
> ĐÁP ÁN SAI:
> (1) 1,500円 — detail swap: đây là giá lớp はじめてのヨガ (Thứ Ba), không phải 週末ヨガ.
> (3) 2,500円 — condition miss: bỏ qua điều kiện giảm giá khi đi cùng bạn.
> (4) 3,000円 — plausible wrong: không có giá này trong bài.
>
> Tóm tắt: Cần kết hợp bảng giá + điều kiện giảm giá để tính đúng.
> ```

#### PHẦN C2: VERIFY ĐÁP ÁN (⛔ QUAN TRỌNG NHẤT)

> **Agent tự giải bài từ đầu — KHÔNG nhìn đáp án đã gen.**
> Đây là bước bắt lỗi tính toán sai, thông tin mơ hồ, distractor bịa.

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 29 | **Tự tính Q1** | Đọc bài + câu hỏi 1, tự tính/tìm đáp án từ đầu (KHÔNG nhìn 4 options) | Kết quả tự tính KHỚP với correct_answer trong CSV |
| 30 | **Tự tính Q2** | Tương tự cho câu hỏi 2 (bỏ qua nếu N5) | Kết quả tự tính KHỚP với correct_answer trong CSV |
| 31 | **Test mơ hồ** | Đọc lại mỗi điều kiện/giảm giá/ngoại lệ, thử hiểu theo 2 cách khác nhau | Chỉ có DUY NHẤT 1 cách hiểu hợp lý. Nếu có 2 cách → FAIL → sửa bài viết cho rõ |
| 32 | **Distractor self-test** | Với TỪNG đáp án sai: trích dẫn chính xác câu/vị trí trong bài dùng để bác bỏ | Mỗi distractor đều trích được câu cụ thể. Không trích được = BỊA → FAIL |
| 33 | **Đếm vị trí cross-ref** | Liệt kê CỤ THỂ các vị trí người đọc phải scan để trả lời mỗi câu hỏi | Mỗi câu hỏi cần scan ≥3 vị trí khác nhau. Ít hơn = câu hỏi quá dễ → FAIL |

#### PHẦN D: ẢNH

Agent mở file PNG và xem:

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 34 | **Screenshot tồn tại** | Xem file PNG | File tồn tại, không rỗng |
| 35 | **Crop sát** | Nhìn ảnh | Không thừa khoảng trắng/viền xám bất kỳ cạnh nào |
| 36 | **Đủ nội dung** | Nhìn ảnh | Không bị cắt cụt — hiển thị đầy đủ bài |
| 37 | **Chữ rõ ràng, không bị che** | Nhìn ảnh | Chữ không mờ, không bị element khác đè, không tràn. Label/badge KHÔNG che text dòng trước |
| 38 | **Furigana hiển thị** | Nhìn ảnh | Ruby text hiện đúng vị trí, không lệch |
| 39 | **Bảng biểu nguyên vẹn** | Nhìn ảnh | Bảng không vỡ layout, cột không tràn |

---

### BƯỚC 4: SỬA & LẶP LẠI

> **⛔ RULE BẮT BUỘC: Bất kỳ khi nào sửa file HTML (dù chỉ 1 ký tự CSS/ruby/content):**
> 1. **Chạy lại screenshot** — ảnh cũ = ảnh sai
> 2. **Cập nhật CSV** — chạy lại `process_html.py --replace` để cập nhật `text_read`, `jp_char_count`, `general_image` trong CSV
>
> Không làm 2 bước này = QC trên data cũ → vô nghĩa.

| Nếu FAIL | Hành động | Sau đó |
|-----------|-----------|--------|
| #1, #11, #12, #13, #15 | Gen lại toàn bộ HTML → **chạy lại screenshot** | Quay lại BƯỚC 2 |
| #2, #3, #4, #5, #9, #10 | Sửa HTML/CSS → **chạy lại screenshot** | Quay lại BƯỚC 2 |
| #6, #7, #8, #16 | Sửa ruby tags → **chạy lại screenshot** | Quay lại BƯỚC 2 |
| #14 | Sửa bố cục bài → **chạy lại screenshot** | Quay lại BƯỚC 2 |
| #17-#28 | Sửa câu hỏi/đáp án/CSV fields (không cần chạy lại screenshot) | Quay lại BƯỚC 2 |
| #29-#30 (tự tính sai) | Kiểm tra lại phép tính, sửa đáp án hoặc sửa bài viết | Quay lại BƯỚC 2 |
| #31 (mơ hồ) | Sửa bài viết cho rõ ràng → **chạy lại screenshot** | Quay lại BƯỚC 2 |
| #32 (distractor bịa) | Viết lại distractor dùng info thật từ bài | Quay lại BƯỚC 2 |
| #33 (câu hỏi dễ) | Viết lại câu hỏi + tình huống phức tạp hơn | Quay lại BƯỚC 2 |
| #34-#39 | Sửa HTML/CSS → **chạy lại screenshot** | Quay lại BƯỚC 2 |

**Lệnh chạy lại screenshot (BẮT BUỘC sau mỗi lần sửa HTML):**
```bash
python3 .claude/skills/jlpt-reading-generator/scripts/screenshot.py \
  --html assets/html/tim_thong_tin/{LEVEL}_{uuid}.html \
  --png  assets/img/tim_thong_tin/{LEVEL}_{uuid}.png
```

> **Vòng lặp: sửa HTML → chạy lại screenshot → quay lại BƯỚC 2 (QC lại TẤT CẢ) → nếu còn FAIL thì lặp lại.**
> **Tối đa 5 vòng. Sau 5 vòng vẫn FAIL → báo lỗi cho user, KHÔNG bỏ qua.**

---

### BƯỚC 5: ✅ HOÀN THÀNH → BÀI TIẾP THEO

Chỉ khi **TẤT CẢ 33 checks PASS** → log:
```
🎉 ALL PASSED (39/39) — {_id} hoàn thành
```
→ Chuyển sang bài tiếp theo (quay lại BƯỚC 1).

---

## BƯỚC CUỐI: GỘP CSV (sau khi gen xong TẤT CẢ bài)

> Sau khi hoàn thành toàn bộ batch, gộp các file CSV theo level thành **1 file duy nhất**.

```bash
python3 -c "
import csv, glob, os
files = sorted(glob.glob('sheets/N*.csv'))
rows = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        rows.extend(list(csv.DictReader(fh)))
if rows:
    out = 'sheets/all_tim_thong_tin.csv'
    with open(out, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f'✅ Merged {len(rows)} rows from {len(files)} files → {out}')
"
```

Output: `sheets/all_tim_thong_tin.csv` — chứa tất cả bài từ N1→N5.

---

## Reference Samples

- Passage HTML (61 files): `input/html/` — N1(14), N2(12), N3(15), N4(10), N5(10)
- QA references (20 files): `input/htm_content_qa/` — 4 per level
- Teacher rules: `input/rule_doc_hieu.md`
