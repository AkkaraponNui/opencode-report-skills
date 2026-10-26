import argparse,hashlib,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager
from matplotlib.ticker import PercentFormatter,StrMethodFormatter
import pandas as pd

ASSETS=Path(__file__).resolve().parents[1]/'assets'
def configure():
    font=ASSETS/'Sarabun-Regular.ttf'
    fontManager.addfont(str(font)); fontManager.addfont(str(ASSETS/'Sarabun-Bold.ttf'))
    plt.rcParams.update({'font.family':'Sarabun','font.size':12,'axes.titleweight':'bold',
      'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,
      'axes.spines.bottom':False,'axes.labelcolor':'#334155','text.color':'#172b4d',
      'xtick.color':'#475569','ytick.color':'#475569','svg.fonttype':'none',
      'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
def save(fig,out,name,title,caption,data,source):
    fig.text(.01,-.035,caption+'\nที่มา: '+source,fontsize=8,color='#64748b',va='top')
    fig.savefig(out/(name+'.png'),dpi=200,bbox_inches='tight')
    fig.savefig(out/(name+'.svg'),bbox_inches='tight')
    plt.close(fig)
    pd.DataFrame(data).to_csv(out/(name+'-data.csv'),index=False,encoding='utf-8-sig')
    return {'id':name,'title':title,'png':name+'.png','svg':name+'.svg','caption':caption,
      'data':name+'-data.csv','source':source}
def run(analysis,outdir):
    configure();p=Path(analysis).resolve();a=json.loads(p.read_text(encoding='utf-8'))
    out=Path(outdir).resolve();out.mkdir(parents=True,exist_ok=True)
    months=[r['month'] for r in a['monthly']]; x=list(range(len(months)))
    rows=a['monthly']; source=f"{a['source']} / {a['sheet']}; month-level aggregates; duplicate rows removed"
    fig,ax=plt.subplots(figsize=(10.5,4.9),layout='constrained')
    ax.bar([v-.18 for v in x],[r['received'] for r in rows],width=.34,color='#203c73',label='รับเข้า')
    ax.bar([v+.18 for v in x],[r['completed'] for r in rows],width=.34,color='#09857f',label='ปิดงาน')
    title='ปริมาณงานรายเดือน'; ax.set_title(title,loc='left',pad=20,fontsize=19)
    ax.set_xticks(x,months);ax.set_ylabel('งาน');ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'));ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    ax.legend(frameon=False,ncol=2,loc='upper left');
    for xx,r in zip(x,rows): ax.annotate(f"{r['received']:,}",(xx-.18,r['received']),xytext=(0,5),textcoords='offset points',ha='center',fontsize=10)
    manifest=[save(fig,out,'workload',title,'งานปิดในเดือนอาจรวมงานค้าง ไม่ใช่กลุ่มเดียวกับงานรับเข้า',
      [{'month':r['month'],'received':r['received'],'completed':r['completed']} for r in rows],source)]
    fig,ax=plt.subplots(figsize=(10.5,4.9),layout='constrained')
    rates=[r['on_time_rate'] if r['on_time_rate'] is not None else float('nan') for r in rows]
    ax.plot(x,rates,color='#09857f',linewidth=3,marker='o',markersize=8)
    ax.fill_between(x,rates,alpha=.07,color='#09857f')
    title='อัตรางานเสร็จตรงเวลา';ax.set_title(title,loc='left',pad=20,fontsize=19)
    ax.set_xticks(x,months);ax.set_ylabel('งานตรงเวลา / งานปิด');ax.set_ylim(0,1)
    ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    for xx,v in zip(x,rates):
        if math.isfinite(v): ax.annotate(f'{v:.1%}',(xx,v),xytext=(0,10),textcoords='offset points',ha='center',fontsize=11)
    manifest.append(save(fig,out,'timeliness',title,'คำนวณจากผลรวมงานตรงเวลาหารผลรวมงานปิดในแต่ละเดือน',
      [{'month':r['month'],'on_time_completed':r['on_time_completed'],'completed':r['completed'],'rate':r['on_time_rate']} for r in rows],source))
    result={'analysis_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'figures':manifest}
    (out/'chart-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
def generic(csvfile,xcol,ycol,kind,title,ylabel,outdir):
    configure();df=pd.read_csv(csvfile);out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    if df[xcol].duplicated().any(): raise ValueError('Duplicate x labels; explicitly aggregate before plotting.')
    y=pd.to_numeric(df[ycol],errors='raise')
    if y.isna().any(): raise ValueError('Missing y values; resolve or disclose before plotting.')
    fig,ax=plt.subplots(figsize=(10.5,4.9),layout='constrained')
    if kind=='bar': ax.bar(df[xcol].astype(str),y,color='#203c73');ax.set_ylim(bottom=min(0,y.min()))
    else: ax.plot(df[xcol].astype(str),y,marker='o',color='#09857f',linewidth=2.5)
    ax.set_title(title,loc='left',fontsize=19,pad=18);ax.set_ylabel(ylabel);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    return save(fig,out,'custom-chart',title,'ตรวจช่วงเวลา หน่วย และแหล่งข้อมูลก่อนเผยแพร่',df[[xcol,ycol]].to_dict('records'),str(Path(csvfile).resolve()))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis');p.add_argument('--output',required=True)
    p.add_argument('--csv');p.add_argument('--x');p.add_argument('--y');p.add_argument('--kind',choices=['bar','line'],default='bar');p.add_argument('--title',default='ผลวิเคราะห์');p.add_argument('--ylabel',default='ค่า')
    a=p.parse_args()
    if a.csv:
        if not a.x or not a.y: p.error('--csv requires --x and --y')
        generic(a.csv,a.x,a.y,a.kind,a.title,a.ylabel,a.output)
    elif a.analysis: run(a.analysis,a.output)
    else:p.error('Provide --analysis or --csv')
    print('Charts saved.')
