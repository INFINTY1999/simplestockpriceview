from dash import Dash,dcc,html,Input,Output
import yfinance as yf
import plotly.express as px
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import date, timedelta,datetime
import calendar
from dateutil.relativedelta import relativedelta

app = Dash(__name__)
server = app.server

def dat(m):
    global startdate
    if m == None:
        now = date.today()
        l = datetime.strptime(str(now), '%Y-%m-%d').date()
        startdate = date(l.year,1,1)
    else:
        startdate = datetime.now() - relativedelta(years=m)
        

#get the data 
def get_data(ticker):
    df = yf.Ticker(ticker)
    nam = df.info['longName']
    df = yf.download(ticker,start=startdate,period='max')
    df.reset_index(inplace=True)
    return df,nam

#build graph 
def build_graph(df,nam):
    chart = px.line(df,x=df["Date"], y=df["Close"],title=nam)
    chart.layout.template='plotly_dark'
    return chart

#get data for month
def get_data2(ticker):
    df = yf.Ticker(ticker)
    nam = df.info['longName']
    df = yf.download(ticker,start=startdate,period='max')
    df.reset_index(inplace=True)
    
    q = df.iloc[-1]
    
    now = q['Date'].date()
    
    n = datetime.strptime(str(now), '%Y-%m-%d').date()
    
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    
    retur_date = []
    
    retur = []
    
    for i in range(0,n.month):
        first_day = now.replace(day=1)
        
        last_day = first_day - timedelta(days=1)
        
        l = datetime.strptime(str(last_day), '%Y-%m-%d').date()
        
        end_check = calendar.weekday(l.year,l.month,l.day)
        
        if (end_check==5):
            last_day = last_day - timedelta(days=1)
        elif(end_check==6):
            last_day = last_day - timedelta(days=2)
        
        retur_date.append(last_day)
        
        start_data=df.loc[(df['Date'].dt.date == now)]
        end_data=df.loc[(df['Date'].dt.date == last_day)]
        
        up = float(start_data['Close'])
        down = float(end_data['Close'])
        
        ret=((up/down)-1)
        g = float("{:.2f}".format(ret))
        
        retur.append(g)
        
        now = last_day 
    return retur_date,retur,nam

#buid graph 
def build_graph2(ret,retu,nam):
    chart = px.bar(x=ret,y=retu,title=nam+" Monthly Return")
    chart.layout.template='plotly_dark'
    return chart

#build dashboard 

colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}
app.title ="Stock Price Viewer"
app.layout = html.Div([
    html.H1(
        children='Stock Price Viewer',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.H3(
        children='Get a stock performance in a glimpse',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    
    html.Div([
        'Enter Stock Symbol : ',
        dcc.Input(id='input', value='', type='text')
    ],
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'marginBottom': '2rem'
        }
    ),
    
#    html.Div([
#        html.H3(id='my-output')
#    ],
#        style={
#            'textAlign': 'center',
#            'color': colors['text']
#        }
#    ),
    html.Div([   
              dcc.Dropdown(id="dropdown",
                 options =[
                   {"label":"1 Year", "value":1},
                   {"label":"3 Year", "value":3},
                   {"label":"5 Year", "value":5},
                 ]),
            ],
        style={'width': '49%','color': 'black'}),
    html.Div([
        dcc.Graph(id="graph"),
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    
    html.Div([
        dcc.Graph(id="graph-2")
    ], style={'display': 'inline-block', 'width': '49%'}),
    
])


# call backing fuctions 
@app.callback(
    [Output("graph","figure")],
    [Input("input","value")],
    [Input("dropdown","value")]
)
def build_the_dash(v,c):
    if v == '':
        raise PreventUpdate
    dat(c)
    df,nam = get_data(v)
    fig = build_graph(df,nam)
    return [fig]

@app.callback(
    [Output("graph-2","figure")],
    [Input("input","value")],
    [Input("dropdown","value")]
)
def build_the_dash1(v,c):
    if v == '':
        raise PreventUpdate
    dat(c)
    r,re,nam = get_data2(v)
    fig = build_graph2(r,re,nam)
    return [fig]  

if __name__ == '__main__':
    app.run_server(debug=True)