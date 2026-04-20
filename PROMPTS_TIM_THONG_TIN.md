# Prompt Guide — Gen nội dung Tìm Thông Tin (JLPT 情報検索)

Bộ sưu tập prompts để gen dữ liệu training đa dạng. Copy-paste và chỉnh sửa theo nhu cầu.

> **Trước khi gen, BẮT BUỘC đọc SKILL.md** (`.claude/` hoặc `.gemini/skills/jlpt-reading-generator/SKILL.md`).
> File này chỉ là prompt template — tất cả quy tắc chi tiết nằm trong SKILL.md.

---

## Quy tắc nhắc nhở (phải có trong MỌI prompt)

Mỗi prompt gen dữ liệu **PHẢI** bao gồm các nhắc nhở sau (copy block này vào cuối prompt):

```
Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

---

## 1. Gen theo level — Batch 5 bài

### N5 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N5 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: store_flyer, event_announcement, regulation_notice, schedule_timetable, travel_listing, access_guide
- Chars: 200-290 (Hard reject < 180)
- Furigana: 0-1 từ vượt N5, ưu tiên viết hiragana thay vì furigana. KHÔNG dùng dạng Ab
- 1 câu hỏi/bài
- Text flow liên tục, KHÔNG <br> trong paragraph
- Layout A4

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

### N4 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N4 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: event_announcement, class_enrollment, regulation_notice, menu_guide, price_comparison_table, service_guide
- Chars: 400-500 (Hard reject < 360)
- Furigana: 0-2 từ vượt N4, ưu tiên thay từ đơn giản. KHÔNG dùng dạng Ab
- 2 câu hỏi/bài
- Text flow liên tục, KHÔNG <br> trong paragraph
- Layout A4

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

### N3 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N3 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: class_enrollment, service_guide, event_announcement, facility_guide, travel_listing, price_comparison_table, recruitment_notice, menu_guide
- Chars: 550-750 (Hard reject < 495)
- Furigana: 0-3 từ vượt N3, ưu tiên thay từ đơn giản. KHÔNG dùng dạng Ab
- 2 câu hỏi/bài
- Text flow liên tục, KHÔNG <br> trong paragraph
- Layout A4

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

### N2 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N2 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: facility_guide, service_guide, comparison_article, event_announcement, class_enrollment, schedule_timetable, menu_guide
- Chars: 620-770 (Hard reject < 558)
- Furigana: 0-2 từ N1, ưu tiên thay từ đơn giản. KHÔNG dùng dạng Ab
- 2 câu hỏi/bài
- Text flow liên tục, KHÔNG <br> trong paragraph
- Layout A4

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

### N1 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N1 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: price_comparison_table, service_guide, facility_guide, schedule_timetable, medicine_info, recruitment_notice, member_notification, event_announcement
- Chars: 650-800 (Hard reject < 585)
- Furigana: gần như không có (0-1 từ cực hiếm). KHÔNG dùng dạng Ab
- 2 câu hỏi/bài
- Text flow liên tục, KHÔNG <br> trong paragraph
- Layout A4

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

---

## 2. Gen batch lớn — Đa level

### 10 bài (2 per level)

```
Gen 10 bài tìm thông tin, 2 bài mỗi level N1-N5, lưu CSV mới trong sheets/

Yêu cầu:
- Mỗi level chọn 2 format khác nhau
- Tổng 10 bài → tối thiểu 10 format khác nhau
- Đọc mẫu tham khảo trong input/html/ + input/htm_content_qa/ trước
- Chủ đề đa dạng, không trùng nhau

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

### 15 bài (3 per level) — Dùng hết 15 format

```
Gen 15 bài tìm thông tin, 3 bài mỗi level N1-N5, lưu CSV mới trong sheets/

Yêu cầu:
- Tổng 15 bài → dùng hết 15 format trong Format Catalog, mỗi format đúng 1 lần
- Phân bổ format theo level cho phù hợp (ví dụ store_flyer → N5, medicine_info → N1)
- Chia nhỏ: gen 5 bài/lượt, kiểm tra chars + layout + furigana rồi gen tiếp

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

---

## 3. Gen theo format cụ thể

### Chỉ định format + level

```
Gen 1 bài tìm thông tin level N2, format: comparison_article

