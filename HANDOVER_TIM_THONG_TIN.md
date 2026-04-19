# Handover: Gen câu hỏi dạng Tìm Thông Tin (JLPT 情報検索)

## Mục đích dự án

Tạo dữ liệu training cho AI fine-tuning: bài đọc hiểu dạng **tìm thông tin** (information retrieval) của JLPT từ N1 đến N5. Mỗi bài gồm:

- File HTML đẹp (styled với Tailwind CSS + Noto Sans JP) — mô phỏng tài liệu thực tế
- Ảnh chụp màn hình (PNG) từ file HTML
- Clean HTML (bỏ hết attribute, class) để lưu trong CSV
- Dòng CSV theo schema 45 cột (có `question_label`)

---

## Cấu trúc thư mục

```
gen-questions-label-ver-2/
├── input/
│   ├── html/                      ← 61 mẫu tham khảo bài đọc (N1×14, N2×12, N3×15, N4×10, N5×10)
│   ├── htm_content_qa/            ← 20 mẫu câu hỏi + đáp án (4 per level)
│   ├── question_sheet.csv         ← Schema CSV gốc (45 cột)
│   ├── question_format.json       ← Số câu hỏi per level/kind
│   ├── mission.json               ← 9 loại nhãn câu hỏi
│   ├── kind_mission_mapping.json  ← Độ dài ký tự theo level
│   └── topic.json                 ← 287 chủ đề có thể dùng
├── assets/
│   ├── html/tim_thong_tin/        ← HTML output
│   └── img/tim_thong_tin/         ← Screenshot PNG tương ứng
├── sheets/                        ← CSV output
├── .claude/skills/jlpt-reading-generator/
│   ├── SKILL.md                   ← Skill chính (PHẢI đọc trước khi gen)
│   ├── scripts/
│   │   └── process_html.py
│   └── references/
│       ├── design-patterns.md     ← Phân tích 61 mẫu HTML + format labels
│       └── question-patterns.md   ← Phân tích 20 mẫu câu hỏi
├── tim_thong_tin_backup.json      ← Backup dữ liệu gốc (ảnh + HTML thô)
├── HANDOVER_TIM_THONG_TIN.md     ← File này
└── PROMPTS_TIM_THONG_TIN.md      ← Các prompt mẫu để gen nội dung
```

---

## Luồng gen nội dung (Generation Workflow)

### Bước 1 — Chuẩn bị

1. **Đọc SKILL.md** — `.claude/skills/jlpt-reading-generator/SKILL.md` chứa toàn bộ quy tắc chi tiết
2. **Kiểm tra file đã có** — `ls assets/html/tim_thong_tin/` để xác định ID tiếp theo cho mỗi level
3. **Đọc 1–2 mẫu tham khảo** — `input/html/` cho level cần gen
4. **Đọc 1 mẫu QA** — `input/htm_content_qa/` cho level cần gen (để biết cách viết câu hỏi)

### Bước 2 — Chọn Format (BẮT BUỘC đa dạng)

Mỗi bài phải được gán 1 format label từ **Format Catalog (15 formats)**. Quy tắc quan trọng nhất:

> **Trong cùng 1 batch gen, KHÔNG được lặp format.** Mỗi bài phải dùng format khác nhau. Chỉ được lặp khi batch > 15 bài.

#### Format Catalog (15 loại)

