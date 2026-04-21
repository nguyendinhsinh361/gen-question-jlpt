---
name: jlpt-quality-check
description: >
  Kiểm tra chất lượng toàn diện các bài đọc JLPT 情報検索 (tìm thông tin) đã gen.
  Đánh giá 6 tiêu chí: ký tự, chủ đề & format, đoạn văn & layout, từ vựng & ngữ pháp, 
  furigana, và chất lượng câu hỏi & lựa chọn.
  Trigger: kiểm tra chất lượng, quality check, review bài, đánh giá bài, check bài đã gen,
  QC, quality review, kiểm tra bài tìm thông tin.
---

# JLPT 情報検索 — Quality Check (Kiểm Tra Chất Lượng)

Skill này kiểm tra chất lượng toàn diện các bài đọc JLPT tìm thông tin đã gen. Mỗi bài được đánh giá trên 6 tiêu chí, cho điểm PASS/FAIL từng tiêu chí và kết luận PASS/REJECT tổng thể.

> **Nguyên tắc: 1 FAIL = REJECT cả bài.** Không có ngoại lệ, không có "gần đạt".

## Đầu vào

Skill nhận 1 trong 3 dạng:

1. **File CSV** — kiểm tra tất cả bài trong CSV (đọc HTML tương ứng)
2. **Thư mục HTML** — kiểm tra tất cả file `.html` trong thư mục
3. **Bài đơn lẻ** — kiểm tra 1 file HTML cụ thể + dòng CSV tương ứng

Đường dẫn mặc định:
- HTML: `assets/html/tim_thong_tin/`
- CSV: `sheets/` (file mới nhất)
- Mẫu tham khảo: `input/html/` và `input/htm_content_qa/`

## 6 Tiêu Chí Đánh Giá

---

### 1. SỐ LƯỢNG KÝ TỰ (Character Count)

Đếm ký tự bằng đúng hàm `count_body_chars()` trong SKILL.md chính.

| Level | Target Range | FAIL nếu |
|-------|-------------|----------|
| N1 | 700–800 | < 700 |
| N2 | 700–770 | < 700 |
| N3 | 600–750 | < 600 |
| N4 | 400–500 | < 400 |
| N5 | 250–290 | < 250 |

```python
from html.parser import HTMLParser
import re

class BodyTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._pieces = []
        self._skip = False
        self._in_body = False
    def handle_starttag(self, tag, attrs):
        if tag == "body": self._in_body = True
        if tag in ("rt", "style", "script"): self._skip = True
    def handle_endtag(self, tag):
        if tag in ("rt", "style", "script"): self._skip = False
    def handle_data(self, data):
        if self._in_body and not self._skip:
            self._pieces.append(data)
    def get_text(self):
        return "".join(self._pieces)

def count_body_chars(html_string: str) -> int:
    ext = BodyTextExtractor()
    ext.feed(html_string)
    raw = ext.get_text()
    raw = re.sub(r'\s+', '', raw)
    return len(raw.strip())
```

**Kiểm tra:**
- Đọc HTML → chạy `count_body_chars()` → so sánh với minimum
- `< minimum` → **FAIL** (REJECT — phải gen lại)
- Ghi nhận số chars thực tế

---

### 2. CHỦ ĐỀ & FORMAT (Topic & Format Appropriateness)

Kiểm tra nội dung có phù hợp với level JLPT và format đã chọn không.

**2a. Chủ đề phù hợp level:**

| Level | Chủ đề phù hợp | Chủ đề KHÔNG phù hợp |
|-------|----------------|----------------------|
| N5 | Mua sắm, ăn uống, lịch đơn giản, quy tắc cơ bản | Hợp đồng, bảo hiểm, y tế chuyên sâu |
| N4 | Sự kiện, lớp học, quy tắc khu phố, thực đơn | Luật pháp, tài chính doanh nghiệp |
| N3 | Dịch vụ, tuyển dụng, du lịch, thư viện/hồ bơi | Quy định y tế phức tạp, hợp đồng pháp lý |
| N2 | So sánh dịch vụ, hội thảo, cơ sở vật chất formal | Không hạn chế nhiều, nhưng từ vựng phải phù hợp |
| N1 | Y tế, bảo hiểm, pháp lý, tài chính, dịch vụ phức tạp | Không hạn chế |

- ❌ Bài N5 về bảo hiểm y tế → **FAIL**
- ❌ Bài N4 về quy trình ứng tuyển với 5+ điều kiện phức tạp → **FAIL**
- ✅ Bài N5 về tờ rơi siêu thị giảm giá → PASS

