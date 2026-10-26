"""One content model -> editable DOCX + printable HTML/PDF.
Can also render a user-authored JSON document spec with --spec.
"""
import argparse,base64,html,json,os,shutil,subprocess,tempfile
import uuid,zipfile
from lxml import etree as ET
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ASSETS=Path(__file__).resolve().parents[1]/'assets'
def h(x):return html.escape(str(x))
def font_uri(name):return 'data:font/ttf;base64,'+base64.b64encode((ASSETS/name).read_bytes()).decode()
def embed_docx_fonts(file):
    """Embed OFL-licensed Sarabun in OOXML so Word need not guess a Thai font."""
    W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    REL='http://schemas.openxmlformats.org/package/2006/relationships'
    CT='http://schemas.openxmlformats.org/package/2006/content-types'
    ET.register_namespace('w',W);ET.register_namespace('r',R)
    with zipfile.ZipFile(file) as z:parts={n:z.read(n) for n in z.namelist()}
    fonts=ET.fromstring(parts['word/fontTable.xml'])
    entry=next((x for x in fonts if x.get('{'+W+'}name')=='Sarabun'),None)
    if entry is None:entry=ET.SubElement(fonts,'{'+W+'}font',{'{'+W+'}name':'Sarabun'})
    relationships=ET.Element('{'+REL+'}Relationships')
    for style,name in [('Regular','Sarabun-Regular.ttf'),('Bold','Sarabun-Bold.ttf')]:
        key=uuid.uuid5(uuid.NAMESPACE_URL,'https://fonts.google.com/Sarabun/'+style)
        mask=key.bytes[::-1];data=bytearray((ASSETS/name).read_bytes())
        for i in range(32):data[i]^=mask[i%16]
        member='fonts/Sarabun-'+style+'.odttf';rid='font'+style
        parts['word/'+member]=bytes(data)
        ET.SubElement(entry,'{'+W+'}embed'+style,{'{'+R+'}id':rid,'{'+W+'}fontKey':'{'+str(key).upper()+'}'})
        ET.SubElement(relationships,'{'+REL+'}Relationship',{'Id':rid,'Type':R+'/font','Target':member})
    parts['word/fontTable.xml']=ET.tostring(fonts,encoding='utf-8',xml_declaration=True)
    parts['word/_rels/fontTable.xml.rels']=ET.tostring(relationships,encoding='utf-8',xml_declaration=True)
    types=ET.fromstring(parts['[Content_Types].xml'])
    if not any(x.get('Extension')=='odttf' for x in types):ET.SubElement(types,'{'+CT+'}Default',{'Extension':'odttf','ContentType':'application/vnd.openxmlformats-officedocument.obfuscatedFont'})
    parts['[Content_Types].xml']=ET.tostring(types,encoding='utf-8',xml_declaration=True)
    settings=ET.fromstring(parts['word/settings.xml'])
    if settings.find('{'+W+'}embedTrueTypeFonts') is None:ET.SubElement(settings,'{'+W+'}embedTrueTypeFonts')
    parts['word/settings.xml']=ET.tostring(settings,encoding='utf-8',xml_declaration=True)
    temp=Path(file).with_suffix('.tmp.docx')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    temp.replace(file)
