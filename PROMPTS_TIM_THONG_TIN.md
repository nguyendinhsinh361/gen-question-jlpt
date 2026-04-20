# Prompt Guide — Gen nội dung Tìm Thông Tin (JLPT 情報検索)

Bộ sưu tập prompts để gen dữ liệu training đa dạng. Copy-paste và chỉnh sửa theo nhu cầu.

> **Trước khi gen, BẮT BUỘC đọc SKILL.md** (`.claude/` hoặc `.gemini/skills/jlpt-reading-generator/SKILL.md`).
> File này chỉ là prompt template — tất cả quy tắc chi tiết nằm trong SKILL.md.

---

## Tổng quan độ khó theo level

Hiểu rõ sự khác biệt giữa các level là điều **quan trọng nhất** khi gen dữ liệu. Bài gen phải phản ánh đúng độ khó — không được quá dễ hoặc quá khó so với level.

### Nội dung & Ngữ pháp

| Level | Chủ đề | Văn phong | Cấu trúc câu |
|-------|--------|-----------|--------------|
| N5 | Đời sống cực kỳ đơn giản: mua sắm, giờ mở cửa, giá cả | Thân mật, hiragana nhiều | Câu ngắn, ～です/～ます, ～てください |
| N4 | Đời sống hàng ngày: sự kiện, lớp học, quy tắc cơ bản | Lịch sự đơn giản | ～ことができます, ～なければなりません, ～てもいいです |
| N3 | Xã hội: dịch vụ, tuyển dụng, du lịch, so sánh | Nửa formal nửa conversational | ～について, ～による, ～場合は, ～ために |
| N2 | Chuyên sâu: so sánh phức tạp, hướng dẫn chi tiết, quy trình | Formal, văn viết | ～に伴い, ～に基づき, ～を踏まえて, ～に限り |
| N1 | Chuyên môn: y tế, pháp luật, tài chính, hợp đồng | Rất formal, keigo cao cấp | ～いかんによらず, ～をもって, ～に先立ち, 敬語 phức tạp |

### Độ phức tạp thông tin

| Level | Số điều kiện để trả lời 1 câu hỏi | Cấu trúc bài đọc |
|-------|-------------------------------------|-------------------|
| N5 | 1 điều kiện (tìm giá, tìm ngày) | 1 bảng đơn giản hoặc 1 danh sách |
| N4 | 1-2 điều kiện (ai + khi nào) | Bảng + 1-2 đoạn mô tả ngắn |
| N3 | 2 điều kiện (ai + điều kiện gì + ở đâu) | Nhiều section, bảng phức tạp hơn |
| N2 | 2-3 điều kiện (cross-reference bảng + văn xuôi) | Multi-section, flowchart, bảng so sánh |
| N1 | 3+ điều kiện (cross-reference nhiều bảng/đoạn) | Dense data, footnotes, điều khoản ngoại lệ |

### Câu hỏi & Đáp án

| Level | Số câu hỏi | Kiểu câu hỏi | Đáp án sai (distractor) |
|-------|-----------|---------------|------------------------|
| N5 | 1 | "Bao nhiêu tiền?", "Mấy giờ?", "Ở đâu?" | Sai rõ ràng nhưng liên quan bài đọc |
| N4 | 2 | "Ai có thể tham gia?", "Câu nào đúng?" | Đúng 1 phần nhưng sai chi tiết |
| N3 | 2 | "Phải mang gì?", "Điền form thế nào?" | Đúng 1 điều kiện, sai điều kiện khác |
| N2 | 2 | "Ai đủ tiêu chuẩn?", "Quy trình đăng ký?" | Lẫn thông tin giữa các section |
| N1 | 2 | "Ai đáp ứng TẤT CẢ điều kiện?", "Thủ tục nào đúng trình tự?" | Đúng gần hết, sai đúng 1 điều kiện khó nhận ra |

---

## Nhắc nhở bắt buộc (copy vào cuối MỌI prompt)

```
Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

---

## 1. Gen theo level — Batch 5 bài

### N5 — 5 mẫu đa dạng

```
Gen 5 bài tìm thông tin level N5, mỗi bài format khác nhau. Lưu CSV mới trong sheets/

Format chọn từ: store_flyer, event_announcement, regulation_notice, schedule_timetable, travel_listing, access_guide

