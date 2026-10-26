# Content specification

UTF-8 JSON object: `title`, `footer` and `pages` (array). Each page has `blocks` in reading order. Use short pages with a purpose; target 4–5 pages for the workshop report.

Supported blocks:
- `{"type":"title","text":"ชื่อรายงาน"}`
- `{"type":"heading","text":"ผลที่พบ"}`
- `{"type":"paragraph","text":"ข้อความพร้อมแหล่งอ้างอิง"}`
- `{"type":"bullets","items":["รายการแรก","รายการถัดไป"]}`
- `{"type":"table","headers":["รายการ","ค่า"],"rows":[["ตัวชี้วัด","12"]]}`
- `{"type":"image","path":"charts/figure.png","caption":"คำอธิบาย หน่วย และที่มา"}`

Image paths in --spec files resolve from the specification's directory. The script embeds PNG images in DOCX/HTML and fonts in printable HTML. Output content JSON keeps relative image paths for portability.

Use text for sources and provenance, not invented URLs. Figures should refer to source file/sheet/range or document page. Numeric claims must agree with saved calculations. Page divisions are editorial: if content overflows, shorten or split it; do not keep reducing font size.
