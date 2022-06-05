import pandas
from matplotlib import pyplot as plt
ch_time_varying_r_ = pandas.read_csv("EstimatedR.csv")

fig, ax = plt.subplots(1, 1, figsize=(12, 4))

ch_time_varying_r_.loc[:, 'Mean(R)'].plot(ax=ax, color='red')
ax.fill_between(ch_time_varying_r_.index,
                ch_time_varying_r_['Quantile.0.025(R)'],
                ch_time_varying_r_['Quantile.0.975(R)'],
                color='red', alpha=0.2)
ax.set_xlabel('date')
ax.set_ylabel('R(t) with 95%-CI')
ax.set_ylim([0, 3])
ax.axhline(y=1)
ax.set_title('Estimate of time-varying effective reproduction number for Shanghai 2022')
plt.show()