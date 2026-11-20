"""Перестворює PowerPoint на основі перевірених результатів аналізу."""
from pathlib import Path
import json
import pandas as pd
from PIL import Image as PILImage
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT/'outputs'/'figures'
METRICS = ROOT/'outputs'/'tables'
S = json.loads((ROOT/'outputs'/'metadata'/'run_info.json').read_text(encoding='utf-8'))
CV = pd.read_csv(METRICS/'cv_summary.csv')
TEST = pd.read_csv(METRICS/'test_metrics.csv')
C = pd.read_csv(METRICS/'base_coefficients_cluster95.csv').set_index('term')
D = S['diagnostics']

prs = Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
NAVY='#15253C'; INK='#22334D'; MID='#566A83'; BLUE='#3F6EAE'; TEAL='#3D9088'; ORANGE='#D97955'; BG='#F8FAFD'; PALE='#E8EEF6'; WHITE='#FFFFFF'; LINE='#D9E2ED'; GOLD='#B39953'

def rgb(code):return RGBColor.from_string(code.lstrip('#'))

def box(slide, x,y,w,h,fill=WHITE,stroke=None,radius=True):
    shp=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid();shp.fill.fore_color.rgb=rgb(fill)
    shp.line.fill.background() if not stroke else None
    if stroke:shp.line.color.rgb=rgb(stroke);shp.line.width=Pt(.8)
    if radius:
        try:shp.adjustments[0]=.13
        except Exception:pass
    return shp

