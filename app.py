# Immediate Aims: evaluate options prices and greeks based on usual inputs //
#                 return implied volatility based on usual inputs and the price of the option //
#                 return simple graphs - option price vs strike/vol/time to expiry 
#                 output implied vol curve
#                 apply to real data
#                 how to evaluate the real volatiliy of a stock
#                 generate web app to play around with it
#                 implement dividends
#
# Later Aims: research and implement Monte Carlo simulation
#             handle American options
#             research and implement 'calibration of volatility models (e.g. Heston)'
#             

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
from utils.charting_utils import generate_data_for_independent_variable
import dash_bootstrap_components as dbc

variable_label_dict = {'S': 'Stock Price', 'K': 'Strike', 'r': 'Interest rate', 'sigma': 'Volatility', 't': 'Time to maturity (Years)'}
initial_range_dict = {'S': [0, 500], 'K': [5, 500], 'r': [-0.02, 0.1], 'sigma': [0, 2], 't': [0, 2]}
option_type_colour_dict = {'call': '#960019', 'put': '#0041C2'}


tabs_styles = {
    'height': '44px',
    'borderBottom': '2px solid #444',
    'fontWeight': 500,
    'display': 'flex'
}

tab_style = {
  'backgroundColor': '#222',
  'color': '#bbb',
  'padding': '8px 16px',
  'border-radius': '8px 8px 0 0',
  'cursor': 'pointer',
  'border': 'none',
  'transition': 'background-color 0.2s ease, color 0.2s ease'
}

tab_selected_style = {
    'backgroundColor': '#1f77b4',
    'color': '#fff',
    'padding': '8px 16px',
    'borderRadius': '8px 8px 0 0',
    'cursor': 'pointer',
    'border': 'none',
    'transition': 'background-color 0.2s ease, color 0.2s ease'
}

external_stylesheets=[dbc.themes.SUPERHERO]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "greeks_visualization_tool"

