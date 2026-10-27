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

หากเคยติดตั้ง Skill นี้แล้ว ให้ดึง repo รุ่นล่าสุด สำรองโฟลเดอร์ Skill เดิมไว้นอกโฟลเดอร์ที่ OpenCode ค้นหา แล้วแทนทั้งโฟลเดอร์ด้วยรุ่นใหม่ เพื่อให้ไฟล์ที่ถูกถอดออกไม่ค้างอยู่ คำสั่งติดตั้งแบบ Global ด้านบนจะข้ามชื่อที่มีอยู่แล้ว จึงไม่ใช่คำสั่งอัปเดต

Python dependencies ติดตั้งใน `.venv` ของ repo นี้ หากทำงานในโปรเจกต์อื่น ให้ติดตั้ง `requirements.txt` ใน environment ของโปรเจกต์นั้น หรือระบุ path ของ Python ที่ติดตั้งไว้ให้ agent ใช้

## ใช้งาน

เปิด OpenCode ในโฟลเดอร์งาน แล้วขอให้ใช้ Skill ตามชื่อ เช่น:

> ใช้ work-data-analysis อ่านเอกสารและตารางใน input ตรวจคุณภาพข้อมูลก่อนวิเคราะห์ บันทึกหลักฐานและผลลัพธ์ใน output/analysis

> ใช้ work-data-charts สร้างกราฟจากผลวิเคราะห์ที่ตรวจแล้ว เก็บ PNG, SVG และข้อมูลกราฟใน output/charts

> ใช้ work-report-writing ทำรายงานจากหลักฐานและกราฟ แยกข้อเท็จจริง การตีความ ข้อเสนอแนะ และข้อจำกัด ส่งออก Word และ PDF

> ใช้ Skill consolidate-company-data รวมไฟล์ CSV และ Excel ที่แนบเข้า template บริษัทนี้ สำรวจคอลัมน์และเสนอ mapping จากไฟล์จริง ถ้ามีจุดที่ยังระบุรายการเดียวกันหรือแปลงข้อมูลไม่ได้ให้ถามก่อน แล้วสร้างผลลัพธ์ใน output

Skill รวมข้อมูลเป็นคำแนะนำให้ agent ใช้เครื่องมือ ไม่ใช่สคริปต์แปลงข้อมูลสำเร็จรูป รองรับ CSV/XLSX เป็นต้นทางและ XLSX เป็นผลลัพธ์ เริ่มจากไฟล์ต้นทางกับ template ของคุณได้ โดยไม่ต้องเตรียม mapping หรือชุดข้อมูลตัวอย่างมาก่อน หากมีคำอธิบายคอลัมน์ กติกา หรือทะเบียนอ้างอิง ให้แนบเพิ่มหรืออธิบายในแชต AI จะใช้สิ่งที่มีหลักฐานและถามเฉพาะข้อมูลสำคัญที่ยังขาด เช่น หนึ่งแถวหมายถึงอะไรหรือใช้ช่องใดระบุรายการเดียวกัน

ชื่อเริ่มต้นของผลลัพธ์คือ `output/consolidated-data.xlsx` โดยรักษาคอลัมน์และชีตของ template พร้อม Mapping, Pending, Decisions, Lineage และ Summary หากต้องการตรวจ mapping ก่อนสร้างไฟล์ ให้เพิ่มคำสั่ง “แสดง mapping และตัวอย่างก่อน ยังไม่ต้องสร้างผลลัพธ์” เมื่อกติกาครบและขอให้รวมข้อมูลแล้ว AI จะทำต่อโดยไม่บังคับให้อนุมัติ mapping ซ้ำ

กฎวันที่ หน่วย ช่องจำเป็น วิธีจับคู่ และการจัดการข้อมูลซ้ำยึดตามงานที่แนบ ไม่กำหนดว่าต้องเป็นข้อมูลขายหรือว่าตัวเลขทุกช่องต้องเป็นบวก คีย์เดียวกันที่ค่าหลักขัดแย้งจะถูกพักไว้พร้อมหลักฐาน หากไม่มีกฎเลือกแหล่งที่เชื่อถือได้ และจะไม่เดาเติมข้อมูลที่ขาด

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
