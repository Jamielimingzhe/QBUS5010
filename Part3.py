from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_excel('Factor_Data/US.xlsx',index_col='Ticker_s')
stock_price = pd.read_excel('US_stock.xlsx')
# countries = ['Australia', 'China', 'Japan', 'USA']

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
            'CAPE Equity Index Forecast'
            ),
    html.Div([
        dcc.Dropdown(['Momentum','Value','Profitability'], value='Momentum', id='Factor'),
        dcc.Dropdown([10,20,30], value=30, id='Num')],
        # dcc.Dropdown(['Market Index'], value='Australia', id='Benchmark')],
        style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id='graph'),
])

@app.callback(
     Output('graph', 'figure'),
     Input('Factor', 'value'),
     Input('Num', 'value'),
    #  Input('Benchmark', 'value')
    )
    
def update_graph(Factor,Num):
    temp = (stock_price[df[Factor + ' Rank'].sort_values()[0:Num].index].pct_change().mean(axis=1)+1).cumprod()
    temp = pd.DataFrame(temp,columns=[f'{Factor}_{Num}'])
    temp.index = stock_price['Date']
    temp.iloc[0,0] = 1
    fig = px.line(
        data_frame = temp,
        x = temp.index,
        y = f'{Factor}_{Num}')
    # fig.update_layout(yaxis_tickformat=".0%")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
