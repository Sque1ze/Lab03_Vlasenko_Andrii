"""Локальний HTML-перегляд через Pandoc, якщо Quarto CLI не встановлено.

ЦЕ НЕ quarto render: Quarto-проєкт можна зібрати власне через quarto render.
Для поточного пакета результати коду заздалегідь згенеровані/перевірені.
"""
import re
import os
import subprocess
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
src = ROOT/'reports'/'report.qmd'
text = src.read_text(encoding='utf-8')
# Прибираємо приховану виконувану комірку (аналіз вже виконувався через src.analysis).
text = re.sub(r'```\{python\}.*?```\s*', '', text,flags=re.S)
with tempfile.TemporaryDirectory() as tmp:
    md = ROOT/'reports'/'__report_for_pandoc.md'
    try:
        md.write_text(text,encoding='utf-8')
        cmd=['pandoc', str(md),'-f','markdown','-t','html5','-s','--toc','--embed-resources','--resource-path='+str(ROOT/'reports')+os.pathsep+str(ROOT),
             '--css',str(ROOT/'reports'/'style.css'),'-o',str(ROOT/'reports'/'report.html')]
        subprocess.run(cmd,cwd=ROOT,check=True)
    finally:
        md.unlink(missing_ok=True)
print('Зібраний автономний HTML (Pandoc fallback):',ROOT/'reports'/'report.html')
