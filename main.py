#Import required packages and libraries

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pandas_ta as ta
import requests

#Different bootstrap themes can be added to the web applications using this 
app= Dash(external_stylesheets = [dbc.themes.CYBORG])


#Designing the dropdowns for the web application to get user input
def create_dropdown(option, id_value):

    return html.Div(
            [
                html.H2(" ".join(id_value.replace("-"," ").split(" ")[:-1]),
                    style={"padding":"10px 10px 10px 20px"}),    
                dcc.Dropdown(option,id=id_value, value=option[0])
                ],style={"padding":"0px 20px 0px 30px"}
        )   


#Layout of the web application- the position of the elements and how they appear can be modified here

app.layout = html.Div([
                    
                        html.Div([
                                    html.H1("Crypto Currency Dashboard",style={"text-align-last": "center", "font-variant-caps": "small-caps","padding":"20px 20px 30px 30px"})

                        ]),
                        

                        html.Div([
                            html.Div([
                                    html.Div([
                                    create_dropdown(["btcusd","ethusd","xrpusd","ltcusd","gbpusd","eurusd","bchusd","paxusd","dogeusd"],"Currency-select"),
                                    create_dropdown(["259200", "86400", "43200", "21600", "14400", "7200", "3600", "1800", "900", "300", "180"],"Timeframe-select"),
                                    create_dropdown(["200","150","100","50","20"],"Candles-select"),
                                    create_dropdown(["Off","On"],"Bollinger-select"),
                                    create_dropdown(["Off","On"],"Fibonacci-select"),
                                    
                                ], style={"display":"table-row","margin":"auto", "width":"800px","justify-content":"space-around"}),

                                    
                                    
                                    ]), 
                            html.Div([

                            dcc.Graph(id="candlesticks"),
                            dcc.Graph(id="indicator"),
                            

                            
                            
                            ],style={"display":"flex","flex-direction":"column","width":"900px"}),

                        
                        ],style={"display":"flex","flex-direction":"row"})


                        ],style={"display":"flex","flex-direction":"column"})


#application callbacks to handle the inputs and outputs when undating the figures in the web application

@app.callback(
        Output("candlesticks","figure"),
        Output("indicator","figure"),
        Input("Currency-select","value"),
        Input("Timeframe-select","value"),
        Input("Candles-select","value"),
        Input("Bollinger-select","value"),
        Input("Fibonacci-select","value"),
        
        
)

def update_figure(Currency, timeframe, candles,bands,lines):
   
    #API #Requires the name of the currency to be added into it to get the data
    url=f"https://www.bitstamp.net/api/v2/ohlc/{Currency}/"
    
    #Api parameters
    params = {
        "step":timeframe,
        "limit":int(candles)+14,
            }
    

    data = requests.get(url, params=params).json()["data"]["ohlc"]
    data= pd.DataFrame(data) #Pandas dataframe with OHLC data 
    data.timestamp = pd.to_datetime(pd.to_numeric(data.timestamp), unit='s')
    data["rsi"] = ta.rsi(data.close.astype(float)) #data for the RSI
    
    

    data= data.iloc[14:]

    

    # Compute Bollinger Bands
    rolling_mean = data['close'].rolling(window=20).mean()
    rolling_std = data['close'].rolling(window=20).std()
    upper_band = rolling_mean + 2 * rolling_std
    lower_band = rolling_mean - 2 * rolling_std

    # Compute Fibonacci retracement levels
    max_price = data["high"].max()
    min_price = data["low"].min()
    diff = float(max_price) - float(min_price)
    levels = [float(max_price),float(max_price) - (0.236 * diff), float(max_price) - (0.382 * diff), float(max_price) - (0.5 * diff),
              float(max_price) - (0.618 * diff), float(max_price) - (0.786 * diff),float(max_price) - (0.886 * diff), float(min_price)]
    
    # Create the Candlestick trace
    candlesticks_trace = go.Candlestick(
        x=data.timestamp,
        open=data.open,
        high=data.high,
        low=data.low,
        close=data.close,
        
    )
    
    # Create the Bollinger Bands traces
    upper_band_trace = go.Scatter(
        x=data.timestamp,
        y=upper_band,
        name='Upper Bollinger Band',
        visible=True if bands == "On" else False
        
    )
    
    lower_band_trace = go.Scatter(
        x=data.timestamp,
        y=lower_band,
        name='Lower Bollinger Band',
        visible=True if bands == "On" else False
    )
    #Create Fibonacci level traces
    level_traces = []
    for i, level in enumerate(levels):
        level_trace = go.Scatter(
            x=data.timestamp,
            y=np.repeat(level, len(data)),
            name=f"Level {i+1}",
            visible=True if lines == "On" else False,
            line_color=f"rgb(255, {(i+1)*40}, 0)"
        )
        level_traces.append(level_trace)


    # Update the figure with the new traces
    candlesticks = go.Figure(data=[candlesticks_trace, upper_band_trace, lower_band_trace]+level_traces)
    


    #Modifying how the Candlesticks plot and RSI plot looks like
    candlesticks.update_layout(xaxis_rangeslider_visible=False,height=400, template="plotly_dark",title=f"{Currency.upper()} Candlesticks with Bollinger bands and Fibonacci Retracement Levels")
    indicator = px.line(x=data.timestamp,y=data.rsi , height = 300, template="plotly_dark", labels={ "x": "DateTime", "y":"RSI"}, title="Relative Strength Index")
    

    return candlesticks, indicator


if __name__== '__main__':
    app.run_server(debug=True,)
