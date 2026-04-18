# HTML Design Patterns Reference — 61 Samples + 20 QA Samples

Catalog of all design patterns from 61 approved passage reference samples in `input/html/`.

Additionally, 20 QA reference samples in `input/htm_content_qa/` (4 per level) contain reading passages paired with questions, answer options, and correct answers. For question-specific analysis, see `question-patterns.md`.

## Table of Contents
1. [Statistics Overview](#statistics-overview)
2. [N1 Patterns (14 files)](#n1-patterns)
3. [N2 Patterns (12 files)](#n2-patterns)
4. [N3 Patterns (15 files)](#n3-patterns)
5. [N4 Patterns (10 files)](#n4-patterns)
6. [N5 Patterns (10 files)](#n5-patterns)
7. [Shared CSS Patterns](#shared-css-patterns)
8. [Design Elements Index](#design-elements-index)

---

## Statistics Overview

| Level | Files | Chars Min | Chars Max | Chars Avg | Ruby Min | Ruby Max | Ruby Avg |
|-------|-------|-----------|-----------|-----------|----------|----------|----------|
| N1    | 14*   | 499       | 799       | 694       | 86       | 167      | 132      |
| N2    | 12    | 478       | 767       | 697       | 85       | 146      | 121      |
| N3    | 15    | 342       | 747       | 618       | 74       | 155      | 119      |
| N4    | 10    | 306       | 491       | 419       | 32       | 97       | 60       |
| N5    | 10    | 137       | 285       | 210       | 13       | 59       | 32       |

*N1: n1_10.html is empty (0 bytes) — 13 valid files.

---

## N1 Patterns

### n1_1 — 薬の説明書 (Medicine instruction sheet) — `medicine_info`
- Chars: 566 | Ruby: 121
- 5-column data table (No., name, function, cautions, dosage), header with clinic info, footer with pharmacy, unit tag badge

### n1_2 — 外国人生活相談案内 (Foreigner consultation service) — `service_guide`
- Chars: 499 | Ruby: 86
- ◆ bullet list, content boxes with floating labels, dashed contact box, centered date/time

### n1_3 — 奨学金募集リスト (Scholarship listing) — `price_comparison_table`
- Chars: 720 | Ruby: 134
- 5-column table (12 rows), scroll-style title decoration (CSS circles), double-border table

### n1_4 — 博物館催し物案内 (Museum events notice) — `event_announcement`
- Chars: 794 | Ruby: 167
- Section boxes (bordered), diamond-prefixed info rows, underlined title, address footer

### n1_5 — 大学図書館利用案内 (University library guide) — `facility_guide`
- Chars: 693 | Ruby: 126
- 3-column table, numbered sections with sub-sections, indented paragraphs, bold notices

### n1_6 — 新聞読者モニター募集 (Newspaper monitor recruitment) — `recruitment_notice`
- Chars: 769 | Ruby: 145
- Underlined section headers, label-value rows, star-prefixed notes, bordered contact footer

### n1_7 — CPJカード案内 (Credit card guide) — `price_comparison_table`
- Chars: 685 | Ruby: 127
- Comparison table (5-col, merged cells/rowspan), numbered instruction steps, sub-lists

### n1_8 — 就職支援行事スケジュール (Job support event schedule) — `schedule_timetable`
- Chars: 772 | Ruby: 149
- Schedule table (5-col, 10 rows), sub-table for joint events, grid layout for legend

### n1_9 — 市民農園利用者募集 (Community garden recruitment) — `facility_guide`
- Chars: 729 | Ruby: 156
- 3-column table, SVG illustration, bracketed section labels, footer with contact

### n1_11 — アルバイト情報 (Part-time job listings) — `schedule_timetable`
- Chars: 718 | Ruby: 132
- 6-column table (10 rows), centered title

### n1_12 — 買い取りサービス案内 (Buy-back service guide) — `service_guide`
- Chars: 664 | Ruby: 135
- Two tables (process flow + size limits), diamond section headers, numbered flow steps

### n1_13 — オーケストラ年間セット券案内 (Orchestra ticket guide) — `price_comparison_table`
- Chars: 799 | Ruby: 136
- Price table (6-col), bordered note box, numbered instruction list, footer with URL

### n1_14 — 工場見学・陶芸体験案内 (Factory tour & pottery experience) — `member_notification`
- Chars: 619 | Ruby: 102
- Info table (key-value), availability grid (7-day), bullet points, asterisk notes

**N1 Document Types**: Medicine sheet, consultation guide, scholarship list, museum events, library guide, recruitment notice, credit card guide, event schedule, community garden, job listings, buy-back service, concert tickets, factory tour

---

## N2 Patterns

### n2_1 — 住まい比較記事 (Housing comparison article) — `comparison_article`
- Chars: 728 | Ruby: 118
- Lettered A-D sections, section dividers with border-bottom, justified text

### n2_2 — 就職フェアチラシ (Global job fair) — `event_announcement`
- Chars: 478 | Ruby: 85
- Black banner (rotated -1deg), admission box, large date/time, info-grid, star-bullet list

### n2_3 — 図書館利用案内 (Library guide with flowchart) — `facility_guide`
- Chars: 699 | Ruby: 125
- Flowchart (yes/no question boxes + arrows), grid-list for borrowing, footer asterisk notes

### n2_4 — 就職セミナー案内 (Job seminar notice) — `schedule_timetable`
- Chars: 696 | Ruby: 146
- Program table with 3 parts, venue table with nested sub-table, underlined notes

### n2_5 — ビュッフェ案内 (Restaurant buffet guide) — `menu_guide`
- Chars: 674 | Ruby: 89
- Bullet-prefixed sections, diamond sub-headers, 4-column price grid, centered footer

### n2_6 — バーベキュー施設案内 (BBQ venue notice) — `facility_guide`
- Chars: 730 | Ruby: 112
- Bullet-point lists, bordered set-menu box, sub-title, contact footer with URL

### n2_7 — 体験教室案内 (Glass museum workshop) — `class_enrollment`
- Chars: 746 | Ruby: 135
- 2x2 course grid, bordered section boxes, bullet-with-dot info rows, wait-time highlights

### n2_8 — 海岸清掃活動案内 (Beach cleanup event) — `event_announcement`
- Chars: 735 | Ruby: 145
- Right-aligned org header, bordered info table (label + content cells), recruit box, numbered flow

### n2_9 — 書籍予約広告 (Book pre-order ad) — `comparison_article`
- Chars: 691 | Ruby: 120
- Detail rows (label-value), bordered special-box for payment, italic footnote, right-aligned footer

### n2_10 — 冷蔵庫取扱説明 (Refrigerator troubleshooting) — `comparison_article`
- Chars: 767 | Ruby: 119
- Full-width table with rowspan, 3-column layout (issue/check/action), warning section

### n2_11 — 引越サービス比較 (Moving service comparison) — `service_guide`
- Chars: 707 | Ruby: 124
- Two section-boxes (Company A & B), 2x2 plan grid, flowchart with decision nodes

### n2_12 — 着物レンタル案内 (Kimono rental guide) — `service_guide`
- Chars: 707 | Ruby: 133
- Right-aligned header with underline, inline SVG, numbered flow steps, pricing table

**N2 Document Types**: Housing comparison, job fair, library guide, seminar, buffet guide, BBQ venue, workshop, volunteer event, book ad, troubleshooting guide, moving service, kimono rental

---

## N3 Patterns

### n3_1 — 日本語教室案内 (Japanese class notice) — `class_enrollment`
- Chars: 342 | Ruby: 74
- Bullet list with dots, schedule table with circle marks, notes section

### n3_2 — バス旅行案内 (Day-trip bus tour) — `travel_listing`
- Chars: 651 | Ruby: 134
- 2x2 tour grid, pricing table, cancellation policy sections, footer contact

### n3_3 — スキー教室案内 (Ski lesson guide) — `class_enrollment`
- Chars: 612 | Ruby: 125
- Rounded course boxes, SVG ski illustrations, two pricing tables, discount notes

### n3_4 — 大学食堂案内 (University cafeteria) — `menu_guide`
- Chars: 576 | Ruby: 111
- 2x2 grid with gray headers, section headers, triangle/circle bullet markers

### n3_5 — 図書館利用案内 (Library + reading group) — `facility_guide`
- Chars: 627 | Ruby: 115
- Two-part A/B layout, table, diamond bullet points, contact footer

### n3_6 — ボランティア募集 (Cherry blossom festival volunteer) — `recruitment_notice`
- Chars: 613 | Ruby: 133
- Centered festival summary, detailed label/content table

### n3_7 — ギター教室生徒募集 (Guitar lesson recruitment) — `class_enrollment`
- Chars: 665 | Ruby: 113
- Bordered intro box with stars, pricing table, triangle discount markers

### n3_8 — クリーニング店案内 (Dry cleaning sale) — `service_guide`
- Chars: 592 | Ruby: 109
- Two-part A/B layout, pricing table, contact grid

### n3_9 — 大学授業案内 (Newspaper-making class) — `event_announcement`
- Chars: 596 | Ruby: 97
- Schedule table, computer usage table, dashed footer

### n3_10 — 動物園イベント案内 (Zoo events) — `event_announcement`
- Chars: 585 | Ruby: 124
- Bordered section boxes, 2x2 event grid, night zoo info rows

### n3_11 — 鉄道乗り放題きっぷ (Railway ticket guide) — `price_comparison_table`
- Chars: 547 | Ruby: 106
- Underlined title, large comparison table, asterisk footnotes

### n3_12 — 自然教室案内 (Nature classroom) — `class_enrollment`
- Chars: 645 | Ruby: 155
- Section tags with left bar accent, 2x2 program grid, bank info box

### n3_13 — 日本語クラス案内 (Japanese class enrollment) — `class_enrollment`
- Chars: 676 | Ruby: 111
- Table with symbol legends (○×△), underlined section titles, note list

### n3_14 — レストラン特別メニュー (Restaurant special menu) — `service_guide`
- Chars: 688 | Ruby: 113
- Numbered circle shop list, shop cards with info rows, price grids

### n3_15 — パソコン教室受講者募集 (PC/IT skills class) — `class_enrollment`
- Chars: 747 | Ruby: 133
- Table with gray header cells, symbol legend with blue border, bullet notes

**N3 Document Types**: Japanese class, bus tour, ski lesson, university cafeteria, library, volunteer recruitment, guitar lesson, dry cleaning, university class, zoo events, railway ticket, nature classroom, restaurant menu, PC class

---

## N4 Patterns

### n4_1 — 手洗いガイド (Handwashing guide) — `regulation_notice`
- Chars: 389 | Ruby: 34
- Rounded intro box, numbered step list (1-5), dashed footer, ☆◎ markers

### n4_2 — スピーチコンテスト (Speech contest) — `event_announcement`
- Chars: 491 | Ruby: 58
- Pill labels (rounded-full), award grid (3-col), 【】section headers

### n4_3 — ごみ分別案内 (Garbage sorting rules) — `regulation_notice`
- Chars: 306 | Ruby: 43
- Table with garbage categories, SVG map diagram with bin locations, monthly calendar grid

### n4_4 — 日本文化教室 (Japanese culture classes) — `class_enrollment`
- Chars: 337 | Ruby: 65
- 5-row course table (content/day-time/fee), clean tabular layout

### n4_5 — スポーツ教室 (One-day sports class) — `event_announcement`
- Chars: 466 | Ruby: 58
- Table with rowspan grouping (groups 1/2), AM/PM instructions, footer with phone

### n4_6 — 生活相談+予定表 (Consultation + weekly planner) — `service_guide`
- Chars: 470 | Ruby: 86
- Two-part A/B layout, consultation timetable, two side-by-side weekly tables, contact box

### n4_7 — ホテル宿泊料金表 (Hotel pricing) — `price_comparison_table`
- Chars: 440 | Ruby: 67
- Two comparison pricing tables, diagonal header cell (SVG slash), bullet notes

### n4_8 — カレーレストランメニュー (Curry restaurant menu) — `menu_guide`
- Chars: 368 | Ruby: 32
- Single-column menu table (A/B/C/D sets), grouped types, price floated right

### n4_9 — スポーツ教室 (Sports class variant) — `event_announcement`
- Chars: 446 | Ruby: 57
- Table with rowspan, indented detail text, minimal border design

### n4_10 — 市報・春のイベント (City spring events) — `event_announcement`
- Chars: 479 | Ruby: 97
- SVG tulip illustrations, 6-row event table, footer with email

**N4 Document Types**: Handwashing guide, speech contest, garbage sorting, culture class, sports class, consultation schedule, hotel pricing, restaurant menu, city events

---

## N5 Patterns

### n5_1 — 特売チラシ (Weekly bargain shop flyer) — `store_flyer`
- Chars: 285 | Ruby: 59
- 2x2 grid table, date-labeled sections per store, price items with flex layout

### n5_2 — ケーキ屋特売チラシ (Cake shop sale) — `store_flyer`
- Chars: 240 | Ruby: 43
- 6-row price table, SVG cake illustration, price arrows (450→350)

### n5_3 — ごみ出し案内 (Garbage disposal rule change) — `regulation_notice`
- Chars: 283 | Ruby: 14
- Dotted border header box, SVG bottle illustrations, pla-mark symbol box

### n5_4 — スーパー特売チラシ (Supermarket sale) — `store_flyer`
- Chars: 178 | Ruby: 25
- SVG starburst shapes, rounded promo boxes, weekly day-of-week specials, curled corner effect

### n5_5 — 夏の旅行案内 (Summer travel tour) — `travel_listing`
- Chars: 222 | Ruby: 46
- Single-column table with 4 tour options, date ranges, right-aligned prices

### n5_6 — パーティー案内 (Welcome party notice) — `event_announcement`
- Chars: 194 | Ruby: 28
- Main info table (time/place/items), nested sub-table (food by class), footnote

### n5_7 — スーパー特売チラシ (Supermarket sale variant) — `store_flyer`
- Chars: 178 | Ruby: 25
- Grid layout (star column + info), multiple SVG starbursts, rectangular promo boxes

### n5_8 — 交通案内 (Directions to university) — `access_guide`
- Chars: 189 | Ruby: 46
- Route diagram with connected boxes and connector lines, time/cost per route

### n5_9 — 時刻表 (Train & bus timetable) — `schedule_timetable`
- Chars: 137 | Ruby: 13
- Two separate paper sheets, SVG train/bus illustrations, timetable grids, curled paper corners

### n5_10 — スポーツクラブ案内 (Sports club schedule) — `class_enrollment`
- Chars: 193 | Ruby: 21
- Simple 3-column schedule table, bullet markers, large phone CTA, curled corner

**N5 Document Types**: Sale flyer (×3), garbage notice, travel tour, party notice, directions map, timetable, sports club schedule
**N5 Visual Features**: Heavy use of SVG illustrations, starburst shapes, curled paper corners, route diagrams, minimal text

---

## Shared CSS Patterns

### Base container
```css
.container {
    max-width: 800px; /* 750-900px */
    margin: 2rem auto;
    background: white;
    padding: 3rem;
    border: 1px solid #d1d5db;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}
```

### Tables
```css
table { width: 100%; border: 1.5px solid #000; border-collapse: collapse; }
th, td { border: 1px solid #000; padding: 8px 10px; }
th { background-color: #e5e7eb; font-weight: bold; text-align: center; }
```

### Floating-label box
```css
.content-box {
    border: 2px solid #000;
    border-radius: 1rem;
    padding: 1.2rem 1.5rem;
    margin: 1.5rem 0;
    position: relative;
}
.box-label {
    position: absolute;
    top: -12px;
    left: 24px;
    background: white;
    padding: 0 10px;
    font-weight: bold;
}
```

### Pill label
```css
.label-pill {
    border: 1.5px solid #000;
    border-radius: 9999px;
    padding: 2px 20px;
    text-align: center;
    font-weight: bold;
}
```

### Info grid
```css
.info-grid {
    display: grid;
    grid-template-columns: 100px 1fr;
    gap: 0.5rem 1.5rem;
}
```

### 2x2 grid layout
```css
.grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
```

### Dashed contact box
```css
.contact-box {
    border: 2px dashed #000;
    padding: 1.5rem;
    margin-top: 2rem;
}
```

### Black banner (rotated)
```css
.black-banner {
    background-color: #1a1a1a;
    color: white;
    padding: 1.5rem;
    text-align: center;
    transform: rotate(-1deg);
}
```

### SVG illustrations (N4/N5 common)
```css
/* Inline SVG for visual interest — starburst, icons, route diagrams */
svg { display: inline-block; }
```

### Curled paper corner (N5 common)
```css
.paper-curl {
    position: relative;
}
.paper-curl::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 30px; height: 30px;
    background: linear-gradient(135deg, white 50%, #ddd 50%);
}
```

---

## Design Elements Index

Quick reference of which elements appear at which levels:

| Element | N1 | N2 | N3 | N4 | N5 |
|---------|----|----|----|----|-----|
| Data tables | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ |
| Merged cells / rowspan | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓ |
| Content boxes (rounded border) | ✓ | ✓✓ | ✓✓ | ✓ | — |
| Floating-label boxes | ✓ | ✓ | ✓ | — | — |
| Pill labels | — | — | — | ✓ | — |
| 【】section headers | — | — | — | ✓✓ | — |
| A/B or A/B/C/D sections | — | ✓✓ | ✓✓ | ✓ | — |
| 2x2 grid layout | — | ✓✓ | ✓✓✓ | — | ✓ |
| Flowchart (decision nodes) | — | ✓✓ | — | — | — |
| Info grid (label + value) | ✓✓ | ✓✓ | ✓ | ✓ | — |
| Bullet markers (◆◎※＊☆✓△) | ✓✓ | ✓✓ | ✓✓ | ✓ | ✓ |
| Symbol legends (○×△) | — | — | ✓✓ | — | — |
| SVG illustrations | ✓ | ✓ | ✓ | ✓✓ | ✓✓✓ |
| SVG starburst shapes | — | — | — | — | ✓✓ |
| Route diagrams | — | — | — | — | ✓ |
| Curled paper corners | — | — | — | — | ✓✓ |
| Black banner (rotated) | — | ✓ | — | — | — |
| Dashed contact box | ✓ | ✓ | ✓ | ✓ | — |
| Numbered flow steps | ✓✓ | ✓✓ | — | ✓ | — |
| Comparison tables (side-by-side) | ✓ | ✓✓ | ✓ | ✓✓ | — |
| Calendar / timetable grids | ✓ | — | ✓ | ✓ | ✓✓ |
| Diagonal header cell (SVG) | — | — | — | ✓ | — |
| Section tags with accent bar | — | — | ✓ | — | — |
| Right-aligned org header | — | ✓✓ | — | — | — |

**Key insight**: Lower levels (N4/N5) rely more on visual elements (SVG, starburst, route diagrams) to convey information with less text. Higher levels (N1/N2) use dense tabular data, flowcharts, and multi-section prose.
