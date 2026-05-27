# jlpt-info-search-post-qc

## Mô tả
QC hậu kỳ cho CSV output của dạng tìm thông tin (情報検索). N1-N5. Dùng khi muốn kiểm tra lại chất lượng sau khi gen xong.

**Module này ĐẶC BIỆT:**
- Có SCREENSHOT — cột `general_image` phải có giá trị (đường dẫn ảnh)
- HTML là layout phức tạp (tables, cards, flowcharts) — KHÔNG phải prose đơn giản
- Câu hỏi về tìm thông tin cụ thể từ tài liệu có cấu trúc (poster, brochure, lịch trình, thông báo)
- `question_label` thường là `question_information_search`
- Có 19 format types (xem `rules/content.md` R7) — cần kiểm tra đa dạng format trong batch

## Trigger
- "QC lại tìm thông tin"
- "kiểm tra CSV tìm thông tin"
- "post-QC info search"
- "post-QC 情報検索"

---

## QUY TRÌNH POST-QC

### BƯỚC 1: AUTO-CHECK (chạy script)

Chạy post_qc.py chính:
```bash
python3 .gemini/skills/jlpt-reading-generator-post-qc/scripts/post_qc.py \
  --csv sheets/samples_v1.csv \
  --rules-dir rules/ \
  --verbose
```

Chạy thêm các script kiểm tra bổ sung từ generator skill:
```bash
python3 .gemini/skills/jlpt-reading-generator/scripts/check_furigana.py --html-dir assets/html/tim_thong_tin --level-from-filename --csv rules/kanji_jlpt_sensei.csv
python3 .gemini/skills/jlpt-reading-generator/scripts/check_spacing.py --html-dir assets/html/tim_thong_tin --level-from-filename
python3 .gemini/skills/jlpt-reading-generator/scripts/check_csv_fields.py --csv sheets/samples_v1.csv --kind info
python3 .gemini/skills/jlpt-reading-generator/scripts/check_answer_punctuation.py --csv sheets/samples_v1.csv
```

Thu thập tất cả kết quả từ các script trên. Nếu có lỗi HARD REJECT, dừng lại và báo cáo ngay.

**Lưu ý đường dẫn:**
- HTML files: `assets/html/tim_thong_tin/`
- Image files: `assets/img/tim_thong_tin/`

---

### BƯỚC 2: LLM REVIEW (agent đọc từng row)

Với mỗi row trong CSV, agent đọc `text_read` + `question` + `answer` và kiểm tra các tiêu chí sau:

#### L1: Thể chia nhất quán (文体の統一)
- N1-N3: dùng 普通形 (だ/である). Cả bài + câu hỏi + 4 đáp án phải cùng thể.
- N4-N5: dùng ます形.
- **ĐẶC BIỆT**: không trộn です/ます trong Q/A của N1-N3.

#### L2: Paraphrase quality
- Đáp án đúng KHÔNG copy nguyên từ bài đọc.
- **Tìm thông tin đặc thù**: câu hỏi thường dùng điều kiện cụ thể (ngày, giờ, số người, giá...) — kiểm tra điều kiện trong câu hỏi/đáp án có THỰC SỰ xuất hiện trong tài liệu gốc hay không.
- N3 trở lên: cụm ≥4 từ liên tiếp giống bài gốc = **FAIL**.
- N4-N5: cụm ≥6 từ liên tiếp giống bài gốc = **FAIL**.

#### L3: Distractor validity
- 3 đáp án sai phải dùng thông tin THẬT từ tài liệu nhưng cho SAI điều kiện/kịch bản.
- **REJECT** nếu đáp án sai bịa thông tin không có trong tài liệu.
- **REJECT** nếu đáp án sai hiển nhiên (ai đọc cũng biết sai ngay).
- Ví dụ tốt: đáp án sai dùng giá đúng nhưng cho ngày sai, hoặc dịch vụ đúng nhưng điều kiện sai.

#### L4: Key term level
- Từ then chốt (cần để trả lời câu hỏi) phải ≤ level mục tiêu.
- Từ vượt level chỉ được phép xuất hiện ở phần bối cảnh + phải có furigana.

