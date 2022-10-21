from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv('index.csv',index_col='Date')

index_list = ['^AXJO','^GSPC','^HSI']


app = Dash(__name__)

app.layout = html.Div([
    html.H1(
            'Stock Index Price'
            ),
    html.Div([
            dcc.Dropdown(
                index_list,value = '^AXJO',id='stock_index'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(
        id='graph'
    )
])


@app.callback(
     Output('graph', 'figure'),
     Input('stock_index', 'value')
    )
def update_graph(stock_index):
    filtered_df = df[stock_index]

    fig = px.line(
        data_frame = filtered_df,
        x = filtered_df.index,
        y = stock_index)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
