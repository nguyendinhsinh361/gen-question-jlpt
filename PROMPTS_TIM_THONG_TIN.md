# Prompt — Gen bài Tìm Thông Tin (JLPT 情報検索)

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.

---

```
Đọc jlpt-reading-generator/SKILL.md rồi gen bài tìm thông tin:
- N5: {số} bài
- N4: {số} bài
- N3: {số} bài
- N2: {số} bài
- N1: {số} bài

Lưu CSV vào sheets/. Làm đúng theo SKILL.md — từng bài một, đọc rules/ trước khi gen.
1 FAIL = sửa ngay + QC lại. KHÔNG bỏ qua.
Sửa HTML = chạy lại screenshot + check_furigana trước khi QC lại.
Gen xong tất cả → gộp CSV thành sheets/all_tim_thong_tin.csv.
```
