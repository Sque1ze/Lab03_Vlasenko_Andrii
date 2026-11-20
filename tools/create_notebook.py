"""Генерує структурований ноутбук для лабораторної №3."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook()
M=lambda s: nbf.v4.new_markdown_cell(s)
C=lambda s: nbf.v4.new_code_cell(s)
nb.cells=[
M('''# Лабораторна робота №3 — регресійне моделювання Gapminder

**Власенко Андрій, КН-41 · Python · 18.11.2026**

Продовження EDA лабораторної №2: 142 країни × 12 років = 1704 спостереження. Ціль — `lifeExp` (роки). Для оцінки прогнозу на **нових країнах** відокремлюємо тест за країнами та використовуємо групову 5-fold CV.

> Після EDA всього датасету в №2 гіпотези вважаються розвідувальними. Дані тесту №3 не використовуються для вибору моделі. **Запускайте з кореня проєкту**, обравши Python із `.venv`.'''),
M('## 1. Підготовка та відтворюваний запуск'),
C('''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image, Markdown

ROOT = Path.cwd()
if not (ROOT / 'data' / 'raw' / 'gapminder.csv').exists():
    ROOT = ROOT.parent
assert (ROOT / 'data' / 'raw' / 'gapminder.csv').exists(), 'Відкрийте корінь папки Lab03 у VS Code'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.analysis import run_analysis
result = run_analysis(ROOT)
print('Успішне виконання моделей, графіків і таблиць')'''),
M('## 2. Якість даних та груповий holdout'),
C('''display(result['train_stats'].round(3))
print('Навчальні країни:', result['train']['country'].nunique())
print('Тестові країни:', result['test']['country'].nunique())
print('Перетин країн:', set(result['train'].country) & set(result['test'].country))
assert set(result['train'].country).isdisjoint(result['test'].country)'''),
M('## 3. EDA лише навчальної частини\n\nЛогарифм ВВП, рік і континент обрані з огляду на джерела та лабораторну №2; нижче — *train-only* графіки.'),
C('''for name in ['01_train_target.png', '02_train_income.png', '03_train_time.png']:
    display(Image(filename=str(ROOT / 'outputs' / 'figures' / name), width=780))'''),
M('## 4. План моделей і групова перехресна валідація\n\nПорівняно константне середнє, базову OLS, OLS з квадратичним членом та OLS із взаємодією доходу та континенту. Всі моделі використовують однакові 5 групових фолдів. Первинна метрика **RMSE** у роках.'),
C('''display(result['cv_folds'].round(3))
display(result['cv_summary'].round(3))
print('Обрана модель (до тесту):', result['selected'])
display(Image(filename=str(ROOT / 'outputs' / 'figures' / '06_cv_comparison.png'), width=780))'''),
M('## 5. Гіпотези та кластерні 95% довірчі інтервали\n\n**H1:** позитивний зв’язок `log10_gdp` з `lifeExp` за контролю року та континенту. **H2:** позитивний зв’язок `year_5`. Нижче — базова OLS з кластерними стандартними похибками за країною, а не коефіцієнти адаптивно обраної моделі.'),
C('''display(result['coefficients'].round(4))
for term in ['log10_gdp', 'year_5']:
    row = result['coefficients'].set_index('term').loc[term]
    print(f"{term}: {row['estimate']:.3f}; кластерний 95% ДІ [{row['ci_low']:.3f}; {row['ci_high']:.3f}]")'''),
M('## 6. Залишки та впливові спостереження\n\nПеревірено гетероскедастичність тестом Бройша—Пагана й впливові точки за Куком. Незвичні історичні спостереження не вилучаємо автоматично.'),
C('''display(Image(filename=str(ROOT / 'outputs' / 'figures' / '04_base_residuals.png'), width=780))
print('Діагностика:', result['diagnostics'])
display(result['influential'].head(10).round(4))'''),
M('## 7. Одноразовий відкладений тест і помилки\n\nМодель зафіксована за CV та перенавчена на всіх навчальних країнах. Нижче — єдина оцінка на 36 відкладених країнах.'),
C('''display(result['test_scores'].round(3))
for name in ['05_test_actual_vs_pred.png', '07_test_error_continents.png']:
    display(Image(filename=str(ROOT / 'outputs' / 'figures' / name), width=780))
display(result['test_details'].sort_values('abs_error',ascending=False).head(10).round(3))'''),
M('''## 8. Висновок

Модель із взаємодією має найменший середній RMSE на груповій CV; на відкладених нових країнах її похибка становить близько **5,97 року RMSE** проти **13,18** для константного прогнозу. H1 і H2 заздалегідь оцінені базовою OLS та отримали позитивні кластерні 95% ДІ. Асоціації не є причинними ефектами. Велика гетероскедастичність і впливові спостереження обмежують упевненість у прогнозі; дані історичні (1952–2007).

Повний IMRaD-звіт — `reports/report.qmd` та `reports/report.html`; презентація — `reports/Presentation.pptx`, текст виступу — `reports/defense_script.md`.'''),
]
nb.metadata = {'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'},'title':'Лабораторна робота №3 — Gapminder'}
out=ROOT/'notebooks'/'Regression.ipynb'
nbf.write(nb,out)
print(out)