| Format Label | Mô tả | Ví dụ |
|---|---|---|
| `price_comparison_table` | So sánh giá, bảng cạnh nhau | Thẻ tín dụng, khách sạn, dịch vụ chuyển nhà |
| `event_announcement` | Sự kiện: ngày/giờ/nơi/phí + điều kiện | Job fair, dọn bãi biển, cuộc thi |
| `facility_guide` | Hướng dẫn sử dụng cơ sở | Thư viện, hồ bơi, sở thú, vườn cộng đồng |
| `class_enrollment` | Khóa học: lịch, phí, sĩ số, cách đăng ký | Guitar, nấu ăn, IT, tiếng Nhật, trượt tuyết |
| `service_guide` | Dịch vụ: quy trình, điều kiện, bảng giá | Mua lại, giặt, thuê kimono, tư vấn |
| `schedule_timetable` | Lịch/bảng thời gian, ○/× | Tàu, CLB thể thao, sự kiện việc làm |
| `recruitment_notice` | Tuyển dụng/tình nguyện + điều kiện | Tình nguyện viên, giám sát viên |
| `store_flyer` | Tờ rơi giảm giá, sản phẩm + giá | Siêu thị, tiệm bánh, ưu đãi tuần |
| `menu_guide` | Thực đơn nhà hàng/cafeteria | Curry, ăn trưa, buffet, căng-tin |
| `travel_listing` | Tour du lịch: điểm đến, ngày, giá | Tour mùa hè, bus 1 ngày, tour trượt tuyết |
| `medicine_info` | Thuốc: tên, liều, thời gian, lưu ý | Phiếu hướng dẫn từ phòng khám |
| `regulation_notice` | Quy định/thay đổi quy tắc | Phân loại rác, rửa tay, tái chế |
| `comparison_article` | Bài so sánh dạng văn xuôi A/B/C/D | So sánh nhà ở, dịch vụ |
| `member_notification` | Thông báo cho hội viên/thẻ viên | Thẻ tín dụng, đổi vé, gia hạn |
| `access_guide` | Hướng dẫn đường đi, phương tiện | Bản đồ campus, sơ đồ tuyến |

#### Format phù hợp theo level

| Level | Formats phù hợp |
|-------|-----------------|
| **N5** | `store_flyer`, `event_announcement`, `regulation_notice`, `schedule_timetable`, `travel_listing`, `access_guide` |
| **N4** | `event_announcement`, `class_enrollment`, `regulation_notice`, `menu_guide`, `price_comparison_table`, `service_guide` |
| **N3** | `class_enrollment`, `service_guide`, `event_announcement`, `facility_guide`, `travel_listing`, `price_comparison_table`, `recruitment_notice`, `menu_guide` |
| **N2** | `facility_guide`, `service_guide`, `comparison_article`, `event_announcement`, `class_enrollment`, `schedule_timetable`, `menu_guide` |
| **N1** | `price_comparison_table`, `service_guide`, `facility_guide`, `schedule_timetable`, `medicine_info`, `recruitment_notice`, `member_notification`, `event_announcement` |

### Bước 3 — Gen HTML

- Theo đúng format đã chọn, sử dụng visual elements phù hợp (bảng, pill label, 【】, ◆, ※…)
- Viết nội dung tiếng Nhật đúng level (xem chi tiết trong SKILL.md)
- Áp dụng đúng quy tắc furigana (xem phần bên dưới)

### Bước 4 — Kiểm tra ký tự

Dùng script hoặc hàm Python để đếm chính xác:

```bash
python3 .claude/skills/jlpt-reading-generator/scripts/process_html.py --count-only --file <html-file>
```

| Level | Khoảng ký tự |
|-------|-------------|
| N1 | 500–800 |
| N2 | 480–770 |
| N3 | 340–750 |
| N4 | 300–500 |
| N5 | 130–290 |

### Bước 5 — Screenshot + Clean HTML + CSV

