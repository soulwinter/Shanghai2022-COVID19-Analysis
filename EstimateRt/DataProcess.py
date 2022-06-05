import pandas as pd

date_list = pd.date_range(start='2022-02-27', end='2022-06-04')
date_str_list = [str(i.year) + str(i.month).zfill(2) + str(i.day).zfill(2) for i in date_list]

path = '/Users/soulwinter/PycharmProjects/Shanghai2022/Shanghai2022-COVID19-Analysis/EstimateRt/DataInfo2/district/'
df_list = []
for date in date_str_list:
    df = pd.read_excel(path + date + '_city.xlsx')
    df_list.append(df)
df_city = pd.concat(df_list)
df_city['累计总数'] = df_city['总数'].cumsum()
df_city = df_city.reset_index(drop=True)
df_city.to_csv("processed.csv")
