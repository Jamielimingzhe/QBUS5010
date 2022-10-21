from dash import Dash, dcc, html, Input, Output,dash_table
import plotly.express as px
import pandas as pd

df = pd.read_csv('index.csv',index_col='Date')
df_table = pd.read_csv('rank_table_demo.csv')

index_list = ['^AXJO','^GSPC','^HSI']


app = Dash(__name__)

app.layout = html.Div([
    html.H1(
            'Stock Index Price'
            ),
    html.Div([dcc.Dropdown(index_list,value = '^AXJO',id='stock_index')], style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id='graph'),
    dash_table.DataTable(
    id='datatable-paging',
    columns=[
        {"name": i, "id": i} for i in df_table.columns
    ],
    page_current=0,
    page_size=10,
    page_action='custom'
)
])

@app.callback(
    Output('datatable-paging', 'data'),
    Input('datatable-paging', "page_current"),
    Input('datatable-paging', "page_size"))
def update_table(page_current,page_size):
    return df_table.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')


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