1. Lưu HTML → `assets/html/tim_thong_tin/{LEVEL}_{uuid}.html` (ví dụ: `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5.html`)
2. Chụp screenshot (Playwright, viewport 1000×800, full_page, 1500ms chờ font) → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
3. Trích clean HTML (bỏ attribute, class, gom whitespace) → cột `text_read` trong CSV
4. Gen câu hỏi + đáp án + giải thích → điền vào CSV
5. Cột `general_image` trong CSV = local path `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
6. Lưu CSV vào `sheets/`

---

## Quy tắc Furigana (QUAN TRỌNG — khớp thực tế đề thi JLPT)

### Nguyên tắc cốt lõi

Furigana (`<ruby>/<rt>`) **CHỈ** dùng cho từ **vượt level** của bài. Từ nằm trong level hoặc dưới level → **KHÔNG furigana**.

Một bài viết tốt nên có **rất ít** từ vượt level. Nếu thấy cần thêm nhiều furigana → **viết lại bằng từ đơn giản hơn**.

| Level | Số từ vượt level | Ruby tags |
|-------|-------------------|-----------|
| N5 | 0–2 | 0–5 |
| N4 | 0–3 | 0–8 |
| N3 | 0–5 | 0–12 |
| N2 | 0–3 | 0–8 |
| N1 | 0–2 | 0–5 |

### Quy tắc từ ghép kanji — Cấm dạng "Ab"

Khi từ có kanji vượt level, **LUÔN viết nguyên bộ kanji** rồi đặt furigana. **TUYỆT ĐỐI KHÔNG** tách nửa kanji nửa hiragana (dạng "Ab"). Thực tế đề thi JLPT không bao giờ viết dạng này.

Chỉ chọn 1 trong 2 cách:

| Cách | Khi nào dùng | Ví dụ |
|------|-------------|-------|
| **Full kanji + furigana** | Khi muốn người học thấy kanji | `<ruby>週間<rt>しゅうかん</rt></ruby>` |
| **Full hiragana** | Ở level thấp (N5, N4) | `しゅうかん` |

**Ví dụ sai — KHÔNG BAO GIỜ viết thế này:**

| Sai ❌ | Đúng ✅ | Lý do |
|--------|---------|-------|
| `週かん` | `<ruby>週間<rt>しゅうかん</rt></ruby>` hoặc `しゅうかん` | Dạng Ab — không tồn tại trong thực tế |
| `友だち` (ở N5) | `ともだち` | N5 chưa học kanji này → viết full hiragana |
| `拠てん` | `<ruby>拠点<rt>きょてん</rt></ruby>` | Dạng Ab — không tự nhiên |

**Ngoại lệ duy nhất — Okurigana:** Từ có phần đuôi hiragana chuẩn (okurigana) thì furigana chỉ phủ phần kanji, okurigana đứng riêng. Đây là chính tả chuẩn, KHÔNG phải dạng "Ab":

- ✅ `<ruby>届<rt>とど</rt></ruby>く` — đúng (kanji gốc + okurigana)
- ❌ `<ruby>届く<rt>とどく</rt></ruby>` — sai (furigana không phủ okurigana)

### Bảng quyết định theo level

| Level | Từ đúng level | Từ chỉ biết hiragana | Từ vượt level |
|-------|--------------|---------------------|---------------|
| N5 | Kanji N5 viết trần (日, 月, 人…) | Full hiragana: `ともだち`, `きょう` | Full hiragana (ưu tiên) hoặc full kanji + furi |
| N4 | Kanji N5+N4 viết trần | Hiragana: từ chưa học kanji | Full kanji + furi hoặc full hiragana |
| N3 | Kanji N5+N4+N3 viết trần | Kana nếu từ thường viết kana: `きれい` | Full kanji + furi |
| N2 | Kanji N5–N2 viết trần | — | Full kanji + furi |
| N1 | Gần như tất cả kanji viết trần | — | Chỉ từ cực hiếm mới cần furi |

---

## Schema CSV (45 cột)

```
_id, level, tag, jp_char_count, kind, general_audio, general_image,
text_read, text_read_vn, text_read_en,
question_label_1, question_1, question_image_1, answer_1, correct_answer_1, explain_vn_1, explain_en_1,
question_label_2, question_2, question_image_2, answer_2, correct_answer_2, explain_vn_2, explain_en_2,
question_label_3, question_3, question_image_3, answer_3, correct_answer_3, explain_vn_3, explain_en_3,
question_label_4, question_4, question_image_4, answer_4, correct_answer_4, explain_vn_4, explain_en_4,
question_label_5, question_5, question_image_5, answer_5, correct_answer_5, explain_vn_5, explain_en_5
```

### Các trường chính

| Cột | Giá trị |
|-----|---------|
| `_id` | `{LEVEL}_{uuid}` — ví dụ `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5`. Dùng `uuid.uuid4().hex` (full 32-char) |
| `kind` | Luôn `tìm thông tin` |
| `tag` | Format label từ Format Catalog (ví dụ: `store_flyer`, `facility_guide`) |
| `general_image` | `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png` — cùng ID với `_id` |
| `text_read` | Clean HTML (không attribute, không class, gom whitespace) |
| `question_label_{i}` | Luôn `question_information_search` |
| `answer_{i}` | 4 đáp án ngăn cách bởi `\n`: `1. ĐA1\n2. ĐA2\n3. ĐA3\n4. ĐA4` |
| `correct_answer_{i}` | Số 1–4 |
| `explain_vn_{i}` | Giải thích tiếng Việt |
| `explain_en_{i}` | Giải thích tiếng Anh |

### Số câu hỏi theo level

| Level | Số câu hỏi/bài |
|-------|----------------|
| N1–N4 | 2 (`question_1` + `question_2`) |
| N5 | 1 (`question_1` only) |

---

## Prompts sử dụng

### Prompt 1 — Gen batch theo level (phổ biến nhất)

```
Giúp tôi tạo dữ liệu level N3 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- Mỗi bài dùng format khác nhau từ Format Catalog
- Kiểm tra số ký tự nằm đúng khoảng cho phép
- Furigana chỉ cho từ vượt level, không dùng dạng Ab
- Lưu HTML, screenshot, và CSV đầy đủ
```

### Prompt 2 — Gen batch lớn đa level

```
Gen 15 bài tìm thông tin (3 bài mỗi level N1-N5).