Yêu cầu nội dung N5:
- Chars: 250-290 (< 250 → gen lại)
- Chủ đề cực đơn giản: tờ rơi siêu thị, giờ mở cửa, bảng giá, lịch xe bus
- Viết gần như toàn hiragana + kanji N5 cơ bản (日, 月, 人, 円, 時...)
- Câu ngắn: ～です, ～ます, ～てください. KHÔNG dùng ngữ pháp N4+
- Furigana: 0-1 từ, ưu tiên viết hiragana thay kanji. KHÔNG dùng dạng Ab
- 1 câu hỏi/bài: hỏi thông tin cụ thể đơn giản (giá bao nhiêu? mấy giờ? ở đâu?)
- Đáp án sai: liên quan bài đọc nhưng sai thông tin (sai giá, sai ngày, sai địa điểm)

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### N4 — 5 mẫu đa dạng

```
Gen 5 bài tìm thông tin level N4, mỗi bài format khác nhau. Lưu CSV mới trong sheets/

Format chọn từ: event_announcement, class_enrollment, regulation_notice, menu_guide, price_comparison_table, service_guide

Yêu cầu nội dung N4:
- Chars: 400-500 (< 400 → gen lại)
- Chủ đề đời sống: sự kiện khu phố, đăng ký lớp học, quy tắc rác, thực đơn nhà hàng
- Kanji N5+N4, câu lịch sự cơ bản: ～ことができます, ～なければなりません
- Bảng đơn giản + 1-2 đoạn mô tả ngắn
- Furigana: 0-2 từ vượt N4. KHÔNG dùng dạng Ab
- 2 câu hỏi/bài:
  - Q1: ai có thể tham gia? (check 1-2 điều kiện)
  - Q2: câu nào đúng? (fact-check đơn giản)
- Đáp án sai: đúng 1 phần nhưng sai ở 1 chi tiết cụ thể

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### N3 — 5 mẫu đa dạng

```
Gen 5 bài tìm thông tin level N3, mỗi bài format khác nhau. Lưu CSV mới trong sheets/

Format chọn từ: class_enrollment, service_guide, event_announcement, facility_guide, travel_listing, price_comparison_table, recruitment_notice, menu_guide

Yêu cầu nội dung N3:
- Chars: 600-750 (< 600 → gen lại)
- Chủ đề xã hội: khóa học, dịch vụ công, hướng dẫn cơ sở, so sánh giá, tuyển dụng
- Kanji N5-N3, nửa formal nửa conversational: ～について, ～による, ～場合は
- Nhiều section, bảng có nhiều cột, điều kiện kèm ghi chú
- Furigana: 0-3 từ vượt N3. KHÔNG dùng dạng Ab
- 2 câu hỏi/bài:
  - Q1: cần mang/chuẩn bị gì? (cross-reference 2 điều kiện)
  - Q2: điền form/đăng ký thế nào? (áp dụng quy tắc)
- Đáp án sai: đúng 1 điều kiện, sai điều kiện khác

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### N2 — 5 mẫu đa dạng

```
Gen 5 bài tìm thông tin level N2, mỗi bài format khác nhau. Lưu CSV mới trong sheets/

Format chọn từ: facility_guide, service_guide, comparison_article, event_announcement, class_enrollment, schedule_timetable, menu_guide

Yêu cầu nội dung N2:
- Chars: 700-770 (< 700 → gen lại)
- Chủ đề chuyên sâu: so sánh dịch vụ chi tiết, hướng dẫn bảo hiểm, lịch hội thảo
- Kanji N5-N2, formal văn viết: ～に伴い, ～に基づき, ～を踏まえて, ～に限り
- Multi-section, bảng so sánh phức tạp, flowchart, nhiều điều kiện phụ
- Furigana: 0-2 từ N1. KHÔNG dùng dạng Ab
- 2 câu hỏi/bài:
  - Q1: ai đủ tiêu chuẩn? (cross-reference 2-3 điều kiện từ bảng + văn xuôi)
  - Q2: quy trình đăng ký/thủ tục thế nào? (tổng hợp nhiều bước)
- Đáp án sai: lẫn thông tin giữa các section, đúng ở section A nhưng sai ở section B

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### N1 — 5 mẫu đa dạng

```
Gen 5 bài tìm thông tin level N1, mỗi bài format khác nhau. Lưu CSV mới trong sheets/

Format chọn từ: price_comparison_table, service_guide, facility_guide, schedule_timetable, medicine_info, recruitment_notice, member_notification, event_announcement

