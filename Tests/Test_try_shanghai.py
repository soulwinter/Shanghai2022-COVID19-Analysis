import epyestim
import epyestim.covid19 as covid19
import pandas
from matplotlib import pyplot as plt

data = pandas.read_csv("ShanghaiTest.csv"
                       , parse_dates=['Date']).set_index('Date')['Cases']
# data.rename(columns={'date': 'Date'}, inplace=True)
# data.set_index('Date', inplace=True)
# data.drop(columns=['Shanghai_quezheng'], inplace=True) # 事实上不可以只算无症状，只是测试
# data.reset_index(inplace=True)
print(data)
# dataSeries = pandas.Series(data['Shanghai_wuzhengzhuang'].values, index=data['Date'])


ch_time_varying_r_ = covid19.r_covid(data, auto_cutoff=False)



fig, ax = plt.subplots(1, 1, figsize=(12, 4))

ch_time_varying_r_.loc[:, 'Q0.5'].plot(ax=ax, color='red')
ax.fill_between(ch_time_varying_r_.index,
                ch_time_varying_r_['Q0.025'],
                ch_time_varying_r_['Q0.975'],
                color='red', alpha=0.2)
ax.set_xlabel('date')
ax.set_ylabel('R(t) with 95%-CI')
ax.set_ylim([0, 3])
ax.axhline(y=1)
ax.set_title('Estimate of time-varying effective reproduction number for Switzerland')
plt.show()
