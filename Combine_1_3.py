from dash import Dash, dcc, html, Input, Output
from numpy import datetime64
import plotly.express as px
import pandas as pd

cape = pd.read_excel('CAPE_Data_Final.xlsx')
countries = ['Australia', 'China', 'Japan', 'USA']

benchmarks = pd.read_csv('benchmarks.csv',index_col='Date')

rank_dict = {
  "USA": pd.read_excel('Factor_Ranking/US_rank.xlsx',index_col='Ticker'),
  "Australia": pd.read_excel('Factor_Ranking/Aus_rank.xlsx',index_col='Ticker'),
  "China": pd.read_excel('Factor_Ranking/China_rank.xlsx',index_col='Ticker',dtype={'Ticker': object}),
  "Japan": pd.read_excel('Factor_Ranking/Japan_rank.xlsx',index_col='Ticker',dtype={'Ticker': object})
}

price_dict = {
  "USA": pd.read_csv('Factor_Prices/US_stock.csv',index_col='Date'),
  "Australia": pd.read_csv('Factor_Prices/Aus_stock.csv',index_col='Date'),
  "China": pd.read_excel('Factor_Prices/China_stock.xlsx',index_col='Date'),
  "Japan": pd.read_csv('Factor_Prices/Japan_stock.csv',index_col='Date')
}

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
            'CAPE Equity Index Forecast'
            ),
    dcc.Tabs(id='prediction_type', value='return_prediction', children=[
    dcc.Tab(label='Return Prediction', value='return_prediction'),
    dcc.Tab(label='Price Prediction', value='price_prediction'),
    ]),
    html.Div([
        dcc.Dropdown(countries, value='Australia', id='country_name')],
        style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id='cape_graph'),
    html.H1(
            'Portfolio Backtest'
            ),
    html.Div([
        dcc.Dropdown(['Momentum','Value','Profitability'], value='Momentum', id='Factor'),
        dcc.Dropdown([10,20,30], value=30, id='Num')],
        # dcc.Dropdown(['Market Index'], value='Australia', id='Benchmark')],
        style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id='factor_graph'),
])

@app.callback(
     Output('cape_graph', 'figure'),
     Input('prediction_type', 'value'),
     Input('country_name', 'value'),
    )
def update_graph(prediction_type, country_name):
    if country_name == None: 
        country_name = 'Australia'
    
    filtered_cape = cape[['Date'] + [col for col in cape.columns if country_name in col]]
    
    if prediction_type == 'return_prediction':
        filtered_cape = filtered_cape.dropna(subset=[country_name + ' 10Y Return', country_name + ' 10Y Prediction'], how='all')
        fig = px.line(
            data_frame = filtered_cape,
            x = 'Date',
            y = [country_name + ' 10Y Return', country_name + ' 10Y Prediction'])
        fig.update_layout(yaxis_tickformat=".0%")
    else:
        filtered_cape = filtered_cape.dropna(subset=[country_name + ' Price', country_name + ' 10Y Price Prediction'], how='all')
        fig = px.line(
            data_frame = filtered_cape,
            x = 'Date',
            y = [country_name + ' Price', country_name + ' 10Y Price Prediction'])
    return fig

@app.callback(
     Output('factor_graph', 'figure'),
     Input('country_name', 'value'),
     Input('Factor', 'value'),
     Input('Num', 'value'),
    )
def update_graph(Country,Factor,Num):
    temp = (price_dict[Country].loc['2021-10-20':,rank_dict[Country][Factor].sort_values()[0:Num].index].pct_change().mean(axis=1)+1).cumprod()
    temp = pd.DataFrame(temp,columns=[f'{Factor}_{Num}'])
    temp.iloc[0,0] = 1
    temp = pd.concat([temp,benchmarks],axis=1)
    fig = px.line(
        data_frame = temp,
        x = temp.index,
        y = [f'{Factor}_{Num}',Country])
    # fig.update_layout(yaxis_tickformat=".0%")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
