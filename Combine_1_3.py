from dash import Dash, dcc, html, Input, Output,dash_table
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
  "China": pd.read_csv('Factor_Prices/China_stock.csv',index_col='Date'),
  "Japan": pd.read_csv('Factor_Prices/Japan_stock.csv',index_col='Date')
}
price_dict["China"].columns = [i[1:] for i in price_dict["China"].columns]

factor_dict = {
  "USA": pd.read_csv('Factor_Data/US.csv',index_col='Ticker_s'),
  "Australia": pd.read_csv('Factor_Data/Aus.csv',index_col='Ticker_s'),
  "China": pd.read_csv('Factor_Data/China.csv',index_col='Ticker_s'),
  "Japan": pd.read_csv('Factor_Data/Japan.csv',index_col='Ticker_s')
}
factor_dict['China'].index = [i[1:] for i in factor_dict['China'].index.astype(str)]
factor_dict['China']['Ticker'] = [i[1:] for i in factor_dict['China']['Ticker'].astype(str)]
factor_dict['Japan'].index = factor_dict['Japan'].index.astype(str)
factor_dict['Japan']['Ticker'] = factor_dict['Japan']['Ticker'].astype(str)



app = Dash(__name__)

tab1 = html.Div([
    html.H3('Choose your factor:'),
    dcc.Dropdown(['Momentum','Value','Profitability'], value='Momentum', id='Factor'),
    html.H3('How many stocks:'),
    dcc.Dropdown([10,20,30], value=30, id='Num')
])

tab2 = html.Div([
    html.H3('Select your stocks:'),
    dcc.Dropdown(
        id='my-input',
        multi=True,
    ),
    html.H6(' '),
    dash_table.DataTable(
        id='datatable-paging',
        columns=[{'id': c, 'name': c} for c in ['Ticker','Name','MKT CAP','Sector','1Y Return','P/E','ROE']],
        fixed_rows={'headers': True},
        fill_width=False,
        style_table={'height': '180px','width':'400px', 'overflowY': 'auto', 'overflowX': 'auto'}
    )
])


app.layout = html.Div([
    html.H1("Equity Valuation and Stock Rankings", style={'textAlign': 'center'}),
    html.Div([       
        html.H3("Choose a Country:",
        style={'flex':1,'position':'relative',"top":"0px"}),
        html.Div([
        dcc.Dropdown(countries, value='Australia', id='country_name')]
        ,style={'flex':1,'position':'relative',"top":"10px"})
    ], style={'display': 'flex', 'flex-direction': 'row','width': '30%','margin': 'Auto'}),
    html.Div([
        html.H2(
                'CAPE Equity Index Forecast'
                ),
        dcc.Tabs(id='prediction_type', value='return_prediction', children=[
        dcc.Tab(label='Return Prediction', value='return_prediction'),
        dcc.Tab(label='Price Prediction', value='price_prediction'),
        ]),
        dcc.Graph(id='cape_graph')
    ],style={'width': '95%','margin': 'Auto'}),
    html.H2(
        'Portfolio Backtest'
    ,style={'width': '95%','margin': 'Auto'}),   
    html.Div([
        html.Div(children=[
            dcc.Tabs(id='tabs', value='1', children=[
                dcc.Tab(
                    label='Presets',
                    value='1',
                    children=tab1
                ),
                dcc.Tab(
                    label='Custom',
                    value='2',
                    children=tab2
                ),
            ]),
        ],style = {'padding':5,'flex':0.3,'position':'relative',"top":"30px"}),
        html.Div(children=[
            dcc.Graph(id='factor_graph')
        ],style = {'padding':5,'flex':0.7}),
    ],style={'display': 'flex', 'flex-direction': 'row','width': '95%','margin': 'Auto'})
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
    fig.update_layout(legend=dict(
    title = None,
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.05
    ))

    return fig

@app.callback(
     Output('my-input', 'options'),
     Output('my-input', 'value'),
     Input('country_name', 'value'),
    )
def update_tab(Country):
    if Country == None: 
        Country = 'Australia'
    opts = price_dict[Country].columns
    options= [{'label':opt, 'value':opt} for opt in opts] 
    value = opts[:10]
    return options,value


@app.callback(
     Output('factor_graph', 'figure'),
     Input('tabs','value'),
     Input('my-input','value'),
     Input('country_name', 'value'),
     Input('Factor', 'value'),
     Input('Num', 'value'),
    )
def update_graph(Tabs,Tickers,Country,Factor,Num):
    if Country == None: 
        Country = 'Australia'
    if Factor == None: 
        Factor = 'Momentum'
    if Num == None: 
        Num = 30
    
    if Tabs == '1':
        temp = (price_dict[Country].loc['2021-10-20':,rank_dict[Country][Factor].sort_values()[0:Num].index].pct_change().mean(axis=1)+1).cumprod()
        temp = pd.DataFrame(temp,columns=[f'{Factor}_{Num}'])
        temp.iloc[0,0] = 1
        temp = pd.concat([temp,benchmarks],axis=1)
        fig = px.line(
        data_frame = temp,
        x = temp.index,
        y = [f'{Factor}_{Num}',Country],
        title = f'{Country} {Num} Stock {Factor} Facotr Portfolio 1Y Performance')
    else:
        temp = (price_dict[Country].loc['2021-10-20':,Tickers].pct_change().mean(axis=1)+1).cumprod()
        temp = pd.DataFrame(temp,columns=['Custom Porfolio'])
        temp.iloc[0,0] = 1
        temp = pd.concat([temp,benchmarks],axis=1)
        fig = px.line(
        data_frame = temp,
        x = temp.index,
        y = ['Custom Porfolio',Country],
        title = f'{Country} {len(Tickers)} Stock Custom Portfolio 1Y Performance')
    fig.update_layout(legend=dict(
        title = None,
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.82))
    return fig
    
@app.callback(
    Output('datatable-paging', 'data'),
    Input('my-input','value'),
    Input('country_name', 'value'))
def update_table(Tickers,Country):
    custom_table = factor_dict[Country].loc[Tickers,['Ticker','Name','MKT CAP','Sector','1Y Return','P/E','ROE']]
    return custom_table.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
