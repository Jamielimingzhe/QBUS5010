from dash import Dash, dcc, html, Input, Output,dash_table
from numpy import datetime64
import plotly.express as px
import pandas as pd

cape = pd.read_excel('Data/CAPE_Data_Final.xlsx')
countries = ['Australia', 'China', 'Japan', 'USA']

benchmarks = pd.read_csv('Data/benchmarks.csv',index_col='Date')

rank_dict = {
  "USA": pd.read_excel('Data/Factor_Ranking/US_rank.xlsx',index_col='Ticker'),
  "Australia": pd.read_excel('Data/Factor_Ranking/Aus_rank.xlsx',index_col='Ticker'),
  "China": pd.read_excel('Data/Factor_Ranking/China_rank.xlsx',index_col='Ticker',dtype={'Ticker': object}),
  "Japan": pd.read_excel('Data/Factor_Ranking/Japan_rank.xlsx',index_col='Ticker',dtype={'Ticker': object})
}

price_dict = {
  "USA": pd.read_csv('Data/Factor_Prices/US_stock.csv',index_col='Date'),
  "Australia": pd.read_csv('Data/Factor_Prices/Aus_stock.csv',index_col='Date'),
  "China": pd.read_csv('Data/Factor_Prices/China_stock.csv',index_col='Date'),
  "Japan": pd.read_csv('Data/Factor_Prices/Japan_stock.csv',index_col='Date')
}
price_dict["China"].columns = [i[1:] for i in price_dict["China"].columns]

factor_dict = {
  "USA": pd.read_csv('Data/Factor_Data/US.csv',index_col='Ticker_s'),
  "Australia": pd.read_csv('Data/Factor_Data/Aus.csv',index_col='Ticker_s'),
  "China": pd.read_csv('Data/Factor_Data/China.csv',index_col='Ticker_s'),
  "Japan": pd.read_csv('Data/Factor_Data/Japan.csv',index_col='Ticker_s')
}
factor_dict['China'].index = [i[1:] for i in factor_dict['China'].index.astype(str)]
factor_dict['China']['Ticker'] = [i[1:] for i in factor_dict['China']['Ticker'].astype(str)]
factor_dict['Japan'].index = factor_dict['Japan'].index.astype(str)
factor_dict['Japan']['Ticker'] = factor_dict['Japan']['Ticker'].astype(str)

factor_columns = {
  "Momentum": ['Momentum Rank','Ticker','Name','MKT CAP (US$M)','Sector','1Y Return'],
  "Value": ['Value Rank','Ticker','Name','MKT CAP (US$M)','Sector','P/S','P/E','P/FCF','P/B'],
  "Profitability": ['Profitability Rank','Ticker','Name','MKT CAP (US$M)','Sector','ROA','ROE','Gross margin','GPOA']
}


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
        style_cell={'textAlign': 'center'},
        fill_width=False,
        style_table={'height': '180px','width':'400px', 'overflowY': 'auto'}
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
        html.Div([
            html.P("This chart shows annualised returns/prices predicted by the CAPE ratio for the next 10 years aginst its realised annualised returns/prices. For example, Australia's Return prediction in Sep 2022 is 6%, this means the model predicts the annualised return of Australia's equity market index will be 6 percent for the next 10 years. The predictions are only valid on average in the long-term (10Y) and should not be used to justify daily market timing decisions.")
        ], className="help-tip"),
        html.H2(
                'CAPE Equity Index Forecasts'
                ),
        dcc.Tabs(id='prediction_type', value='return_prediction', children=[
        dcc.Tab(label='Return Prediction', value='return_prediction'),
        dcc.Tab(label='Price Prediction', value='price_prediction'),
        ]),
        dcc.Graph(id='cape_graph')
    ],style={'width': '95%','margin': 'Auto'}),

    html.Div([
        html.P("This table rank stocks in the selected country by factors (Momentum, Value, Profitability) that predict higher expected returns. Higher ranking stocks is expected to outperform lower ranking stocks in the future. Momentum is measured using past 1Y returns. Value is measured using an equal weighted average of four metrics: Price-to-Sales, Price-to-Earnings, Price-to-Free Cash Flow, Price-to-Book Value. Profitability is also mesured using an equal weighted average of four metrics: Return on Assets, Return on Equity, Gross Margin, Gross Profit on Assets. Missing data is ignored for the calculation of the average.")
    ], className="help-tip1"),
    html.H2(
        'Stock Factor Rankings'
    ,style={'width': '95%','margin': 'Auto'}),   
    html.H6(' '),
    html.Div([
        dcc.Tabs(id='Factor_type', value='Momentum', children=[
        dcc.Tab(label='Momentum', value='Momentum'),
        dcc.Tab(label='Value', value='Value'),
        dcc.Tab(label='Profitability', value='Profitability'),
        ]),
        dash_table.DataTable(
        id='table_large',
        style_as_list_view=True,
        style_cell={'textAlign': 'center'},
        style_header={
            'backgroundColor': '#1b4d9e',
            'color': 'white',
            'fontWeight': 'bold'
        },
        page_current=0,
        page_size=10,
        page_action='custom'
        )
    ],style={'width': '95%','margin': 'Auto'}),


    html.Div([
        html.P("This backtesting tool shows portfolio performance for the past 1 year. The presets tab will create an equal weight portfolio of the highest ranking stocks in the selected country based on what factor and how many stocks you want. The custom tab lets you create your own porfolio by selecting multiple stocks in the dropdown menu. The construted portfolio is benchmarked against the country's equity index.")
    ], className="help-tip2"),
    html.H2(
        'Portfolio Backtesting Tool'
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
    custom_table = factor_dict[Country].loc[Tickers,['Ticker','Name','MKT CAP (US$M)','Sector']]
    return custom_table.to_dict('records')

@app.callback(
    Output('table_large', 'data'),
    Input('table_large', "page_current"),
    Input('table_large', "page_size"),
    Input('country_name', 'value'),
    Input('Factor_type', "value"))
def update_large_table(page_current,page_size,Country,Factor_type):
    large_table = factor_dict[Country].loc[:,factor_columns[Factor_type]].sort_values(f'{Factor_type} Rank')
    return large_table.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
