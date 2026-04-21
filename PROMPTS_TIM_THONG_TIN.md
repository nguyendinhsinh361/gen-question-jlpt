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
- Furigana: chỉ <ruby>+<rt> cho từ vượt level. KHÔNG ngoặc (), KHÔNG dạng Ab. Gen xong → scan lại
- Layout compact: viewport=700, container.screenshot(), margin:0, padding:12px 16px. Flow text, không <br>, không tách từ
- Format đa dạng: scan format đã dùng → chọn format chưa dùng/ít dùng
```

---

## 1. Gen theo level — Batch 5 bài

```
Gen 5 bài tìm thông tin level {LEVEL}, mỗi bài format khác nhau. Lưu CSV trong sheets/

BƯỚC 1: Scan format đã dùng → chọn 5 format chưa dùng/ít dùng
BƯỚC 2: Gen nội dung theo SKILL.md

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
BƯỚC 2: Gen tối đa 5 bài/lượt, kiểm tra rồi gen tiếp

{Paste nhắc nhở bắt buộc}
```

---

## 3. Gen theo format cụ thể

```
Gen 1 bài tìm thông tin level {LEVEL}, format: {FORMAT}

Chủ đề: {mô tả ngắn}
- Đọc mẫu {LEVEL}_*.html trước

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
```

---

## 5. Kiểm tra & sửa lỗi

```
Kiểm tra tất cả bài trong assets/html/tim_thong_tin/:

1. Chars đạt minimum?
2. Nội dung logic, thực tế?
3. Từ vựng đúng level? (≥80%, N4/N5 không kanji N3+)
4. Câu hỏi tình huống? Tên thật? Q1≠Q2?
5. Đáp án đúng paraphrase? Đáp án sai có căn cứ?
6. Che bài → đoán được đáp án? → sửa
7. Furigana đúng? (<ruby>+<rt>, không Ab, không ngoặc)
8. Layout: crop sát? Flow text? Không tách từ? Không che chữ?

Sửa HTML → chụp lại → cập nhật CSV.
```
