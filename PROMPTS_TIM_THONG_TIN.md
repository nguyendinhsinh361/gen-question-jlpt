# Prompt — Gen bài Tìm Thông Tin (JLPT 情報検索)

## Cách dùng

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.
SKILL.md chứa workflow + checklist 32 mục QC. rules/ chứa chi tiết. Prompt chỉ cần nói **cái gì** và **bao nhiêu**.

---

## Prompt ngắn (khuyên dùng)

```
Đọc jlpt-reading-generator/SKILL.md rồi gen bài tìm thông tin:
- N5: {số} bài
- N4: {số} bài
- N3: {số} bài
- N2: {số} bài
- N1: {số} bài

Lưu CSV vào sheets/. Làm đúng theo SKILL.md — từng bài một, đọc rules/ trước khi gen. Sau khi gen xong mỗi bài, tự QC checklist 32 mục (đọc lại HTML + CSV + ảnh, log PASS/FAIL từng mục). Tất cả 32 mục PASS mới chuyển sang bài tiếp. Chụp ảnh bằng scripts/screenshot.py (KHÔNG tự viết code).
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
1. Đọc rules/content.md + rules/vocabulary.md + rules/technical.md
2. Đọc 1-2 mẫu input/html/ + 1 mẫu input/htm_content_qa/ cho level cần gen
3. Scan sheets/ xem format nào đã dùng → chọn format chưa/ít dùng
4. Lên kế hoạch: mỗi bài khác format, khác chủ đề

Sau khi gen xong mỗi bài, BẮT BUỘC tự QC theo checklist 32 mục trong SKILL.md:
- Đọc lại HTML → check Phần A (HTML) + Phần B (Nội dung & Từ vựng)
- Đọc lại CSV → check Phần C (Câu hỏi & Đáp án)
- Mở ảnh PNG → check Phần D (Ảnh)
- Log PASS/FAIL từng mục. 1 FAIL = sửa → QC lại. Tất cả 32/32 PASS mới sang bài tiếp.
Chụp ảnh bằng scripts/screenshot.py (KHÔNG tự viết code).
```
