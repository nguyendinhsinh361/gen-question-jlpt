# Prompt — Gen bài Tìm Thông Tin (JLPT 情報検索)

## Cách dùng

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.
SKILL.md chứa workflow, rules/ chứa chi tiết. Prompt chỉ cần nói **cái gì** và **bao nhiêu**.

---

## Prompt ngắn (khuyên dùng)

```
Đọc jlpt-reading-generator/SKILL.md rồi gen bài tìm thông tin:
- N5: {số} bài
- N4: {số} bài
- N3: {số} bài
- N2: {số} bài
- N1: {số} bài

Lưu CSV vào sheets/. Làm đúng theo SKILL.md — từng bài một, đọc rules/ trước khi gen, QC 6 TC, PASS hết rồi mới chụp ảnh (dùng scripts/screenshot.py), kiểm tra ảnh, rồi sang bài tiếp.
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

Làm đúng theo SKILL.md — từng bài một, QC 6 TC (cả PHẦN A lẫn PHẦN B), PASS hết rồi mới chụp ảnh bằng scripts/screenshot.py (KHÔNG tự viết code), kiểm tra ảnh, lặp đến khi đạt.
```