**2b. Format phù hợp level:**

Tham chiếu bảng "Per-Level Format Distribution" trong SKILL.md chính. Nếu bài dùng format không nằm trong danh sách level đó → cảnh báo (warning, không tự động FAIL nhưng cần review).

**2c. Nội dung logic và thực tế:**

- ❌ Giá quá vô lý (cốc cà phê 50,000円, vé xe bus 1円) → **FAIL**
- ❌ Thời gian mâu thuẫn (đăng ký trước ngày 5 nhưng sự kiện ngày 3) → **FAIL**
- ❌ Điều kiện tự mâu thuẫn → **FAIL**
- ❌ Thông tin không thực tế (bể bơi mở 24/7) → **FAIL**
- ❌ Ngữ cảnh không phù hợp format (tờ rơi siêu thị viết như hợp đồng pháp lý) → **FAIL**

---

### 3. ĐOẠN VĂN & LAYOUT (Format & Layout Quality)

**3a. Flow text (QUAN TRỌNG NHẤT):**
- Văn xuôi phải nằm trong `<p>` liên tục, KHÔNG có `<br>` ngắt dòng giữa câu
- ❌ Mỗi câu 1 dòng riêng → **FAIL**
- ✅ Text chảy liên tục, tự wrap

**Cách kiểm tra:** Tìm `<br>` trong HTML → nếu nằm giữa 2 câu tiếng Nhật (。<br>) → FAIL

**3b. Container & viewport:**
- Container: `width: 700px`, `margin: 0`, `padding: 12px 16px`
- ❌ `margin: 0 auto` → warning (có thể gây thừa khoảng trắng)
- ❌ `min-height` → warning

**3c. Bảng & box:**
- Table phải có `table-layout: fixed; width: 100%`
- Content box có floating label → `padding-top ≥ 20px` và `margin-top ≥ 16px`
- ❌ Table/box bị cắt mép phải → **FAIL**

**3d. Screenshot (nếu có):**
- ❌ Khoảng trắng lớn 2 bên hoặc phía dưới → **FAIL**
- ❌ Chữ bị che bởi label/box → **FAIL**

---

### 4. TỪ VỰNG & NGỮ PHÁP (Vocabulary & Grammar)

**4a. Tỉ lệ từ vựng (≥80% đúng level):**

Kiểm tra bằng cách đọc bài, ước lượng tỉ lệ từ vựng thuộc level mục tiêu hoặc thấp hơn.

- ≥80% từ thuộc level mục tiêu hoặc dưới → PASS
- <80% → **FAIL** (nhồi thuật ngữ)

**4b. Từ vượt level — dùng level gần nhất:**

| Bài level | Từ vượt level nên thuộc | KHÔNG nên dùng |
|-----------|------------------------|----------------|
| N5 | N4 | N3+ |
| N4 | N3 | N2+ |
| N3 | N2 | N1 (trừ khi không thể thay) |
| N2 | N1 thông dụng | Thuật ngữ hiếm |
| N1 | N1 đầy đủ | Thuật ngữ cực hiếm ngoài JLPT |

- ❌ Bài N3 nhảy thẳng lên dùng thuật ngữ N1 hiếm → **FAIL**
- ❌ Bài N4/N5 dùng kanji N3+ (当, 届, 締, 割, 欄) → **FAIL**

**4c. Nguồn tạo độ khó:**

Độ khó phải đến từ CẤU TRÚC THÔNG TIN (cross-reference, ngoại lệ, điều kiện chồng chéo), KHÔNG phải từ nhồi thuật ngữ chuyên ngành.

- ❌ Bài N2 về gym dùng "施設利用規約に基づく減免措置" → **FAIL** (quá formal, nhồi thuật ngữ)
- ✅ Bài N2 về gym dùng từ bình thường nhưng có nhiều điều kiện cross-reference → PASS

**4d. Ngữ pháp phù hợp level:**

| Level | Ngữ pháp mong đợi |
|-------|--------------------|
| N5 | ～です/ます, ～てください, ～ことができます |
| N4 | ～たら, ～ても, ～なければならない, ～ようにしてください |
| N3 | ～場合, ～ことになっている, ～に限り, ～とする |
| N2 | ～において, ～に伴い, ～を踏まえ, ～次第 |
| N1 | ～をもって, ～に基づき, ～を経て, formal keigo |

- ❌ Bài N5 dùng ～において → **FAIL**
- ❌ Bài N4 dùng ～を踏まえ → **FAIL**

---

### 5. FURIGANA

**5a. Số lượng ruby tags (minimum bắt buộc):**

