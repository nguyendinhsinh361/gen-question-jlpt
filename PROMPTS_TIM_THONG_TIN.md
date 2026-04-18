# Prompt Guide — Gen nội dung Tìm Thông Tin (JLPT 情報検索)

Bộ sưu tập prompts để gen dữ liệu training đa dạng. Copy-paste và chỉnh sửa theo nhu cầu.

> **Nguyên tắc vàng:** Mỗi batch gen phải dùng format khác nhau. Nếu gen 5 bài → 5 format khác nhau. Nếu gen 15 bài → dùng hết 15 format rồi mới được lặp.

---

## 1. Gen theo level — Batch nhỏ (5 bài)

### N5 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N5 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: store_flyer, event_announcement, regulation_notice, schedule_timetable, travel_listing, access_guide
- Furigana chỉ cho từ vượt N5 (rất ít, 0-2 từ), không dùng dạng Ab
- Chars: 130-290
- 1 câu hỏi/bài
```

### N4 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N4 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: event_announcement, class_enrollment, regulation_notice, menu_guide, price_comparison_table, service_guide
- Furigana chỉ cho từ vượt N4 (0-3 từ), không dùng dạng Ab
- Chars: 300-500
- 2 câu hỏi/bài
```

### N3 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N3 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: class_enrollment, service_guide, event_announcement, facility_guide, travel_listing, price_comparison_table, recruitment_notice, menu_guide
- Furigana chỉ cho từ vượt N3 (0-5 từ), không dùng dạng Ab
- Chars: 340-750
- 2 câu hỏi/bài
```

### N2 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N2 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: facility_guide, service_guide, comparison_article, event_announcement, class_enrollment, schedule_timetable, menu_guide
- Furigana chỉ cho từ N1 (0-3 từ), không dùng dạng Ab
- Chars: 480-770
- 2 câu hỏi/bài
```

### N1 — 5 mẫu đa dạng

```
Giúp tôi tạo dữ liệu level N1 có tổng cộng 5 mẫu đa dạng trong một file mới trong folder sheets/

Yêu cầu:
- 5 bài, mỗi bài dùng format khác nhau từ Format Catalog
- Chọn từ: price_comparison_table, service_guide, facility_guide, schedule_timetable, medicine_info, recruitment_notice, member_notification, event_announcement
- Gần như không furigana (0-2 từ cực hiếm), không dùng dạng Ab
- Chars: 500-800
- 2 câu hỏi/bài
```

---

## 2. Gen batch lớn — Đa level

### 10 bài (2 per level)

```
Gen 10 bài tìm thông tin, 2 bài mỗi level N1-N5, lưu CSV mới trong sheets/

Yêu cầu:
- Mỗi level chọn 2 format khác nhau
- Tổng 10 bài → tối thiểu 10 format khác nhau (không trùng format giữa các level nếu có thể)
- Đọc mẫu tham khảo trong input/html/ trước
- Chủ đề đa dạng, không trùng nhau
```

### 15 bài (3 per level) — Dùng hết 15 format

```
Gen 15 bài tìm thông tin, 3 bài mỗi level N1-N5, lưu CSV mới trong sheets/

Yêu cầu:
- Tổng 15 bài → dùng hết 15 format trong Format Catalog, mỗi format đúng 1 lần
- Phân bổ format theo level cho phù hợp (ví dụ store_flyer → N5, medicine_info → N1)
- Đọc mẫu tham khảo + mẫu QA trước khi gen
- Kiểm tra chars + furigana cho từng bài
```

### 25 bài (5 per level) — Quy mô vừa

```
Gen 25 bài tìm thông tin, 5 bài mỗi level N1-N5, lưu CSV mới trong sheets/

Yêu cầu:
- Mỗi level: 5 format khác nhau, không trùng trong cùng level
- Giữa các level có thể lặp format nhưng phải khác chủ đề
  (ví dụ: event_announcement ở N5 là "おまつり", ở N2 là "就職フェア")
- Tham khảo input/topic.json để đa dạng chủ đề
- Kiểm tra kỹ chars, furigana, format diversity
```

