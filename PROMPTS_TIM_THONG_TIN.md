# Prompt — Gen bài Tìm Thông Tin (JLPT 情報検索)

## Cách dùng

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.
SKILL.md chứa workflow + checklist 38 mục QC. rules/ chứa chi tiết. Prompt chỉ cần nói **cái gì** và **bao nhiêu**.

---

## Prompt ngắn (khuyên dùng)

```
Đọc jlpt-reading-generator/SKILL.md rồi gen bài tìm thông tin:
- N5: {số} bài
- N4: {số} bài
- N3: {số} bài
- N2: {số} bài
- N1: {số} bài

Lưu CSV vào sheets/. Làm đúng theo SKILL.md — từng bài một, đọc rules/ trước khi gen.
Sau khi gen xong mỗi bài, tự QC checklist 38 mục (đọc lại HTML + CSV + ảnh, log PASS/FAIL từng mục). Tất cả 38 mục PASS mới chuyển sang bài tiếp.
Điền Q&A vào CSV bằng scripts/fill_qa.py (KHÔNG sửa CSV bằng tay).
Chụp ảnh bằng scripts/screenshot.py (KHÔNG tự viết code).
Sửa HTML = PHẢI chạy lại screenshot trước khi QC lại.
Gen xong tất cả → gộp CSV thành sheets/all_tim_thong_tin.csv.
```

---

## Prompt có thêm ràng buộc (khi cần kiểm soát)

```
Đọc jlpt-reading-generator/SKILL.md rồi gen bài tìm thông tin:
- N5: {số} bài
- N4: {số} bài
- N3: {số} bài
- N2: {số} bài
- N1: {số} bài

Lưu CSV vào sheets/. Trước khi gen:
1. Đọc rules/content.md + rules/vocabulary.md + rules/technical.md + rules/questions.md
2. Đọc 1-2 mẫu input/html/ + 1 mẫu input/htm_content_qa/ cho level cần gen
3. Scan sheets/ xem format nào đã dùng → chọn format chưa/ít dùng
4. Lên kế hoạch: mỗi bài khác format, khác chủ đề

Yêu cầu chất lượng câu hỏi (áp dụng tất cả level):
- Tình huống: nhân vật tên thật + profile + ≥3 điều kiện ràng buộc đồng thời
- Cross-reference: đáp án phải scan ≥3 vị trí trong bài mới tìm được
- Paraphrase: đáp án đúng KHÔNG copy nguyên văn, phải diễn đạt lại
- Distractor: đủ 4 loại bẫy (condition miss, calculation trap, detail swap, partial match), mỗi đáp án sai phải dùng info thật từ bài, phải quay lại bài mới loại được
- Explanation: giải thích đủ 3 phần (đáp án đúng + từng đáp án sai + tóm tắt)

Sau khi gen xong mỗi bài, BẮT BUỘC tự QC theo checklist 38 mục trong SKILL.md:
- Đọc lại HTML → check Phần A (HTML) + Phần B (Nội dung & Từ vựng)
- Đọc lại CSV → check Phần C (Câu hỏi & Đáp án) — đặc biệt check paraphrase + 4 loại bẫy + distractor khó loại
- Mở ảnh PNG → check Phần D (Ảnh)
- Log PASS/FAIL từng mục. 1 FAIL = sửa → QC lại. Tất cả 33/33 PASS mới sang bài tiếp.

Lưu ý kỹ thuật:
- Điền Q&A vào CSV bằng scripts/fill_qa.py (KHÔNG sửa CSV bằng tay — commas sẽ vỡ cột)
- Chụp ảnh bằng scripts/screenshot.py (KHÔNG tự viết code)
- Sửa HTML = PHẢI chạy lại screenshot trước khi QC lại
- Gen xong tất cả → gộp CSV thành sheets/all_tim_thong_tin.csv
```