def text(slide,value,x,y,w,h,fs=19,color=INK,bold=False,align='left',font='Aptos',margin=0,italic=False):
    t=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=t.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=Inches(margin);tf.margin_right=Inches(margin)
    tf.margin_top=Inches(.02);tf.margin_bottom=Inches(.02)
    mapping={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}
    for i,line in enumerate(str(value).split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=line;p.alignment=mapping.get(align,PP_ALIGN.LEFT)
        p.space_before=Pt(0);p.space_after=Pt(4)
        for r in p.runs:
            r.font.name=font;r.font.size=Pt(fs);r.font.bold=bold;r.font.italic=italic;r.font.color.rgb=rgb(color)
    return t

def img(slide, filename, x,y,w,h):
    path=FIG/filename
    with PILImage.open(path) as im: aw,ah=im.size
    iw,ih=w,h
    if aw/ah > w/h: ih=w*ah/aw
    else: iw=h*aw/ah
    slide.shapes.add_picture(str(path),Inches(x+(w-iw)/2),Inches(y+(h-ih)/2),width=Inches(iw),height=Inches(ih))

def add_slide(title, eyebrow='ЛАБОРАТОРНА РОБОТА №3', page=None):
    sl=prs.slides.add_slide(prs.slide_layouts[6]);
    box(sl,0,0,13.333,7.5,BG,radius=False)
    box(sl,0,0,.14,7.5,TEAL,radius=False)
    text(sl,eyebrow.upper(),.57,.35,10,.25,10,TEAL,True)
    text(sl,title,.55,.81,12.2,.73,28,NAVY,True)
    box(sl,.58,1.6,12.15,.018,LINE,radius=False)
    box(sl,.58,7.14,12.15,.012,LINE,radius=False)
    text(sl,'ВЛАСЕНКО АНДРІЙ  ·  КН-41  ·  GAPMINDER',.61,7.19,10,.2,9,MID)
    text(sl,f'{len(prs.slides):02d}',12.24,7.13,.4,.27,10,MID,align='right')
    return sl

def pill(slide,label,x,y,w,fg=TEAL,bg='#E4F1EE'):
    box(slide,x,y,w,.39,bg,radius=True)
    text(slide,label,x+.07,y+.055,w-.14,.23,11,fg,True,align='center')

def key_metric(slide,value,label,x,y,w=3.2,accent=TEAL):
    box(slide,x,y,w,1.18,WHITE,LINE)
    text(slide,str(value),x+.2,y+.15,w-.4,.47,29,accent,True)
    text(slide,label,x+.2,y+.76,w-.4,.28,12,MID)

def point(slide,tag,body,x,y,w,tag_color=TEAL):
    box(slide,x,y,.09,.84,tag_color,radius=False)
    text(slide,tag,x+.25,y+.05,w-.3,.26,15,INK,True)
    text(slide,body,x+.25,y+.39,w-.3,.42,13,MID)

# 1. Cover
sl=prs.slides.add_slide(prs.slide_layouts[6]);box(sl,0,0,13.333,7.5,NAVY,radius=False)
box(sl,0,0,.2,7.5,TEAL,radius=False)
pill(sl,'АНАЛІЗ ТА ВІЗУАЛІЗАЦІЯ ДАНИХ',.73,.69,4.0,TEAL,'#E3F0EF')
text(sl,'Чи можна передбачити\nтривалість життя країни?',.7,1.65,11.5,2.1,39,WHITE,True)
text(sl,'Лабораторна робота №3 · Основи регресійного моделювання',.75,4.08,11.5,.5,21,'#C7D8EA')
box(sl,.74,5.3,3.0,.025,TEAL,radius=False)
text(sl,'Gapminder · 1952–2007\nВласенко Андрій · КН-41\nPython · 18.11.2026',.75,5.62,8.6,1.22,17,WHITE)
text(sl,'03',11.0,5.82,1.6,1.05,53,'#6A8DAA',True,align='right')

# 2. Goal
sl=add_slide('Питання: наскільки точно прогнозуємо для нових країн?','01  ·  МЕТА')
text(sl,'Маємо показники добробуту, року й регіону. Чи достатньо їх, щоб оцінити тривалість життя країни, яка не входила в навчання?',.79,1.96,11.8,1.1,23,NAVY,True)
key_metric(sl,'lifeExp','ціль: роки життя',.83,3.34,3.5,BLUE)
key_metric(sl,'країна-рік','одиниця спостереження',4.92,3.34,3.5,TEAL)
key_metric(sl,'нові країни','ціль групового тесту',9.02,3.34,3.5,ORANGE)
text(sl,'Прогноз історичних спостережень 1952–2007, не екстраполяція в майбутнє.',.84,5.36,11.4,.76,18,MID)

# 3. Split
sl=add_slide('142 країни · 1704 спостереження · 0 пропусків','02  ·  ДАНІ')
key_metric(sl,'1704','країна-рік',.84,1.97,3.63,BLUE)
key_metric(sl,'142','країни',4.86,1.97,3.63,TEAL)
key_metric(sl,'1952–2007','12 часових зрізів',8.88,1.97,3.63,ORANGE)
text(sl,'Поділ виконано за країнами (не випадково за рядками):',.83,3.72,11.5,.43,20,INK,True)
box(sl,.85,4.34,8.96,.67,PALE)
box(sl,.85,4.34,6.69,.67,BLUE)
text(sl,'НАВЧАННЯ: 106 КРАЇН · 1272 РЯДКИ',.97,4.5,6.54,.27,14,WHITE,True)
text(sl,'ТЕСТ',7.58,4.5,2.01,.27,14,INK,True,align='center')
text(sl,'Тестові 36 країн повністю відсутні у навчанні та CV.',.86,5.46,11.5,.54,20,TEAL,True)
text(sl,'Джерело: Gapminder (локальний CSV із Plotly Express).',.86,6.38,11.2,.3,13,MID)

# 4. Hypotheses
sl=add_slide('Від наукових джерел — до перевірюваних гіпотез','03  ·  ЛІТЕРАТУРА')
box(sl,.78,1.88,5.67,2.0,WHITE,LINE)
box(sl,6.81,1.88,5.67,2.0,WHITE,LINE)
text(sl,'PRESTON, 1975',1.02,2.04,5.1,.3,16,TEAL,True)
text(sl,'Рівень доходу й смертність пов’язані; історичний час може змінювати залежність.',1.02,2.52,5.05,1.0,18,INK)
text(sl,'PRITCHETT & SUMMERS, 1996',7.05,2.04,5.08,.31,16,BLUE,True)
text(sl,'Дохід інформативний для здоров’я, але проста OLS не встановлює причинності.',7.05,2.52,5.1,1.0,18,INK)
point(sl,'H1 · Дохід (+)','Позитивний коефіцієнт log₁₀(ВВП) та 95% ДІ.',.92,4.46,5.48,TEAL)
point(sl,'H2 · Час (+)','Позитивний коефіцієнт року та 95% ДІ.',6.83,4.46,5.54,BLUE)
text(sl,'Обидві гіпотези — розвідувальні після EDA лабораторної №2.',1.0,6.19,11.5,.45,16,ORANGE,True)

# 5. EDA income
sl=add_slide('EDA: вищий дохід пов’язаний із довшим життям','04  ·  EDA НАВЧАННЯ')
box(sl,.73,1.81,8.85,4.94,WHITE,LINE)
img(sl,'02_train_income.png',.81,1.88,8.7,4.73)
text(sl,'Що підказує графік',9.77,2.02,2.9,.38,19,TEAL,True)
point(sl,'Логарифм ВВП','Широкий діапазон доходів.',9.73,2.79,2.8,BLUE)
point(sl,'Можлива кривизна','Перевіряємо квадрат.',9.73,3.86,2.8,ORANGE)
point(sl,'Різні континенти','Перевіряємо взаємодію.',9.73,4.95,2.8,TEAL)

# 6. EDA time
sl=add_slide('EDA: історичний тренд і неоднорідність цілі','05  ·  EDA НАВЧАННЯ')
box(sl,.65,1.89,6.01,4.75,WHITE,LINE);box(sl,6.84,1.89,5.83,4.75,WHITE,LINE)
img(sl,'03_train_time.png',.76,2.07,5.78,4.32)
img(sl,'01_train_target.png',6.99,2.07,5.55,4.32)
text(sl,'Рік і континент потрібні як пояснювальні ознаки; розкид цілі — причина оцінювати RMSE.',.79,6.72,11.65,.23,13,MID)

# 7. CV
sl=add_slide('Захист від витоку: групове розбиття + 5-fold CV','06  ·  МЕТОДИ')
text(sl,'Країна ніколи не потрапляє одночасно у дві частини однієї перевірки.',.79,1.87,11.8,.53,20,INK,True)
box(sl,.83,2.65,7.55,.75,BLUE)
text(sl,'106 країн  ·  навчальна частина',1.09,2.85,7.0,.27,19,WHITE,True)
box(sl,8.64,2.65,3.85,.75,'#F2E3DA')
text(sl,'36 країн · тест',8.87,2.84,3.25,.27,18,ORANGE,True)
for i in range(5):
    y=3.76+i*.48
    for j in range(5): box(sl,.91+j*1.47,y,1.36,.34,'#E5ECF5' if i!=j else TEAL,radius=False)
    text(sl,f'{i+1}',8.01,y+.03,.25,.22,10,MID)
text(sl,'П’ять однакових фолдів для ВСІХ моделей',.94,6.49,7.36,.3,15,TEAL,True)
text(sl,'Вибір моделі — тільки за CV. Тест — один раз після вибору.',8.75,4.09,3.42,1.52,19,NAVY,True)

# 8. Models
sl=add_slide('Чотири кандидати · одна основна метрика','07  ·  МОДЕЛІ')
rows=[('01','Орієнтир','Середня lifeExp у навчанні'),('02','Лінійна OLS','log₁₀(ВВП) + рік + континент'),('03','Квадратична','Лінійна + квадрат log₁₀(ВВП)'),('04','Взаємодія','log₁₀(ВВП) × континент + рік')]
for i,(n,a,b) in enumerate(rows):
    y=1.89+i*1.04
    box(sl,.83,y,11.7,.89,WHITE,LINE)
    text(sl,n,1.08,y+.2,.66,.35,20,TEAL,True)
    text(sl,a,1.94,y+.17,3.03,.41,20,NAVY,True)
    text(sl,b,5.15,y+.20,6.8,.41,17,MID)
pill(sl,'ПЕРВИННА: RMSE  ↓',.93,6.33,3.22,BLUE,'#E3ECFA')
pill(sl,'ДОДАТКОВА: MAE  ↓',4.47,6.33,3.22,TEAL,'#E3F0EC')
text(sl,'Обидві в роках; порівнюємо середнє та SD за фолдами.',8.07,6.36,4.31,.3,12,MID)

# 9. Coefficients
sl=add_slide('H1 і H2: позитивні зв’язки за кластерними 95% ДІ','08  ·  БАЗОВА OLS')
for term,name,descr,color,x in [('log10_gdp','+10× ВВП','Вища lifeExp за фіксованих року і континенту',BLUE,.84),('year_5','+5 років часу','За фіксованих ВВП і континенту',TEAL,6.94)]:
    t=C.loc[term];v=t['estimate']
    box(sl,x,1.99,5.54,3.65,WHITE,LINE)
    text(sl,name,x+.25,2.27,4.9,.39,19,MID,True)
    text(sl,f'+{v:.2f} року'.replace('.',','),x+.23,3.03,4.99,.79,33,color,True)
    text(sl,f"95% ДІ: [{t['ci_low']:.2f}; {t['ci_high']:.2f}] року".replace('.',','),x+.26,4.05,5.0,.47,19,NAVY,True)
    text(sl,descr,x+.25,4.72,4.95,.71,14,MID)
text(sl,'ДІ враховують повторні вимірювання країн; асоціація ≠ причинний ефект.',.9,6.2,11.6,.48,17,ORANGE,True)

# 10. Diagnostics
sl=add_slide('OLS: залишки не цілком випадкові','09  ·  ДІАГНОСТИКА')
box(sl,.67,1.82,8.48,4.91,WHITE,LINE)
img(sl,'04_base_residuals.png',.77,1.94,8.27,4.62)
text(sl,'Бройш—Паган',9.44,2.04,3.21,.45,18,TEAL,True)
text(sl,'p = 2,28 × 10⁻¹⁴',9.43,2.61,3.1,.64,22,ORANGE,True)
text(sl,'Неоднакова дисперсія залишків.',9.43,3.35,3.0,.84,16,INK)
text(sl,'Впливові: 59 рядків',9.44,4.6,3.08,.67,20,NAVY,True)
text(sl,'За порогом Кука 4/n. Не видаляємо без підстав.',9.44,5.43,3.07,.77,15,MID)

# 11. CV
sl=add_slide('Переможець за CV — взаємодія доходу й континенту','10  ·  ВАЛІДАЦІЯ')
box(sl,.62,1.88,8.41,4.79,WHITE,LINE)
img(sl,'06_cv_comparison.png',.7,2.01,8.21,4.42)
text(sl,'Найкращий RMSE',9.25,2.13,3.28,.36,16,MID,True)
text(sl,'5,86 року',9.25,2.59,3.26,.67,29,TEAL,True)
text(sl,'Лінійна: 5,91 року',9.27,3.56,3.06,.36,17,NAVY)
text(sl,'Різниця лише 0,055 року — менша за SD між фолдами.',9.27,4.35,3.13,1.12,16,INK)
text(sl,'Вибір зроблено ДО відкриття тесту.',9.25,5.9,3.17,.63,15,ORANGE,True)

# 12. Test
sl=add_slide('Відкладений тест: RMSE 5,97 проти 13,18','11  ·  ФІНАЛЬНА ОЦІНКА')
box(sl,.68,1.84,8.47,4.91,WHITE,LINE)
img(sl,'05_test_actual_vs_pred.png',.81,1.92,8.18,4.63)
text(sl,'Обрана OLS',9.41,1.99,3.01,.34,17,TEAL,True)
text(sl,'MAE  4,42 року',9.4,2.49,3.11,.52,21,NAVY,True)
text(sl,'RMSE 5,97 року',9.4,3.12,3.17,.52,21,NAVY,True)
box(sl,9.38,3.99,3.11,.027,LINE,radius=False)
text(sl,'Орієнтир',9.41,4.2,2.92,.32,17,MID,True)
text(sl,'RMSE 13,18 року',9.42,4.7,3.13,.48,19,ORANGE,True)
text(sl,'Найбільші помилки: історичні кризи та чинники поза моделлю.',9.42,5.55,3.05,.83,14,MID)

# 13. Conclusion
sl=add_slide('Висновок: прогноз корисний, але має межі','12  ·  ВИСНОВКИ')
for i,(h,body,clr) in enumerate([
    ('01 · Працює','MAE 4,42 року на 36 нових країнах; точніше за середній прогноз.',TEAL),
    ('02 · Не причина','Дохід і рік асоційовані з lifeExp, але OLS не доводить причинність.',BLUE),
    ('03 · Не сучасність','1952–2007; потрібна перевірка на незалежних даних після 2007 року.',ORANGE),
]):
    x=.85+i*4.15
    box(sl,x,2.05,3.83,3.52,WHITE,LINE)
    box(sl,x,2.05,3.83,.14,clr,radius=False)
    text(sl,h,x+.25,2.61,3.38,.49,20,clr,True)
    text(sl,body,x+.25,3.36,3.29,1.63,19,INK)
text(sl,'Наступний крок: нові роки + дані про медицину, освіту та конфлікти.',1.06,6.14,11.24,.44,18,NAVY,True,align='center')

out=ROOT/'reports'/'Presentation.pptx'
prs.save(out)
print('Saved:', out, 'slides:',len(prs.slides), 'size:',out.stat().st_size)
