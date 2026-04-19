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
- Character counting (500-800 chars cho N1, 130-290 cho N5, v.v.)
- 15 format catalog + per-level distribution
- CSV schema 45 cột
- Question generation rules (N5: 1 câu, N1-N4: 2 câu)
- File naming: `{LEVEL}_{uuid}` (e.g. `N3_a1b2c3d4`)

## Quy trình gen dữ liệu (tóm tắt)

1. Đọc SKILL.md để nắm rules
2. Đọc 1-2 mẫu tham khảo từ `input/html/` và `input/htm_content_qa/`
3. Gen HTML → count chars → verify range
4. Save HTML → capture screenshot (Playwright)
5. Extract clean HTML → gen questions → fill CSV
6. Verify tất cả

## Lưu ý quan trọng

- **Furigana**: N1 gần như 0 furigana, N5 viết hiragana thay kanji. KHÔNG BAO GIỜ dùng dạng "Ab" (混ぜる partial kanji+hiragana).
- **UUID naming**: Dùng `uuid.uuid4().hex[:8]` cho _id và tên file. Level prefix UPPERCASE (N1, N2...).
- **general_image**: Local path `assets/img/tim_thong_tin/{LEVEL}_{uuid}.png`.
- **question_label**: Luôn là `question_information_search`.