def style_doc(doc,footer_text):
    sec=doc.sections[0];sec.page_height=Inches(11.69);sec.page_width=Inches(8.27)
    sec.top_margin=sec.bottom_margin=Inches(.7);sec.left_margin=sec.right_margin=Inches(.75)
    for n in ['Normal','Title','Heading 1','Heading 2','Heading 3','List Bullet']:
        st=doc.styles[n];st.font.name='Sarabun';st.font.color.rgb=RGBColor(0,0,0)
        rpr=st.element.get_or_add_rPr()
        for key in ['ascii','hAnsi','eastAsia','cs']:rpr.rFonts.set(qn('w:'+key),'Sarabun')
        for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme','csTheme']:
            rpr.rFonts.attrib.pop(qn('w:'+key),None)
        st.font.size=Pt(12 if n in ['Normal','List Bullet'] else 22 if n=='Title' else 16)
        cs=rpr.find(qn('w:szCs'))
        if cs is None:cs=OxmlElement('w:szCs');rpr.append(cs)
        cs.set(qn('w:val'),str(int(st.font.size.pt*2)))
        if st.element.pPr is not None:
            for border in list(st.element.pPr.findall(qn('w:pBdr'))):st.element.pPr.remove(border)
        st.paragraph_format.space_after=Pt(7)
    doc.styles['Normal'].paragraph_format.line_spacing=1.13
    footer=sec.footer.paragraphs[0];footer.text=footer_text+'  |  '
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
def render_spec(spec,outdir,basename='report',pdf=True):
    out=Path(outdir).resolve();out.mkdir(parents=True,exist_ok=True)
    doc=Document();style_doc(doc,spec.get('footer','รายงานจากข้อมูลที่ระบุ'));pages=[]
    for pi,page in enumerate(spec['pages']):
        if pi:doc.add_page_break()
        fragments=[]
        for block in page['blocks']:
            kind=block['type'];text=block.get('text','')
            if kind=='title':doc.add_paragraph(text,'Title');fragments.append('<h1>'+h(text)+'</h1>')
            elif kind=='heading':doc.add_heading(text,level=2);fragments.append('<h2>'+h(text)+'</h2>')
            elif kind=='paragraph':doc.add_paragraph(text);fragments.append('<p>'+h(text)+'</p>')
            elif kind=='bullets':
                for s in block['items']:doc.add_paragraph(s,'List Bullet')
                fragments.append('<ul>'+''.join('<li>'+h(s)+'</li>' for s in block['items'])+'</ul>')
            elif kind=='table':
                rows=[block['headers'],*block['rows']];t=doc.add_table(rows=0,cols=len(rows[0]));t.style='Table Grid'
                for ri,row in enumerate(rows):
                    cells=t.add_row().cells
                    for ci,value in enumerate(row):
                        cells[ci].text=str(value)
                        for p in cells[ci].paragraphs:
                            for run in p.runs:run.font.size=Pt(10)
                        if ri==0:
                            for run in cells[ci].paragraphs[0].runs:run.bold=True
                            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EEF5');cells[ci]._tc.get_or_add_tcPr().append(shade)
                fragments.append('<table>'+''.join('<tr>'+''.join(('<th>' if ri==0 else '<td>')+h(v)+('</th>' if ri==0 else '</td>') for v in row)+'</tr>' for ri,row in enumerate(rows))+'</table>')
            elif kind=='image':
                f=Path(block['path']).resolve();doc.add_picture(str(f),width=Inches(block.get('width',6.6)))
                doc.add_paragraph(block.get('caption',''))
                encoded=base64.b64encode(f.read_bytes()).decode()
                fragments.append('<figure><img src="data:image/png;base64,'+encoded+'"><figcaption>'+h(block.get('caption',''))+'</figcaption></figure>')
            else:raise ValueError('Unsupported block '+kind)
        pages.append('<section>'+''.join(fragments)+'<footer>'+h(spec.get('footer','ข้อมูลสมมติเพื่อการฝึก'))+f' · {pi+1}</footer></section>')
    doc.save(out/(basename+'.docx'))
    embed_docx_fonts(out/(basename+'.docx'))
    css=f'''@font-face{{font-family:Sarabun;src:url("{font_uri('Sarabun-Regular.ttf')}");font-weight:400}}
    @font-face{{font-family:Sarabun;src:url("{font_uri('Sarabun-Bold.ttf')}");font-weight:700}}
    @page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0;color:#182433;font-family:Sarabun,sans-serif;font-size:12pt;line-height:1.48}}
    section{{width:210mm;min-height:297mm;padding:17mm 19mm 19mm;position:relative;break-after:page;background:white}}
    section:last-child{{break-after:auto}}h1{{font-size:23pt;line-height:1.35;margin:0 0 12pt;color:#000}}h2{{font-size:15pt;margin:12pt 0 6pt;color:#000}}
    p{{margin:6pt 0 10pt}}ul{{padding-left:20pt;margin:6pt 0 10pt}}li{{margin:3pt 0}}table{{border-collapse:collapse;width:100%;font-size:10pt;margin:10pt 0}}
    th,td{{text-align:left;border:1px solid #cbd5e1;padding:7pt 8pt}}th{{background:#e8eef5}}figure{{margin:9pt 0}}img{{width:100%;display:block}}figcaption{{font-size:9pt;color:#475569}}
    footer{{position:absolute;left:19mm;right:19mm;bottom:10mm;border-top:1px solid #cbd5e1;padding-top:5pt;color:#64748b;font-size:9pt}}
    @media screen{{body{{background:#dce4ed}}section{{margin:12px auto}}}}'''
    htmlfile=out/(basename+'.html');htmlfile.write_text('<!DOCTYPE html><html lang="th"><meta charset="utf-8"><title>'+h(spec.get('title',basename))+'</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>',encoding='utf-8')
    portable=json.loads(json.dumps(spec))
    for page in portable['pages']:
        for block in page['blocks']:
            if block['type']=='image':block['path']=os.path.relpath(Path(block['path']).resolve(),out).replace('\\','/')
    (out/(basename+'-content.json')).write_text(json.dumps(portable,ensure_ascii=False,indent=2),encoding='utf-8')
    if pdf:print_pdf(htmlfile,out/(basename+'.pdf'))
    return out/(basename+'.docx')
