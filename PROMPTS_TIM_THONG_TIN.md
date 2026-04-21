# Prompt Guide — Gen nội dung Tìm Thông Tin (JLPT 情報検索)

> **BẮT BUỘC đọc SKILL.md** trước khi gen. File này chỉ là prompt template ngắn gọn.

---

## Prompt chính — Gen + QC xuyên suốt

Đây là prompt duy nhất cần dùng. Bao gồm đầy đủ: chuẩn bị → gen → QC → sửa → output.

```
Đọc jlpt-reading-generator/SKILL.md và jlpt-quality-check/SKILL.md trước khi bắt đầu.

Gen {SỐ LƯỢNG} bài tìm thông tin, lưu CSV trong sheets/
- N1: {số} bài
- N2: {số} bài
- N3: {số} bài
- N4: {số} bài
- N5: {số} bài

═══ BƯỚC 1: CHUẨN BỊ ═══
- Đọc 1-2 mẫu từ input/html/ và input/htm_content_qa/ cho level cần gen
- Scan format đã dùng trong sheets/ → chọn format chưa dùng/ít dùng
- Lên kế hoạch: mỗi bài gán format + chủ đề + visual elements (không trùng nhau)

═══ BƯỚC 2: GEN NỘI DUNG (tối đa 5 bài/lượt) ═══
Với mỗi bài, thực hiện tuần tự:

2a. Gen HTML theo SKILL.md:
    - ≥80% từ vựng đúng level. Từ vượt level → level gần nhất. N4/N5 KHÔNG kanji N3+
    - Độ khó từ CẤU TRÚC THÔNG TIN, KHÔNG nhồi thuật ngữ
    - Layout compact: viewport=700, container 700px, margin:0, padding:12px 16px
    - Flow text (không <br> ngắt câu), word-break: keep-all

2b. Gen câu hỏi + đáp án:
    - MỌI câu hỏi là TÌNH HUỐNG: nhân vật tên thật + profile + điều kiện. KHÔNG Aさん/Bさん
    - Q1 và Q2 khác kiểu (8 kiểu: chọn phương án / tư cách / thủ tục / chi phí / đúng-sai / ngoại lệ / so sánh / xử lý vấn đề)
    - Đáp án đúng: paraphrase, KHÔNG copy nguyên văn
    - Đáp án sai: thông tin CÓ trong bài nhưng sai điều kiện. KHÔNG bịa

2c. Furigana verification (BLOCKING — không qua không được tiếp):
    - Scan kanji → check level → thêm furigana thiếu
    - Đếm <ruby> tags: N1≥3, N2≥5, N3≥5. Nếu dưới minimum → sửa ngay
    - Chỉ <ruby>+<rt>. KHÔNG ngoặc (), KHÔNG dạng Ab

2d. Screenshot + CSV:
    - Chụp container.screenshot() (KHÔNG page.screenshot())
    - Ghi CSV: correct_answer = integer ("2" không "2.0")

═══ BƯỚC 3: QUALITY CHECK — PHẦN A: HTML (TC1-TC5) ═══
Với MỖI bài vừa gen, kiểm tra 5 tiêu chí HTML. 1 FAIL = phải sửa.

TC1 — Ký tự:
  count_body_chars() ≥ minimum? (N1:700, N2:700, N3:600, N4:400, N5:250)

TC2 — Chủ đề & Format:
  Chủ đề phù hợp level? (N5 không bảo hiểm, N4 không pháp lý)
  Nội dung logic? (giá hợp lý, thời gian không mâu thuẫn, điều kiện nhất quán)

TC3 — Layout:
  Flow text? (tìm 。<br> → nếu có = FAIL)
  Container: width 700px, margin:0, padding 12px 16px?
  Table: table-layout fixed, width 100%?

TC4 — Từ vựng & Ngữ pháp:
  ≥80% từ đúng level?
  Từ vượt level dùng level gần nhất? (N3→N2, không N3→N1)
  N4/N5 không kanji N3+ (当, 届, 締, 割)?
  Độ khó từ cấu trúc, không từ nhồi thuật ngữ?
  Ngữ pháp phù hợp level? (N5 không dùng ～において)

TC5 — Furigana:
  Ruby count ≥ minimum? (N1≥3, N2≥5, N3≥5)
  Chỉ dùng <ruby>+<rt>? (không ngoặc, không Ab)
  Furigana chỉ cho từ VƯỢT level? (không furigana cho từ đúng level)

═══ BƯỚC 4: QUALITY CHECK — PHẦN B: CÂU HỎI & ĐÁP ÁN (TC6) — KHÔNG ĐƯỢC BỎ QUA ═══
⛔ AI HAY BỎ QUÊN BƯỚC NÀY. Check TC1-TC5 xong CHƯA PHẢI LÀ XONG.
Đọc lại câu hỏi + đáp án từ CSV, kiểm tra từng mục:

TC6a — Tình huống: MỌI câu hỏi (Q1 VÀ Q2) có nhân vật tên thật + profile + điều kiện?
  ❌ "～について正しいものはどれか" = FAIL (thiếu tình huống)
  ❌ "Aさん" = FAIL (tên chung chung)
TC6b — Kiểu hỏi: Q1 và Q2 dùng kiểu khác nhau?
  (chọn phương án / tư cách / thủ tục / chi phí / đúng-sai / ngoại lệ / so sánh / xử lý)
TC6c — Đáp án đúng: paraphrase, không copy nguyên văn từ bài?
TC6d — Đáp án sai: có căn cứ trong bài nhưng sai điều kiện? Không bịa thông tin?
TC6e — Test che bài: che bài đọc, nhìn 4 đáp án → đoán được = FAIL
TC6f — Format: correct_answer = integer ("2" không "2.0")

→ CHECKPOINT: "Tôi đã đọc question_1, question_2, answer_1, answer_2 từ CSV chưa?"
→ Nếu chưa đọc = QC chưa hoàn thành, KHÔNG được kết luận.

═══ BƯỚC 5: SỬA BÀI FAIL ═══
- TC1 (chars thiếu) / TC2 (topic sai) / TC4 (vocab sai): gen lại toàn bộ HTML
- TC3 (layout): sửa HTML (bỏ <br>, fix CSS) → chụp lại screenshot
- TC5 (furigana): thêm/sửa ruby tags → chụp lại screenshot
- TC6 (question): sửa câu hỏi/đáp án → cập nhật CSV
→ Sau khi sửa → chạy lại QC (CẢ PHẦN A + B) bài đó → confirm PASS

═══ BƯỚC 6: LẶP LẠI ═══
Quay lại BƯỚC 2 cho lượt 5 bài tiếp theo. Tiếp tục đến hết số lượng yêu cầu.

Kết thúc: output bảng tổng kết PASS/FAIL toàn batch (bảng PHẢI có cả PHẦN A + PHẦN B).
```