Chủ đề: so sánh 3 phòng gym (giá, giờ mở, tiện ích)
- Đọc mẫu n2_1.html hoặc n2_10.html trước
- Dạng văn xuôi A/B/C, mỗi section mô tả 1 phòng gym
- Chars: 620-770 (Hard reject < 558)
- 2 câu hỏi: Q1 hỏi điều kiện, Q2 hỏi giá/thời gian

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- HTML phải giống tờ A4: container width=794px, min-height=1123px
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph
- KHÔNG tách giữa từ khi xuống dòng
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản
- Sau khi gen: count chars → capture screenshot → review layout
```

### Chỉ định format hiếm

```
Gen 1 bài tìm thông tin level N1, format: medicine_info

Chủ đề: phiếu hướng dẫn thuốc từ phòng khám
- Đọc mẫu n1_1.html trước
- Bảng: tên thuốc, tác dụng, liều dùng, lưu ý. Dùng table-layout:fixed
- Gần như không furigana
- Chars: 650-800 (Hard reject < 585)
- 2 câu hỏi phức tạp: cross-reference nhiều điều kiện

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- HTML phải giống tờ A4: container width=794px, min-height=1123px
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph
- KHÔNG tách giữa từ khi xuống dòng
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản
- Sau khi gen: count chars → capture screenshot → review layout
```

---

## 4. Gen theo chủ đề cụ thể

### Chủ đề đời sống hàng ngày

```
Gen 3 bài tìm thông tin N4 về chủ đề đời sống hàng ngày, mỗi bài format khác nhau:
1. menu_guide — thực đơn nhà hàng cơm gà
2. regulation_notice — quy tắc phân loại rác khu chung cư
3. event_announcement — lễ hội mùa hè khu phố

Lưu CSV mới trong sheets/

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

### Chủ đề giáo dục

```
Gen 3 bài tìm thông tin N3 về chủ đề giáo dục, mỗi bài format khác nhau:
1. class_enrollment — đăng ký lớp tiếng Nhật buổi tối
2. facility_guide — hướng dẫn sử dụng thư viện đại học
3. price_comparison_table — so sánh học phí 3 trường dạy nghề

Lưu CSV mới trong sheets/

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

### Chủ đề công việc

```
Gen 3 bài tìm thông tin N2 về chủ đề công việc, mỗi bài format khác nhau:
1. recruitment_notice — tuyển nhân viên part-time cửa hàng
2. schedule_timetable — lịch hội thảo hướng nghiệp
3. service_guide — hướng dẫn đăng ký bảo hiểm lao động

Lưu CSV mới trong sheets/

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- Đọc 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/
- HTML phải giống tờ A4: container width=794px, min-height=1123px, nền xám + tờ trắng
- Text chảy liên tục (flow text): KHÔNG dùng <br> trong paragraph. Các câu cùng đoạn gộp trong 1 <p>
- KHÔNG tách giữa từ khi xuống dòng: CSS word-break:keep-all + line-break:strict
- Furigana: phải dùng <ruby>+<rt>, ưu tiên thay từ đơn giản hơn thay vì rắc furigana
- Sau khi gen: count chars → nếu < Hard Reject thì gen lại. Capture screenshot → review layout
- UUID: dùng uuid.uuid4().hex (full 32-char, KHÔNG cắt)
```

---

## 5. Chỉ gen câu hỏi (cho bài đã có)

### Gen câu hỏi cho 1 file CSV

```
Cho các bài tìm thông tin đã có trong sheets/n5_samples_v2.csv, gen câu hỏi cho mỗi bài.

- Đọc HTML mỗi bài trong assets/html/tim_thong_tin/ trước
- N5: 1 câu hỏi/bài, đơn giản, tìm thông tin cụ thể
- 4 đáp án (1 đúng, 3 sai nhưng hợp lý — sai ở chi tiết, không sai hiển nhiên)
- Giải thích VN + EN
- Cập nhật CSV
```

### Gen câu hỏi cho level cao (N1-N2)

```
Cho các bài N1 đã có trong sheets/n1_samples.csv, gen câu hỏi.

- Đọc HTML mỗi bài trước
- 2 câu hỏi/bài:
  - Q1: cross-reference nhiều điều kiện (ai đủ tiêu chuẩn? cần làm gì?)
  - Q2: quy trình/thủ tục (phải nộp gì? theo thứ tự nào?)
- Đáp án sai phải hợp lý (đúng 1 điều kiện, sai điều kiện khác)
- Furigana trong câu hỏi: cùng quy tắc với bài đọc
- Kiểm tra kỹ: đảm bảo CHỈ CÓ 1 đáp án đúng, không có 2 đáp án cùng đúng
```

---

## 6. Kiểm tra & sửa lỗi

### Kiểm tra toàn bộ (chạy sau mỗi batch)

```
Kiểm tra tất cả bài tìm thông tin trong assets/html/tim_thong_tin/:

