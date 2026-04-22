---
name: jlpt-tim-thong-tin
description: >
  Generate JLPT 情報検索 (tìm thông tin / information retrieval) reading passages as beautifully
  styled HTML files, capture screenshots, produce clean HTML, and output CSV training data.
  Skill này bao gồm TOÀN BỘ luồng: gen → QC loop (6 tiêu chí) → sửa → chụp ảnh.
  Gen từng bài một, kiểm tra đến khi đạt chất lượng mới chuyển sang bài tiếp theo.
  Use this skill whenever the user wants to: generate tìm thông tin content, create 情報検索 passages,
  batch-generate HTML reading materials, produce AI fine-tuning data for JLPT N1-N5,
  kiểm tra chất lượng, quality check, review bài, QC.
---

# JLPT 情報検索 / Tìm Thông Tin — Generator & Quality Check

> **⚠️ CẢNH BÁO DÀNH CHO GEMINI:**
> Gemini có 3 xu hướng lỗi nghiêm trọng cần đặc biệt chú ý:
> 1. **Gen khó hơn level** — bài N4 nhưng dùng từ vựng/ngữ pháp N2-N3
> 2. **Dùng ngoặc thay ruby** — `漢字(かんじ)` thay vì `<ruby>漢字<rt>かんじ</rt></ruby>` → REJECT
> 3. **Thiếu `<rt>` trong `<ruby>`** — `<ruby>漢字</ruby>` mà không có `<rt>` → VÔ NGHĨA → REJECT
>
> Đọc kỹ R3, R4 trước khi gen.

> **Nguyên tắc cốt lõi:**
> 1. **Gen từng bài một** — không batch rồi QC sau
> 2. **QC loop** — check 6 TC → FAIL → sửa → check lại → lặp đến khi PASS
> 3. **Screenshot cuối cùng** — CHỈ sau khi PASS tất cả 6 TC
> 4. **1 FAIL = REJECT** — không có ngoại lệ

## Outputs Per Passage

1. **Styled HTML** → `assets/html/tim_thong_tin/{LEVEL}_{uuid}.html`
2. **Screenshot PNG** → `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png` (container.screenshot(), viewport=700)
3. **Clean HTML** → CSV column `text_read` (giữ nguyên `<ruby>/<rt>`, strip style/script/attributes)

---

# ═══════════════════════════════════════════════
# PHẦN 1: QUY TẮC (định nghĩa 1 lần duy nhất)
# ═══════════════════════════════════════════════

## R1. Chủ đề (Topic)

### Nguyên tắc chung

- **Tính thực tế cao**: mô phỏng tình huống thực tế tại Nhật Bản (tờ rơi, thông báo, brochure...)
- **Mục đích tra cứu**: văn bản phục vụ tra cứu thông tin, KHÔNG phải đọc hiểu nghệ thuật
- **Dữ liệu cụ thể**: BẮT BUỘC có giá cả, thời gian, địa điểm, điều kiện ràng buộc
- **Công bằng**: không gây bất lợi về văn hóa, tôn giáo, giới tính; không lỗi thời

### Chủ đề phù hợp theo level

| Level | Chủ đề phù hợp | Ví dụ |
|-------|----------------|-------|
| N5 | Đời sống hàng ngày cơ bản, thông báo công cộng đơn giản | Lịch xe buýt, giờ mở cửa bể bơi, nội quy cấm hút thuốc |
| N4 | Sinh hoạt cộng đồng, dịch vụ đơn giản, lịch trình học tập | Thực đơn nhà hàng, lịch học yoga, bảng giá thuê phòng, tờ rơi khuyến mãi |
| N3 | Dịch vụ phổ biến, giải trí, du lịch, sức khỏe cơ bản | Brochure tour, quy định khách sạn, hướng dẫn gym, thông báo khu dân cư |
| N2 | Tài liệu kinh doanh, hành chính, giáo dục, y tế cơ bản | Thông báo tuyển dụng, hợp đồng thuê phòng, hướng dẫn thuốc, đào tạo chuyên môn |
| N1 | Văn bản chuyên sâu, pháp lý, tài chính, kỹ thuật phức tạp | Quy chế bảo hiểm, khai báo thuế, phân tích thị trường, hợp đồng lao động |

### Chủ đề KHÔNG đạt chuẩn (loại trừ)