Yêu cầu nội dung N1:
- Chars: 700-800 (< 700 → gen lại)
- Chủ đề chuyên môn: hướng dẫn thuốc, hợp đồng dịch vụ, quy chế tuyển dụng, thông báo hội viên
- Kanji N5-N1 đầy đủ, very formal + keigo: ～いかんによらず, ～をもって, ～に先立ち
- Dense data: bảng nhiều cột + footnote, điều khoản ngoại lệ, cross-reference phức tạp
- Furigana: gần như 0 (0-1 từ cực hiếm). KHÔNG dùng dạng Ab
- 2 câu hỏi/bài:
  - Q1: ai đáp ứng TẤT CẢ điều kiện? (cross-reference 3+ điều kiện, bảng + chú thích)
  - Q2: thủ tục nào đúng trình tự? (tổng hợp nhiều quy tắc + ngoại lệ)
- Đáp án sai: đúng gần hết, chỉ sai đúng 1 điều kiện khó nhận ra — test khả năng đọc kỹ

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

---

## 2. Gen batch lớn — Chỉ định số lượng per level

> **Cách dùng**: Thay số lượng `{N}` cho từng level. Chủ đề và format sẽ được chọn ngẫu nhiên,
> đa dạng, không trùng lặp trong cùng batch.

### Template chung

```
Gen batch bài tìm thông tin theo số lượng sau, lưu CSV mới trong sheets/

- N1: {số} bài
- N2: {số} bài
- N3: {số} bài
- N4: {số} bài
- N5: {số} bài

Yêu cầu:
- Chủ đề: chọn NGẪU NHIÊN, đa dạng, KHÔNG trùng chủ đề trong cùng batch
- Format: chọn ngẫu nhiên từ Format Catalog phù hợp level, KHÔNG trùng format liên tiếp
- Mỗi bài phải phản ánh ĐÚNG độ khó level:
  - N5 (250-290 chars): hiragana nhiều, ～です/～ます, 1 câu hỏi tìm thông tin đơn giản
  - N4 (400-500 chars): câu lịch sự cơ bản, 2 câu hỏi check 1-2 điều kiện
  - N3 (600-750 chars): nửa formal, 2 câu hỏi cross-reference 2 điều kiện
  - N2 (700-770 chars): formal văn viết, 2 câu hỏi cross-reference 2-3 điều kiện
  - N1 (700-800 chars): keigo, 2 câu hỏi cross-reference 3+ điều kiện + ngoại lệ
- Đáp án sai phải hợp lý THEO LEVEL: N5 sai rõ hơn, N1 sai tinh vi
- Chia nhỏ: gen tối đa 5 bài/lượt, kiểm tra chars + layout rồi gen tiếp

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### Ví dụ sử dụng

```
Gen batch bài tìm thông tin theo số lượng sau, lưu CSV mới trong sheets/

- N1: 3 bài
- N2: 5 bài
- N3: 5 bài
- N4: 4 bài
- N5: 3 bài

Yêu cầu:
- Chủ đề: chọn NGẪU NHIÊN, đa dạng, KHÔNG trùng chủ đề trong cùng batch
- Format: chọn ngẫu nhiên từ Format Catalog phù hợp level, KHÔNG trùng format liên tiếp
- Mỗi bài phải phản ánh ĐÚNG độ khó level:
  - N5 (250-290 chars): hiragana nhiều, ～です/～ます, 1 câu hỏi tìm thông tin đơn giản
  - N4 (400-500 chars): câu lịch sự cơ bản, 2 câu hỏi check 1-2 điều kiện
  - N3 (600-750 chars): nửa formal, 2 câu hỏi cross-reference 2 điều kiện
  - N2 (700-770 chars): formal văn viết, 2 câu hỏi cross-reference 2-3 điều kiện
  - N1 (700-800 chars): keigo, 2 câu hỏi cross-reference 3+ điều kiện + ngoại lệ
- Đáp án sai phải hợp lý THEO LEVEL: N5 sai rõ hơn, N1 sai tinh vi
- Chia nhỏ: gen tối đa 5 bài/lượt, kiểm tra chars + layout rồi gen tiếp

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo từ input/html/ và input/htm_content_qa/ trước khi gen
- Nội dung phải ĐÚNG level: từ vựng, ngữ pháp, độ phức tạp thông tin, kiểu câu hỏi
- Số ký tự PHẢI đạt minimum (count bằng count_body_chars(), < Min → gen lại)
- Đáp án sai phải hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên
- Format phù hợp level (store_flyer → N5, medicine_info → N1)
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

---

## 3. Gen theo format cụ thể

