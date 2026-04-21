# Prompt Guide — Gen nội dung Tìm Thông Tin (JLPT 情報検索)

> **BẮT BUỘC đọc SKILL.md** trước khi gen. File này chỉ là prompt template ngắn gọn.

---

## Nhắc nhở bắt buộc (copy vào cuối MỌI prompt)

```
Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu từ input/html/ và input/htm_content_qa/
- ≥80% từ vựng đúng level. Từ vượt level → ưu tiên level gần nhất, hạn chế thuật ngữ. N4/N5 KHÔNG dùng kanji N3+ (当, 届, 締, 割...)
- Độ khó từ CẤU TRÚC THÔNG TIN (cross-reference, ngoại lệ), KHÔNG từ nhồi thuật ngữ
- Chars đạt minimum (N1:700-800, N2:700-770, N3:600-750, N4:400-500, N5:250-290). Dưới Min → gen lại
- Nội dung phải logic, thực tế (giá hợp lý, thời gian không mâu thuẫn). Phi logic → gen lại
- Câu hỏi TÌNH HUỐNG: nhân vật tên thật + profile + điều kiện → chọn gì. KHÔNG Aさん/Bさん
- Q1 và Q2 phải khác kiểu (chọn phương án / kiểm tra tư cách / thủ tục / tính chi phí / đúng-sai / ngoại lệ / so sánh / xử lý vấn đề)
- Đáp án đúng: paraphrase từ bài đọc, KHÔNG copy nguyên văn
- Đáp án sai: chứa thông tin CÓ trong bài nhưng sai điều kiện, phải đọc kỹ mới loại được. KHÔNG bịa thông tin
- Test: che bài đọc, nhìn 4 đáp án → nếu đoán được → gen lại
- Furigana: chỉ <ruby>+<rt> cho từ vượt level. KHÔNG ngoặc (), KHÔNG dạng Ab. Gen xong → đếm ruby tags → N1≥3, N2≥5, N3≥5. Nếu = 0 → gen lại
- Layout compact: viewport=700, container.screenshot(), margin:0, padding:12px 16px. Flow text, không <br>, không tách từ
- Format đa dạng: scan format đã dùng → chọn format chưa dùng/ít dùng
- QC: gen xong → chạy quality check (6 tiêu chí) → 1 FAIL = gen lại
```

---

## 1. Gen theo level — Batch 5 bài

```
Gen 5 bài tìm thông tin level {LEVEL}, mỗi bài format khác nhau. Lưu CSV trong sheets/

BƯỚC 1: Scan format đã dùng → chọn 5 format chưa dùng/ít dùng
BƯỚC 2: Gen nội dung theo SKILL.md
BƯỚC 3 (QC): Với MỖI bài vừa gen, chạy quality check 6 tiêu chí:
  - TC1: count_body_chars() ≥ minimum?
  - TC2: chủ đề phù hợp level? nội dung logic?
  - TC3: flow text (không <br>)? container CSS đúng?
  - TC4: ≥80% từ vựng đúng level? ngữ pháp phù hợp?
  - TC5: đếm <ruby> tags ≥ minimum? format furigana đúng?
  - TC6: câu hỏi tình huống? paraphrase? distractor cần suy nghĩ?
  → 1 FAIL bất kỳ = sửa/gen lại → chạy lại QC đến khi PASS

{Paste nhắc nhở bắt buộc}
```

---

## 2. Gen batch lớn — Chỉ định số lượng

```
Gen batch bài tìm thông tin, lưu CSV trong sheets/

- N1: {số} bài
- N2: {số} bài
- N3: {số} bài
- N4: {số} bài
- N5: {số} bài

BƯỚC 1: Scan format đã dùng → lên kế hoạch format cho từng bài
BƯỚC 2: Gen tối đa 5 bài/lượt
BƯỚC 3 (QC): Sau mỗi lượt 5 bài, chạy quality check 6 tiêu chí cho từng bài:
  TC1(chars) → TC2(topic) → TC3(layout) → TC4(vocab) → TC5(furigana) → TC6(question)
  → Sửa bài FAIL → confirm PASS → gen lượt tiếp

{Paste nhắc nhở bắt buộc}
```

---

## 3. Gen theo format cụ thể

```
Gen 1 bài tìm thông tin level {LEVEL}, format: {FORMAT}

Chủ đề: {mô tả ngắn}
- Đọc mẫu {LEVEL}_*.html trước

Sau khi gen xong → chạy quality check 6 tiêu chí (TC1-TC6). Nếu FAIL → sửa/gen lại.

{Paste nhắc nhở bắt buộc}
```

---

## 4. Chỉ gen câu hỏi (cho bài đã có)

```
Gen câu hỏi cho các bài trong sheets/{file}.csv

- Đọc HTML mỗi bài trước
- Câu hỏi TÌNH HUỐNG với tên thật + profile cụ thể
- Q1 và Q2 khác kiểu
- Đáp án đúng paraphrase, đáp án sai có căn cứ trong bài
- Test: che bài → nhìn đáp án → không đoán được
- Cập nhật CSV

QC sau khi gen: kiểm tra TC6 cho từng bài (tình huống, kiểu hỏi, paraphrase, distractor, correct_answer format). FAIL → sửa lại.
```

---

## 5. Kiểm tra & sửa lỗi (Quality Check toàn bộ)

```
Đọc jlpt-quality-check/SKILL.md, sau đó kiểm tra chất lượng tất cả bài trong sheets/{file}.csv

Chạy 6 tiêu chí cho từng bài:
  TC1: Ký tự (count_body_chars ≥ minimum)
  TC2: Chủ đề & format phù hợp level, nội dung logic thực tế
  TC3: Layout (flow text không <br>, container 700px margin:0)
  TC4: Từ vựng ≥80% đúng level, ngữ pháp phù hợp, không nhồi thuật ngữ
  TC5: Furigana (ruby count ≥ minimum, chỉ <ruby>+<rt>, không ngoặc/Ab)
  TC6: Câu hỏi tình huống, Q1≠Q2, paraphrase, distractor có căn cứ, correct_answer integer

Output: bảng PASS/FAIL từng bài + tổng kết batch.
Sửa bài FAIL:
  - TC3/TC5: sửa HTML → chụp lại screenshot
  - TC6: sửa câu hỏi/đáp án → cập nhật CSV
  - TC1/TC2/TC4: gen lại toàn bộ
Chạy lại QC sau khi sửa → confirm PASS.
```
