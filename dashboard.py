import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


df = pd.read_csv(r"D:\Personal_expense_tracker_github\Personal-Expense-Tracker\MOCK_DATA.csv")

# Dash app
app = Dash(__name__)

# dashboard layout
app.layout = html.Div([
    html.H1('Financial Dashboard'),
    html.Div([
        html.Label('Select Attribute'),
        dcc.Dropdown(
            id='attribute-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            value='Rent'
        )
    ]),
    html.Div([
        html.Label('Select Plot Type'),
        dcc.Dropdown(
            id='plot-type-dropdown',
            options=[
                {'label': 'Histogram', 'value': 'Histogram'},
                {'label': 'Scatter', 'value': 'Scatter'},
                {'label': 'Bar', 'value': 'Bar'},
                {'label': 'Line', 'value': 'Line'}
            ],
            value='Histogram'
        )
    ]),
    dcc.Graph(id='attribute-graph'),
    html.H2('Pie Chart of All Attributes'),
    html.Div([
        html.Label('Select Attributes for Pie Chart'),
        dcc.Dropdown(
            id='pie-attributes-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns if col not in ['Year', 'Month', 'Date']],
            value=['Rent', 'Mortgage', 'Food', 'Water', 'Electricity', 'EMI', 'Utilities'],
            multi=True
        )
    ]),
    dcc.Graph(id='pie-chart')
])

#  functions to create different types of plots
def create_histogram(df, attribute):
    fig = px.histogram(df, x=attribute, title=f'Histogram of {attribute}')
    return fig

def create_scatter_plot(df, attribute):
    fig = px.scatter(df, x='Date', y=attribute, color='Month', title=f'Scatter plot of {attribute}')
    return fig

def create_bar_chart(df, attribute):
    fig = px.bar(df, x='Date', y=attribute, color='Month', title=f'Bar chart of {attribute}')
    return fig

def create_line_chart(df, attribute):
    fig = px.line(df, x='Date', y=attribute, color='Month', title=f'Line chart of {attribute}')
    return fig

def create_pie_chart(df, attributes):
    sums = df[attributes].sum()
    fig = px.pie(values=sums.values, names=sums.index, title='Pie Chart of Selected Attributes')
    return fig

# Define callback to update the main graph based on selected attribute and plot type
@app.callback(
    Output('attribute-graph', 'figure'),
    [Input('attribute-dropdown', 'value'),
     Input('plot-type-dropdown', 'value')]
)
def update_graph(selected_attribute, plot_type):
    if plot_type == 'Histogram':
        fig = create_histogram(df, selected_attribute)
    elif plot_type == 'Scatter':
        fig = create_scatter_plot(df, selected_attribute)
    elif plot_type == 'Bar':
        fig = create_bar_chart(df, selected_attribute)
    elif plot_type == 'Line':
        fig = create_line_chart(df, selected_attribute)
    return fig


@app.callback(
    Output('pie-chart', 'figure'),
    [Input('pie-attributes-dropdown', 'value')]
)
def update_pie_chart(selected_attributes):
    fig = create_pie_chart(df, selected_attributes)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
