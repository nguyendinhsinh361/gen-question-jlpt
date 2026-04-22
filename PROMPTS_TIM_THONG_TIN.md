# Prompt Guide — Gen nội dung Tìm Thông Tin (JLPT 情報検索)

> **BẮT BUỘC đọc jlpt-reading-generator/SKILL.md** trước khi gen. File này chỉ là prompt template ngắn gọn.
> Skill đã gộp chung gen + QC thành 1 luồng duy nhất. Không cần đọc file nào khác.

---

## Prompt chính — Gen + QC xuyên suốt (từng bài một)

```
Đọc jlpt-reading-generator/SKILL.md trước khi bắt đầu.

Gen {SỐ LƯỢNG} bài tìm thông tin, lưu CSV trong sheets/
- N1: {số} bài
- N2: {số} bài
- N3: {số} bài
- N4: {số} bài
- N5: {số} bài

Thực hiện theo SKILL.md: gen từng bài một, QC loop cho đến khi PASS tất cả 6 TC, chụp ảnh cuối cùng, rồi mới chuyển sang bài tiếp.
```

---

## Prompt chi tiết (nếu cần kiểm soát chặt hơn)

```
Đọc jlpt-reading-generator/SKILL.md trước khi bắt đầu.

Gen {SỐ LƯỢNG} bài tìm thông tin, lưu CSV trong sheets/
- N1: {số} bài
- N2: {số} bài
- N3: {số} bài
- N4: {số} bài
- N5: {số} bài

═══ CHUẨN BỊ ═══
- Đọc 1-2 mẫu từ input/html/ và input/htm_content_qa/ cho level cần gen
- Đọc input/rule_gen_tim_thong_tin.md (quy tắc giáo viên: 3-tier vocabulary, character counts, distractor types)
- Scan format đã dùng trong sheets/ → chọn format chưa dùng/ít dùng
- Lên kế hoạch: mỗi bài gán format + chủ đề + visual elements (không trùng nhau)

═══ VỚI MỖI BÀI (từng bài một, không batch) ═══

1. Gen HTML + Furigana verification (BLOCKING)
2. Gen câu hỏi + đáp án → ghi CSV
3. QC PHẦN A (TC1-TC5): ký tự, chủ đề, layout, từ vựng, furigana
4. QC PHẦN B (TC6): tình huống, kiểu hỏi, paraphrase, distractor, test che bài
   ⛔ KHÔNG ĐƯỢC BỎ QUA PHẦN B
5. Nếu FAIL → sửa → quay lại bước 3 (QC lại CẢ A + B)
6. PASS → chụp container.screenshot() → bài tiếp theo

Kết thúc: output bảng tổng kết PASS/FAIL toàn batch.
```