- Chủ đề kể chuyện (story), tự sự, văn chương
- Nội dung thiếu dữ liệu cụ thể để tra cứu/đối chiếu
- Thiên về ý kiến cá nhân thay vì thông tin khách quan
- Sai cấp độ (hợp đồng pháp lý cho N5, tờ rơi siêu thị cho N1)
- Văn bản giả định, thiếu hơi thở đời sống thực

---

## R2. Hình thức trình bày (Format & Layout)

### Nguyên tắc cốt lõi

- **Tính quét thông tin (Scannability)**: thí sinh quét nhanh bằng mắt, KHÔNG đọc hiểu toàn bộ
- **Cấu trúc đa dạng**: kết hợp đoạn văn ngắn + **bảng biểu** + **danh sách** + **ghi chú (※)**
- **Phân tán thông tin**: thông tin trả lời KHÔNG nằm tập trung 1 chỗ → phải nằm ở **≥2 vị trí** (ví dụ: bảng giá + phần lưu ý)
- **Ký hiệu đặc trưng Nhật Bản**: BẮT BUỘC dùng ○, ×, △, ※, ★, ◆, 【】 khi phù hợp

### Đặc điểm theo level

| Level | Layout |
|-------|--------|
| N5 | Bố cục đơn giản. Bảng tối giản 2-3 cột/hàng. Tiêu đề, thời gian, địa điểm tách biệt rõ |
| N4 | Bảng 3-5 hàng, nhóm thông tin riêng biệt. Dấu hiệu phân cách 【】, ◆ |
| N3 | Bảng nhiều cột/hàng hơn (4-6 cột). Kết hợp nhiều nguồn + chú thích điều kiện phức tạp |
| N2 | Bảng phức tạp với điều kiện lồng nhau. Brochure 2-3 phần, phần "Lưu ý" dài |
| N1 | Đa bảng biểu, mật độ thông tin dày (6-8+ dòng). Tham chiếu chéo ("xem chú thích 1, 2") |

### Loại trừ (format KHÔNG đạt)

- Văn bản thuần túy (chỉ đoạn văn dài, không bảng biểu/danh sách)
- Thông tin tập trung 1 chỗ (không cần scan)
- Thiếu tính thực tế (không giống tờ rơi/thông báo thật)

### Số lượng ký tự (đếm bằng `count_body_chars()`)

| Level | Tiêu chuẩn | Ngưỡng chấp nhận | Hard Reject |
|-------|-----------|-------------------|-------------|
| N5 | ~250 | 230–280 | < 230 → gen lại |
| N4 | ~400 | 370–430 | < 370 → gen lại |
| N3 | ~600 | 560–640 | < 560 → gen lại |
| N2 | ~700 | 660–740 | < 660 → gen lại |
| N1 | ~700-800 | 660–740 | < 660 → gen lại |

```python
from html.parser import HTMLParser
import re

class BodyTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts, self.skip_depth, self.in_body = [], 0, False
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.in_body = True
        if tag in ('rt', 'style', 'script'): self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag in ('rt', 'style', 'script'): self.skip_depth -= 1
    def handle_data(self, d):
        if self.in_body and self.skip_depth == 0: self.texts.append(d)

def count_body_chars(html_string):
    ext = BodyTextExtractor()
    ext.feed(html_string)
    return len(re.sub(r'[ \t\n\r\u3000]', '', ''.join(ext.texts)))
```

### Flow Text (NGHIÊM CẤM `<br>` ngắt câu)

- Văn bản cùng đoạn → 1 thẻ `<p>`, KHÔNG `<br>` bên trong. `。<br>` → REJECT
- Chỉ ngắt khi: chuyển section, sau heading, list items, key-value, chuyển ý hoàn toàn

### Container & Capture

- Container: `width: 700px; margin: 0; padding: 12px 16px;` — KHÔNG `auto`, KHÔNG `min-height`
- Viewport Playwright = 700px. Capture bằng `container.screenshot()` (KHÔNG `page.screenshot()`)
- Table: `table-layout: fixed; width: 100%`

### Cấm che khuất chữ

- Floating label → box có `margin-top ≥ 16px`, `padding-top ≥ 24px`, label có `background-color` solid
- **Không thể hiển thị cả hình VÀ chữ rõ 100% → BỎ HÌNH, GIỮ CHỮ**

---

## R3. Trình độ kiến thức (Kanji, Từ vựng, Ngữ pháp)