#### L5: Marker-question consistency
- Tìm thông tin thường **KHÔNG có markers** (①②) trong bài — focus vào việc điều kiện trong câu hỏi khớp với thông tin trong tài liệu.
- Nếu có markers (hiếm), kiểm tra tính nhất quán.
- Quan trọng hơn: kiểm tra điều kiện (conditions) trong câu hỏi mapping đúng với dữ liệu trong bảng/danh sách.

#### L6: Correct answer verification
- Xác nhận đáp án đúng bằng cách **truy vết từng điều kiện** trong tài liệu:
  1. Đọc câu hỏi → xác định điều kiện (ví dụ: 土曜日, 3人, 午前中)
  2. Tra trong bảng/danh sách → tìm entry khớp TẤT CẢ điều kiện
  3. Đối chiếu entry đó với đáp án đúng
- Xác nhận 3 đáp án sai **THỰC SỰ** sai (không thể chọn được khi áp dụng đúng điều kiện).

#### L7: Topic-level appropriateness
- Chủ đề phải **thực tế** (practical), là tài liệu có cấu trúc:
  - N5: flyer cửa hàng, thông báo sự kiện đơn giản, lịch trình cơ bản
  - N4: hướng dẫn lớp học, menu, bảng giá, quy định
  - N3: hướng dẫn dịch vụ, tuyển dụng, so sánh sản phẩm
  - N2: hướng dẫn cơ sở, lịch tư vấn, xử lý sự cố
  - N1: so sánh giá phức tạp, thông tin thuốc, thông báo hội viên
- **REJECT** nếu text_read là bài luận/prose essay — tìm thông tin BẮT BUỘC phải là tài liệu có cấu trúc.

#### L8: Explanation quality
- `explain_vn` và `explain_en` có đầy đủ.
- **BẮT BUỘC truy vết từng bước** qua điều kiện:
  - Bước 1: nêu điều kiện từ câu hỏi
  - Bước 2: tra bảng/danh sách theo từng điều kiện
  - Bước 3: kết luận đáp án đúng + giải thích tại sao các đáp án sai không khớp

#### EXTRA CHECK 1: Screenshot required
- Cột `general_image` **KHÔNG ĐƯỢC rỗng** — screenshot bắt buộc cho tìm thông tin.
- Kiểm tra file ảnh tồn tại trong `assets/img/tim_thong_tin/`.

#### EXTRA CHECK 2: HTML structured layout
- Mở HTML file trong `assets/html/tim_thong_tin/` và kiểm tra:
  - Phải có layout có cấu trúc: `<table>`, `<div>` với class, `<ul>`/`<ol>`, cards, grid...
  - **REJECT** nếu HTML chỉ toàn `<p>` prose text — tìm thông tin PHẢI có bảng biểu/danh sách.

#### L9: Trap-type classification — 5 bẫy chuẩn

Với MỖI distractor (3 đáp án sai), agent PHẢI phân loại vào 1 trong 5 loại bẫy chuẩn:

| Bẫy | Mô tả | Dấu hiệu |
|-----|-------|----------|
| **Reversal** ❌ | Đảo ngược ý nghĩa/kết luận từ bài | Bài: "Aによって元気になった" → Bẫy: "Aの後で体が重くなった" |
| **Detail Swap** 🔄 | Gán thông tin đúng vào ngữ cảnh sai (đối tượng/thời điểm/địa điểm khác) | Bài: "Aは嵐山, Bは金閣寺" → Bẫy: "Aは金閣寺" |
| **Fabrication** 🎭 | Thêm thông tin KHÔNG có trong bài | Bài không nói X → Bẫy: "XだからY" |
| **Scope** 📐 | Quá RỘNG (over-generalization) hoặc quá HẸP | Bài: "金閣寺で写真" → Bẫy rộng: "京都で写真" / Bẫy hẹp: "池のそばで写真" |
| **Mixing** 🧩 | Kết hợp 2 thông tin đúng riêng lẻ thành ý sai | A đúng + B đúng → Bẫy: "AだからB" (không liên quan) |

