# Gen Questions Label Ver 2

Project tạo dữ liệu training AI fine-tuning: bài đọc hiểu dạng **tìm thông tin** (情報検索 / information retrieval) của JLPT từ N1 đến N5.

## Cấu trúc thư mục

```
gen-questions-label-ver-2/
├── input/                             ← Mẫu tham khảo (61 HTML + 20 QA + schema)
│   ├── html/                          ← 61 bài mẫu (N1×14, N2×12, N3×15, N4×10, N5×10)
│   ├── htm_content_qa/                ← 20 mẫu câu hỏi + đáp án (4 per level)
│   ├── question_sheet.csv             ← Schema CSV gốc (45 cột)
│   ├── question_format.json           ← Số câu hỏi per level
│   └── mission.json                   ← Nhãn câu hỏi
├── assets/
│   ├── html/tim_thong_tin/            ← HTML output
│   └── img/tim_thong_tin/             ← Screenshot PNG
├── sheets/                            ← CSV output
├── HANDOVER_TIM_THONG_TIN.md          ← Tài liệu tổng quan project
└── PROMPTS_TIM_THONG_TIN.md           ← Prompt templates
```

## Skill chính

Project có skill **jlpt-tim-thong-tin** tại `.gemini/skills/jlpt-reading-generator/SKILL.md`.

**BẮT BUỘC đọc SKILL.md trước khi gen dữ liệu.** File này chứa tất cả rules quan trọng:
- Quy tắc furigana (KHÔNG dùng dạng Ab, chỉ furigana cho từ vượt level)
- Character counting (650-800 chars cho N1, 620-770 cho N2, 550-750 cho N3, 400-500 cho N4, 200-290 cho N5). Hard reject nếu dưới 10% Min.
- 15 format catalog + per-level distribution
- CSV schema 45 cột
- Question generation rules (N5: 1 câu, N1-N4: 2 câu)
- File naming: `{LEVEL}_{uuid}` (e.g. `N3_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5`)

## Quy trình gen dữ liệu (tóm tắt)

1. Đọc SKILL.md để nắm rules
2. Đọc 1-2 mẫu tham khảo từ `input/html/` và `input/htm_content_qa/`
3. Gen HTML → count chars → verify range
4. Save HTML → capture screenshot (Playwright)
5. Extract clean HTML → gen questions → fill CSV
6. Verify tất cả

## Lưu ý quan trọng

- **Furigana**: N1 gần như 0 furigana, N5 viết hiragana thay kanji. KHÔNG BAO GIỜ dùng dạng "Ab" (混ぜる partial kanji+hiragana). **BẮT BUỘC dùng CẢ HAI thẻ `<ruby>` và `<rt>` cho furigana** — chỉ có `<ruby>` mà thiếu `<rt>` thì vô nghĩa. KHÔNG dùng ngoặc `()` hay `【】`. Ví dụ đúng: `<ruby>拠点<rt>きょてん</rt></ruby>`.
- **UUID naming**: Dùng `uuid.uuid4().hex` (full 32-char, KHÔNG cắt) cho _id và tên file. Level prefix UPPERCASE (N1, N2...).
- **general_image**: Local path `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`.
- **question_label**: Luôn là `question_information_search`.
- **Layout A4**: HTML phải trông như 1 tờ A4 khi capture. Container `width: 794px`, `min-height: 1123px`, nền xám + tờ trắng. Viewport Playwright = 854px. Table dùng `table-layout: fixed`. Nội dung không được tràn ra ngoài container.
- **NGHIÊM CẤM ngắt dòng sau mỗi câu**: KHÔNG dùng `<br>` trong paragraph. Text phải chảy liên tục (flow text), tự wrap khi đến mép container — giống đề JLPT thật. Các câu cùng đoạn nằm trong 1 thẻ `<p>` duy nhất. Chỉ ngắt khi chuyển section/heading/list.
- **NGHIÊM CẤM tách giữa từ khi xuống dòng**: Giống tiếng Việt không tách "CH-ÀO", tiếng Nhật không được tách「いたしま-す」hay「くださ-い」. CSS `word-break: keep-all` + `line-break: strict` đã xử lý. Nếu vẫn bị tách, dùng `<span style="display:inline-block">` wrap cụm từ.