> **⚠️ GEMINI ĐẶC BIỆT CHÚ Ý**: Gemini có xu hướng gen nội dung KHÓ HƠN so với level yêu cầu.
> Ví dụ: gen bài N4 nhưng dùng từ vựng/ngữ pháp N2-N3, hoặc nhồi thuật ngữ chuyên ngành vào N2/N1.
> **Độ khó đến từ CẤU TRÚC THÔNG TIN (cross-reference, ngoại lệ, điều kiện chồng chéo), KHÔNG phải từ vựng khó.**

> **NGUYÊN TẮC NỀN TẢNG**: Thí sinh KHÔNG CẦN hiểu hết 100% từ vựng vẫn có thể hoàn thành bài bằng cách tìm, đối chiếu, lọc thông tin.

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

### Hướng dẫn chi tiết per level (Gemini reference table)

> **⚠️ Gemini: PHẢI đối chiếu bảng này khi gen. Nếu bài N4 mà dùng từ/ngữ pháp trong cột N2 → REJECT.**

| Level | Từ vựng & Kanji | Ngữ pháp | Chủ đề | Ví dụ câu |
|-------|----------------|----------|--------|-----------|
| N5 | Hiragana nhiều, kanji N5 cơ bản (日月人円時) | ～です, ～ます, ～てください, ～があります | Mua sắm, giờ mở cửa, bảng giá | おみせは あさ 9じから よる 8じまでです。 |
| N4 | Kanji N5+N4, ít hiragana hơn | ～ことができます, ～なければなりません, ～てもいいです | Sự kiện, lớp học, quy tắc | 小学生以下のお子様は無料で参加できます。 |
| N3 | Kanji N5-N3 | ～について, ～による, ～場合は, ～ために | Dịch vụ, tuyển dụng, du lịch | 応募の場合は、履歴書を郵送してください。 |
| N2 | Kanji N5-N2 | ～に伴い, ～に基づき, ～を踏まえて, ～に限り | So sánh, hướng dẫn, quy trình | 本サービスは会員登録に基づき提供されます。 |
| N1 | Kanji đầy đủ N5-N1 | ～いかんによらず, ～をもって, ～に先立ち, 敬語 | Y tế, pháp luật, tài chính | 理由のいかんによらず、返金には応じかねます。 |

### N4/N5: KHÔNG dùng kanji vượt level

Các kanji 当, 届, 締, 割, 欄 là N3+ → KHÔNG xuất hiện trong bài N4/N5 (kể cả có furigana). Viết hiragana thay thế.

### Nguồn tạo độ khó ĐÚNG CÁCH

| Level | Nguồn khó ĐÚNG | Nguồn khó SAI |
|-------|----------------|---------------|
| N5 | Thông tin rải ở nhiều vị trí trong bài | Dùng kanji khó, từ N3+ |
| N4 | 2 điều kiện cần kết hợp, ghi chú nhỏ | Ngữ pháp N2, từ vựng formal |
| N3 | Bảng nhiều cột + điều kiện phụ trong văn xuôi | Thuật ngữ chuyên ngành N1 |
| N2 | Cross-reference bảng + văn xuôi, nhiều ngoại lệ | Nhồi thuật ngữ pháp lý/y tế |
| N1 | 3+ điều kiện chồng chéo, footnote, ngoại lệ ẩn | Từ hiếm không ai dùng, keigo cực đoan |

### Red flags (cần kiểm tra lại)

- Từ then chốt vượt level (thí sinh không trả lời được vì không biết từ khó)
- Thuật ngữ ngành ở vị trí nổi bật (tiêu đề, tên khóa) mà không furigana/giải thích
- Từ ghép Hán-Nhật hiếm gặp là chìa khóa chọn đáp án

---

## R4. Furigana

> **⚠️ GEMINI: 3 LỖI NGHIÊM TRỌNG HAY GẶP:**
>
> **LỖI 1 — Dùng ngoặc thay ruby tag:**
> - `拠点(きょてん)` → **REJECT** (phải dùng `<ruby>拠点<rt>きょてん</rt></ruby>`)
> - `集荷（しゅうか）` → **REJECT**
> - `漢字【かんじ】` → **REJECT**
> **🚫 HARD REJECT — Phát hiện furigana dạng ngoặc `()` hoặc `【】` → bài PHẢI gen lại từ đầu.**
>
> **LỖI 2 — Thiếu `<rt>` trong `<ruby>`:**
> - `<ruby>拠点</ruby>` → **VÔ NGHĨA** (không có reading) → **REJECT**
> - PHẢI có CẢ HAI: `<ruby>` VÀ `<rt>` bên trong
>
> **LỖI 3 — Furigana toàn bộ kanji:**
> - Rắc furigana lên MỌI kanji kể cả từ đúng level → **REJECT nếu ruby count vượt ngưỡng**