# App layout
app.layout = dbc.Container([
    
    html.Br(),
    

    dbc.Row([
        html.Div(children= 'Visualising Black-Scholes option values and Greeks', 
                 style={'textAlign': 'center', 'color': 'white', 'fontSize': 30})
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='dependent_variable',
                options=[
                    {'label': 'Value', 'value': 'value'},
                    {'label': 'Delta', 'value': 'delta'},
                    {'label': 'Gamma', 'value': 'gamma'},
                    {'label': 'Vega', 'value': 'vega'},
                    {'label': 'Theta', 'value': 'theta'},
                    {'label': 'Rho', 'value': 'rho'}
                ],
                multi=False,
                value='value',
            ),
        ),
        
        dbc.Col(
            dcc.Dropdown(
                id='independent_variable',
                options=[
                    {'label': 'Stock Price', 'value': 'S'},
                    {'label': 'Strike', 'value': 'K'},
                    {'label': 'Interest rate', 'value': 'r'},
                    {'label': 'Volatility', 'value': 'sigma'},
                    {'label': 'Time to maturity (Years)', 'value': 't'}
                ],
                multi=False,
                value='sigma',
            ),
        ),
    ]),

    html.Br(),

    dcc.Tabs(
        id='option_type_tabs', 
        value='call',
        children=
        [
            dcc.Tab(label='Call', value='call', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Put', value='put', style=tab_style, selected_style=tab_selected_style),
        ],
        style=tabs_styles
    ),

    dcc.Graph(id='call_graph'),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText("S"),
                    dbc.Input(id='S_input', placeholder="Stock Price", value= 100, type="number", min=0, debounce=True)
                ]
            )
        ),
        
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText("K"),
                    dbc.Input(id='K_input', placeholder="Strike", value= 100, type="number", min=0, debounce=True)
                ]
            )
        ),

        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText("r"),
                    dbc.Input(id='r_input', placeholder="Interest rate", value= 0.05, type="number", step=0.01, debounce=True)
                ]
            )
        ),

        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText("σ"),
                    dbc.Input(id='σ_input', placeholder="Volatility", value= None, type="number", disabled=True, min=0, step=0.01, debounce=True)
                ]
            )
        ),

        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText("t"),
                    dbc.Input(id='t_input', placeholder="Time to maturity (Years)", value= 1, type="number", min=0, debounce=True)
                ]
            )
        ),
    ]),

    html.Br(),

    dbc.Row([
        html.Div(
            id = 'range_slider_text_prompt',
            children= 'Select the range for Volatility', 
            style={'textAlign': 'center', 'color': 'white', 'fontSize': 20}
        )
    ]),

    html.Br(),

    dcc.RangeSlider(
        id = 'independent_variable_slider',
        min=0, 
        max=2,
        value=[0.02, 0.1],
        marks=None,
        tooltip={
            "placement": "bottom",
            "always_visible": True,
            "style": {"fontSize": "20px"},
        },
    ),

    html.Br(),

    dbc.Col(
        dbc.Button(
            "Information",
            id="information_button",
            class_name="custom-info-btn",
            color='primary',
            n_clicks=0,
            style={'borderRadius': '20px', 'padding': '8px 20px'}
        ),
        width='auto',
        className='d-flex justify-content-center align-items-center'
    ),
    dbc.Offcanvas(
        [
            html.H4("About this app", className="mb-3"),

            html.P(
                "This is a visualisation tool for the Black-Scholes model for option contracts. "
                "You can explore how option values and Greeks change when adjusting inputs."
                
            ),

            html.P(
                "An option contract is a financial derivative that gives the owner the right "
                "to buy/sell (call/put) an underlying item for a prespecified price (strike) at "
                "a prespecified time."
            ),

            html.H5("Parameters", className="mt-4"),
            html.Ul([
                html.Li(html.Span("S – Stock Price: Current price of the underlying stock", style={"fontWeight": "bold"})),
                html.Li(html.Span("K – Strike Price: Price at which the owner can buy/sell", style={"fontWeight": "bold"})),
                html.Li(html.Span("r – Interest Rate: Rate at which you can borrow risk free", style={"fontWeight": "bold"})),
                html.Li(html.Span("σ – Volatility: A measure of how 'noisy' or 'calm' the underlying is expected to be", style={"fontWeight": "bold"})),
                html.Li(html.Span("T – Time to Expiry: Time until maturity of the contract", style={"fontWeight": "bold"})),
            ]),

            html.H5("Greeks", className="mt-4"),
            html.Ul([
                html.Li(html.Span("Delta – Sensitivity to underlying price")),
                html.Li(html.Span("Gamma – Sensitivity of Delta to price")),
                html.Li(html.Span("Vega – Sensitivity to volatility")),
                html.Li(html.Span("Theta – Time decay")),
                html.Li(html.Span("Rho – Sensitivity to interest rate")),
            ]),

            html.P(
                "Use the dropdowns at the top to choose your independent and dependent variables, and the "
                "controls on the bottom to vary inputs and visualise how the model behaves.",
                className="mt-4"
            ),
        ],
        id="information_offcanvas",
        title="Information",
        is_open=False,
        placement="start",
        scrollable=True,
    ),

    html.Br(),
    html.Br(),
    

    dcc.Store(id="variable_values_memory", data={"S": 100, "K": 100, "r": 0.05, "sigma": 0.1, "t": 1}),

])

###############################################################################################################################################
# Updating the Graph

@app.callback(
    Output(component_id='call_graph', component_property='figure'),
    [
        Input(component_id='independent_variable', component_property='value'),
        Input(component_id='dependent_variable', component_property='value'),
        Input(component_id='option_type_tabs', component_property='value'),
        Input(component_id='S_input', component_property='value'),
        Input(component_id='K_input', component_property='value'),
        Input(component_id='r_input', component_property='value'),
        Input(component_id='σ_input', component_property='value'),
        Input(component_id='t_input', component_property='value'),
        Input(component_id='independent_variable_slider', component_property='value'),
    ]
)

def update_graph(independent_variable, dependent_variable, option_type, S_input, K_input, r_input, σ_input, t_input, slider_input):
    try:
        # We get the initial values, and want to keep them the same while the chosen independent variable varies for the graph. 
        # We input the chosen dependent variable, independent variables and values to keep the other parameters at, and use 
        # generate_data_for_independent_variable to get the correct df, and plot using px.line
        unchanged_values = {'S': S_input, 'K': K_input, 'r': r_input, 'sigma': σ_input, 't': t_input}
        df = generate_data_for_independent_variable(
            unchanged_values= unchanged_values,
            independent_variable = independent_variable,
            independent_variable_range = slider_input,
            option_type = option_type,
            dependent_variable = dependent_variable,
            n = 1000
        )
        x = variable_label_dict[independent_variable]
        y = dependent_variable.capitalize()
        labels = {'x': x, 'y': y}
        fig = px.line(df, x='x', y='y', labels=labels, template="plotly_dark", title=f'{y} vs {x}')
        fig.update_traces(
            line=dict(width=3, color=option_type_colour_dict[option_type]),
            marker=dict(size=6, symbol="circle", line=dict(width=1, color="#000"))
        )

        # Layout styling
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#333",
            paper_bgcolor="#333",
            font=dict(family="Arial, sans-serif", size=14, color="#ddd"),
            xaxis=dict(
                showgrid=True, gridcolor="#333", zeroline=False,
                linecolor="#555", ticks="outside", tickcolor="#555",
            ),
            yaxis=dict(
                showgrid=True, gridcolor="#333", zeroline=False,
                linecolor="#555", ticks="outside", tickcolor="#555"
            ),
            title={
                'text': f"Black–Scholes {y} vs {x}",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top', 
            },
            title_font=dict(
                family="Times New Roman",
                size=26,
                color="white"
            ),
            margin=dict(l=60, r=30, t=40, b=50),
            hovermode="x unified",
        )
    except Exception:
        # fallback empty figure with a message
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text="⚠️ Please enter valid input values",
                    x=0.5, y=0.5, xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=18, color="red")
                )
            ]
        )
        return fig
    return fig

