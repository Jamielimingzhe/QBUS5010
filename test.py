import pandas as pd
china_factor = pd.read_csv('Factor_Data/China.csv',index_col='Ticker')
china_factor.index = [i[1:] for i in china_factor.index.astype(str)]

print(china_factor.index)