### Core Rule — CHỈ cho từ ngữ cảnh vượt level

> **🚫 LỖI PHỔ BIẾN NHẤT: AI rắc furigana lên MỌI kanji.**
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
- SAI → REJECT: `<ruby>漢字</ruby>` (thiếu `<rt>`)

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

### Danh sách từ KHÔNG cần furigana (AI hay nhầm)

| Level | Từ KHÔNG cần furigana (đúng level hoặc dưới) |
|-------|----------------------------------------------|
| N5 | 日, 月, 人, 円, 大, 小, 時, 年, 何, 前, 後, 店, 上, 下, 中, 外 |
| N4 | 場所, 仕事, 電話, 大丈夫, 手紙, 先生, 買う, 使う, 教える, 名前, 方, 時間, 市, 町, 村, 写真, 必要 |
| N3 | 最近, 生活, 機会, 質問, 内容, 基本, 簡単, 教室, 文書, 作成, 地域, 説明, 練習, 経験, 予約, 申し込み |
| N2 | 受付, 締切, 割引, 対象, 詳細, 申込, 制度, 条件, 届出, 規定, 設備, 施設, 担当, 了承, 開催 |
| N1 | Hầu hết kanji thông thường — chỉ furigana cho thuật ngữ chuyên ngành hiếm |

### Danh sách từ thường vượt level — HAY BỊ QUÊN furigana

| Trong bài N3 (cần furigana) | Trong bài N2 (cần furigana) | Trong bài N1 (cần furigana) |
|------------------------------|-----------------------------|-----------------------------|
| `<ruby>締切<rt>しめきり</rt></ruby>` (N2) | `<ruby>概要<rt>がいよう</rt></ruby>` (N1) | `<ruby>遵守<rt>じゅんしゅ</rt></ruby>` (ngoài JLPT) |
| `<ruby>受付<rt>うけつけ</rt></ruby>` (N2) | `<ruby>控除<rt>こうじょ</rt></ruby>` (N1) | `<ruby>瑕疵<rt>かし</rt></ruby>` (ngoài JLPT) |
| `<ruby>割引<rt>わりびき</rt></ruby>` (N2) | `<ruby>還付<rt>かんぷ</rt></ruby>` (N1) | `<ruby>斡旋<rt>あっせん</rt></ruby>` (ngoài JLPT) |
| `<ruby>申込<rt>もうしこみ</rt></ruby>` (N2) | `<ruby>免責<rt>めんせき</rt></ruby>` (N1) | `<ruby>拠点<rt>きょてん</rt></ruby>` (N1 hiếm) |
| `<ruby>対象<rt>たいしょう</rt></ruby>` (N2) | `<ruby>規約<rt>きやく</rt></ruby>` (N1) | `<ruby>稀<rt>まれ</rt></ruby>` (ngoài JLPT) |
| `<ruby>詳細<rt>しょうさい</rt></ruby>` (N2) | `<ruby>併用<rt>へいよう</rt></ruby>` (N1) | `<ruby>滞納<rt>たいのう</rt></ruby>` (ngoài JLPT) |
| `<ruby>持参<rt>じさん</rt></ruby>` (N2) | `<ruby>添付<rt>てんぷ</rt></ruby>` (N1) | `<ruby>譲渡<rt>じょうと</rt></ruby>` (ngoài JLPT) |
| `<ruby>掲載<rt>けいさい</rt></ruby>` (N1) | `<ruby>履歴<rt>りれき</rt></ruby>` (N1) | `<ruby>充填<rt>じゅうてん</rt></ruby>` (ngoài JLPT) |

---

## R5. Câu hỏi đọc hiểu

### Nguyên tắc cốt lõi

- **100% căn cứ vào văn bản**: đáp án xác nhận rõ ràng bởi thông tin trong bài. KHÔNG dựa kiến thức ngoài
- **Đọc chéo (Cross-reading)**: câu hỏi PHẢI buộc kết hợp thông tin từ **≥2 phần khác nhau** (bảng + lưu ý, bảng + văn xuôi...). Đáp án tìm thấy trong 1 câu duy nhất = KHÔNG ĐẠT
- **Tình huống cụ thể**: nhân vật có **tên thật** + profile + điều kiện ràng buộc

### Yêu cầu nhận thức theo level

