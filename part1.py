from dash import Dash, dcc, html, Input, Output,dash_table
import plotly.express as px
import pandas as pd

df = pd.read_excel('CAPE_Data_Final.xlsx')
countries = ['Australia', 'China', 'Japan', 'USA']

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
            'CAPE Equity Index Forecast'
            ),
    html.Div([
        dcc.RadioItems(['Return Prediction', 'Price Prediction'], 'Return Prediction', id='prediction_type', inline=True)
    ]),
    html.Div([
        dcc.Dropdown(countries, value='Australia', id='country_name')],
        style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id='graph'),
])

@app.callback(
     Output('graph', 'figure'),
     Input('prediction_type', 'value'),
     Input('country_name', 'value')
    )
    
def update_graph(prediction_type, country_name):
    filtered_df = df[[col for col in df.columns if country_name in col]]
    filtered_df['Date'] = df['Date']
    if prediction_type == 'Return Prediction':
        fig = px.line(
            data_frame = filtered_df,
            x = 'Date',
            y = [country_name + ' 10Y Return', country_name + ' 10Y Prediction'])
    else:
        fig = px.line(
            data_frame = filtered_df,
            x = 'Date',
            y = [country_name + ' Price', country_name + ' 10Y Price Prediction'])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
