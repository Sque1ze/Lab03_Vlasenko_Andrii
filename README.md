# Лабораторна робота №3 — Основи регресійного моделювання

**Виконав:** Власенко Андрій, КН-41  
**Курс:** «Аналіз та візуалізація даних у R»  
**Мова:** Python (дозволено умовами ЛР №3)  
**Датасет:** Gapminder 1952–2007; **та сама ціль `lifeExp`**, що й у [ЛР №2](https://github.com/Sque1ze/Lab02_Vlasenko_Andrii).  
**Дата формування пакета:** 18.11.2026.

## Результат і метод

На 1704 спостереженнях для 142 країн оцінено орієнтир, базову OLS, квадратичну OLS та OLS з взаємодією `log10(gdpPercap) × continent`. Оскільки є повторні країна-роки, дані поділено **за цілими країнами**: 106 країн (1272 рядків) на навчання; 36 (432 рядки) на тест, `random_state=42`. Усередині навчання — **спільна 5-fold GroupKFold CV за країнами**. Модель зафіксовано на основі **середнього CV RMSE**, а не тесту.

| Модель | MAE CV середнє ± SD | RMSE CV середнє ± SD |
|---|---:|---:|
| Орієнтир (середнє навчальної частини) | 11,455 ± 1,142 | 13,082 ± 1,118 |
| Базова лінійна OLS | 4,577 ± 0,465 | 5,911 ± 0,698 |
| Квадратична OLS | 4,527 ± 0,452 | 5,885 ± 0,760 |
| **OLS із взаємодією** | **4,443 ± 0,523** | **5,856 ± 0,717** |

**Відкладений тест для обраної OLS:** MAE **4,424 року**, RMSE **5,972 року**. Для константного орієнтира — MAE 11,620, RMSE 13,178 року. Перевага взаємодії порівняно з базовою OLS на CV **невелика**, тож її не слід перебільшувати. Економічні та часові коефіцієнти **не є причинними ефектами**.

Гіпотези, методи, два предметні джерела з DOI, кластерні 95% ДІ, діагностика та обмеження детально описані у звіті. **Важливо:** EDA ЛР №2 охоплювало весь датасет; тому гіпотези й тестова оцінка інтерпретуються як **розвідувальні**, хоча для підбору моделей у ЛР №3 тест не використовувався.

## Структура папки

```text
Lab03_Vlasenko_Andrii/
├── data/raw/gapminder.csv                 # локальні дані (без інтернету)
├── notebooks/Regression.ipynb             # виконаний ноутбук із виходами
├── src/analysis.py                        # увесь відтворюваний аналіз
├── outputs/
│   ├── figures/                           # 7 PNG-графіків
│   ├── tables/                            # fold-метрики, ДІ, помилки, дані поділу
│   └── metadata/run_info.json             # параметри, SHA-256, версія даних
├── reports/
│   ├── report.qmd                         # виконуваний Quarto IMRaD-звіт
│   ├── report.html                        # готовий автономний HTML із графіками
│   ├── style.css                          # CSS для автономної HTML-копії
│   ├── Presentation.pptx                  # презентація PowerPoint (13 слайдів)
│   └── defense_script.md                 # доповідь по слайдах + запитання
├── tools/
│   ├── create_notebook.py                 # генерація структури ноутбука
│   ├── create_presentation.py             # генерація PPTX з актуальних таблиць/PNG
│   ├── build_html_preview.py              # резервна збірка HTML через Pandoc
│   └── smoke_test.py                      # мінімальні автоматичні тести
├── _quarto.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Запуск у VS Code на Windows 11 (PowerShell)

1. **Відкрийте у VS Code саме кореневу папку** `Lab03_Vlasenko_Andrii` через `File → Open Folder`. Не відкривайте лише `notebooks`.
2. Рекомендована версія — **Python 3.13** (для перевірки коду використовувався **CPython 3.13.5**; залежності зафіксовані в `requirements.txt`). Також потрібні розширення VS Code **Python** і **Jupyter**.
3. У терміналі VS Code, із кореня папки, виконайте:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.analysis
```

**Очікується:** буде виведено таблицю чотирьох CV-моделей і фінальні метрики тесту; будуть створені файли в `outputs/tables/`, `outputs/figures/` та `outputs/metadata/`. **Інтернет для аналізу не потрібний** (необхідний лише одноразово для встановлення бібліотек, якщо їх ще немає).

4. Відкрийте `notebooks/Regression.ipynb`. У верхньому правому куті оберіть **Select Kernel → Python Environments → .venv**. Виконайте `Restart & Run All`. Код перевірено саме в такому порядку; графіки та таблиці у ноутбуці вже збережені, тому можна переглядати його без нового виконання.
5. Щоб **відтворити презентацію** після повторного аналізу, виконайте:

```powershell
.\.venv\Scripts\python.exe -m tools.create_presentation
```

Файл з’явиться у `reports/Presentation.pptx`; його можна відкрити через PowerPoint. Текст для виступу — `reports/defense_script.md`.

## Quarto: готовий звіт і його збірка

У папці вже є **`reports/report.html`** — автономний HTML зі всіма 7 вбудованими графіками. Він відкривається подвійним клацанням без доступу до інтернету. Вихідний **`reports/report.qmd`** має повну структуру IMRaD та виконуваний Python-блок, який заново запускає аналіз. Один `.qmd` разом із виконуваним `.ipynb` забезпечує код і реплікацію.

Для **офіційного рендеру саме Quarto** додатково встановіть [Quarto CLI](https://quarto.org/docs/get-started/) і виконайте **з кореня проєкту**:

```powershell
quarto --version
quarto check jupyter
$env:QUARTO_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
quarto render reports/report.qmd --to html
```

**Результат:** `reports/report.html` (може бути також створено службові файли Quarto). У середовищі підготовки цього архіву **Quarto CLI не був доступний**, тому вкладений HTML був зібраний **Pandoc 3.1.11.1** з того самого `.qmd` *після окремого успішного виконання Python-аналізу*, із вбудованими графіками. Це готовий звіт для перегляду, але **не слід видавати його початкову збірку за перевірений запуск `quarto render`**. На вашому ПК ці команди створять власне Quarto-версію HTML.

## Перевірка відтворюваності з чистої копії

Розпакуйте архів в окрему порожню папку, відкрийте її корінь, створіть **нову** `.venv`, встановіть `requirements.txt` і виконайте:

```powershell
.\.venv\Scripts\python.exe -m src.analysis
.\.venv\Scripts\python.exe -m tools.smoke_test
```

Тест перевіряє неперетин країн, fold-метрики, фінальний тест, наявність 7 PNG, 13 слайдів, `.qmd` і HTML. Для ще суворішого повторення запустіть `Restart & Run All` у `notebooks/Regression.ipynb` та повторний Quarto render.

## Походження даних і обмеження

- Основний первинний сайт: [Gapminder Data](https://www.gapminder.org/data/).
- Історичний екстракт 142 країн (1952–2007): [CRAN `gapminder` 1.0.1](https://cran.r-project.org/package=gapminder), ліцензія **CC0** для екстракту; [DOI пакета](https://doi.org/10.32614/CRAN.package.gapminder).
- У проєкт включено CSV з вбудованого `plotly.express.data.gapminder()` з **Plotly 6.5.2**, стан файлу зафіксований 18.11.2026. Звірка здійснюється за SHA-256 у `outputs/metadata/run_info.json`. **Не змінюйте `data/raw/gapminder.csv`,** якщо хочете отримати точно ті ж числа.
- `lifeExp` — середня очікувана тривалість життя при народженні *на рівні країни*, не індивідуальний прогноз; `gdpPercap` — ВВП на душу, `year` — рік, `continent` — географічний регіон. Статистика за континентами не зважена за населенням.
- Моделі оцінені тільки для історичного періоду, прогнозу для 2026 року немає. Спостережні зв’язки не дають причинних висновків. Обмеження неповної незалежності через загальний EDA №2 задокументоване в звіті.

## Методологічні джерела й туторіали

- Preston (1975): [DOI](https://doi.org/10.1080/00324728.1975.10410201)
- Pritchett & Summers (1996): [DOI](https://doi.org/10.2307/146149)
- James та ін., [An Introduction to Statistical Learning](https://www.statlearning.com/)
- [NIST — перевірка адекватності моделі за залишками](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd44.htm)
- [Quarto — Python](https://quarto.org/docs/computations/python) · [Quarto — HTML](https://quarto.org/docs/output-formats/html-basics.html)
- DataCamp: [OLS](https://app.datacamp.com/learn/tutorials/ols-regression), [Simple Linear Regression](https://app.datacamp.com/learn/tutorials/simple-linear-regression), [Linear Regression in R](https://app.datacamp.com/learn/tutorials/linear-regression-R), [Multiple Linear Regression in R](https://app.datacamp.com/learn/tutorials/multiple-linear-regression-r-tutorial). Деякі сторінки можуть вимагати вхід до DataCamp; для запуску коду не потрібні.

## Публікація на GitHub і здача

У VS Code відкрийте `Source Control → Publish to GitHub`. Назва нового репозиторію, наприклад, **`Lab03_Vlasenko_Andrii`**. Перед публікацією переконайтеся, що завантажилися `data/raw/`, `notebooks/`, `src/`, `reports/`, `outputs/`, `tools/`, `README.md`, `_quarto.yml` та `requirements.txt`. Папку **`.venv` завантажувати не потрібно**: вона вже в `.gitignore`.

Викладачу дайте **три посилання**: на репозиторій, безпосередньо на `reports/report.html` у репозиторії (для завантаження/перегляду) та на `reports/Presentation.pptx`. За потреби також `reports/defense_script.md`. **Не видавайте посилання з прикладу за реальний опублікований репозиторій:** його потрібно опублікувати зі свого VS Code.