1. Chars — đếm bằng count_body_chars(), báo bài nào ngoài Target Range hoặc dưới Hard Reject
2. Layout A4 — screenshot có giống tờ A4 không? Nội dung tràn ra ngoài container?
3. Flow text — có dùng <br> trong paragraph không? Mỗi câu có nằm trên 1 dòng riêng không?
4. Ngắt từ — có từ nào bị tách giữa 2 dòng không? (kiểm tra trong screenshot)
5. Furigana — có dạng "Ab" không? Có từ đúng level bị gắn furigana không? Có quá 3 ruby tags không?
6. Furigana tags — có dùng <ruby>+<rt> đúng cách không? (không dùng ngoặc, không thiếu <rt>)
7. Format diversity — có bài nào trùng format trong cùng batch?
8. Baseline — từ có furigana có bị thấp xuống so với text xung quanh không?

Nếu lỗi, sửa lại HTML → chụp lại screenshot → cập nhật CSV.
```

### Kiểm tra furigana chuyên sâu

```
Kiểm tra furigana cho tất cả bài N4 trong assets/html/tim_thong_tin/n4_*.html:

1. Liệt kê tất cả <ruby> tags trong mỗi file
2. Với mỗi ruby tag, xác nhận từ đó THẬT SỰ vượt N4 (thuộc N3/N2/N1)
3. Kiểm tra có dạng "Ab" nào không (nửa kanji nửa hiragana)
4. Kiểm tra có <ruby> thiếu <rt> không (vô nghĩa nếu thiếu)
5. Đếm tổng ruby tags — phải ≤ 4
6. Nếu quá nhiều furigana: đề xuất thay bằng từ đơn giản hơn

Báo cáo kết quả và sửa nếu cần.
```

---

## 7. Bổ sung & mở rộng

### Thêm bài cho level thiếu

```
Kiểm tra tổng số bài đã gen cho mỗi level, rồi gen thêm cho level nào ít nhất.

Mục tiêu: mỗi level có ít nhất 10 bài.
- Kiểm tra format đã dùng → chọn format chưa dùng trước
- Lưu CSV mới riêng cho mỗi level

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- HTML phải giống tờ A4, text flow liên tục, không tách từ giữa dòng
- Furigana: dùng <ruby>+<rt>, ưu tiên thay từ đơn giản
- Count chars + capture screenshot + review layout sau mỗi bài
```

### Gen bài với visual elements đặc biệt

```
Gen 5 bài tìm thông tin (1 per level) với visual elements đặc biệt:

1. N1 — price_comparison_table: bảng phức tạp có rowspan/colspan + chú thích footnote
2. N2 — facility_guide: flowchart (yes/no decision boxes)
3. N3 — class_enrollment: 2×2 course grid
4. N4 — event_announcement: pill labels + 【】section headers
5. N5 — store_flyer: promo boxes + highlight text

Đọc references/design-patterns.md để biết visual elements.
Lưu ý: table dùng table-layout:fixed, flex/grid tổng width ≤ 100%.

Nhắc nhở bắt buộc:
- Đọc SKILL.md trước khi gen
- HTML phải giống tờ A4: container width=794px, min-height=1123px
- Text chảy liên tục, KHÔNG <br> trong paragraph, KHÔNG tách từ giữa dòng
- Furigana: dùng <ruby>+<rt>, ưu tiên thay từ đơn giản
- Count chars + capture screenshot + review layout sau mỗi bài
```

---

## Mẹo sử dụng prompt

1. **Luôn kèm block "Nhắc nhở bắt buộc"** — đây là cách hiệu quả nhất để AI tuân thủ quy tắc
2. **Nêu rõ level** — mỗi level có constraints khác nhau (chars, furigana, số câu hỏi)
3. **Nêu rõ "lưu CSV mới trong sheets/"** — tránh ghi đè file cũ
4. **Chia nhỏ batch** — gen 5 bài/lượt, kiểm tra rồi gen tiếp. Không gen >5 bài 1 lần
5. **Nêu format cụ thể** — "format: comparison_article" rõ ràng hơn "dạng so sánh"
6. **Gen xong = kiểm tra ngay** — chạy prompt kiểm tra (section 6) sau mỗi batch
7. **Review screenshot** — quan trọng nhất là nhìn screenshot, không chỉ đọc HTML