| Level | Minimum ruby tags | FAIL nếu |
|-------|------------------|----------|
| N1 | ≥ 3 | 0-2 ruby |
| N2 | ≥ 5 | 0-4 ruby |
| N3 | ≥ 5 | 0-4 ruby |
| N4 | ≥ 0 | Không bắt buộc số lượng |
| N5 | ≥ 0 | Không bắt buộc số lượng |

**Cách đếm:** `grep -o '<ruby>' file.html | wc -l`

**5b. Format furigana:**
- ✅ Chỉ dùng `<ruby>漢字<rt>かんじ</rt></ruby>`
- ❌ Dùng ngoặc đơn `漢字(かんじ)` → **FAIL**
- ❌ Dùng brackets `漢字【かんじ】` → **FAIL**
- ❌ Dạng "Ab" hỗn hợp `拠てん` → **FAIL**

**5c. Furigana đúng từ:**
- Chỉ furigana cho từ VƯỢT level — từ đúng level hoặc dưới level KHÔNG có furigana
- ❌ Bài N3 mà furigana cho từ N3 (ví dụ: `<ruby>届<rt>とど</rt></ruby>く` trong bài N3) → **FAIL**
- ❌ Bài N3 mà từ N1 `拠点` viết trần không furigana → **FAIL**

**5d. N4/N5 — kanji vượt level:**
- N4/N5 KHÔNG được dùng kanji N3+ kể cả có furigana
- ❌ Bài N5 dùng `<ruby>届<rt>とど</rt></ruby>く` → **FAIL** (không nên có kanji N3 trong N5, viết hiragana `とどく`)

---

### 6. CHẤT LƯỢNG CÂU HỎI & LỰA CHỌN (Question & Answer Quality)

**6a. Tình huống (BẮT BUỘC cho MỌI câu hỏi):**
- MỌI câu hỏi (Q1 VÀ Q2) phải là TÌNH HUỐNG: nhân vật có tên thật + profile + điều kiện
- ❌ Q dạng "～について、正しいものはどれか" → **FAIL**
- ❌ Q dùng Aさん/Bさん → **FAIL**
- ✅ Q có "田中さんは30歳で、週末だけ通いたい。どのコースが合いますか。" → PASS

**6b. Đa dạng kiểu hỏi:**
- Q1 và Q2 trong cùng bài PHẢI dùng kiểu khác nhau (8 kiểu: chọn phương án / kiểm tra tư cách / thủ tục / tính chi phí / đúng-sai / ngoại lệ / so sánh / xử lý vấn đề)
- ❌ Q1 = "chọn phương án", Q2 = "chọn phương án" → **FAIL**

**6c. Đáp án đúng — paraphrase:**
- Đáp án đúng PHẢI có căn cứ trong bài VÀ được paraphrase (diễn đạt lại)
- ❌ Copy nguyên văn từ bài → **FAIL** (quá dễ nhận ra)
- ❌ Chứa thông tin không có trong bài → **FAIL** (suy luận, không phải tìm thông tin)

**6d. Đáp án sai (distractor) — phải cần suy nghĩ mới loại:**
- Distractor PHẢI chứa thông tin CÓ trong bài nhưng áp dụng sai (sai điều kiện, sai đối tượng)
- ❌ Distractor bịa thông tin không có trong bài → **FAIL** (loại ngay không cần đọc bài)
- ❌ Distractor sai hiển nhiên → **FAIL**
- ❌ 3 đáp án tích cực + 1 phủ định rõ ràng → **FAIL** (đoán được)

**6e. Test che bài:**
- Che bài đọc, chỉ nhìn 4 đáp án → nếu đoán được đáp án đúng → **FAIL**

**6f. correct_answer format:**
- Phải là integer string: `1`, `2`, `3`, `4`
- ❌ `2.0` → **FAIL**

**6g. Nhân vật Q1 ≠ Q2:**
- Q1 và Q2 phải dùng nhân vật khác nhau

---

## Quy Trình Kiểm Tra

### Bước 1: Thu thập dữ liệu

```python
import os, csv, re, glob

# Đọc CSV
csv_path = "sheets/<file>.csv"  # hoặc file mới nhất
html_dir = "assets/html/tim_thong_tin/"

# Đọc tất cả HTML
html_files = glob.glob(f"{html_dir}*.html")
```

### Bước 2: Kiểm tra từng bài

Với mỗi bài (HTML + dòng CSV tương ứng):