### Chỉ định format + level

```
Gen 1 bài tìm thông tin level N2, format: comparison_article

Chủ đề: so sánh 3 phòng gym (giá, giờ mở cửa, tiện ích, điều kiện hội viên)
- Đọc mẫu n2_1.html hoặc n2_10.html trước
- Dạng văn xuôi A/B/C, mỗi section mô tả chi tiết 1 phòng gym
- Dùng từ vựng N2: ～に伴い, ～に基づき, ～に限り
- Chars: 700-770 (< 700 → gen lại)
- 2 câu hỏi:
  - Q1: "Tanaka muốn tập buổi tối + có bể bơi + dưới 8000円/tháng → phòng gym nào?" (cross-reference 3 điều kiện)
  - Q2: "Câu nào đúng về thủ tục đăng ký hội viên?" (tổng hợp từ nhiều section)
- Đáp án sai: đúng 2/3 điều kiện, sai 1 (ví dụ: đúng giá + bể bơi, nhưng không mở buổi tối)

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo trước khi gen
- Nội dung phải ĐÚNG level N2: từ vựng, ngữ pháp formal, câu hỏi cross-reference 2-3 điều kiện
- Số ký tự PHẢI đạt minimum, đáp án sai phải hợp lý
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### Chỉ định format hiếm

```
Gen 1 bài tìm thông tin level N1, format: medicine_info

Chủ đề: phiếu hướng dẫn thuốc từ phòng khám nội khoa
- Đọc mẫu n1_1.html trước
- Bảng dense: tên thuốc, thành phần, tác dụng, liều dùng, chống chỉ định, lưu ý
- Dùng table-layout:fixed, có footnote chú thích + điều khoản ngoại lệ
- Từ vựng N1 formal: 服用, 禁忌, 併用, 副作用 (KHÔNG cần furigana — N1 phải biết)
- Chars: 700-800 (< 700 → gen lại)
- 2 câu hỏi phức tạp:
  - Q1: "Bệnh nhân A (60 tuổi, dị ứng X, đang uống thuốc Y) nên dùng thuốc nào?" (cross-reference 3+ điều kiện: tuổi + dị ứng + tương tác thuốc)
  - Q2: "Khi nào phải ngừng thuốc Z và liên hệ bác sĩ?" (tổng hợp nhiều lưu ý + ngoại lệ)
- Đáp án sai: đúng gần hết điều kiện, sai 1 chi tiết khó nhận ra (ví dụ: thuốc đúng nhưng chống chỉ định với dị ứng X)

Nhắc nhở bắt buộc:
- Đọc SKILL.md + mẫu n1_1.html trước khi gen
- Nội dung phải ĐÚNG level N1: keigo, từ chuyên ngành, câu hỏi cross-reference 3+ điều kiện
- Số ký tự PHẢI đạt minimum, đáp án sai phải tinh vi
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

---

## 4. Gen theo chủ đề cụ thể

### Chủ đề đời sống hàng ngày (N4)

```
Gen 3 bài tìm thông tin N4 về chủ đề đời sống hàng ngày, mỗi bài format khác nhau:
1. menu_guide — thực đơn nhà hàng cơm gà (bảng giá + set meal + điều kiện giảm giá)
2. regulation_notice — quy tắc phân loại rác khu chung cư (bảng loại rác + ngày thu gom)
3. event_announcement — lễ hội mùa hè khu phố (lịch trình + đăng ký + điều kiện tham gia)

Mỗi bài: 400-500 chars, 2 câu hỏi N4 (check 1-2 điều kiện đơn giản)
- Q kiểu: "Ai có thể tham gia?", "Câu nào đúng?", "Phải làm gì trước ngày X?"
- Đáp án sai: đúng 1 phần nhưng sai 1 chi tiết (sai ngày, sai đối tượng)
- Từ vựng N4: ～ことができます, ～までに, ～なければなりません

Lưu CSV mới trong sheets/

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo trước khi gen
- Nội dung phải ĐÚNG level N4: từ vựng, ngữ pháp, câu hỏi 1-2 điều kiện
- Số ký tự PHẢI đạt minimum, đáp án sai phải hợp lý
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### Chủ đề giáo dục (N3)

```
Gen 3 bài tìm thông tin N3 về chủ đề giáo dục, mỗi bài format khác nhau:
1. class_enrollment — đăng ký lớp tiếng Nhật buổi tối (điều kiện, lịch học, học phí, ưu đãi)
2. facility_guide — hướng dẫn sử dụng thư viện đại học (giờ mở cửa theo mùa, thẻ mượn, quy tắc)
3. price_comparison_table — so sánh học phí 3 trường dạy nghề (bảng: khóa học × trường × giá)

