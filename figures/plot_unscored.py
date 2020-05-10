import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import matplotlib.font_manager as fm
import seaborn as sns

import matplotlib
from matplotlib.gridspec import GridSpec

from utils import palette_robustness_light, palette_robustness, palette_robustness_dark

matplotlib.rc('text', usetex=True)
matplotlib.rcParams['mathtext.fontset'] = 'custom'
matplotlib.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
matplotlib.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
prop = fm.FontProperties(fname='../fonts/JetBrainsMono-1.0.3/ttf/JetBrainsMono-Regular.ttf')
matplotlib.rcParams['mathtext.tt'] = prop.get_name()

columns = ['experiment', 'robustness', 'dataset', 'metric', 'value']
metrics = ['Betweenness', 'Degree', 'Ego1Edges', 'Ego2Nodes', 'LocalClustering', 'PageRank', 'Redundancy']
datasets = ['airports', 'facebook', 'collab', 'internet', 'citation']
robustness_measures = ['RankIdentifiability', 'RankInstability']
experiment_name = 'unscored'
experiments = [experiment_name]

# %%

# DF graffs

df_graffs = pd.read_excel("robustness_graffs.xlsx", sheet_name=0)
df_graffs.columns = map(str.lower, df_graffs.columns)
df_graffs = df_graffs.rename({'robustnessmeasure': 'robustness'}, axis=1)
df_graffs = df_graffs[df_graffs['experiment'].isin(experiments)]
df_graffs = df_graffs[df_graffs['metric'].isin(metrics) & df_graffs['dataset'].isin(datasets)]
df_graffs['metric'] = pd.Categorical(df_graffs['metric'], categories=metrics, ordered=True)
df_graffs = df_graffs[columns]

# DF combined

df_combined = df_graffs
df_combined = df_combined[df_combined['robustness'].isin(robustness_measures)]

# %% Sort columns

# Decide metric order
avgs = df_combined[df_combined['experiment'] == experiment_name].groupby(['metric', 'robustness'], as_index=False).mean()
by_metrics = avgs.pivot_table(values='value', index='metric', columns='robustness', aggfunc='mean')
by_metrics['robustness_overall'] = by_metrics['RankIdentifiability'] - by_metrics['RankInstability']
by_metrics = by_metrics.drop(robustness_measures, axis=1)
by_metrics = by_metrics.sort_values('robustness_overall', ascending=False)
metrics_sorted = list(by_metrics.index.values)

df = df_combined.copy()
df['experiment'] = pd.Categorical(df_combined['experiment'], categories=experiments, ordered=True)
df['robustness'] = pd.Categorical(df_combined['robustness'], categories=robustness_measures, ordered=True)
df['dataset'] = pd.Categorical(df_combined['dataset'], categories=datasets, ordered=True)
df['metric'] = pd.Categorical(df_combined['metric'], categories=metrics_sorted, ordered=True)
df = df.sort_values(['experiment', 'robustness', 'dataset', 'metric'])

# %% Bar plot for one robustness measure

# data = df
# r = 'RankIdentifiability'
# data = data[data['robustness'] == r]
# # data = data.groupby(['metric','source'], as_index=False).mean()
# plt.subplots(figsize=(8, 7))
#
# plt.subplot(111)
# sns.barplot(
#     x=data['metric'],
#     y=data['value'],
#     hue=data['dataset'],
#     # style=data['source'],
# )
# plt.ylim(0, 1)
# plt.title(r + " paper")
#
# plt.show()

# %% Reproduction plot

# noinspection PyTypeChecker
fig = plt.subplots(figsize=(8, 4.5), sharex=True, squeeze=True)

gs1 = GridSpec(2, 1)
gs1.update(hspace=0.0)


# noinspection PyUnresolvedReferences
def plot_for_robustness(robustness_measure, pos):
    ax1 = plt.subplot(gs1[pos])
    data = df[df['robustness'] == robustness_measure]
    palette_experiment = {
        "paper": palette_robustness_light[robustness_measure],
        "reproduce": palette_robustness[robustness_measure],
        experiment_name: palette_robustness_dark[robustness_measure],
    }
    dashes_experiment = {
        "paper": (5, 4),
        "reproduce": (1, 0),
        experiment_name: (1.5, 1.5),
    }
    print(palette_experiment)

    sns.lineplot(
        x=data['metric'],
        y=data['value'],
        hue=data['dataset'],  # .rename("\\textbf{Robustness measure}"),
        # style=data_local['experiment'],  # .rename("\\textbf{Data source}"),
        estimator='mean',
        # palette=palette_experiment,
        # dashes=dashes_experiment,
    )

    plt.margins(x=0.05)
    if pos == 0:
        plt.ylim(0.5, 1.04)
        ax1.set_xticklabels([])
        ax1.set_xlabel(None)
    elif pos == 1:
        plt.gca().yaxis.set_major_locator(plticker.FixedLocator(np.linspace(0, 1, 11)))
        plt.ylim(-0.04, 0.5)
    plt.gca().yaxis.set_minor_locator(plticker.MultipleLocator(0.05))
    plt.grid(color='0.8', linestyle=':', which='both', axis='both')

    plt.ylabel("Rank " + robustness_measure[4:])


plot_for_robustness('RankIdentifiability', 0)
plt.title("The \\texttt{unscored} experiment: RankIdentifiability and RankInstability computed\n"
          "on 7 metrics and 5 new unscored datasets")

plot_for_robustness('RankInstability', 1)
plt.xlabel("\\textsl{Metric}")

plt.tight_layout()
plt.savefig("plot_unscored.pdf")
plt.show()