| Level | Dạng câu hỏi | Yêu cầu nhận thức |
|-------|-------------|-------------------|
| N5 | Tìm 1 thông tin trực tiếp | Tra cứu đúng ô/dòng với 1 điều kiện đơn giản |
| N4 | Kết hợp 2 nguồn thông tin | Tính toán cộng/trừ đơn giản, so sánh 2 dòng |
| N3 | Kết hợp thông tin + quy tắc | Xử lý 3+ điều kiện, tính %, kết hợp bảng + chú thích |
| N2 | Điều kiện lồng nhau & mapping | Xác định trường hợp áp dụng, xử lý ngoại lệ "nếu... thì" |
| N1 | Lọc thông tin mâu thuẫn & suy luận | Nhiều ngoại lệ tinh tế, thuật ngữ chuyên môn, điều kiện phức tạp |

### Số lượng & tên nhân vật

| Level | Questions | Nhân vật |
|-------|-----------|----------|
| N1-N4 | 2 (Q1, Q2) | Tên thật, Q1 ≠ Q2 nhân vật khác nhau |
| N5 | 1 (Q1 only) | Tên thật |

- SAI: Aさん, Bさん, 人A → REJECT
- ĐÚNG: 田中さん, 佐藤さん, リンさん, マリアさん

### 8 kiểu câu hỏi — Q1 và Q2 PHẢI khác kiểu

| # | Kiểu | Level |
|---|------|-------|
| 1 | Chọn phương án phù hợp | All |
| 2 | Kiểm tra tư cách/điều kiện | N3-N1 |
| 3 | Xác định thủ tục/trình tự | N3-N1 |
| 4 | Tính toán chi phí/thời gian | N4-N1 |
| 5 | Xác định đúng/sai về nội dung | All |
| 6 | Tìm ngoại lệ/điều kiện đặc biệt | N2-N1 |
| 7 | So sánh và chọn | N3-N1 |
| 8 | Hành động khi có vấn đề | N4-N1 |

### Paraphrasing (N3 trở lên)

Câu hỏi và đáp án KHÔNG copy nguyên văn → dùng **từ đồng nghĩa hoặc cách diễn đạt tương đương**. Từ dùng để paraphrase cũng phải đúng level thí sinh.

### Nhất quán thì động từ

Câu hỏi + 4 lựa chọn phải **thống nhất thì** (ưu tiên thì hiện tại).

---

## R6. Lựa chọn đáp án (Options)

### Nguyên tắc

- **Đáp án đúng**: xác nhận rõ bởi thông tin trong bài, paraphrase (N3+)
- **Đáp án sai (distractor)**: có thể bác bỏ dựa trên dữ liệu trong bài. **NGHIÊM CẤM bịa thông tin**
- **Duy nhất 1 đáp án đúng tuyệt đối**
- **Độ dài tương đương**: các lựa chọn phải cùng độ dài. 1 đáp án quá dài/ngắn = lộ
- **Từ vựng trong đáp án ≤ level thí sinh**

### 4 loại bẫy chuẩn (distractor types)

| Loại bẫy | Mô tả | Ví dụ |
|-----------|--------|-------|
| **Bẫy điều kiện (※)** | Đúng số liệu nhưng sai điều kiện áp dụng | Nhầm ngày, nhầm đối tượng, bỏ qua lưu ý |
| **Bẫy tính toán** | Kết quả phép tính sai | Quên giảm giá, nhầm %, tính nhầm giờ |
| **Bẫy thông tin nhiễu** | Dữ liệu có trong bài nhưng thuộc đối tượng khác | Giá vé người lớn cho câu hỏi trẻ em |
| **Bẫy đọc nhầm** | Nhầm mục hoặc dòng tương tự trong bảng | Nhầm cột A và cột B cùng bảng |

> Mỗi bài nên có **ít nhất 2 bẫy "chất lượng"** (bẫy điều kiện hoặc tính toán).

### Loại trừ

- Bịa thông tin không có trong bài
- Sai hiển nhiên (loại ngay không cần đọc bài)
- 3 đáp án tích cực + 1 phủ định rõ ràng
- **Test che bài**: che bài, nhìn 4 đáp án → đoán được = FAIL

---

## R7. Document Formats (15 formats)

> **KHÔNG lặp format** trong batch. **Ưu tiên format ít dùng**. Visual elements + chủ đề phải khác nhau.