def find_browser():
    candidates=[os.environ.get('CHROME_PATH'),shutil.which('google-chrome'),shutil.which('chromium'),
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      r'C:\Program Files\Google\Chrome\Application\chrome.exe',r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']
    return next((str(x) for x in candidates if x and Path(x).is_file()),None)
def print_pdf(htmlfile,destination):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browserpath=find_browser()
        browser=p.chromium.launch(executable_path=browserpath,headless=True) if browserpath else p.chromium.launch(headless=True)
        try:
            page=browser.new_page();page.goto(Path(htmlfile).resolve().as_uri());page.evaluate('document.fonts.ready')
            issues=page.evaluate('''() => [...document.querySelectorAll('section')].flatMap((s,i)=>{
              let f=s.querySelector('footer').getBoundingClientRect(),b=s.getBoundingClientRect();
              return [...s.children].filter(x=>x.tagName!=='FOOTER'&&x.getBoundingClientRect().bottom>f.top-8).map(x=>({page:i+1,text:x.innerText.slice(0,100)}));})''')
            if issues:raise ValueError('Report content overlaps footer: '+json.dumps(issues,ensure_ascii=False))
            page.pdf(path=str(destination),format='A4',print_background=True,prefer_css_page_size=True)
        finally:browser.close()
def report_spec(analysis,charts):
    a=json.loads(Path(analysis).read_text(encoding='utf-8'));t=a['totals'];q=a['quality'];m=a['monthly'];chartdir=Path(charts).resolve()
    manifest=json.loads((chartdir/'chart-manifest.json').read_text(encoding='utf-8'))
    import hashlib
    if manifest['analysis_sha256']!=hashlib.sha256(Path(analysis).read_bytes()).hexdigest():raise ValueError('Charts were made from a different analysis file.')
    f=lambda v:f'{v:,.0f}';p=lambda v:f'{v:.1%}' if v is not None else 'ไม่มีข้อมูล';n=lambda v:f'{v:.2f}' if v is not None else 'ไม่มีข้อมูล'
    ratechange=(m[-1]['on_time_rate']-m[0]['on_time_rate'])*100 if all(v['on_time_rate'] is not None for v in [m[0],m[-1]]) else None
    firstlast=f"อัตราตรงเวลาจาก {p(m[0]['on_time_rate'])} เป็น {p(m[-1]['on_time_rate'])}"+(f' เปลี่ยน {ratechange:+.1f} จุดร้อยละ' if ratechange is not None else '')
    low=min((v for v in m if v['on_time_rate'] is not None),key=lambda v:v['on_time_rate'],default=None)
    source=f"{a['source']} / {a['sheet']} แถว 2–{q['input_rows']+1} ตัดซ้ำแถว {q['duplicate_rows_removed']} ดูหลักฐานและสูตรใน evidence.json และ analysis.json"
    title='รายงานผลดำเนินงานและคุณภาพบริการ'
    label='ข้อมูลสมมติเพื่อการฝึก ไม่ใช่ผลการดำเนินงานจริง' if a.get('synthetic') else 'รายงานจากข้อมูลที่ผู้ใช้ระบุ'
    return {'title':title,'footer':label,'pages':[
      {'blocks':[{'type':'title','text':title},{'type':'paragraph','text':f"ช่วง {a['period'][0]} ถึง {a['period'][1]} | เอกสารสรุปสำหรับพิจารณาการปรับปรุงบริการ"},
       {'type':'heading','text':'สรุปผลที่พบ'},
       {'type':'paragraph','text':f"รับงาน {f(t['received'])} งาน ปิดงาน {f(t['completed'])} งาน ในจำนวนงานปิดมี {f(t['on_time_completed'])} งานที่ตรงเวลา คิดเป็น {p(t['on_time_rate'])} ระยะเวลาดำเนินงานเฉลี่ย {n(t['average_days'])} วันทำการต่องาน"},
       {'type':'table','headers':['ตัวชี้วัด','ผลรวมช่วงรายงาน','หน่วย / ฐานคำนวณ'],'rows':[
         ['งานรับเข้า',f(t['received']),'งาน'],['งานปิด',f(t['completed']),'งานที่ปิดในช่วงรายงาน'],
         ['อัตราตรงเวลา',p(t['on_time_rate']),'งานตรงเวลา / งานปิด'],['ระยะเวลาเฉลี่ย',n(t['average_days']),'วันทำการต่องาน'],
         ['ความพึงพอใจ',n(t['satisfaction']),'คะแนนจาก 5 เฉพาะข้อมูลที่มีคะแนน']]},
       {'type':'paragraph','text':firstlast+' ข้อมูลนี้แสดงแนวโน้มเชิงพรรณนา ยังไม่ยืนยันสาเหตุของการเปลี่ยนแปลง'},
       {'type':'heading','text':'ประเด็นที่ควรติดตาม'},
       {'type':'bullets','items':[f"ตรวจงานล่าช้าในเดือน {low['month']} ซึ่งมีอัตราตรงเวลา {p(low['on_time_rate'])}" if low else 'ตรวจข้อมูลตัวหารก่อนคำนวณอัตรา',
         'ติดตามภาระงานรายช่องทางร่วมกับระยะเวลาดำเนินงาน ก่อนตัดสินใจปรับทรัพยากร',
         f"ยืนยันคะแนนความพึงพอใจที่ขาด {len(q['missing_score_rows'])} จุดก่อนสรุปภาพรวมผู้ตอบทั้งหมด"]},
       {'type':'paragraph','text':'ที่มา: '+source}]},
      {'blocks':[{'type':'title','text':'ปริมาณงานและภาระบริการ'},
       {'type':'image','path':str(chartdir/'workload.png'),'caption':manifest['figures'][0]['caption']+' | ที่มา: '+a['source']+' / '+a['sheet']},
       {'type':'table','headers':['เดือน','รับเข้า (งาน)','ปิด (งาน)','เฉลี่ย (วันทำการ)'],'rows':[[r['month'],f(r['received']),f(r['completed']),n(r['average_days'])] for r in m]},
       {'type':'paragraph','text':'งานรับเข้าและงานปิดเป็นคนละกลุ่มเวลา งานปิดอาจรวมงานค้างจากเดือนก่อน จึงไม่ตีความปิด/รับเข้าเป็นอัตราสำเร็จของงานรับเข้าชุดเดียวกัน'}]},
      {'blocks':[{'type':'title','text':'ความตรงเวลาและความแตกต่างรายช่องทาง'},
       {'type':'image','path':str(chartdir/'timeliness.png'),'caption':manifest['figures'][1]['caption']+' | ที่มา: '+a['source']+' / '+a['sheet']},
       {'type':'table','headers':['ช่องทาง','งานปิด','ตรงเวลา','เฉลี่ย (วันทำการ)'],'rows':[[r['service'],f(r['completed']),p(r['on_time_rate']),n(r['average_days'])] for r in a['by_service']]},
       {'type':'paragraph','text':firstlast+' การเปรียบเทียบช่องทางยังต้องคำนึงถึงประเภทและความยากของงานซึ่งไม่มีในตารางนี้'}]},
      {'blocks':[{'type':'title','text':'วิธีวิเคราะห์ ข้อจำกัด และข้อเสนอแนะ'},
       {'type':'heading','text':'คุณภาพข้อมูลและวิธีคำนวณ'},
       {'type':'bullets','items':[f"ข้อมูลเดิม {q['input_rows']} แถว ใช้ {q['used_rows']} แถว ตัดแถวซ้ำทุกช่องที่แถว {q['duplicate_rows_removed']} โดยไม่แก้ต้นฉบับ",
        'อัตราตรงเวลา = ผลรวมงานตรงเวลา / ผลรวมงานปิด ไม่เฉลี่ยเปอร์เซ็นต์ของแต่ละแถว',
        'ระยะเวลาเฉลี่ย = ผลรวมวันทำการของงานปิด / ผลรวมงานปิด',
        f"คะแนนเฉลี่ยถ่วงน้ำหนัก {n(t['satisfaction'])}/5 ใช้ผู้ตอบ {t['scored_responses']:,} จาก {t['survey_responses']:,} คน ครอบคลุม {p(t['score_coverage'])} คะแนนขาดที่แถว {q['missing_score_rows']} ไม่แทนด้วยศูนย์"]},
       {'type':'heading','text':'ข้อจำกัด'},
       {'type':'paragraph','text':'ข้อมูลเป็นระดับเดือนและช่องทาง ไม่มีรายละเอียดรายงานหรือเหตุผลล่าช้า จึงไม่พิสูจน์เหตุและผล คะแนนของกลุ่มที่ขาดอาจต่างจากกลุ่มที่มีข้อมูล และข้อเสนอแนะต่อไปนี้เป็นแนวทางตรวจสอบ ไม่ใช่ข้อเท็จจริงที่พิสูจน์แล้ว'},
       {'type':'heading','text':'ข้อเสนอแนะ'},
       {'type':'bullets','items':['เจ้าของข้อมูลตรวจและยืนยันคะแนนที่ขาด พร้อมเพิ่มการตรวจ key ซ้ำก่อนส่งข้อมูลรอบถัดไป',
        'ผู้รับผิดชอบบริการสุ่มตรวจงานล่าช้าในเดือนที่อัตราต่ำ เพื่อหาเหตุผลจริงก่อนจัดทำมาตรการ',
        'ทีมงานติดตามตัวชี้วัดเดิมในรอบถัดไป และบันทึกประเภทงานเพื่อเปรียบเทียบช่องทางได้เหมาะสมขึ้น']},
       {'type':'heading','text':'แหล่งข้อมูลและการตรวจย้อนกลับ'},
       {'type':'paragraph','text':source+'; ขอบเขตและบริบทดูไฟล์นำเข้าและนิยามตัวชี้วัด; '+label}]}
    ]}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis');p.add_argument('--charts');p.add_argument('--spec');p.add_argument('--output',required=True);p.add_argument('--name',default='report');p.add_argument('--no-pdf',action='store_true')
    a=p.parse_args()
    if a.spec:
        specfile=Path(a.spec).resolve();spec=json.loads(specfile.read_text(encoding='utf-8'))
        for page in spec['pages']:
            for block in page['blocks']:
                if block['type']=='image' and not Path(block['path']).is_absolute():block['path']=str(specfile.parent/block['path'])
    elif a.analysis and a.charts:spec=report_spec(a.analysis,a.charts)
    else:p.error('Use --spec or both --analysis and --charts')
    render_spec(spec,a.output,a.name,not a.no_pdf);print('DOCX and HTML'+('' if a.no_pdf else '/PDF')+' saved.')