Mỗi bài: 600-750 chars, 2 câu hỏi N3 (cross-reference 2 điều kiện)
- Q kiểu: "Cần chuẩn bị gì?", "Điền form thế nào?", "Khóa nào phù hợp với người X?"
- Đáp án sai: đúng 1 điều kiện, sai điều kiện khác
- Từ vựng N3: ～について, ～場合は, ～ために, ～ことになっている

Lưu CSV mới trong sheets/

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo trước khi gen
- Nội dung phải ĐÚNG level N3: từ vựng, ngữ pháp, câu hỏi cross-reference 2 điều kiện
- Số ký tự PHẢI đạt minimum, đáp án sai phải hợp lý
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### Chủ đề công việc (N2)

```
Gen 3 bài tìm thông tin N2 về chủ đề công việc, mỗi bài format khác nhau:
1. recruitment_notice — tuyển nhân viên part-time cửa hàng (điều kiện, ca làm, phúc lợi, thủ tục)
2. schedule_timetable — lịch hội thảo hướng nghiệp (nhiều phòng, nhiều time slot, đăng ký trước)
3. service_guide — hướng dẫn đăng ký bảo hiểm lao động (flowchart quy trình, giấy tờ cần thiết)

Mỗi bài: 700-770 chars, 2 câu hỏi N2 (cross-reference 2-3 điều kiện)
- Q kiểu: "Ai đủ tiêu chuẩn ứng tuyển?", "Quy trình đăng ký gồm những bước nào?"
- Đáp án sai: lẫn thông tin giữa các section (đúng ở phần A, sai ở phần B)
- Từ vựng N2 formal: ～に伴い, ～に基づき, ～に限り, ～を踏まえて

Lưu CSV mới trong sheets/

Nhắc nhở bắt buộc:
- Đọc SKILL.md + 1-2 mẫu tham khảo trước khi gen
- Nội dung phải ĐÚNG level N2: từ vựng formal, câu hỏi cross-reference 2-3 điều kiện
- Số ký tự PHẢI đạt minimum, đáp án sai phải hợp lý
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

---

## 5. Chỉ gen câu hỏi (cho bài đã có)

### Gen câu hỏi theo level

```
Cho các bài tìm thông tin đã có trong sheets/{file}.csv, gen câu hỏi cho mỗi bài.

- Đọc HTML mỗi bài trong assets/html/tim_thong_tin/ trước
- Câu hỏi phải ĐÚNG level:
  - N5: 1 câu, hỏi thông tin cụ thể (giá, giờ, nơi), đáp án sai rõ ràng
  - N4: 2 câu, check 1-2 điều kiện, đáp án sai 1 chi tiết
  - N3: 2 câu, cross-reference 2 điều kiện, đáp án sai 1 điều kiện
  - N2: 2 câu, cross-reference 2-3 điều kiện, đáp án lẫn thông tin giữa section
  - N1: 2 câu, cross-reference 3+ điều kiện + ngoại lệ, đáp án sai tinh vi
- 4 đáp án/câu (1 đúng, 3 sai hợp lý — sai ở chi tiết, KHÔNG sai hiển nhiên)
- Kiểm tra kỹ: CHỈ CÓ 1 đáp án đúng, không có 2 đáp án cùng đúng
- Giải thích VN + EN cho mỗi câu
- Cập nhật CSV
```

---

## 6. Kiểm tra & sửa lỗi

### Kiểm tra toàn bộ (chạy sau mỗi batch)

```
Kiểm tra tất cả bài tìm thông tin trong assets/html/tim_thong_tin/:

1. Chars — đếm bằng count_body_chars(), báo bài nào dưới minimum
2. Nội dung vs Level — từ vựng/ngữ pháp có đúng level? (N5 dùng ～です/～ます, N1 dùng keigo)
3. Câu hỏi vs Level — độ khó câu hỏi đúng chưa? (N5: 1 điều kiện, N1: 3+ điều kiện + ngoại lệ)
4. Đáp án — chỉ 1 đáp án đúng? Đáp án sai hợp lý? (không sai hiển nhiên, sai ở chi tiết)
5. Format vs Level — format có phù hợp level? (store_flyer cho N5, medicine_info cho N1)
6. Layout A4 — screenshot giống tờ A4? Nội dung tràn ra ngoài container?
7. Flow text — có dùng <br> trong paragraph? Mỗi câu có nằm trên 1 dòng riêng?
8. Che khuất — có chữ nào bị che bởi icon/label/hình vẽ?
9. Ngắt từ — có từ nào bị tách giữa 2 dòng?
10. Furigana — dạng Ab? từ đúng level bị gắn furigana? <ruby> thiếu <rt>?

