"""Build version-history PDF and editable PPTX from site/version_history.json.

Both downloads and the in-dashboard history share one reviewed JSON source.
"""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"site"/"version_history.json"
OUT=ROOT/"site"/"docs"
BG="#0B1423"; CARD="#142840"; WHITE="#F0F7FD"; BLUE="#6ABFFF"; MUTED="#B2C9E0"
def rgb(s):return RGBColor.from_string(s[1:])
def page_data(data):
    entries=data["entries"]
    pages=[
        ("RELEASE HISTORY","AI Global Observatory",
         "생성형 AI 글로벌 평가 플랫폼 · 버전별 전체 개발 이력",
         [("현재 버전",data["latest_version"]),("업데이트",data["updated_on"]),
          ("공식 기록",f"{len(entries)} verified releases")]),
        ("EXECUTIVE SUMMARY","개발 전체 흐름",
         "평가 데이터 → 수집 자동화 → 라이선스 → 뉴스 동향 → 개발 히스토리",
         [("기반 구축","공식 평가 수집기와 GitHub Pages 주간 게시"),
          ("분석 심화","Arena 순위·모델 비교·주간 추세·모바일"),
          ("출처 신뢰성","공개 이용조건 및 평가 방법론을 분리"),
          ("운영 관리","일일 AI 업데이트·버전별 변경 이력과 공유 문서")])
    ]
    for item in entries:
        pages.append((item["version"],item["version"]+"  "+item["title"],
          item["summary"],
          [("WHY · 개발 배경",item["background"]),
           ("WHAT · 핵심 변경",item["changes"]),
           ("VALUE · 사용자 가치",item["value"])]))
    pages.append(("NEXT RELEASE RULE","차기 버전 관리 규칙",
       "Single source of truth: site/version_history.json",
       [("01","릴리스마다 버전·날짜·근거 링크·한줄 요약 기록"),
        ("02","동일 JSON으로 사이드 History 패널 업데이트"),
        ("03","배포 워크플로에서 PDF와 PPTX를 함께 생성"),
        ("04","변경사항 단위 테스트와 Pages 파일 검증")]))
    return pages
def register_pdf_font():
 """Prefer an embedded Korean TrueType font; never require apt on CI runners.

 ReportLab's built-in Adobe-Korea1 CID fallback keeps Korean text searchable
 even on fresh GitHub runners without Nanum fonts. PDF viewers may substitute
 a local CJK font for the CID face.
 """
 for p in ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
           "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
           "/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf"):
  if Path(p).is_file():
   pdfmetrics.registerFont(TTFont("AIHistoryKorean",p))
   return "AIHistoryKorean"
 pdfmetrics.registerFont(UnicodeCIDFont("HYGothic-Medium"))
 print("NOTICE: no embeddable Korean TTF installed; using ReportLab Adobe-Korea1 CID fallback")
 return "HYGothic-Medium"
def ppt_text(sl,s,x,y,w,h,size=16,color=WHITE,bold=False):
 t=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame
 t.clear();t.word_wrap=True
 t.margin_left=t.margin_right=t.margin_top=t.margin_bottom=Pt(0)
 for i,line in enumerate(str(s).split("\n")):
  pp=t.paragraphs[0] if not i else t.add_paragraph()
  pp.text=line;pp.font.name="NanumGothic";pp.font.size=Pt(size);pp.font.bold=bold;pp.font.color.rgb=rgb(color)
def ppt(pages,path):
 prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
 for i,(tag,title,sub,blocks) in enumerate(pages):
  sl=prs.slides.add_slide(prs.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=rgb(BG)
  ppt_text(sl,"AI OBSERVATORY / "+tag,.68,.38,11,.3,12,BLUE,True)
  ppt_text(sl,title,.68,.98,11.9,.76,30,WHITE,True)
  ppt_text(sl,sub,.68,1.85,11.8,.7,17,MUTED)
  step=1.08 if len(blocks)<=3 else .77;start=2.8
  for j,(label,value) in enumerate(blocks):
   y=start+j*step
   shape=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(.68),Inches(y),Inches(11.95),Inches(step-.1))
   shape.fill.solid();shape.fill.fore_color.rgb=rgb(CARD);shape.line.color.rgb=rgb("#355777")
   ppt_text(sl,label,.95,y+.13,3.0,.4,15,BLUE,True)
   ppt_text(sl,value,3.7,y+.11,8.55,step-.18,16 if step>1 else 14,WHITE)
  ppt_text(sl,f"GitHub commits + implementation history  |  {i+1:02d} / {len(pages):02d}",.68,7.02,12,.27,10,MUTED)
 prs.save(path)
def pdf(pages,path):
 font=register_pdf_font()
 c=canvas.Canvas(str(path),pagesize=(960,540));c.setTitle("AI Global Observatory Version History")
 def words(s,maxw,size):
  lines=[];line=""
  for word in str(s).split(" "):
   probe=(line+" "+word).strip()
   if pdfmetrics.stringWidth(probe,font,size)>maxw and line:lines.append(line);line=word
   else:line=probe
  if line:lines.append(line)
  return lines
 def write(s,x,y,size,color,maxw=850,maxlines=3):
  c.setFillColor(HexColor(color));c.setFont(font,size)
  for j,line in enumerate(words(s,maxw,size)[:maxlines]):c.drawString(x,540-y-j*(size*1.45),line)
 for i,(tag,title,sub,blocks) in enumerate(pages):
  c.setFillColor(HexColor(BG));c.rect(0,0,960,540,fill=1,stroke=0)
  c.setFillColor(HexColor(BLUE));c.rect(0,533,960,7,fill=1,stroke=0)
  write("AI OBSERVATORY / "+tag,47,36,10,BLUE);write(title,47,89,27,WHITE,850,2)
  write(sub,48,139,14,MUTED)
  step=78 if len(blocks)<=3 else 56
  for j,(label,value) in enumerate(blocks):
   top=201+j*step
   c.setFillColor(HexColor(CARD));c.roundRect(47,540-top-(step-9),866,step-9,9,stroke=0,fill=1)
   write(label,65,top+16,12,BLUE,205,2)
   write(value,264,top+15,14 if step>60 else 12,WHITE,619,3)
  write(f"GitHub commits + implementation history    {i+1:02d} / {len(pages):02d}",47,510,9,MUTED)
  c.showPage()
 c.save()
def main():
 d=json.loads(SRC.read_text(encoding="utf8"));e=d["entries"]
 assert d["latest_version"]==e[-1]["version"]
 assert len({r["version"] for r in e})==len(e)
 OUT.mkdir(parents=True,exist_ok=True);pages=page_data(d)
 ppt(pages,OUT/"ai-observatory-version-history.pptx")
 pdf(pages,OUT/"ai-observatory-version-history.pdf")
 print(f"Built {len(pages)} release history slides in PPTX and PDF")
if __name__=="__main__":main()