**Quy tắc**:
- 3 distractor PHẢI dùng **≥ 3 loại bẫy khác nhau** (không lặp 3 lần cùng loại)
- Mỗi distractor PHẢI dùng info THẬT từ bài (trừ Fabrication có thể cận-context)
- Distractor "generic wrong" không khớp 1 trong 5 loại → **FAIL** (cần redesign)

#### L10: 情報検索 — Condition count đúng level

Số điều kiện kết hợp trong câu hỏi PHẢI khớp level:

| Level | Số điều kiện | Đặc trưng |
|-------|:-----------:|-----------|
| **N5** | 1-2 | Tìm thông tin trực tiếp, 1 cột bảng |
| **N4** | 3-4 | Có ※ điều kiện ẩn |
| **N3** | 5-6 | Deadline kép + % hủy |
| **N2** | 6-8 | Flowchart, ngưỡng có ngoại lệ, "không kết hợp" |
| **N1** | 7+ | Đồng thời bắt buộc, loại trừ đặc biệt |

- Agent đếm điều kiện trong câu hỏi + xác minh khớp level
- Sai level (vd N3 chỉ 2 điều kiện) → FAIL — bài quá dễ so với level mục tiêu

#### L11: 情報検索 — 4 bẫy chuẩn

- **Bẫy điều kiện ※** (chính): bỏ qua điều kiện ẩn trong dấu ※ — phổ biến nhất
- **Bẫy tính toán**: sai phép cộng/trừ/% (vd hủy 50%, deadline cộng ngày)
- **Bẫy thông tin nhiễu**: thông tin gần đúng nhưng sai 1 chi tiết
- **Bẫy đọc nhầm**: hiểu sai ký hiệu ○×△※★◆【】 hoặc nhãn cột

#### L12: 情報検索 — Cross-reading + ký hiệu đặc trưng

- **Cross-reading**: thông tin trả lời PHẢI phân tán ≥ 2 vị trí (bảng + ※ chú thích, hoặc 2 hàng bảng) — yêu cầu cốt lõi
- Nếu thông tin chỉ ở 1 vị trí → bài quá đơn giản, FAIL
- HTML PHẢI có **bảng/bullet** + ký hiệu đặc trưng: ○ × △ ※ ★ ◆ 【】 — không phải prose-only
- N5 BẮT BUỘC dùng 全角スペース (U+3000) — script check_spacing đã enforce

#### L14: 「」 vs `<u>` consistency (Phần 2.1)

- Nếu text_read dùng `<u>...</u>` để đánh dấu cụm được hỏi → câu hỏi PHẢI dùng `<u>...</u>` (KHÔNG bao quanh `「」`)
- Nếu text_read dùng `「...」` (ngoặc kép Nhật) → câu hỏi cũng dùng `「...」`
- Auto-check: `check_quotes_underline_consistency` đã enforce — agent confirm
- KHÔNG được: text_read `<u>X</u>` mà question stem `「X」` → FAIL

#### L15: 固有名詞 (Tên riêng) — Furigana

- Tên người và địa danh BẮT BUỘC có furigana ở **mọi level** nếu cách đọc không hiển nhiên
- Ví dụ: `金閣寺(きんかくじ)` ở N4 → cần furigana dù 金/閣 là N2/N3
- Ngoại lệ: tên phổ biến đã học không cần (田中, 山田, 佐藤 ở N5-N4)
- Agent kiểm tên người (Surname + Given) và địa danh — flag nếu thiếu furigana

#### L16: 注 KHÔNG được hỏi trực tiếp (Phần 2.3)

- 注 (annotation) chỉ giải thích bối cảnh — câu hỏi KHÔNG được hỏi nội dung trực tiếp về 注
- Vi dụ SAI: 注1 nói `XXX: 〜という考え方` → Q hỏi "XXX là gì?" và đáp án copy nguyên 注 → FAIL
- Distractor N1 长文 dùng nội dung 注 làm đáp án sai = **Peripheral Source trap** (đúng/được phép)
- Agent confirm: question chính KHÔNG hỏi trực tiếp content trong 注


---

### BƯỚC 3: CROSS-BATCH (script đã check, agent review)

