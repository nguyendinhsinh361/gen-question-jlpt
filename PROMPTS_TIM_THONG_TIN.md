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

⛔ ĐA DẠNG CHỦ ĐỀ + FORMAT + LAYOUT — BẮT BUỘC:
1. Đọc rules/content.md — chứa bảng slug chủ đề + star rating + thước đo + LAYOUT VARIANTS (R2) + 19 formats (R7).
   (Nguồn gốc: input/rule_doc_hieu.md — dùng để cross-check nếu cần)
2. Scan sheets/ xem chủ đề + format + layout đã dùng trong các bài trước.
3. Lên kế hoạch: liệt kê bảng (level, slug chủ đề, format từ R7, layout variant từ R2) cho từng bài.
   - KHÔNG trùng topic giữa các bài (cùng level VÀ cross-level).
   - KHÔNG trùng format giữa các bài cùng level.
   - KHÔNG trùng layout variant giữa các bài (cùng level VÀ cross-level).
   - Ưu tiên slug ★★★ → ★★ → ★. Chọn slug phù hợp level (tra bảng tổng hợp).
   - Kiểm tra số điều kiện đúng thước đo level (N5:1–2 / N4:3–4 / N3:5–6 / N2:6–8 / N1:7+).
   - Tra bảng "Format × Layout" trong R7 để chọn kết hợp tự nhiên.
4. Xác nhận kế hoạch không trùng cả 3 chiều (topic + format + layout) → mới bắt đầu gen.

⛔ COLOR PALETTE — BẮT BUỘC:
Đọc rules/content.md R8 "Color Palette" — chứa palette chuẩn (base + 5 accent).
- CHỈ dùng hex code trong palette. KHÔNG tự nghĩ màu.
- Tối đa 2 accent / bài. Fill nhạt, text tối. KHÔNG dùng nền đậm + chữ trắng.
- ○=Green, ×=Red, △=Amber (cố định).

⛔ FURIGANA ZERO-TOLERANCE:
Sau khi gen HTML, BẮT BUỘC chạy scripts/check_furigana.py --html {file} --level {LEVEL}.
Exit 1 = có kanji vượt level thiếu furigana → sửa (thêm ruby hoặc viết hiragana) → chạy lại.
KHÔNG được QC nếu check_furigana chưa PASS.

⛔ NGHIÊM CẤM CHO SẴN DỮ KIỆN TRONG CÂU HỎI (Data Leak):
Đọc rules/questions.md "⛔ NGHIÊM CẤM — Cho sẵn dữ kiện trong câu hỏi".
- Câu hỏi chỉ cho TÌNH HUỐNG (ai, khi nào, muốn gì) — KHÔNG cho số liệu/dữ kiện.
- Mọi điều kiện trong câu hỏi PHẢI ảnh hưởng đáp án — không có thông tin thừa.
- Nếu bài có ※ trap, câu hỏi KHÔNG được bypass bằng cách cho sẵn kết quả.
- Test: đọc câu hỏi MỘT MÌNH → nếu đã đủ số để tính = ❌ phải viết lại.

Sau khi gen xong mỗi bài, tự QC checklist (đọc lại HTML + CSV + ảnh, log PASS/FAIL từng mục). Tất cả PASS mới chuyển sang bài tiếp.
Điền Q&A vào CSV bằng scripts/fill_qa.py (KHÔNG sửa CSV bằng tay).
Chụp ảnh bằng scripts/screenshot.py (KHÔNG tự viết code).
Sửa HTML = PHẢI chạy lại screenshot + check_furigana trước khi QC lại.
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
2. Đọc input/kanji_jlpt_sensei.csv để tra level kanji khi quyết định furigana
3. Đọc 1-2 mẫu input/html/ + 1 mẫu input/htm_content_qa/ cho level cần gen
4. Scan sheets/ xem chủ đề + format + layout nào đã dùng → chọn chủ đề + format + layout chưa/ít dùng
   (rules/content.md đã chứa bảng slug + star rating + thước đo + LAYOUT VARIANTS (R2) + 19 formats (R7). input/rule_doc_hieu.md là nguồn gốc — dùng để cross-check)

⛔ ĐA DẠNG CHỦ ĐỀ + FORMAT + LAYOUT — BẮT BUỘC:
- Chọn slug chủ đề từ bảng tổng hợp trong rules/content.md. Chọn slug phù hợp level (★★★ → ★★ → ★).
- Chọn layout variant từ bảng "Layout Variants" trong R2 — mỗi level có 5-6 layout riêng.
- Mỗi bài PHẢI khác topic VÀ khác format VÀ khác layout variant với tất cả bài trước.
- Ưu tiên slug/layout chưa dùng → đảm bảo đa dạng tối đa.
- Lên kế hoạch trước: liệt kê bảng (level, slug, format, layout variant) → xác nhận không trùng → mới gen.
- Kiểm tra số điều kiện đúng thước đo level (N5:1–2 / N4:3–4 / N3:5–6 / N2:6–8 / N1:7+).
- Tra bảng "Format × Layout" trong R7 để chọn kết hợp tự nhiên.

⛔ COLOR PALETTE — BẮT BUỘC:
- Đọc rules/content.md R8 "Color Palette" — chứa palette chuẩn (9 base + 5 accent).
- CHỈ dùng hex code trong palette. KHÔNG tự nghĩ màu.
- Tối đa 2 accent / bài. Fill nhạt pastel, text/stroke tối. KHÔNG dùng nền đậm + chữ trắng.
- ○=Green(#2f855a), ×=Red(#c53030), △=Amber(#92400e) — cố định.
- Cùng loại element trong bài → cùng màu (nhất quán).

⛔ NGHIÊM CẤM CHO SẴN DỮ KIỆN TRONG CÂU HỎI (Data Leak):
- Câu hỏi chỉ cho TÌNH HUỐNG (ai, khi nào, muốn gì) — KHÔNG cho số liệu mà thí sinh cần tra cứu.
- Mọi điều kiện trong câu hỏi PHẢI ảnh hưởng đáp án — không có thông tin thừa/trang trí.
- Nếu bài có ※ trap, câu hỏi KHÔNG được bypass ※ bằng cách cho sẵn kết quả.
- Test: đọc câu hỏi MỘT MÌNH (không nhìn bài) → nếu đã đủ số để tính đáp án = ❌ phải viết lại.
- Test: bỏ từng điều kiện → đáp án không đổi = điều kiện thừa = ❌.
- Test: liệt kê ※ → câu hỏi cho sẵn kết quả của ※ = bẫy bị vô hiệu = ❌.
(Chi tiết + ví dụ: rules/questions.md "⛔ NGHIÊM CẤM — Cho sẵn dữ kiện trong câu hỏi")

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
- Kiểm tra furigana bằng scripts/check_furigana.py (KHÔNG đoán level kanji — phải dùng script)
- Sửa HTML = PHẢI chạy lại screenshot + check_furigana trước khi QC lại
- Gen xong tất cả → gộp CSV thành sheets/all_tim_thong_tin.csv
```
