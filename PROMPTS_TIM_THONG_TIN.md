# Prompt — Gen bài Tìm Thông Tin (JLPT 情報検索)

## Cách dùng

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.
SKILL.md chứa workflow + checklist 39 mục QC. rules/ chứa chi tiết (bảng slug chủ đề, thước đo độ phức tạp, 4 loại bẫy...). Prompt chỉ cần nói **cái gì** và **bao nhiêu**.

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

⛔ ĐA DẠNG CHỦ ĐỀ — BẮT BUỘC:
1. Đọc rules/content.md — chứa bảng slug chủ đề + star rating theo level + thước đo độ phức tạp.
   (Nguồn gốc: input/rule_doc_hieu.md — dùng để cross-check nếu cần)
2. Scan sheets/ xem chủ đề + format đã dùng trong các bài trước.
3. Lên kế hoạch: liệt kê bảng (level, slug chủ đề, format từ R7) cho từng bài.
   - KHÔNG trùng topic giữa các bài (cùng level VÀ cross-level).
   - KHÔNG trùng format giữa các bài cùng level.
   - Ưu tiên slug ★★★ → ★★ → ★. Chọn slug phù hợp level (tra bảng tổng hợp).
   - Kiểm tra số điều kiện đúng thước đo level (N5:1–2 / N4:3–4 / N3:5–6 / N2:6–8 / N1:7+).
4. Xác nhận kế hoạch không trùng → mới bắt đầu gen.

Sau khi gen xong mỗi bài, tự QC checklist 39 mục (đọc lại HTML + CSV + ảnh, log PASS/FAIL từng mục). Tất cả 39 mục PASS mới chuyển sang bài tiếp.
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
2. Đọc input/jlpt_kanji.csv để tra level kanji khi quyết định furigana
3. Đọc 1-2 mẫu input/html/ + 1 mẫu input/htm_content_qa/ cho level cần gen
4. Scan sheets/ xem chủ đề + format nào đã dùng → chọn chủ đề + format chưa/ít dùng
   (rules/content.md đã chứa bảng slug + star rating + thước đo. input/rule_doc_hieu.md là nguồn gốc — dùng để cross-check)

⛔ ĐA DẠNG CHỦ ĐỀ — BẮT BUỘC:
- Chọn slug chủ đề từ bảng tổng hợp trong rules/content.md. Chọn slug phù hợp level (★★★ → ★★ → ★).
- Mỗi bài PHẢI khác topic VÀ khác format với tất cả bài trước.
- Ưu tiên slug chưa dùng → đảm bảo đa dạng tối đa.
- Lên kế hoạch trước: liệt kê bảng (level, slug, format) → xác nhận không trùng → mới gen.
- Kiểm tra số điều kiện đúng thước đo level (N5:1–2 / N4:3–4 / N3:5–6 / N2:6–8 / N1:7+).

Yêu cầu chất lượng câu hỏi (áp dụng tất cả level):
- Tình huống: nhân vật tên thật + profile + ≥3 điều kiện ràng buộc đồng thời
- Cross-reference: đáp án phải scan ≥3 vị trí trong bài mới tìm được
- Paraphrase: đáp án đúng KHÔNG copy nguyên văn, phải diễn đạt lại
- Distractor: đủ 4 loại bẫy (condition miss, calculation trap, detail swap, partial match), mỗi đáp án sai phải dùng info thật từ bài, phải quay lại bài mới loại được
- Red flag: kiểm tra "đúng vì lý do sai" — nếu thí sinh dùng logic sai vẫn chọn được đáp án đúng → thiết kế lại
- KHÔNG dùng phủ định kép gây khó hiểu không cần thiết
- Thì động từ: câu hỏi + 4 lựa chọn PHẢI nhất quán thì
- Explanation: giải thích đủ 3 phần (đáp án đúng + từng đáp án sai + tóm tắt)

Sau khi gen xong mỗi bài, BẮT BUỘC tự QC theo checklist 39 mục trong SKILL.md:
- Đọc lại HTML → check Phần A (HTML) + Phần B (Nội dung & Từ vựng)
- Đọc lại CSV → check Phần C (Câu hỏi & Đáp án) + Phần C2 (Verify đáp án)
- Mở ảnh PNG → check Phần D (Ảnh)
- Log PASS/FAIL từng mục. 1 FAIL = sửa → QC lại. Tất cả 39/39 PASS mới sang bài tiếp.

Lưu ý kỹ thuật:
- Điền Q&A vào CSV bằng scripts/fill_qa.py (KHÔNG sửa CSV bằng tay — commas sẽ vỡ cột)
- Chụp ảnh bằng scripts/screenshot.py (KHÔNG tự viết code)
- Sửa HTML = PHẢI chạy lại screenshot trước khi QC lại
- Gen xong tất cả → gộp CSV thành sheets/all_tim_thong_tin.csv
```