Yêu cầu:
- Mỗi level chọn 3 format khác nhau từ Format Catalog
- Không trùng format trong cùng level
- Đọc mẫu tham khảo trước khi gen
- Kiểm tra chars, furigana, format diversity
- Lưu tất cả vào assets/ và CSV trong sheets/
```

### Prompt 3 — Gen bài đơn lẻ theo format cụ thể

```
Gen 1 bài tìm thông tin N2, format: comparison_article, chủ đề so sánh phòng gym.

- Đọc mẫu n2_1.html hoặc n2_10.html để tham khảo style
- Kiểm tra chars trong khoảng 480-770
- Furigana chỉ cho từ N1 (rất ít)
```

### Prompt 4 — Chỉ gen câu hỏi cho bài đã có

```
Cho các bài tìm thông tin đã có trong sheets/n3_samples.csv, gen câu hỏi cho mỗi bài.

Mỗi bài N3 cần 2 câu hỏi:
- Câu hỏi tìm thông tin cụ thể (ngày, giờ, điều kiện, giá…)
- 4 đáp án (1 đúng, 3 sai nhưng hợp lý)
- Giải thích VN + EN
- Furigana trong câu hỏi: cùng quy tắc với bài đọc
```

### Prompt 5 — Kiểm tra và sửa bài đã gen

```
Kiểm tra tất cả bài tìm thông tin trong assets/html/tim_thong_tin/:
1. Đếm ký tự, báo bài nào ngoài khoảng
2. Kiểm tra furigana: có dạng "Ab" nào không? Có furigana cho từ đúng level không?
3. Kiểm tra format diversity: có bài nào trùng format trong cùng batch không?
4. Screenshot có khớp HTML không?

Nếu lỗi, sửa lại.
```

---

## Cài đặt môi trường

```bash
# Playwright (cho screenshot)
pip install playwright --break-system-packages
python3 -m playwright install chromium

# Verify script hoạt động
python3 .claude/skills/jlpt-reading-generator/scripts/process_html.py --count-only --html-dir assets/html/tim_thong_tin
```

---

## Checklist trước khi nộp batch

- [ ] Mỗi bài có format label khác nhau trong batch
- [ ] Số ký tự nằm đúng khoảng cho phép (±10%)
- [ ] Furigana CHỈ ở từ vượt level, KHÔNG có dạng "Ab"
- [ ] Số ruby tags phù hợp (N5: 0–5, N4: 0–8, N3: 0–12, N2: 0–8, N1: 0–5)
- [ ] CSV đủ 45 cột, answer dùng `\n` ngăn cách (không dùng `|`)
- [ ] `question_label_{i}` = `question_information_search`
- [ ] N1–N4: 2 câu hỏi/bài, N5: 1 câu hỏi/bài
- [ ] HTML, PNG, CSV paths nhất quán
- [ ] Cột `general_image` chứa đúng local path `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`
- [ ] Chủ đề không trùng với bài đã có

---

## Lưu ý cho developer mới

1. **LUÔN đọc SKILL.md trước** — `.claude/skills/jlpt-reading-generator/SKILL.md` là nguồn chân lý, file này chỉ là tóm tắt
2. **Đếm ký tự bằng script**, không ước lượng
3. **Format đa dạng là BẮT BUỘC** — đây là yêu cầu cứng, không phải khuyến khích
4. **Furigana = chỉ từ vượt level** — nếu thấy nhiều furigana → viết lại đơn giản hơn
5. **Không viết dạng "Ab"** — `週かん`, `友だち`, `拠てん` đều SAI
6. **File naming & _id**: `{LEVEL}_{uuid}` — ví dụ `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5`. UUID 32 ký tự hex (full), không cần check số thứ tự
7. **Answer format**: `1. A\n2. B\n3. C\n4. D` (dùng `\n`, KHÔNG dùng `|`)
8. **Đọc `references/design-patterns.md`** để biết format label của từng mẫu tham khảo