### 50 bài (10 per level) — Quy mô lớn

```
Gen 50 bài tìm thông tin, 10 bài mỗi level N1-N5, lưu CSV mới trong sheets/

Yêu cầu:
- Mỗi level: 10 bài → tối thiểu 6-8 format khác nhau (một số format dùng 2 lần với chủ đề khác)
- Khi lặp format, phải khác:
  - Chủ đề hoàn toàn khác
  - Layout/visual elements khác (ví dụ: cùng event_announcement nhưng 1 bài dùng bảng, 1 bài dùng pill label)
- Chia nhỏ: gen 5 bài/lượt, kiểm tra rồi gen tiếp
- Tham khảo input/topic.json
```

---

## 3. Gen theo format cụ thể

### Chỉ định format + level

```
Gen 1 bài tìm thông tin level N2, format: comparison_article

Chủ đề: so sánh 3 phòng gym (giá, giờ mở, tiện ích)
- Đọc mẫu n2_1.html hoặc n2_10.html trước
- Dạng văn xuôi A/B/C, mỗi section mô tả 1 phòng gym
- Chars: 480-770
- 2 câu hỏi: Q1 hỏi điều kiện, Q2 hỏi giá/thời gian
```

### Chỉ định format hiếm

```
Gen 1 bài tìm thông tin level N1, format: medicine_info

Chủ đề: phiếu hướng dẫn thuốc từ phòng khám
- Đọc mẫu n1_1.html trước
- Bảng: tên thuốc, tác dụng, liều dùng, lưu ý
- Gần như không furigana
- Chars: 500-800
- 2 câu hỏi phức tạp: cross-reference nhiều điều kiện
```

### Gen format chưa từng dùng

```
Gen 1 bài tìm thông tin level N5, format: access_guide

Chủ đề: hướng dẫn đường đến trường
- Đọc mẫu n5_8.html trước
- Sơ đồ tuyến đường: nhà ga → bus → trường
- Viết gần như toàn hiragana, rất ít kanji
- Chars: 130-290
- 1 câu hỏi đơn giản
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
```

### Chủ đề giáo dục

```
Gen 3 bài tìm thông tin N3 về chủ đề giáo dục, mỗi bài format khác nhau:
1. class_enrollment — đăng ký lớp tiếng Nhật buổi tối
2. facility_guide — hướng dẫn sử dụng thư viện đại học
3. price_comparison_table — so sánh học phí 3 trường dạy nghề

Lưu CSV mới trong sheets/
```

### Chủ đề công việc

```
Gen 3 bài tìm thông tin N2 về chủ đề công việc, mỗi bài format khác nhau:
1. recruitment_notice — tuyển nhân viên part-time cửa hàng
2. schedule_timetable — lịch hội thảo hướng nghiệp
3. service_guide — hướng dẫn đăng ký bảo hiểm lao động

Lưu CSV mới trong sheets/
```

### Chủ đề du lịch & giải trí

```
Gen 3 bài tìm thông tin N3 về du lịch và giải trí, mỗi bài format khác nhau:
1. travel_listing — 4 tour bus mùa thu (núi, biển, onsen, lâu đài)
2. event_announcement — lễ hội pháo hoa bên sông
3. facility_guide — hướng dẫn sử dụng khu cắm trại

Lưu CSV mới trong sheets/
```

---

## 5. Chỉ gen câu hỏi (cho bài đã có)

### Gen câu hỏi cho 1 file CSV

```
Cho các bài tìm thông tin đã có trong sheets/n5_samples_v2.csv, gen câu hỏi cho mỗi bài.

- Đọc HTML mỗi bài trong assets/html/tim_thong_tin/ trước
- N5: 1 câu hỏi/bài, đơn giản, tìm thông tin cụ thể
- 4 đáp án (1 đúng, 3 sai nhưng hợp lý)
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
```

