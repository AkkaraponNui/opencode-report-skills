# OpenCode Report Skills

Skill สำหรับอ่านเอกสาร วิเคราะห์ข้อมูล รวมข้อมูลเข้า template บริษัท สร้างกราฟภาษาไทย และทำรายงาน Word/PDF จากไฟล์บนเครื่อง

| Skill | หน้าที่ |
| --- | --- |
| `work-data-analysis` | อ่าน PDF/DOCX และ CSV/XLSX ตรวจข้อมูลซ้ำ/ขาด และบันทึกผลวิเคราะห์พร้อมหลักฐาน |
| `work-data-charts` | สร้างกราฟ PNG/SVG พร้อมข้อมูลที่ใช้สร้างและฟอนต์ไทย |
| `work-report-writing` | สร้างรายงาน DOCX/HTML/PDF จากเนื้อหาชุดเดียวกัน |
| `consolidate-company-data` | รวม CSV/XLSX หลายแหล่งเข้า template XLSX พร้อม mapping รายการรอตรวจ และที่มาทุกแถว |

## ติดตั้งแบบ Global

ต้องมี Git, Python 3.12 และ Chrome/Edge สำหรับสร้าง PDF หรือใช้ Playwright Chromium แทน

**Windows PowerShell**

```powershell
git clone https://github.com/AkkaraponNui/opencode-report-skills.git
cd opencode-report-skills
$target = Join-Path $HOME '.config/opencode/skills'
New-Item -ItemType Directory -Force -Path $target | Out-Null
Get-ChildItem ./skills -Directory | ForEach-Object {
    $destination = Join-Path $target $_.Name
    if (Test-Path -LiteralPath $destination) {
        Write-Warning "ข้าม Skill ที่มีอยู่แล้ว: $destination"
    } else {
        Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse
    }
}
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS Terminal**

```sh
git clone https://github.com/AkkaraponNui/opencode-report-skills.git
cd opencode-report-skills
target="$HOME/.config/opencode/skills"
mkdir -p "$target"
for skill in skills/*; do
  name="$(basename "$skill")"
  if [ -e "$target/$name" ]; then
    printf 'ข้าม Skill ที่มีอยู่แล้ว: %s\n' "$target/$name"
  else
    cp -R "$skill" "$target/$name"
  fi
done
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

ถ้า repo เป็น private ต้องล็อกอิน GitHub ที่มีสิทธิ์ก่อน clone คำสั่งติดตั้งจะข้าม Skill ชื่อเดิมและไม่แก้ config ของ OpenCode

สำหรับติดตั้งเฉพาะโปรเจกต์ ให้คัดลอกโฟลเดอร์ Skill ที่ต้องการจาก `skills/` ไปที่ `<project>/.opencode/skills/` แทน Global

หากต้องการเฉพาะ Skill รวมข้อมูล ให้คัดลอกทั้งโฟลเดอร์ `skills/consolidate-company-data/` รวม `references/` ไปที่ `<project>/.opencode/skills/consolidate-company-data/` แล้วเปิดโปรเจกต์นั้นใน OpenCode ไม่ต้องติดตั้ง Skill อื่นหรือ browser สำหรับงานนี้ Skill จะใช้เครื่องมืออ่านและสร้าง Excel ที่มีในเครื่อง เช่น Python พร้อม openpyxl และแจ้งหากเครื่องมือยังไม่พร้อม

Python dependencies ติดตั้งใน `.venv` ของ repo นี้ หากทำงานในโปรเจกต์อื่น ให้ติดตั้ง `requirements.txt` ใน environment ของโปรเจกต์นั้น หรือระบุ path ของ Python ที่ติดตั้งไว้ให้ agent ใช้

## ใช้งาน

เปิด OpenCode ในโฟลเดอร์งาน แล้วขอให้ใช้ Skill ตามชื่อ เช่น:

> ใช้ work-data-analysis อ่านเอกสารและตารางใน input ตรวจคุณภาพข้อมูลก่อนวิเคราะห์ บันทึกหลักฐานและผลลัพธ์ใน output/analysis

> ใช้ work-data-charts สร้างกราฟจากผลวิเคราะห์ที่ตรวจแล้ว เก็บ PNG, SVG และข้อมูลกราฟใน output/charts

> ใช้ work-report-writing ทำรายงานจากหลักฐานและกราฟ แยกข้อเท็จจริง การตีความ ข้อเสนอแนะ และข้อจำกัด ส่งออก Word และ PDF

> ใช้ Skill consolidate-company-data รวม CSV และ Excel ใน input เข้า company-template.xlsx ตามกติกาบริษัทที่แนบ บันทึกผลลัพธ์ใน output พร้อม Mapping, Pending, Decisions, Lineage และ Summary

Skill รวมข้อมูลเป็นคำแนะนำให้ agent ใช้เครื่องมือ ไม่ใช่สคริปต์แปลงข้อมูลสำเร็จรูป รองรับ CSV/XLSX เป็นต้นทางและ XLSX เป็นผลลัพธ์ อ่าน template คีย์ และกติกาของแต่ละงานก่อนแปลง เมื่อคีย์เดียวกันมีค่าขัดแย้งจะพักทั้งกลุ่มโดยไม่เลือกแหล่งชนะเอง และไม่เติมข้อมูลที่ขาดด้วยการเดา

หากต้องการตรวจ mapping ก่อนสร้างไฟล์ ให้เพิ่มคำสั่ง “แสดง mapping และตัวอย่างก่อน ยังไม่ต้องสร้างผลลัพธ์” กติกาใน `consolidate-company-data/references/workshop-rules.md` ใช้เฉพาะเมื่อระบุโจทย์ workshop ที่ตรงกัน งานอื่นให้ใช้กฎของบริษัทที่แนบแทน

อ่าน `SKILL.md` ของแต่ละ Skill สำหรับพารามิเตอร์และข้อกำหนดของสคริปต์ อย่าสั่งรัน template ข้อมูลบริการกับตารางที่มีความหมายต่างกัน: ใช้ `--profile-only` เพื่อตรวจตารางใหม่ และกำหนดสูตร/โครงสร้างรายงานให้ตรงงานก่อน

หากไม่มี Chrome/Edge ให้ติดตั้ง browser สำหรับ PDF ด้วย Python ของ environment ที่ใช้:

```text
python -m playwright install chromium
```

## ขอบเขตและการตรวจสอบ

- ไม่รวมข้อมูลฝึก เฉลย API key หรือไฟล์จริงของผู้เรียน
- PDF ต้องเลือกข้อความได้ ไม่รองรับ OCR ใน workflow หลัก
- ตัวช่วยวิเคราะห์ข้อมูลบริการใช้เฉพาะ schema ที่อธิบายใน `references/service-contract.md`
- ตรวจตัวหาร ข้อมูลขาด และหลักฐานก่อนเขียนข้อสรุป พร้อมเปิดตรวจกราฟและรายงานทุกหน้า
- ทดสอบการสร้างรายงานบน Windows แล้ว ส่วน macOS ยังไม่ได้ทดสอบบนเครื่องจริง
- Skill รวมข้อมูลผ่านตัวตรวจโครงสร้างและการทดสอบกติกาจาก CSV/XLSX กับ template ยอดขายและคำขอบริการแล้ว ยังไม่ได้ทดสอบการเรียก Skill ผ่านโมเดล OpenCode จริง
- ฟอนต์ Sarabun แจกพร้อมใบอนุญาต SIL OFL ในโฟลเดอร์ assets ของแต่ละ Skill ที่ใช้ฟอนต์