Nếu lỗi, sửa lại HTML → chụp lại screenshot → cập nhật CSV.
```

### Kiểm tra đáp án chuyên sâu

```
Kiểm tra chất lượng câu hỏi & đáp án cho tất cả bài trong sheets/{file}.csv:

1. Với mỗi câu hỏi: đọc lại bài gốc → tìm đáp án → xác nhận CHỈ 1 đáp án đúng
2. Kiểm tra đáp án sai có đủ hợp lý không (test-taker phải đọc kỹ mới loại được)
3. Kiểm tra 2 câu hỏi cùng bài test KHÁC khía cạnh (không hỏi cùng 1 thông tin)
4. Kiểm tra level phù hợp:
   - N5: câu hỏi 1 bước (tìm X), đáp án sai rõ ràng
   - N1: câu hỏi multi-step (cross-reference), đáp án sai tinh vi
5. Báo cáo lỗi và sửa nếu cần
```

---

## 7. Bổ sung & mở rộng

### Thêm bài cho level thiếu

```
Kiểm tra tổng số bài đã gen cho mỗi level, rồi gen thêm cho level nào ít nhất.

Mục tiêu: mỗi level có ít nhất 10 bài.
- Kiểm tra format đã dùng → chọn format chưa dùng trước
- Đảm bảo nội dung đúng level (từ vựng, ngữ pháp, câu hỏi, distractor)
- Lưu CSV mới riêng cho mỗi level

Nhắc nhở bắt buộc:
- Đọc SKILL.md + mẫu tham khảo trước khi gen
- Nội dung phải ĐÚNG level, số ký tự PHẢI đạt minimum
- Đáp án sai phải hợp lý theo level
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

### Gen bài với visual elements đặc biệt

```
Gen 5 bài tìm thông tin (1 per level) với visual elements đặc biệt:

1. N1 — price_comparison_table: bảng có rowspan/colspan + footnote + điều khoản ngoại lệ
2. N2 — facility_guide: flowchart (yes/no decision boxes) + bảng điều kiện
3. N3 — class_enrollment: 2×2 course grid + điều kiện đăng ký
4. N4 — event_announcement: pill labels + 【】section headers
5. N5 — store_flyer: promo boxes + highlight giá (icon/hình KHÔNG được che chữ)

Mỗi bài: nội dung + câu hỏi + đáp án phải ĐÚNG level tương ứng.
- Table dùng table-layout:fixed, flex/grid tổng width ≤ 100%
- Đọc references/design-patterns.md để biết visual elements

Nhắc nhở bắt buộc:
- Đọc SKILL.md + mẫu tham khảo trước khi gen
- Nội dung phải ĐÚNG level, số ký tự PHẢI đạt minimum
- Đáp án sai phải hợp lý theo level
- Layout A4, flow text, không tách từ, không che khuất chữ (xem SKILL.md)
```

---

## Mẹo sử dụng prompt

1. **Luôn nêu rõ level** — mỗi level khác nhau hoàn toàn: từ vựng, ngữ pháp, chars, số câu hỏi, độ khó distractor
2. **Kiểm tra nội dung đúng level** — đây là lỗi phổ biến nhất: N5 dùng từ N3, N4 hỏi câu kiểu N2
3. **Đáp án sai quan trọng bằng đáp án đúng** — distractor tốt = test chất lượng. N1 distractor phải tinh vi hơn N5
4. **Chia nhỏ batch** — gen 5 bài/lượt, kiểm tra rồi gen tiếp. Không gen >5 bài 1 lần
5. **Nêu format cụ thể** — "format: comparison_article" rõ ràng hơn "dạng so sánh"
6. **Gen xong = kiểm tra ngay** — chạy prompt kiểm tra (section 6) sau mỗi batch
7. **Review screenshot** — quan trọng nhất là nhìn screenshot, không chỉ đọc HTML
8. **Các quy tắc kỹ thuật** (UUID, CSS, Playwright, furigana format...) — đã có đầy đủ trong SKILL.md, không cần nhắc lại trong prompt