#### B1: Topic diversity
- Các bài trong cùng level không được trùng tag/chủ đề.
- Agent kiểm tra xem các chủ đề có đa dạng không.

#### B2: Question label diversity
- Các câu hỏi trong cùng level phải dùng nhiều loại `question_label` khác nhau.
- Tối thiểu 2 loại nếu ≤5 câu, 3 loại nếu >5 câu.

#### B3: Content similarity
- Agent đọc `text_read` của các bài cùng level.
- Flag nếu nội dung giống nhau (cùng chủ đề + cùng layout + cùng format).

#### B4: Format tag diversity (19 format types)
- Kiểm tra cột `format_tag` (nếu có) hoặc phân loại thủ công dựa trên nội dung HTML.
- 19 format types: `price_comparison_table`, `event_announcement`, `facility_guide`, `class_enrollment`, `service_guide`, `schedule_timetable`, `recruitment_notice`, `store_flyer`, `menu_guide`, `travel_listing`, `medicine_info`, `regulation_notice`, `comparison_article`, `member_notification`, `access_guide`, `consultation_schedule`, `troubleshooting_guide`, `application_procedure`, `secondhand_shop`.
- **KHÔNG lặp format** trong cùng batch/level — ưu tiên format ít dùng.
- Flag nếu >50% bài cùng level dùng cùng format.

#### B5: (中略) presence rate per dạng-level

Auto-check: `check_chuuryaku_rate` đã enforce — agent xem output.

Teacher kỳ vọng:
- **長文 N1**: (中略) ~30-35% bài
- **主張 N1**: (中略) ~40-45% bài
- **主張 N2**: (中略) ~28-35% bài
- **長文 N3 / 統合 / 短文 / 中文**: (中略) hiếm hoặc không có

Nếu batch ≥ 3 bài cùng level lệch > 50% so với teacher → cảnh báo (rất ít hoặc quá nhiều (中略)).

---

### BÁO CÁO

Log kết quả per row theo format:

```
Row {n} [{level}] {_id}:
  AUTO-CHECK: PASS/FAIL + chi tiết lỗi từ script
  L1 文体: PASS/FAIL + chi tiết
  L2 Paraphrase: PASS/FAIL + chi tiết
  L3 Distractor: PASS/FAIL + chi tiết
  L4 Key term: PASS/FAIL + chi tiết
  L5 Marker/Conditions: PASS/FAIL + chi tiết
  L6 Answer: PASS/FAIL + chi tiết (kèm condition tracing)
  L7 Topic: PASS/FAIL + chi tiết
  L8 Explain: PASS/FAIL + chi tiết
  EXTRA1 Screenshot: PASS/FAIL
  EXTRA2 HTML Structure: PASS/FAIL
```

Tổng hợp cuối:
```
TỔNG KẾT:
  Total: X rows
  PASS: Y rows
  FAIL: Z rows
  Cross-batch issues: N issues
  Format diversity: M/19 formats used
```

---

### BƯỚC 4: AUTO-RETRY — SỬA LỖI (tối đa 3 lần)

> **QUY TẮC BẮT BUỘC**: Nếu có bất kỳ row nào FAIL ở Bước 1 (auto-check) hoặc Bước 2 (LLM review), agent PHẢI tự động sửa row đó. KHÔNG được dừng lại chỉ để báo lỗi. KHÔNG gen lại toàn bộ nội dung — chỉ chỉnh sửa phần vi phạm.

#### Quy trình sửa lỗi:

1. **Xác định lỗi cụ thể**: Thu thập danh sách row bị lỗi, lỗi ở check nào, vi phạm rule gì, ở field nào.