| Format | Description |
|--------|-------------|
| `price_comparison_table` | So sánh plans/services với giá |
| `event_announcement` | Sự kiện: ngày/giờ/phí/quy tắc |
| `facility_guide` | Cơ sở vật chất: giờ/phí/quy tắc |
| `class_enrollment` | Khóa học: lịch/phí/số lượng |
| `service_guide` | Dịch vụ: quy trình/điều kiện/giá |
| `schedule_timetable` | Bảng thời gian ○/× |
| `recruitment_notice` | Tuyển dụng/tình nguyện + điều kiện |
| `store_flyer` | Khuyến mãi: sản phẩm/giá/thời hạn |
| `menu_guide` | Thực đơn nhà hàng |
| `travel_listing` | Tour: điểm đến/ngày/giá |
| `medicine_info` | Thuốc: liều/thời gian/cảnh báo |
| `regulation_notice` | Quy tắc/hướng dẫn thủ tục |
| `comparison_article` | So sánh văn xuôi A/B/C |
| `member_notification` | Thông báo hội viên |
| `access_guide` | Hướng dẫn đường đi |

### Formats theo level

- **N5**: store_flyer, event_announcement, regulation_notice, schedule_timetable, travel_listing, access_guide
- **N4**: event_announcement, class_enrollment, regulation_notice, menu_guide, price_comparison_table, service_guide
- **N3**: class_enrollment, service_guide, event_announcement, facility_guide, travel_listing, price_comparison_table, recruitment_notice, menu_guide
- **N2**: facility_guide, service_guide, comparison_article, event_announcement, class_enrollment, schedule_timetable, menu_guide
- **N1**: price_comparison_table, service_guide, facility_guide, schedule_timetable, medicine_info, recruitment_notice, member_notification, event_announcement

---

## R8. Visual Elements

- **Tables**: bordered, gray header. **Ký hiệu**: ○ (Được), × (Không), △ (Có điều kiện)
- **Pill labels**: `border-radius: 9999px`
- **【】sections**: bracket headers
- **Content boxes**: floating label (padding-top ≥ 24px, margin-top ≥ 16px)
- **Ghi chú**: ※ (Lưu ý quan trọng), ★, ◆, ◎
- **Dashed contact box**, **Footer** với border-top

---

