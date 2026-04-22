# Rules: Từ vựng, Ngữ pháp & Furigana (R3, R4)

## R3. Trình độ kiến thức (Kanji, Từ vựng, Ngữ pháp)

> **NGUYÊN TẮC NỀN TẢNG**: Thí sinh KHÔNG CẦN hiểu hết 100% từ vựng vẫn có thể hoàn thành bài bằng cách tìm, đối chiếu, lọc thông tin.
> **Độ khó đến từ CẤU TRÚC THÔNG TIN (cross-reference, ngoại lệ, điều kiện chồng chéo), KHÔNG phải từ vựng khó.**

### Phân loại từ vựng theo rủi ro (QUAN TRỌNG NHẤT)

| Loại | Định nghĩa | Quy tắc level | Furigana |
|------|-----------|----------------|----------|
| **Từ then chốt (Key terms)** | Từ thí sinh BẮT BUỘC hiểu để chọn đáp án đúng | **PHẢI ≤ level mục tiêu** | KHÔNG furigana |
| **Từ ngữ cảnh (Context)** | Xuất hiện trong bài nhưng không liên quan trực tiếp đến câu hỏi | Có thể > level | Kèm furigana |
| **Thuật ngữ chuyên ngành (Jargon)** | Thuật ngữ chuyên môn | Chỉ dùng nếu KHÔNG liên quan đến câu hỏi, hoặc paraphrase trong chú thích | Furigana + chú thích |

> **Hệ quả trực tiếp**: Vì key terms phải đúng level (không furigana) và chỉ context words mới vượt level (có furigana) → **số lượng furigana phải THẤP** (chỉ ~10-20% từ trong bài).

### Tiêu chuẩn chi tiết theo level

| Level | Kanji | Từ vựng | Ngữ pháp |
|-------|-------|---------|----------|
| N5 | Chỉ kanji N5 (số, ngày, giờ: 月, 火, 円...) hoặc viết hiragana | Từ đời sống cơ bản. 100% key terms thuộc N5 | ～です/ます, ～てください, ～できます |
| N4 | Kanji N4 trở xuống (利用, 予約, 料金...) | Từ dịch vụ/cộng đồng. Cho phép vài từ N3 nhẹ nếu đoán được từ ngữ cảnh | ～たら, ～ば, ～場合は, ～てもいい |
| N3 | Kanji N3 (割引, 申込, 催行...). Bắt đầu từ ghép Hán tự | Tour, y tế cơ bản. Có thể trộn từ N2 nếu có furigana | ～に限り, ～に伴い, ～させていただきます |
| N2 | Kanji N2 (処方箋, 厳禁...). Thuật ngữ chuyên môn nhẹ + keigo | Kinh doanh, hành chính, hợp đồng. Văn phong trang trọng | ～に基づき, ～を除き, ～ようがない |
| N1 | Không giới hạn. Kanji hiếm nên có furigana | Từ chuyên sâu (禁忌, 免責, 効能...). Đoán từ dựa ngữ cảnh | ～ものとする, ～を踏まえ, ～に即して |

### N4/N5: KHÔNG dùng kanji vượt level

Các kanji 当, 届, 締, 割, 欄 là N3+ → KHÔNG xuất hiện trong bài N4/N5 (kể cả có furigana). Viết hiragana thay thế.

### Red flags (cần kiểm tra lại)

- Từ then chốt vượt level (thí sinh không trả lời được vì không biết từ khó)
- Thuật ngữ ngành ở vị trí nổi bật (tiêu đề, tên khóa) mà không furigana/giải thích
- Từ ghép Hán-Nhật hiếm gặp là chìa khóa chọn đáp án

---

## R4. Furigana

### Core Rule — CHỈ cho từ ngữ cảnh vượt level

> **LỖI PHỔ BIẾN NHẤT: AI rắc furigana lên MỌI kanji.**
> Key terms đúng level → KHÔNG furigana. Chỉ context words vượt level → furigana.

| Loại từ | Furigana? |
|---------|-----------|
| Key terms (≤ level) | KHÔNG — người học đã biết |
| Context words (> level) | CÓ — `<ruby>+<rt>` |
| Jargon (> level, không liên quan câu hỏi) | CÓ — `<ruby>+<rt>` + chú thích nếu cần |

### Ruby count hợp lý

| Level | Ruby count | Vượt mức → đang furigana thừa |
|-------|-----------|-------------------------------|
| N5 | **0–3** | > 5 |
| N4 | **0–5** | > 8 |
| N3 | **5–15** | > 20 |
| N2 | **5–15** | > 20 |
| N1 | **3–10** | > 15 |

### Format — Chỉ `<ruby>+<rt>`

- ĐÚNG: `<ruby>漢字<rt>かんじ</rt></ruby>`
- SAI → REJECT: `漢字(かんじ)`
- SAI → REJECT: `漢字【かんじ】`
- SAI → REJECT: `拠てん` (dạng "Ab")

### Compound Word Rule

Từ vượt level → chọn 1 trong 2:
1. Full kanji + furigana: `<ruby>週間<rt>しゅうかん</rt></ruby>`
2. Full hiragana: `しゅうかん`

**NEVER** dạng "Ab" hỗn hợp (週かん, 友だち).

Okurigana ngoại lệ: `<ruby>届<rt>とど</rt></ruby>く` (kanji stem + okurigana riêng).

### N5/N4: Ưu tiên thay thế trước furigana

1. Thay bằng từ cùng level (届く→来る)
2. Viết full hiragana (おおもり)
3. Furigana — chỉ khi không thể thay

### Ví dụ N3

**SAI (111 ruby tags — furigana toàn bộ):**
```html
<ruby>最近<rt>さいきん</rt></ruby>は、<ruby>仕事<rt>しごと</rt></ruby>や<ruby>生活<rt>せいかつ</rt></ruby>で...
```
→ 最近(N3), 仕事(N4), 生活(N3) đều ≤ N3 → KHÔNG furigana

**ĐÚNG (~12 ruby tags — chỉ context words vượt N3):**
```html
最近は、仕事や生活で...
<ruby>経験豊富<rt>けいけんほうふ</rt></ruby>な<ruby>講師<rt>こうし</rt></ruby>が<ruby>丁寧<rt>ていねい</rt></ruby>にお教えします。
```
