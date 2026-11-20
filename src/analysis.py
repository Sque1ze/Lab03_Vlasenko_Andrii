"""ЛР №3: відтворюване групове регресійне моделювання Gapminder.

Запуск із будь-якої директорії: python -m src.analysis (з кореня проєкту).
Усі навчальні рішення приймаються без використання відкладених країн.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.nonparametric.smoothers_lowess import lowess

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
FORMULAS = {
    'Лінійна': 'lifeExp ~ log10_gdp + year_5 + C(continent)',
    'Квадратична': 'lifeExp ~ log10_gdp + I(log10_gdp ** 2) + year_5 + C(continent)',
    'Взаємодія': 'lifeExp ~ log10_gdp * C(continent) + year_5',
}
ALL_MODELS = ['Орієнтир', *FORMULAS]
PALETTE = {'Africa': '#D97757', 'Americas': '#6A9C89', 'Asia': '#6B87BC', 'Europe': '#9072B0', 'Oceania': '#C2A65D'}


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x['log10_gdp'] = np.log10(x['gdpPercap'])
    x['year_5'] = (x['year'] - 1952) / 5
    return x


def metrics(y_true, y_pred) -> dict[str, float]:
    return {'MAE': float(mean_absolute_error(y_true, y_pred)),
            'RMSE': float(np.sqrt(mean_squared_error(y_true, y_pred)))}


def prediction(model_name: str, fitting: pd.DataFrame, target: pd.DataFrame) -> np.ndarray:
    if model_name == 'Орієнтир':
        return np.repeat(fitting['lifeExp'].mean(), len(target))
    model = smf.ols(FORMULAS[model_name], data=fitting).fit()
    return np.asarray(model.predict(target), dtype=float)


def save_figure(fig: plt.Figure, path: Path):
    fig.savefig(path, dpi=175, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_eda(train: pd.DataFrame, figdir: Path):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.titlesize': 15, 'axes.labelsize': 11})
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.hist(train['lifeExp'], bins=27, color='#5874A1', edgecolor='white', alpha=.92)
    ax.axvline(train['lifeExp'].median(), color='#DD8058', ls='--', lw=2, label=f"Медіана: {train['lifeExp'].median():.1f} року")
    ax.set(title='Розподіл тривалості життя — лише навчальні країни', xlabel='Очікувана тривалість життя, роки', ylabel='Кількість спостережень')
    ax.legend(frameon=False)
    fig.tight_layout(); save_figure(fig, figdir/'01_train_target.png')

    # Одна точка = країна-рік; не змішуємо незалежні країни з реальними людьми.
    fig, ax = plt.subplots(figsize=(9.6, 5.5))
    for cont, sub in train.groupby('continent', sort=True):
        ax.scatter(sub['log10_gdp'], sub['lifeExp'], s=13, alpha=.36, color=PALETTE[cont], label=cont)
    trend = lowess(train['lifeExp'], train['log10_gdp'], frac=.28, return_sorted=True)
    ax.plot(trend[:,0], trend[:,1], color='#14233D', lw=2.7, label='LOWESS (описово)')
    ax.set(title='Тривалість життя та логарифм ВВП на душу (навчальна вибірка)', xlabel='log₁₀(ВВП на душу населення, міжнар. $)', ylabel='Очікувана тривалість життя, роки')
    ax.legend(fontsize=9, ncol=3, frameon=False)
    fig.tight_layout(); save_figure(fig, figdir/'02_train_income.png')

    yearly = train.groupby(['continent','year'], as_index=False)['lifeExp'].mean()
    fig, ax = plt.subplots(figsize=(9.6, 5.5))
    for cont, sub in yearly.groupby('continent'):
        ax.plot(sub['year'], sub['lifeExp'], marker='o', ms=3.8, lw=2, color=PALETTE[cont], label=cont)
    ax.set(title='Середня тривалість життя за континентами (навчальні країни)', xlabel='Рік', ylabel='Незважене середнє по країнах, роки', xticks=[1952,1962,1972,1982,1992,2002,2007])
    ax.legend(frameon=False, ncol=3, fontsize=9)
    fig.tight_layout(); save_figure(fig, figdir/'03_train_time.png')


def plot_diagnostics(model, train, figdir):
    fit = np.asarray(model.fittedvalues)
    residual = np.asarray(model.resid)
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.scatter(fit, residual, alpha=.36, s=17, color='#5375A3')
    ax.axhline(0, color='#242D3E', lw=1.5, ls='--')
    smooth = lowess(residual, fit, frac=.3, return_sorted=True)
    ax.plot(smooth[:,0],smooth[:,1],color='#D87957',lw=2.6,label='LOWESS тренд залишків')
    ax.set(title='Діагностика базової регресії: залишки проти прогнозу', xlabel='Прогноз тривалості життя, роки',ylabel='Залишок (факт − прогноз), роки')
    ax.legend(frameon=False)
    fig.tight_layout(); save_figure(fig,figdir/'04_base_residuals.png')

    influence = model.get_influence()
    cook = np.asarray(influence.cooks_distance[0])
    influential = train[['country','year','continent','lifeExp']].copy()
    influential['cooks_distance'] = cook
    influential['studentized_residual'] = influence.resid_studentized_external
    influential['leverage'] = influence.hat_matrix_diag
    influential = influential.sort_values('cooks_distance', ascending=False)
    return influential


def plot_results(test_details: pd.DataFrame, cv_summary: pd.DataFrame, figdir: Path):
    fig, ax = plt.subplots(figsize=(7.7,6.2))
    for cont, sub in test_details.groupby('continent'):
        ax.scatter(sub['lifeExp'],sub['selected_prediction'],color=PALETTE[cont],label=cont,alpha=.68,s=32)
    lo = min(test_details['lifeExp'].min(), test_details['selected_prediction'].min()) - 2
    hi = max(test_details['lifeExp'].max(), test_details['selected_prediction'].max()) + 2
    ax.plot([lo,hi],[lo,hi],color='#233249', ls='--',label='Ідеальний прогноз')
    ax.set(xlim=(lo,hi), ylim=(lo,hi), title='Тест: фактичні та прогнозовані значення (нові країни)', xlabel='Фактична тривалість життя, роки',ylabel='Прогноз, роки')
    ax.legend(frameon=False,ncol=2,fontsize=9)
    fig.tight_layout(); save_figure(fig,figdir/'05_test_actual_vs_pred.png')

    fig, ax = plt.subplots(figsize=(9.0,5.3))
    temp = cv_summary.iloc[::-1]
    x = np.arange(len(temp))
    ax.barh(x,temp['RMSE_mean'],xerr=temp['RMSE_std'],color=['#B8C3D6' if m=='Орієнтир' else '#5C7DAF' for m in temp['model']],ecolor='#222F46',capsize=4)
    ax.set_yticks(x, temp['model'])
    ax.set(title='Групова 5-fold CV: RMSE, середнє ± SD', xlabel='RMSE, роки (менше — краще)')
    ax.set_xlim(0,max(temp['RMSE_mean']+temp['RMSE_std'])*1.18)
    fig.tight_layout(); save_figure(fig,figdir/'06_cv_comparison.png')

    by_cont = test_details.groupby('continent', sort=True).agg(n=('abs_error','size'), mae=('abs_error','mean')).reset_index()
    fig, ax = plt.subplots(figsize=(8.7,5.0))
    ax.bar(by_cont['continent'],by_cont['mae'],color=[PALETTE[c] for c in by_cont['continent']])
    ax.set(title='Помилки на тесті за континентами',xlabel='Континент',ylabel='MAE, роки')
    for i,r in by_cont.iterrows(): ax.text(i,r['mae']+.08, f"n={int(r['n'])}",ha='center',fontsize=10)
    ax.set_ylim(0,max(by_cont['mae'].max()*1.24,1))
    fig.tight_layout(); save_figure(fig,figdir/'07_test_error_continents.png')
    return by_cont


def run_analysis(root: str | Path = ROOT, quiet: bool = False) -> dict:
    root = Path(root).resolve()
    data_path = root/'data'/'raw'/'gapminder.csv'
    tabledir = root/'outputs'/'tables'
    figdir = root/'outputs'/'figures'
    metadir = root/'outputs'/'metadata'
    for directory in [tabledir, figdir, metadir]: directory.mkdir(parents=True,exist_ok=True)
    raw = pd.read_csv(data_path)
    required = {'country','continent','year','lifeExp','pop','gdpPercap','iso_alpha','iso_num'}
    assert required.issubset(raw.columns), 'Відсутні стовпці датасету Gapminder'
    assert len(raw)==1704 and raw['country'].nunique()==142, 'Несподівана версія Gapminder'
    assert raw[list(required)].notna().all().all() and not raw.duplicated(['country','year']).any()
    assert (raw[['gdpPercap','lifeExp','pop']]>0).all().all()
    df = add_features(raw)

    # Country-group holdout: exactly one split, defined BEFORE any Lab03 train EDA.
    train_ix, test_ix = next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=SEED).split(df,groups=df['country']))
    train = df.iloc[train_ix].copy().reset_index(drop=True)
    test  = df.iloc[test_ix].copy().reset_index(drop=True)
    assert set(train['country']).isdisjoint(set(test['country']))
    split = df[['country','year','continent']].copy()
    split['split'] = np.where(split['country'].isin(test['country']),'test','train')
    split.to_csv(tabledir/'split_manifest.csv',index=False)
    plot_eda(train,figdir)

    fold_records = []
    folds = list(GroupKFold(n_splits=5).split(train, groups=train['country']))
    for fold_num, (a,b) in enumerate(folds, start=1):
        fit, val = train.iloc[a], train.iloc[b]
        assert set(fit.country).isdisjoint(set(val.country))
        for model_name in ALL_MODELS:
            pred = prediction(model_name,fit,val)
            s = metrics(val['lifeExp'],pred)
            fold_records.append({'fold':fold_num,'model':model_name,'n_validation':len(val),'n_countries':val.country.nunique(),**s})
    fold_df = pd.DataFrame(fold_records)
    cv_summary = fold_df.groupby('model').agg(
        MAE_mean=('MAE','mean'), MAE_std=('MAE','std'),
        RMSE_mean=('RMSE','mean'), RMSE_std=('RMSE','std')).reset_index()
    cv_summary['model'] = pd.Categorical(cv_summary['model'],categories=ALL_MODELS, ordered=True)
    cv_summary = cv_summary.sort_values('RMSE_mean').reset_index(drop=True)
    selected = str(cv_summary[cv_summary['model']!='Орієнтир'].iloc[0]['model'])

    # Inference uses the PRE-SPECIFIED linear explanatory model, with country-clustered SE.
    base = smf.ols(FORMULAS['Лінійна'],data=train).fit()
    robust = base.get_robustcov_results(cov_type='cluster', groups=train['country'])
    ci = np.asarray(robust.conf_int(alpha=.05))
    coef = pd.DataFrame({'term':base.model.exog_names,'estimate':robust.params,
                        'ci_low':ci[:,0],'ci_high':ci[:,1], 'p_value_clustered':robust.pvalues})
    influential = plot_diagnostics(base,train,figdir)
    bp = het_breuschpagan(base.resid,base.model.exog)
    diagnostics = {'bp_lm_p_value':float(bp[1]), 'bp_f_p_value':float(bp[3]),
                   'cook_threshold_4_over_n':4/len(train),
                   'n_cook_above_threshold':int((influential['cooks_distance']>4/len(train)).sum()),
                   'max_cook_distance':float(influential['cooks_distance'].max()),
                   'base_training_r_squared':float(base.rsquared)}
    # Model selection ended above; this is the SINGLE final evaluation of frozen selected model.
    selected_fit = smf.ols(FORMULAS[selected],data=train).fit()
    test_pred = np.asarray(selected_fit.predict(test),dtype=float)
    dummy_pred = np.repeat(train['lifeExp'].mean(), len(test))
    test_scores = pd.DataFrame([
        {'model':'Орієнтир', **metrics(test['lifeExp'],dummy_pred)},
        {'model':selected, **metrics(test['lifeExp'],test_pred)},
    ])
    detail = test[['country','continent','year','lifeExp','gdpPercap']].copy()
    detail['selected_prediction'] = test_pred
    detail['baseline_prediction'] = dummy_pred
    detail['error'] = detail['lifeExp']-test_pred
    detail['abs_error'] = np.abs(detail['error'])
    by_cont = plot_results(detail,cv_summary,figdir)
    test_worst = detail.sort_values('abs_error',ascending=False).head(12)
    train_stats = pd.DataFrame([{'n_train':len(train),'n_countries_train':train.country.nunique(),
                                 'n_test':len(test),'n_countries_test':test.country.nunique(),
                                 'train_lifeExp_mean':train.lifeExp.mean(),
                                 'train_lifeExp_median':train.lifeExp.median(),
                                 'train_lifeExp_std':train.lifeExp.std(),
                                 'train_lifeExp_min':train.lifeExp.min(),
                                 'train_lifeExp_max':train.lifeExp.max(),
                                 'train_logGDP_lifeExp_pearson_r':pearsonr(train.log10_gdp,train.lifeExp).statistic,
                                 'missing_values':int(raw.isna().sum().sum()), 'duplicate_country_year':int(raw.duplicated(['country','year']).sum())}])
    for filename, table in [
        ('cv_folds.csv',fold_df),('cv_summary.csv',cv_summary),
        ('base_coefficients_cluster95.csv',coef),('diagnostics.csv',pd.DataFrame([diagnostics])),
        ('influence_top12.csv',influential.head(12)),('test_metrics.csv',test_scores),
        ('test_predictions.csv',detail),('test_worst_errors.csv',test_worst),
        ('test_by_continent.csv',by_cont),('train_overview.csv',train_stats),
    ]: table.to_csv(tabledir/filename,index=False,float_format='%.9f')
    metadata = {
        'dataset':'Gapminder 1952–2007, Plotly Express bundled historical extract',
        'data_sha256':hashlib.sha256(data_path.read_bytes()).hexdigest(),
        'target':'lifeExp (years)', 'unit_of_observation':'country-year',
        'seed':SEED,'holdout':'GroupShuffleSplit countries, 25% test','cv':'GroupKFold 5 splits, by country',
        'selection_metric':'mean CV RMSE','selected_model':selected,'selected_formula':FORMULAS[selected],
        'base_formula':FORMULAS['Лінійна'],
        'n_train':len(train),'n_test':len(test),'countries_train':train.country.nunique(),
        'countries_test':test.country.nunique(),'eda_warning':'Lab02 inspected full data; holdout is not perfectly blind in a scientific sense',
        'diagnostics':diagnostics,
        'test_selected':test_scores.iloc[1].to_dict(),
        'test_baseline':test_scores.iloc[0].to_dict(),
    }
    (metadir/'run_info.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False,default=float),encoding='utf-8')
    if not quiet:
        print('ЛР №3 · Gapminder · груповий поділ країн')
        print(f"Навчання: {len(train)} рядків / {train.country.nunique()} країн; тест: {len(test)} / {test.country.nunique()} країн")
        print('\n5-fold CV (групи = країни):\n',cv_summary.to_string(index=False, float_format=lambda x:f'{x:.3f}'))
        print(f"\nОбрана за CV модель: {selected}")
        print('\nНезалежний тест (один раз):\n',test_scores.to_string(index=False, float_format=lambda x:f'{x:.3f}'))
        print('\nЗгенеровано: outputs/figures/, outputs/tables/, outputs/metadata/')
    return {'metadata':metadata,'train':train,'test':test,'cv_folds':fold_df,
            'cv_summary':cv_summary,'test_scores':test_scores,'test_details':detail,
            'coefficients':coef,'diagnostics':diagnostics,'influential':influential,
            'test_by_continent':by_cont,'train_stats':train_stats,'selected':selected}


if __name__ == '__main__':
    run_analysis()