```
1. Đọc HTML file
2. [TC1] Đếm chars → count_body_chars() → so sánh minimum
3. [TC2] Đọc nội dung → đánh giá chủ đề/format/logic
4. [TC3] Kiểm tra layout: <br> trong văn xuôi? Container CSS? 
5. [TC4] Đọc từ vựng → ước lượng tỉ lệ đúng level, kiểm tra kanji N4/N5
6. [TC5] Đếm ruby tags → so sánh minimum, kiểm tra format furigana
7. [TC6] Đọc câu hỏi + đáp án từ CSV → kiểm tra tình huống, paraphrase, distractor
8. Tổng hợp: 1 FAIL = REJECT cả bài
```

### Bước 3: Script tự động (phần kiểm tra được)

```python
import re
from pathlib import Path

def check_html(html_path: str, level: str) -> dict:
    """Kiểm tra tự động các tiêu chí đo được."""
    html = Path(html_path).read_text(encoding='utf-8')
    results = {}
    
    # TC1: Character count
    char_count = count_body_chars(html)
    min_chars = {"N1": 700, "N2": 700, "N3": 600, "N4": 400, "N5": 250}
    results["TC1_chars"] = {
        "count": char_count,
        "min": min_chars[level],
        "pass": char_count >= min_chars[level]
    }
    
    # TC3a: Flow text — tìm <br> giữa câu
    br_in_prose = len(re.findall(r'。\s*<br\s*/?>', html))
    results["TC3_flow_text"] = {
        "br_in_prose": br_in_prose,
        "pass": br_in_prose == 0
    }
    
    # TC3b: Container CSS
    has_margin_auto = bool(re.search(r'margin:\s*0\s+auto', html))
    has_min_height = bool(re.search(r'min-height', html))
    results["TC3_container"] = {
        "margin_auto": has_margin_auto,
        "min_height": has_min_height,
        "pass": not has_margin_auto and not has_min_height
    }
    
    # TC5a: Ruby count
    ruby_count = len(re.findall(r'<ruby>', html))
    min_ruby = {"N1": 3, "N2": 5, "N3": 5, "N4": 0, "N5": 0}
    results["TC5_ruby_count"] = {
        "count": ruby_count,
        "min": min_ruby[level],
        "pass": ruby_count >= min_ruby[level]
    }
    
    # TC5b: Furigana format — tìm ngoặc đơn furigana
    paren_furigana = re.findall(r'[\u4e00-\u9fff]+[（(][ぁ-ん]+[）)]', html)
    bracket_furigana = re.findall(r'[\u4e00-\u9fff]+【[ぁ-ん]+】', html)
    results["TC5_furigana_format"] = {
        "paren_found": paren_furigana,
        "bracket_found": bracket_furigana,
        "pass": len(paren_furigana) == 0 and len(bracket_furigana) == 0
    }
    
    return results


def check_csv_row(row: dict, level: str) -> dict:
    """Kiểm tra tự động các tiêu chí trong CSV."""
    results = {}
    
    # TC6f: correct_answer format
    for i in ["1", "2"]:
        key = f"correct_answer_{i}"
        if key in row and row[key]:
            val = str(row[key]).strip()
            is_int = val in ["1", "2", "3", "4"]
            results[f"TC6_correct_answer_{i}"] = {
                "value": val,
                "pass": is_int
            }
    
    # TC6a: Tình huống — kiểm tra có tên nhân vật (さん) không
    for i in ["1", "2"]:
        key = f"question_{i}"
        if key in row and row[key]:
            has_name = "さん" in row[key]
            has_generic = any(x in row[key] for x in ["Aさん", "Bさん", "人A", "人B"])
            results[f"TC6_scenario_q{i}"] = {
                "has_name": has_name,
                "has_generic_name": has_generic,
                "pass": has_name and not has_generic
            }
    
    return results
```

### Bước 4: Báo cáo

Output bảng tổng hợp cho mỗi bài:

```
╔══════════════════════════════════════════════════════════════╗
║  QUALITY CHECK REPORT — {_id}  (Level: {level})            ║
╠══════════════════════════════════════════════════════════════╣
║ TC1  Ký tự         │ {count} chars (min {min})  │ ✅ PASS   ║
║ TC2  Chủ đề/Format │ {đánh giá}                 │ ✅ PASS   ║
║ TC3  Layout         │ Flow text OK, container OK │ ✅ PASS   ║
║ TC4  Từ vựng/NP    │ ~85% đúng level            │ ✅ PASS   ║
║ TC5  Furigana       │ {count} ruby (min {min})   │ ❌ FAIL   ║
║ TC6  Câu hỏi       │ Q1 ✅ Q2 ❌ (thiếu tên)    │ ❌ FAIL   ║
╠══════════════════════════════════════════════════════════════╣
║ KẾT LUẬN: ❌ REJECT — Cần sửa TC5, TC6                     ║
╚══════════════════════════════════════════════════════════════╝
```