###############################################################################################################################################
# Disable the independent variable Input, and revert previous independent variable to its previous value

@app.callback(
    [
        Output(component_id='S_input', component_property='disabled'),
        Output(component_id='K_input', component_property='disabled'),
        Output(component_id='r_input', component_property='disabled'),
        Output(component_id='σ_input', component_property='disabled'),
        Output(component_id='t_input', component_property='disabled'),
        Output(component_id='S_input', component_property='value'),
        Output(component_id='K_input', component_property='value'),
        Output(component_id='r_input', component_property='value'),
        Output(component_id='σ_input', component_property='value'),
        Output(component_id='t_input', component_property='value'),
    ],
    [
        Input(component_id='independent_variable', component_property='value'),
        Input(component_id='variable_values_memory', component_property='data')
    ]
)

def disable_independent_variable_and_revert_previous_value(independent_variable, memory):
    # We want only the independent variable to be disabled
    disabled_dict = {'S': False, 'K': False, 'r': False, 'sigma': False, 't': False}
    disabled_dict[independent_variable] = True

    # We also want said variable to have value None so that the placeholder is shown instead of the previous value
    values_dict = memory.copy()
    values_dict[independent_variable] = None
    return list(disabled_dict.values()) + list(values_dict.values())

###############################################################################################################################################
# Updating the dcc.Store of the most recent value

@app.callback(
        Output("variable_values_memory", "data"),
    [
        Input("S_input", "value"),
        Input("K_input", "value"),
        Input("r_input", "value"),
        Input("σ_input", "value"),
        Input("t_input", "value"),
        State("variable_values_memory", "data"),
        State(component_id='independent_variable', component_property='value'),
    ],
    prevent_initial_call=True
)
def update_memory(S_input, K_input, r_input, σ_input, t_input, memory, independent_variable):
    # Define dictionary of current inputs
    current_inputs = {'S': S_input, 'K': K_input, 'r': r_input, 'sigma': σ_input, 't': t_input}
    for parameter in list(memory.keys()):
        # Update the memory with the current value if it is not the independent variable
        if parameter != independent_variable:
            memory[parameter] = current_inputs[parameter]
    return memory

###############################################################################################################################################
# Updating the RangeSlider with the correct min, max and value

@app.callback(
    [
        Output("independent_variable_slider", "min"),
        Output("independent_variable_slider", "max"),
        Output("independent_variable_slider", "value"),
    ],
    [
        Input("independent_variable", 'value'),
        State("variable_values_memory", 'data')
    ],
    prevent_initial_call=True
)
def update_range_slider(independent_variable, variable_values_memory):
    # Get the desired min and max from the dictionary
    min, max = initial_range_dict[independent_variable]
    # Get the most recent valid value entered for said variable, and build the starting range around that
    center = variable_values_memory[independent_variable]
    if center > 2*max/3:
        center = 2*max/3
    value = [center/2, 3*center/2]

    return [min, max, value]


###############################################################################################################################################
# Updating the html.Div prompt for the range slider with the name of the variable

@app.callback(
        Output("range_slider_text_prompt", 'children'),
    [
        Input("independent_variable", 'value'),
    ],
    prevent_initial_call=True
)
def update_range_slider(independent_variable):
    # Define dictionary of desired label mappings
    return f'Select the range for {variable_label_dict[independent_variable]}:'

###############################################################################################################################################
# Toggling the information offcanvas

@app.callback(
    Output("information_offcanvas", "is_open"),
    Input("information_button", "n_clicks"),
    [State("information_offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

###############################################################################################################################################
# Running the app

if __name__ == '__main__':
    app.run(debug=True)