## R9. HTML Template

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Title]</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
        body { font-family: 'Noto Sans JP', sans-serif; background: #fff; color: #000; line-height: 2; word-break: keep-all; line-break: strict; overflow-wrap: break-word; margin: 0; padding: 0; }
        .container { width: 700px; margin: 0; background: white; padding: 12px 16px; box-sizing: border-box; }
        table { width: 100%; table-layout: fixed; }
        td, th { overflow-wrap: break-word; }
        .container > * { max-width: 100%; }
        ruby { ruby-align: center; ruby-position: over; vertical-align: baseline; }
        ruby rt { font-size: 0.55em; color: #333; letter-spacing: 0.02em; line-height: 1; vertical-align: top; }
    </style>
</head>
<body>
<div class="container">
    <!-- content -->
</div>
</body>
</html>
```

---

## R10. Clean HTML & Screenshot

### Clean HTML (`text_read`)

```python
class CleanHTMLExtractor(HTMLParser):
    SKIP_TAGS = ('style', 'script')   # ruby, rt được GIỮ NGUYÊN
    def __init__(self):
        super().__init__()
        self.result, self.skip_depth = [], 0
        self.in_body, self.body_done = False, False
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.in_body = True; return
        if not self.in_body or self.body_done: return
        if tag in self.SKIP_TAGS: self.skip_depth += 1; return
        if self.skip_depth > 0: return
        self.result.append(f'<{tag}>')
    def handle_endtag(self, tag):
        if tag == 'body': self.body_done = True; return
        if not self.in_body or self.body_done: return
        if tag in self.SKIP_TAGS: self.skip_depth -= 1; return
        if self.skip_depth > 0: return
        self.result.append(f'</{tag}>')
    def handle_data(self, data):
        if not self.in_body or self.body_done or self.skip_depth > 0: return
        self.result.append(data)

def clean_html(full_html):
    ext = CleanHTMLExtractor()
    ext.feed(full_html)
    raw = ''.join(ext.result)
    raw = re.sub(r'\s+', ' ', raw)
    raw = re.sub(r'\s*<', '<', raw)
    raw = re.sub(r'>\s*', '>', raw)
    raw = re.sub(r'<(\w+)></\1>', '', raw)
    return raw.strip()
```

### Screenshot (PHẢI crop sát — không thừa khoảng trắng)

> **⛔ NGHIÊM CẤM ảnh thừa khoảng trắng / viền xám xung quanh.**
> Dùng `bounding_box()` + `page.screenshot(clip=...)` để crop chính xác pixel.
> KHÔNG dùng `container.screenshot()` vì có thể bao gồm body background.

```python
async def capture_screenshot(html_path, img_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 700, "height": 800})
        await page.goto(f"file://{html_path}", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        container = page.locator('.container')
        box = await container.bounding_box()
        await page.screenshot(path=img_path, clip={
            "x": box["x"],
            "y": box["y"],
            "width": box["width"],
            "height": box["height"]
        })
        await page.close()
        await browser.close()
```

---

## R11. CSV Schema & File Naming

45 columns matching `input/question_sheet.csv`:

| Column | Value |
|--------|-------|
| `_id` | `{LEVEL}_{uuid.uuid4().hex}` |
| `level` | N1-N5 |
| `tag` | Format label |
| `jp_char_count` | `count_body_chars()` |
| `kind` | `tìm thông tin` |
| `general_image` | `assets/img/tim_thong_tin/{id}.png` |
| `text_read` | Clean HTML (giữ ruby/rt) |
| `question_label_{i}` | `question_information_search` |
| `question_{i}` | Question text |
| `answer_{i}` | 4 options `\n` separated, KHÔNG số thứ tự |
| `correct_answer_{i}` | Integer `1`-`4` (KHÔNG `2.0`) |
| `explain_vn_{i}` / `explain_en_{i}` | Explanations |

---

# ═══════════════════════════════════════════════
# PHẦN 2: LUỒNG THỰC HIỆN (end-to-end)
# ═══════════════════════════════════════════════

## BƯỚC 0: CHUẨN BỊ (1 lần cho batch)

1. Scan format đã dùng → chọn format chưa/ít dùng
2. Lập kế hoạch: mỗi bài gán format + visual + chủ đề (không trùng)
3. Read references: 1-2 HTML mẫu + 1 QA mẫu cho level cần gen

## BƯỚC 1–6: LẶP CHO TỪNG BÀI

### BƯỚC 1: GEN HTML
1. Gen ID → gen HTML theo R1-R9
2. `count_body_chars()` → < Hard Reject → gen lại
3. Save HTML

### BƯỚC 2: FURIGANA VERIFICATION (BLOCKING)

> **⚠️ GEMINI: Sau khi gen HTML, BẮT BUỘC kiểm tra:**
> 1. Có bất kỳ furigana nào dùng ngoặc `()` hoặc `【】` không? → gen lại
> 2. Có `<ruby>` nào thiếu `<rt>` không? → sửa ngay
> 3. Có furigana cho từ đúng level không? → xóa bớt

1. Scan kanji → check level từng từ
2. Key terms đúng level → KHÔNG furigana
3. Context words vượt level → PHẢI có `<ruby>+<rt>`
4. Đếm ruby count → vượt ngưỡng R4 → đang furigana thừa, xóa bớt

### BƯỚC 3: GEN CÂU HỎI + ĐÁP ÁN
1. Gen theo R5-R6 (tình huống, cross-reference, 4 loại bẫy)
2. Kiểm tra: thông tin trả lời phân tán ≥2 vị trí?
3. Kiểm tra: đáp án tương đương độ dài? Thì động từ nhất quán?
4. Extract clean HTML → fill CSV

### BƯỚC 4: QC PHẦN A — HTML (TC1-TC5)

| TC | Tiêu chí | FAIL nếu |
|----|----------|----------|
| TC1 | Ký tự | Ngoài ngưỡng chấp nhận (R2) |
| TC2 | Chủ đề & Format | Chủ đề sai level, nội dung phi logic, thiếu dữ liệu tra cứu, thông tin tập trung 1 chỗ |
| TC3 | Layout | `。<br>`, container sai, thiếu bảng biểu/ký hiệu |
| TC4 | Từ vựng & NP | Key terms vượt level, ngữ pháp sai level, thuật ngữ ở vị trí nổi bật không giải thích |
| TC5 | Furigana | Sót furigana context words, thừa furigana key terms, ruby count vượt ngưỡng, format sai (ngoặc/thiếu rt) |

### BƯỚC 5: QC PHẦN B — CÂU HỎI (TC6)

> **AI HAY BỎ QUÊN. Check TC1-TC5 xong CHƯA PHẢI LÀ XONG.**

| TC | Tiêu chí | FAIL nếu |
|----|----------|----------|
| TC6a | Tình huống | Q thiếu nhân vật tên thật + profile + điều kiện |
| TC6b | Cross-reference | Đáp án tìm được trong 1 câu/1 chỗ duy nhất (không cần scan) |
| TC6c | Kiểu hỏi | Q1 = Q2 cùng kiểu |
| TC6d | Đáp án đúng | Copy nguyên văn (N3+), không paraphrase |
| TC6e | Distractor | Bịa thông tin, sai hiển nhiên, thiếu bẫy chất lượng |
| TC6f | Test che bài | Che bài, nhìn 4 đáp án → đoán được |
| TC6g | Hình thức | correct_answer ≠ integer; đáp án không đều độ dài; thì không nhất quán |

> **CHECKPOINT**: "Tôi đã đọc question + answer từ CSV chưa?" Chưa = QC chưa xong.

### BƯỚC 5b: SỬA → QUAY LẠI BƯỚC 4

| FAIL | Hành động |
|------|-----------|
| TC1/TC2/TC4 | Gen lại toàn bộ HTML |
| TC3 | Sửa HTML (bỏ `<br>`, fix CSS) |
| TC5 | Sửa ruby tags |
| TC6 | Sửa câu hỏi/đáp án → cập nhật CSV |

### BƯỚC 6: CHỤP ẢNH (CHỈ SAU KHI PASS)
1. `bounding_box()` + `page.screenshot(clip=box)` — crop sát container, KHÔNG thừa khoảng trắng
2. Save PNG. **Không sửa HTML sau khi chụp.**

## BƯỚC 7: LẶP LẠI → bài tiếp theo

---

# ═══════════════════════════════════════════════
# PHẦN 3: TÀI LIỆU THAM KHẢO
# ═══════════════════════════════════════════════

## Reference Samples

- Passage HTML (61 files): `input/html/` — N1(14), N2(12), N3(15), N4(10), N5(10)
- QA references (20 files): `input/htm_content_qa/` — 4 per level
- Teacher rules: `input/rule_gen_tim_thong_tin.md`

Read 2-3 passage refs + 1 QA ref + teacher rules trước khi gen.

## Bundled Scripts

```bash
python3 <skill>/scripts/process_html.py --count-only --file <html-file>
python3 <skill>/scripts/process_html.py --file <html-file> --img-dir assets/img/tim_thong_tin --csv sheets/<file>.csv
```

## QC Automation Scripts

```python
import re
from pathlib import Path

def check_html(html_path: str, level: str) -> dict:
    """Kiểm tra tự động các tiêu chí đo được."""
    html = Path(html_path).read_text(encoding='utf-8')
    results = {}
    
    # TC1: Character count
    char_count = count_body_chars(html)
    min_chars = {"N1": 660, "N2": 660, "N3": 560, "N4": 370, "N5": 230}
    results["TC1_chars"] = {
        "count": char_count, "min": min_chars[level],
        "pass": char_count >= min_chars[level]
    }
    
    # TC3a: Flow text
    br_in_prose = len(re.findall(r'。\s*<br\s*/?>', html))
    results["TC3_flow_text"] = {"br_in_prose": br_in_prose, "pass": br_in_prose == 0}
    
    # TC3b: Container CSS
    has_margin_auto = bool(re.search(r'margin:\s*0\s+auto', html))
    has_min_height = bool(re.search(r'min-height', html))
    results["TC3_container"] = {"pass": not has_margin_auto and not has_min_height}
    
    # TC5a: Ruby count
    ruby_count = len(re.findall(r'<ruby>', html))
    results["TC5_ruby_count"] = {"count": ruby_count}
    
    # TC5b: Wrong furigana format (GEMINI SPECIFIC — check parentheses)
    paren_furigana = re.findall(r'[\u4e00-\u9fff]+[（(][ぁ-ん]+[）)]', html)
    bracket_furigana = re.findall(r'[\u4e00-\u9fff]+【[ぁ-ん]+】', html)
    results["TC5_furigana_format"] = {
        "paren_found": paren_furigana,
        "bracket_found": bracket_furigana,
        "pass": len(paren_furigana) == 0 and len(bracket_furigana) == 0
    }
    
    # TC5c: Ruby without rt (GEMINI SPECIFIC)
    ruby_without_rt = re.findall(r'<ruby>[^<]*</ruby>(?!.*<rt>)', html)
    results["TC5_ruby_has_rt"] = {
        "missing_rt": ruby_without_rt,
        "pass": len(ruby_without_rt) == 0
    }
    
    return results
```