---

## 6. Kiểm tra & sửa lỗi

### Kiểm tra toàn bộ

```
Kiểm tra tất cả bài tìm thông tin trong assets/html/tim_thong_tin/:

1. Đếm ký tự — báo bài nào ngoài khoảng cho phép
2. Furigana — có dạng "Ab" nào không? (ví dụ: 週かん, 友だち, 拠てん)
3. Furigana — có từ đúng level nhưng bị gắn furigana không?
4. Format diversity — có bài nào trùng format trong cùng batch?
5. Ruby tags — có vượt giới hạn không? (N5: 0-5, N4: 0-8...)
6. Screenshot khớp HTML không?

Nếu lỗi, sửa lại HTML, chụp lại screenshot, cập nhật CSV.
```

### Kiểm tra furigana chuyên sâu

```
Kiểm tra furigana cho tất cả bài N4 trong assets/html/tim_thong_tin/n4_*.html:

1. Liệt kê tất cả <ruby> tags trong mỗi file
2. Với mỗi ruby tag, xác nhận từ đó vượt N4 (thuộc N3/N2/N1)
3. Kiểm tra có dạng "Ab" nào không (nửa kanji nửa hiragana)
4. Kiểm tra từ N5+N4 nào có kanji mà bị viết hiragana không cần thiết
5. Đếm tổng ruby tags — phải ≤ 8

Báo cáo kết quả và sửa nếu cần.
```

### Kiểm tra format diversity

```
Kiểm tra format diversity trong tất cả CSV files trong sheets/:

1. Đọc cột "tag" của mỗi file
2. Báo nếu cùng 1 file CSV có 2+ bài trùng format
3. Báo nếu cùng 1 level có quá 2 bài cùng format (across all CSV files)
4. Đề xuất format thay thế nếu cần
```

---

## 7. Bổ sung & mở rộng

### Thêm bài cho level thiếu

```
Kiểm tra tổng số bài đã gen cho mỗi level, rồi gen thêm cho level nào ít nhất.

Mục tiêu: mỗi level có ít nhất 10 bài.
- Kiểm tra format đã dùng → chọn format chưa dùng trước
- Lưu CSV mới riêng cho mỗi level
```

### Gen bài với visual elements đặc biệt

```
Gen 5 bài tìm thông tin (1 per level) với visual elements đặc biệt:

1. N1 — price_comparison_table: bảng phức tạp có rowspan/colspan + chú thích footnote
2. N2 — facility_guide: flowchart (yes/no decision boxes)
3. N3 — class_enrollment: 2×2 course grid + SVG illustration
4. N4 — event_announcement: pill labels + 【】section headers
5. N5 — store_flyer: SVG starburst shapes + promo boxes

Đọc references/design-patterns.md để biết visual elements của từng mẫu tham khảo.
```

### Gen lại bài cũ với quy tắc mới

```
Đọc tất cả bài đã gen trong assets/html/tim_thong_tin/ và kiểm tra:

1. Bài nào có furigana kiểu cũ (tất cả kanji có furigana)?
2. Bài nào thiếu format label trong CSV (cột tag)?
3. Bài nào dùng answer format cũ (| thay vì \n)?

Liệt kê danh sách cần sửa, rồi sửa lại theo quy tắc mới.
```

---

## Mẹo sử dụng prompt

1. **Luôn nói "format khác nhau"** — đây là trigger để AI chọn đa dạng format
2. **Nêu rõ level** — mỗi level có constraints khác nhau (chars, furigana, số câu hỏi)
3. **Nêu rõ "lưu CSV mới trong sheets/"** — tránh ghi đè file cũ
4. **Nếu gen nhiều, chia nhỏ** — gen 5 bài/lượt, kiểm tra rồi gen tiếp
5. **Nêu format cụ thể nếu biết** — "format: comparison_article" rõ ràng hơn "dạng so sánh"
6. **Kết hợp prompt gen + kiểm tra** — gen xong luôn chạy kiểm tra