Cuối cùng, tổng hợp batch:

```
TỔNG KẾT BATCH: 15 bài
├── ✅ PASS: 3 bài (20%)
├── ❌ REJECT: 12 bài (80%)
│   ├── TC1 (chars): 0 FAIL
│   ├── TC2 (topic): 1 FAIL
│   ├── TC3 (layout): 2 FAIL
│   ├── TC4 (vocab): 3 FAIL
│   ├── TC5 (furigana): 9 FAIL
│   └── TC6 (question): 12 FAIL
└── Lỗi phổ biến nhất: TC5 furigana (60%), TC6 question (80%)
```

---

## Kiểm Tra Thủ Công (Không Tự Động Được)

Một số tiêu chí CẦN đánh giá thủ công bằng cách đọc nội dung:

| Tiêu chí | Cách kiểm tra thủ công |
|-----------|----------------------|
| TC2 — Chủ đề phù hợp level | Đọc bài → chủ đề có phù hợp level? N5 có quá phức tạp? |
| TC2 — Logic nội dung | Giá cả, thời gian, điều kiện có hợp lý không? |
| TC4 — Tỉ lệ từ vựng | Đọc bài → ước lượng % từ đúng level (cần kiến thức JLPT) |
| TC4 — Nguồn tạo độ khó | Độ khó từ cấu trúc hay từ nhồi thuật ngữ? |
| TC4 — Ngữ pháp phù hợp | Cấu trúc ngữ pháp có vượt level? |
| TC5 — Furigana đúng từ | Từ nào cần furigana, từ nào không? |
| TC6 — Paraphrase | Đáp án đúng có paraphrase hay copy nguyên văn? |
| TC6 — Distractor quality | Đáp án sai có cần suy nghĩ mới loại được không? |
| TC6 — Test che bài | Che bài, nhìn 4 đáp án → đoán được không? |
| TC6 — Kiểu hỏi Q1 ≠ Q2 | Q1 và Q2 có dùng kiểu hỏi khác nhau không? |

## Hành Động Sau Kiểm Tra

| Kết quả | Hành động |
|---------|-----------|
| ✅ PASS tất cả 6 TC | Bài đạt chuẩn — giữ nguyên |
| ❌ FAIL TC1 (chars) | Gen lại toàn bộ HTML |
| ❌ FAIL TC2 (topic/logic) | Gen lại toàn bộ (đổi chủ đề nếu không phù hợp level) |
| ❌ FAIL TC3 (layout) | Sửa HTML (bỏ `<br>`, fix CSS) → chụp lại screenshot |
| ❌ FAIL TC4 (vocab) | Gen lại toàn bộ với từ vựng đúng level |
| ❌ FAIL TC5 (furigana) | Thêm/sửa furigana → chụp lại screenshot |
| ❌ FAIL TC6 (question) | Viết lại câu hỏi/đáp án → cập nhật CSV |

> **Sau khi sửa → chạy lại quality check để confirm PASS.**

## Prompt Mẫu

### Kiểm tra toàn bộ batch

```
Kiểm tra chất lượng tất cả bài trong sheets/<file>.csv

Chạy 6 tiêu chí cho từng bài:
1. Ký tự (count_body_chars)
2. Chủ đề & format phù hợp level
3. Layout (flow text, container)
4. Từ vựng & ngữ pháp đúng level
5. Furigana (count ruby, format)
6. Câu hỏi & đáp án (tình huống, paraphrase, distractor)

Output bảng tổng hợp + danh sách bài REJECT kèm lý do.
```

### Kiểm tra 1 bài

```
Kiểm tra chất lượng bài {_id}:
- HTML: assets/html/tim_thong_tin/{_id}.html
- CSV: sheets/<file>.csv (dòng tương ứng)

Đánh giá 6 tiêu chí, cho điểm PASS/FAIL từng tiêu chí.
Nếu FAIL → chỉ rõ lỗi cụ thể và đề xuất cách sửa.
```

### Kiểm tra + sửa luôn

```
Kiểm tra chất lượng tất cả bài trong sheets/<file>.csv
Nếu phát hiện lỗi:
- TC3 (layout) / TC5 (furigana): sửa HTML trực tiếp → chụp lại screenshot
- TC6 (question format, correct_answer): sửa CSV trực tiếp
- TC1/TC2/TC4: báo cáo — cần gen lại

Chạy lại check sau khi sửa để confirm PASS.
```