2. **Sửa chính xác phần lỗi** (KHÔNG viết lại toàn bộ):

   | Loại lỗi | Cách sửa |
   |-----------|----------|
   | **Spacing** (full-width/half-width) | Sửa đúng ký tự space trong field bị lỗi. N5: `text_read` dùng U+3000, các field khác dùng half-width. N1-N4: tất cả dùng half-width. |
   | **Char count** ngoài range | Cắt bớt hoặc thêm câu vào `text_read` sao cho vừa range, giữ nguyên ý nghĩa và logic. |
   | **Ruby/Furigana** sai | Sửa tag `<ruby><rt>` theo Rules A/B/C trong `rules/vocabulary.md`. |
   | **文体 không nhất quán** | Chuyển đổi đúng thể: N1-N3 → 普通形 (だ/である), N4-N5 → ます形. Sửa cả bài + câu hỏi + đáp án. |
   | **Paraphrase vi phạm** | Diễn đạt lại đáp án đúng — thay từ đồng nghĩa, đổi cấu trúc câu. Giữ nguyên ý nghĩa. |
   | **Distractor kém** | Sửa đáp án sai: dùng thông tin có trong bài nhưng sai ngữ cảnh/quan hệ. Không bịa thông tin mới. |
   | **Key term vượt level** | Thay từ khó bằng từ cùng nghĩa ở level phù hợp, hoặc thêm furigana nếu từ ở phần bối cảnh. |
   | **Marker-question mismatch** | Thêm/sửa `<u>` tag hoặc `[ ① ]` trong HTML cho đúng với `question_label`. |
   | **Đáp án đúng sai** | Sửa `correct_answer` hoặc sửa nội dung đáp án/bài đọc cho khớp. |
   | **Tag không có trong topic.json** | Đổi tag sang tag gần nghĩa nhất có trong `rules/topic.json`. |
   | **Answer position skewed** | Đổi vị trí `correct_answer` (1→3, 2→4, v.v.) và xáo trộn thứ tự đáp án tương ứng. |
   | **Label diversity thấp** | Đổi loại câu hỏi (`question_label`) của 1-2 row và sửa lại câu hỏi + đáp án cho phù hợp label mới. |
   | **Explanation thiếu** | Bổ sung `explain_vn`/`explain_en` — giải thích tại sao đáp án đúng đúng và từng đáp án sai sai. |

3. **Cập nhật CSV**: Ghi lại row đã sửa vào file CSV (giữ nguyên `_id`, `level`).

4. **Chạy lại QC**: Chạy lại post_qc.py trên toàn bộ CSV:
   ```bash
   python3 .gemini/skills/jlpt-reading-generator-post-qc/scripts/post_qc.py --csv sheets/samples_v1.csv --verbose
   ```
   Đồng thời chạy lại LLM review (Bước 2) cho các row vừa sửa.

5. **Lặp lại**: Nếu vẫn FAIL → đọc lỗi mới, sửa tiếp. **Tối đa 3 vòng sửa cho mỗi row.**

6. **Dừng khi**:
   - Tất cả row PASS → báo cáo thành công ✅
   - Đã sửa 3 vòng mà vẫn FAIL → báo cáo row nào không thể sửa và lỗi cụ thể ❌

#### Nguyên tắc sửa:
- **Sửa tối thiểu**: Chỉ thay đổi phần vi phạm, giữ nguyên tối đa nội dung gốc.
- **Đọc lại rules**: Trước khi sửa, đọc lại rule liên quan trong `rules/` và `.gemini/skills/jlpt-reading-generator/SKILL.md`.
- **Mỗi vòng đọc lại lỗi**: Tránh sửa xong lỗi A lại tạo ra lỗi B.
- **KHÔNG gen lại row đã PASS** — chỉ sửa row FAIL.
- **Giữ tính nhất quán**: Nếu sửa `text_read`, kiểm tra lại câu hỏi + đáp án vẫn đúng. Nếu sửa đáp án, kiểm tra lại `explain` vẫn khớp.

---

### BÁO CÁO CUỐI CÙNG

```
TỔNG KẾT POST-QC:
  Total rows: X
  PASS (lần đầu): Y rows
  PASS (sau sửa): Z rows
  FAIL (không thể sửa): W rows
  Số vòng sửa đã dùng: R
  Cross-batch issues còn lại: N
```

Nếu có row FAIL sau 3 vòng sửa, liệt kê chi tiết:
```
ROW KHÔNG THỂ SỬA:
  Row {n} [{level}] {_id}:
    Lỗi: {mô tả lỗi cụ thể}
    Đã sửa: 3 vòng
    Gợi ý: {gợi ý xử lý thủ công}
```
