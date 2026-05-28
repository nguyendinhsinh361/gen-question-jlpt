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

---

## Prompt QC hậu kỳ

Chạy QC trên CSV đã gen — auto-check scripts + LLM review + auto-fix tối đa 3 vòng.

```
Đọc .claude/skills/jlpt-reading-generator-post-qc/SKILL.md và chạy QC đầy đủ theo workflow.

CSV cần QC: sheets/all_tim_thong_tin.csv (hoặc per-level sheets/{LEVEL}.csv)

Phạm vi (chọn 1):
- ALL: toàn bộ CSV
- LEVEL: chỉ rows có level = {N1|N2|N3|N4|N5}
- ID: chỉ row có _id = {LEVEL}_{uuid}

Quy trình BẮT BUỘC:
1. BƯỚC 1 — Auto-check: chạy post_qc.py + check_furigana + check_spacing + check_csv_fields + check_answer_punctuation + check_screenshot + check_info_symbols
2. BƯỚC 2 — LLM review: L1-L16 (đặc thù 情報検索: L10 condition count đúng level (N5:1-2 → N1:7+), L11 4 bẫy chuẩn (※ điều kiện/tính toán/nhiễu/đọc nhầm), L12 cross-reading ≥2 vị trí + ký hiệu ○×△※)
3. BƯỚC 3 — Cross-batch: B1-B4 (B4 format diversity 19 types)
4. BƯỚC 4 — Auto-fix: row FAIL → sửa tối thiểu phần lỗi (KHÔNG gen lại toàn bộ), lặp tối đa 3 vòng. Đặc biệt: số điều kiện phải khớp level, format và topic phải tương thích.

Báo cáo theo format trong SKILL.md.
```

---

## Prompt với topic + format chỉ định

Chỉ định topic + format cho từng level. Có 19 format types — chỉ định cả topic (chủ đề thực tế) và format (loại tài liệu).

```
Đọc jlpt-reading-generator/SKILL.md rồi gen bài tìm thông tin với số bài + topic + format chỉ định cho từng level:
- N5: 3 bài | topic: food | format: menu
- N4: 2 bài | topic: school | format: class-list
- N3: 3 bài | topic: travel | format: schedule
- N2: 2 bài | topic: shopping | format: sale
- N1: 2 bài | topic: facility | format: facility-info

Quy tắc topic:
- Topic PHẢI có trong cột `en` của `rules/topic.json` — kiểm tra trước, không có → DỪNG báo user.
- CSV field `tag` của mỗi row = topic của level đó.

Quy tắc format:
- Format PHẢI thuộc 19 format types trong `rules/content.md` R7.
- Format không hợp lệ → DỪNG báo user.
- Trùng format trong cùng level → mỗi bài scenario/setup khác.

Quy tắc kết hợp topic + format:
- Topic và format PHẢI tương thích (vd: `food` + `menu` ✓; `school` + `class-list` ✓; `food` + `class-list` ✗).
- Không tương thích → DỪNG, báo user gợi ý kết hợp phù hợp.

Quy tắc số điều kiện theo level:
- N5: 1-2 điều kiện | N4: 3-4 (※ ẩn) | N3: 5-6 (deadline kép) | N2: 6-8 (flowchart) | N1: 7+ (đồng thời/loại trừ)

Lưu CSV vào sheets/. Lưu HTML: assets/html/tim_thong_tin/{LEVEL}_{uuid}.html.
1 FAIL = sửa ngay + QC lại. KHÔNG bỏ qua.
Sửa HTML = chạy lại screenshot + check_furigana trước khi QC lại.
Gen xong tất cả → gộp CSV thành sheets/all_tim_thong_tin.csv.
```
