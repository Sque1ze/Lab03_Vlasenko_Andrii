"""Малі відтворювані тести. Запуск: python -m tools.smoke_test."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pptx import Presentation
from src.analysis import run_analysis

ROOT=Path(__file__).resolve().parents[1]
a=run_analysis(ROOT,quiet=True)
assert len(a['train'])==1272 and len(a['test'])==432
assert a['train'].country.nunique()==106 and a['test'].country.nunique()==36
assert not(set(a['train'].country) & set(a['test'].country))
assert (a['cv_folds'].groupby('model')['fold'].nunique()==5).all()
assert a['selected']=='Взаємодія'
assert np.isclose(a['test_scores'].iloc[1]['RMSE'],5.972,atol=.005)
assert np.isclose(a['test_scores'].iloc[0]['RMSE'],13.178,atol=.005)
assert len(list((ROOT/'outputs'/'figures').glob('*.png')))==7
assert len(Presentation(ROOT/'reports'/'Presentation.pptx').slides)==13
assert (ROOT/'notebooks'/'Regression.ipynb').exists()
assert (ROOT/'reports'/'report.qmd').exists()
html=(ROOT/'reports'/'report.html').read_text(encoding='utf-8')
assert html.count('<img') >= 7, 'Зібраний HTML має містити щонайменше 7 графіків'
assert 'Preston' in html and 'Pritchett' in html
print('OK: країни не перетинаються, фолди, метрики, 7 PNG, 13 слайдів, QMD, HTML')
