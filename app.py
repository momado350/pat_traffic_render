import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_auth
from users import USERNAME_PASSWORD_PAIRS

# #https://www.rapidtables.com/web/color/RGB_Color.html
# circulationjcb = pd.read_csv('data/M.Ahmed Charge Hist log output with IDscb.csv', parse_dates=['Trans Hist Date'])
# circulationjcb = circulationjcb[circulationjcb['Item Type Code'] == 'EQ-ECFCB']
# circulationjcb = circulationjcb.groupby(['Trans Hist Date', 'Station Library Checkout'])['Item Type Code'].count().reset_index()

circulationjcb = pd.read_csv('data/Chromebooks stats.csv', parse_dates=['Trans Stat Date'])
circulationjcb_2 = circulationjcb.groupby(['Trans Stat Station Library','Trans Stat Itype', pd.Grouper(key='Trans Stat Date', freq='W-SAT',label='left',closed='left')])['Trans Stat Id'].count().reset_index()

circulationjan = pd.read_csv('data/M.Ahmed Charge Hist log output with IDs.csv', parse_dates=['Trans Hist Date'])
circulationaug = pd.read_csv('data/M.Ahmed Charge Hist log output with IDs8.csv', parse_dates=['Trans Hist Date'])
circulation = circulationjan.append(circulationaug, ignore_index=True).drop_duplicates()

#circulation = pd.read_csv('data/M.Ahmed Charge Hist log output with IDs.csv', parse_dates=['Trans Hist Date'])
# import pyodbc
# conn = pyodbc.connect('Driver={SQL Server};'
#                       'Server=kcplsql;'
#                       'Database=KCPL_TBS_Archive;'
#                       'Trusted_Connection=yes;')

# computer = pd.read_sql_query('SELECT * FROM MyPC3SessionAudit WHERE StartTime > ?', conn, parse_dates=['StartTime'], params=['2022-01-21 20:26:15'])
computer = pd.read_csv('data/computer.csv', parse_dates=['StartTime'])

# computer data
mask = computer['SiteName'].isin(['__Not In Use', '_default', '_IS Testing Lab'])
computer = computer[~mask]
replace_values = {'Lucile H. Bluford Branch': 'KC-BLUFORD', 'Plaza Branch': 'KC-PLAZA', 'Central Library': 'KC-CENTRAL', 'Waldo Branch': 'KC-WALDO', 'Southeast Branch': 'KC-SE', 'North-East Branch': 'KC-NE', 'Trails West Branch': 'KC-TRAILS', 'Westport Branch': 'KC-WSTPORT', 'Irene H. Ruiz Biblioteca de las Americas': 'KC-RUIZ', 'Sugar Creek Branch': 'KC-SGCREEK'}
computer = computer.replace({"SiteName": replace_values})
computer1 = computer[['StartTime', 'EndTime', 'SessionID', 'SiteName']]
computer1['Date'] = computer1['StartTime'].dt.date
computer1['time'] = computer1['StartTime'].dt.time
computer1['year'] = computer1['StartTime'].dt.year
computer1['week_day'] = computer1['StartTime'].dt.day_name()
computer1['time'] = computer1['time'].astype(str)
computer1['hour'] = computer1['time'].str.split(':').str[0]
computer1['hour'] = computer1['hour'].astype(int)
computer1['date'] = pd.to_datetime(computer1['Date'])
grouped = computer1.groupby(['date','SiteName', 'hour'])['SessionID'].count().reset_index()
replace_values = {8: '8 AM', 9: "9 AM", 10: "10 AM", 11: "11 AM", 12: "12 PM", 13: "1 PM", 14: "2 PM", 15: "3 PM", 16: "4 PM", 17: "5 PM", 18: "6 PM", 19: "7 PM", 20: "8 PM", 21: '9'}
computer_df = grouped.replace({"hour": replace_values})
computer_df.rename(columns={'date': 'Trans Hist Date', 'SiteName': 'Station Library Checkout', 'hour': 'hours'}, inplace=True)
mask1 = circulation['User Profile'].isin(['MISSING', 'KC-DISPLAY', 'KC-MAINT', 'DISCARD', 'KC-STAFF', 'DAMAGED', 'KC-CATALOG', 'KC-SUSPND',
 'LOST', 'KCP-ILL', 'KC-COLDEV', 'KC-TFRBTG', 'KC_CAT1', 'REPLACE'])
circulation = circulation[~mask1]
circulation['trans_time'] = circulation['Trans Hist Datetime'].str.split(' ').str[1]
circulation['hour'] = circulation['trans_time'].str.split(':').str[0]
circulation1 = circulation.groupby(['Trans Hist Date', 'Station Library Checkout', 'hour'])['User Id'].unique().reset_index()
## circulation1 = pd.DataFrame(circulation1)
#circulation1['patron'] = circulation['User Id'].unique()
circulation1['patrons'] = circulation1['User Id'].apply(lambda x: len(x))#.reset_index()
circulation2 = circulation1[['Trans Hist Date', 'Station Library Checkout', 'hour', 'patrons']]
#circulation2['patrons'] = circulation2['patrons'].fillna(0)
circulation2['hours'] = circulation2['hour'].astype(int)
circulation2['week_day'] = circulation2['Trans Hist Date'].dt.day_name()
replace_values = {9: "9 AM", 10: "10 AM", 11: "11 AM", 12: "12 PM", 13: "1 PM", 14: "2 PM", 15: "3 PM", 16: "4 PM", 17: "5 PM", 18: "6 PM", 19: "7 PM", 20: "8 PM"}
circulation2 = circulation2.replace({"hours": replace_values})
mer_df = pd.merge(circulation2, computer_df)
mer_df['total'] = mer_df['SessionID'] + mer_df['patrons']
#mer_df = pd.merge(mer_df, circulationjcb)

covid_data_1 = mer_df.groupby(['Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
covid_data_1w = mer_df.groupby([pd.Grouper(key='Trans Hist Date', freq='W-SAT',label='left',closed='left')])[['patrons', 'SessionID', 'total']].sum().reset_index()
covid_data_1m = mer_df.groupby([pd.Grouper(key='Trans Hist Date', freq='M')])[['patrons', 'SessionID', 'total']].sum().reset_index()

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server

app.layout = html.Div([
    
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url("lib_logo.png"),
                     id = 'corona-image',
                     style={'height': '60px',
                            'width': 'auto',
                            'margin-bottom': '25px'})


        ], className='one-third column'),

        html.Div([
            html.Div([
                html.H3('Patrons Traffic Dashboard', style={'margin-bottom': '0px', 'color': 'white'}),
                html.H5('Track Patron Traffic by Library Branch', style={'margin-bottom': '0px', 'color': 'white'})
            ])

        ], className='one-half column', id = 'title'),

        html.Div([
            html.H6('Last Updated: ' + str(mer_df['Trans Hist Date'].iloc[-1].strftime('%B %d, %Y')) + ' 00:01 (UTC)',
                    style={'color': 'orange'})

        ], className='one-third column', id = 'title1')

    ], id = 'header', className= 'row flex-display', style={'margin-bottom': '25px'}),

    html.Div([
        html.Div([
            html.H6(children='All Year to Date Traffic',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1['total'].sum():,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Last Month: ' + f"{covid_data_1m['total'].iloc[-1]:,.0f}"
                   + ' (' + str(round(((covid_data_1m['total'].iloc[-1]) /
                                   covid_data_1['total'].sum()) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

html.Div([
            html.H6(children="Total Traffic Last Week",
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1w['Trans Hist Date'].iloc[-2].strftime('%B %d, %Y')}",
            style={'textAlign': 'center',
                           'color': 'white',
                           'fontSize': 14}),
            html.P(f"{covid_data_1w['total'].iloc[-2]:,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Week Before: ' + f"{covid_data_1w['total'].iloc[-3]:,.0f}"
                   + ' (' + str(round(((covid_data_1w['total'].iloc[-2]-covid_data_1w['total'].iloc[-3]) /
                                   covid_data_1w['total'].iloc[-3]) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

html.Div([
            html.H6(children="Patrons used computer Last Week",
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1w['Trans Hist Date'].iloc[-2].strftime('%B %d, %Y')}",
            style={'textAlign': 'center',
                           'color': 'white',
                           'fontSize': 14}),
            html.P(f"{covid_data_1w['SessionID'].iloc[-2]:,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Week Before: ' + f"{covid_data_1w['SessionID'].iloc[-3]:,.0f}"
                   + ' (' + str(round(((covid_data_1w['SessionID'].iloc[-2]-covid_data_1w['SessionID'].iloc[-3]) /
                                   covid_data_1w['SessionID'].iloc[-3]) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

html.Div([
            html.H6(children="patrons checkedout items Last Week",
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1w['Trans Hist Date'].iloc[-2].strftime('%B %d, %Y')}",
            style={'textAlign': 'center',
                           'color': 'white',
                           'fontSize': 14}),
            html.P(f"{covid_data_1w['patrons'].iloc[-2]:,.0f}",
                    style={'textAlign': 'center',
                           'color': 'orange',
                           'fontSize': 40}),
            html.P('Week Before: ' + f"{covid_data_1w['patrons'].iloc[-3]:,.0f}"
                   + ' (' + str(round(((covid_data_1w['patrons'].iloc[-2]-covid_data_1w['patrons'].iloc[-3]) /
                                   covid_data_1w['patrons'].iloc[-3]) * 100, 2)) + '%)',
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),

    ], className='row flex display'),
    html.Div([
        html.Div([
            html.P('Select Branch:', className='fix_label', style={'color': 'white'}),
            dcc.Dropdown(id = 'w_countries',
                         multi = False,
                         searchable= True,
                         value='KC-PLAZA',
                         placeholder= 'Select Countries',
                         options= [{'label': c, 'value': c}
                                   for c in (mer_df['Station Library Checkout'].unique())], className='dcc_compon'),
            html.P('Branch Traffic: ' + ' ' + str(covid_data_1w['Trans Hist Date'].iloc[-2].strftime('%B %d, %Y')),
                   className='fix_label', style={'text-align': 'center', 'color': 'white'}),
            dcc.Graph(id = 'confirmed', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
dcc.Graph(id = 'death', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
dcc.Graph(id = 'recovered', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
# dcc.Graph(id = 'active', config={'displayModeBar': False}, className='dcc_compon',
#                       style={'margin-top': '20px'})

        ], className='create_container three columns'),

        html.Div([
dcc.Graph(id = 'pie_chart', config={'displayModeBar': 'hover'}
                      )
        ], className='create_container four columns'),

html.Div([
dcc.Graph(id = 'line_chart', config={'displayModeBar': 'hover'}
                      )
        ], className='create_container five columns'),

    ], className='row flex-display'),

##########################################################################
    html.Div([
html.Div([
dcc.Graph(id = 'map_chart', config={'displayModeBar': 'hover'}
                      )
        ], className='create_container1 twelve columns')

    ], className='row flex-display'),
####
html.Div([
    html.Div([
            html.P('Select Branch:', className='fix_label', style={'color': 'white'}),
            dcc.Dropdown(id = 'w_countries1',
                         multi = False,
                         searchable= True,
                         value='KC-PLAZA',
                         placeholder= 'Select Countries',
                         options= [{'label': c, 'value': c}
                                   for c in (circulationjcb['Trans Stat Station Library'].unique())], className='dcc_compon'),
            html.P('Chromebooks as of: ' + ' ' + str(circulationjcb_2['Trans Stat Date'].iloc[-1].strftime('%B %d, %Y')),
                   className='fix_label', style={'text-align': 'center', 'color': 'white'}),
            dcc.Graph(id = 'confirmed1', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
dcc.Graph(id = 'death1', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
dcc.Graph(id = 'recovered1', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
# dcc.Graph(id = 'active', config={'displayModeBar': False}, className='dcc_compon',
#                       style={'margin-top': '20px'})

        ], className='create_container three columns'),
html.Div([
dcc.Graph(id = 'map_chart1', config={'displayModeBar': 'hover'}
                      )
        ], className='create_container1 twelve columns')

    ], className='row flex-display')
###########################################################

], id = 'mainContainer', style={'display': 'flex', 'flex-direction': 'column'})

@app.callback(Output('confirmed', 'figure'),
              [Input('w_countries','value')])
def update_confirmed(w_countries):
    mer_df_2 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='W-SAT',label='left',closed='left')])[['patrons', 'SessionID', 'total']].sum().reset_index()
    value_confirmed = mer_df_2[mer_df_2['Station Library Checkout'] == w_countries]['total'].iloc[-2]
    delta_confirmed = mer_df_2[mer_df_2['Station Library Checkout'] == w_countries]['total'].iloc[-3] 

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_confirmed,
               delta = {'reference': delta_confirmed,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Last Week Total',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

@app.callback(Output('death', 'figure'),
              [Input('w_countries','value')])
def update_confirmed(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='W-SAT',label='left',closed='left')])[['patrons', 'SessionID', 'total']].sum().reset_index()
    value_death = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['SessionID'].iloc[-2]
    delta_death = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['SessionID'].iloc[-3]

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_death,
               delta = {'reference': delta_death,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Patrons used computer Last Week',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

@app.callback(Output('recovered', 'figure'),
              [Input('w_countries','value')])
def update_confirmed(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout', pd.Grouper(key='Trans Hist Date', freq='W-SAT',label='left',closed='left')])[['patrons', 'SessionID', 'total']].sum().reset_index()
    value_recovered = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['patrons'].iloc[-2]
    delta_recovered = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['patrons'].iloc[-3]

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_recovered,
               delta = {'reference': delta_recovered,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'patrons checkedout items Last Week',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }
    ########################################################################
@app.callback(Output('confirmed1', 'figure'),
              [Input('w_countries1','value')])
def update_confirmed(w_countries1):
    circulationjcb_2 = circulationjcb.groupby(['Trans Stat Station Library','Trans Stat Itype', pd.Grouper(key='Trans Stat Date', freq='W-SAT',label='left',closed='left')])['Trans Stat Id'].count().reset_index()
    circulationjcb_2 = circulationjcb_2[circulationjcb_2['Trans Stat Itype'] == 'EQ-ECFCB']
    # cols = {'Trans Stat Date':'2022-01-03 00:00:00','Station Library Checkout':['KC-RUIZ'], 'Trans Stat Id':[0]}
    # empty = pd.DataFrame(data=cols)
    # circulationjcb_2 = empty.append(circulationjcb_2, ignore_index=False).drop_duplicates().reset_index().fillna(0)
    value_confirmed1 = circulationjcb_2[circulationjcb_2['Trans Stat Station Library'] == w_countries1]['Trans Stat Id'].iloc[-2]
    delta_confirmed1 = circulationjcb_2[circulationjcb_2['Trans Stat Station Library'] == w_countries1]['Trans Stat Id'].iloc[-3]

    
    


    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_confirmed1,
               delta = {'reference': delta_confirmed1,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Last Week Chromebooks',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

@app.callback(Output('death1', 'figure'),
              [Input('w_countries1','value')])
def update_confirmed(w_countries1):
    circulationjcb_2 = circulationjcb.groupby(['Trans Stat Station Library','Trans Stat Itype', pd.Grouper(key='Trans Stat Date', freq='1M',label='left',closed='left')])['Trans Stat Id'].count().reset_index()
    circulationjcb_2 = circulationjcb_2[circulationjcb_2['Trans Stat Itype'] == 'EQ-ECFCB']
    # cols = {'Trans Hist Date':'2022-01-03 00:00:00','Station Library Checkout':['KC-RUIZ'], 'Item Type Code':[0]}
    # empty = pd.DataFrame(data=cols)
    # circulationjcb_2 = empty.append(circulationjcb_2, ignore_index=False).drop_duplicates().reset_index().fillna(0)
    value_death1 = circulationjcb_2[circulationjcb_2['Trans Stat Station Library'] == w_countries1]['Trans Stat Id'].iloc[-2]
    delta_death1 = circulationjcb_2[circulationjcb_2['Trans Stat Station Library'] == w_countries1]['Trans Stat Id'].iloc[-3]

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_death1,
               delta = {'reference': delta_death1,
                        'position': 'right',
                        'valueformat': ',g',
                        'relative': False,
                        'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Last Month Chromebooks',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

@app.callback(Output('recovered1', 'figure'),
              [Input('w_countries1','value')])
def update_confirmed(w_countries1):
    circulationjcb_2 = circulationjcb.groupby(['Trans Stat Station Library','Trans Stat Itype', pd.Grouper(key='Trans Stat Date', freq='1M',label='left',closed='left')])['Trans Stat Id'].count().reset_index()
    circulationjcb_2 = circulationjcb_2[circulationjcb_2['Trans Stat Itype'] == 'EQ-ECFCB']
    value_recovered1 = circulationjcb_2['Trans Stat Id'].sum()
    
    # circulationjcb_2 = circulationjcb_2[circulationjcb_2['Station Library Checkout'] == w_countries1]['Item Type Code'].iloc[-1]
    #delta_recovered1 = circulationjcb_2[circulationjcb_2['Station Library Checkout'] == w_countries1]['Item Type Code'].iloc[-2]

    return {
        'data': [go.Indicator(
               mode='number+delta',
               value=value_recovered1,
            #    delta = {'reference': delta_recovered1,
            #             'position': 'right',
            #             'valueformat': ',g',
            #             'relative': False,
            #             'font': {'size': 15}},
               number={'valueformat': ',',
                       'font': {'size': 20}},
               domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'Legacy Chromebook Checkouts',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height = 50,

        )
    }

# @app.callback(Output('active', 'figure'),
#               [Input('w_countries','value')])
# def update_confirmed(w_countries):
#     covid_data_2 = covid_data.groupby(['date', 'Station Library Checkout'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
#     value_active = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-1] - covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-2]
#     delta_active = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-2] - covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-3]

#     return {
#         'data': [go.Indicator(
#                mode='number+delta',
#                value=value_active,
#                delta = {'reference': delta_active,
#                         'position': 'right',
#                         'valueformat': ',g',
#                         'relative': False,
#                         'font': {'size': 15}},
#                number={'valueformat': ',',
#                        'font': {'size': 20}},
#                domain={'y': [0, 1], 'x': [0, 1]}
#         )],

#         'layout': go.Layout(
#             title={'text': 'New Active',
#                    'y': 1,
#                    'x': 0.5,
#                    'xanchor': 'center',
#                    'yanchor': 'top'},
#             font=dict(color='#e55467'),
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             height = 50,

#         )
#     }

@app.callback(Output('pie_chart', 'figure'),
              [Input('w_countries','value')])
def update_graph(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout', 'Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
    confirmed_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['patrons'].sum()
    death_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['SessionID'].sum()
    recovered_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['total'].sum()
    #active_value = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries]['active'].iloc[-1]
    colors = ['orange', 'blue']

    return {
        'data': [go.Pie(
            # labels=['Circulation', 'Computer', 'Total of Both'],
            labels=['patrons checkedout items Last Week', 'Patrons used computer Last Week'],
            values=[confirmed_value, death_value, recovered_value],
            marker=dict(colors=colors),
            hoverinfo='label+value+percent',
            textinfo='label+value',
            hole=.7,
            rotation=45,
            # insidetextorientation= 'radial'

        )],

        'layout': go.Layout(
            title={'text': 'Branch Total (Year to Date): ' + (w_countries),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7}


        )
    }

@app.callback(Output('line_chart', 'figure'),
              [Input('w_countries','value')])
def update_graph(w_countries):
    covid_data_2 = mer_df.groupby(['Station Library Checkout','Trans Hist Date'])[['patrons', 'SessionID', 'total']].sum().reset_index()
    covid_data_21 = covid_data_2[covid_data_2['Station Library Checkout'] == w_countries][['Station Library Checkout', 'Trans Hist Date', 'total']].reset_index()
    covid_data_21['daily confirmed'] = covid_data_21['total'].shift(1)
    covid_data_21['Rolling Ave.'] = covid_data_21['total'].rolling(window=7).mean()


    return {
        'data': [go.Bar(
            x=covid_data_21['Trans Hist Date'].tail(30),
            y=covid_data_21['daily confirmed'].tail(30),
            name='Daily Patron Traffic',
            marker=dict(color='orange'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + covid_data_21['Trans Hist Date'].tail(30).astype(str) + '<br>' +
            '<b>Daily Traffic Numbers</b>: ' + [f'{x:,.0f}' for x in covid_data_21['daily confirmed'].tail(30)] + '<br>' +
            '<b>Branch</b>: ' + covid_data_21['Station Library Checkout'].tail(30).astype(str) + '<br>'


        ),
            go.Scatter(
                x=covid_data_21['Trans Hist Date'].tail(30),
                y=covid_data_21['Rolling Ave.'].tail(30),
                mode='lines',
                name='Rolling Average of the last 7 days - daily Patron Traffic',
                line=dict(width=3, color='#FF00FF'),
                hoverinfo='text',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['Trans Hist Date'].tail(30).astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['Rolling Ave.'].tail(30)] + '<br>'


            )],

        'layout': go.Layout(
            title={'text': 'Last 30 Days Daily Patron Traffic: ' + (w_countries),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Daily Patron Traffic</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       )


        )
    }

@app.callback(Output('map_chart', 'figure'),
              [Input('w_countries','value')])
def update_graph(w_countries):
    
    covid_data_21 = mer_df.groupby(['Station Library Checkout','Trans Hist Date', 'hours'])['total'].sum().reset_index()
    covid_data_21 = covid_data_21[covid_data_21['Station Library Checkout'] == w_countries][['Station Library Checkout', 'Trans Hist Date','hours', 'total']].reset_index()
    covid_data_21 = pd.pivot_table(covid_data_21, columns='hours', values='total', index='Trans Hist Date').fillna(0).round(decimals = 0)
    cols = {'date':'2022-01-03 00:00:00','1 PM':[0], '10 AM':[0], '11 AM':[0], '12 PM':[0], '2 PM':[0], '3 PM':[0], '4 PM':[0], '5 PM':[0],
       '6 PM':[0], '7 PM':[0], '8 PM':[0], '9 AM':[0]}
    empty = pd.DataFrame(data=cols).set_index("date")
    
    covid_data_21 = empty.append(covid_data_21, ignore_index=False).drop_duplicates().reset_index().fillna(0)
    #covid_data_211['daily confirmed'] = covid_data_211['total'].shift(1)
    #covid_data_21['Rolling Ave.'] = covid_data_21['total'].rolling(window=7).mean()
    


    return {
        'data': [go.Scatter(
            x=covid_data_21['index'],
            y=covid_data_21['9 AM'],
            name='9 AM',
            marker=dict(color='orange'),
            hoverinfo='text',
            visible='legendonly',
            hovertext=
            '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
            '<b>Daily Traffic Numbers</b>: ' + [f'{x:,.0f}' for x in covid_data_21['9 AM']] + '<br>' 
            + '<b>Hour</b>: ' + '9 AM' + '<br>'


        ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['10 AM'],
                mode='lines',
                name='10 AM',
                line=dict(width=3, color='#FF00FF'),
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['10 AM']] + '<br>' 
                + '<b>Hour</b>: ' + '10 AM' + '<br>'


            ),
                go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['11 AM'],
                mode='lines',
                name='11 AM',
                line=dict(width=3, color='red'),
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['11 AM']] + '<br>'
                + '<b>Hour</b>: ' + '11 AM' + '<br>'


            ),
                go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['12 PM'],
                mode='lines',
                name='12 PM',
                line=dict(width=3, color='green'),
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['12 PM']] + '<br>'
                + '<b>Hour</b>: ' + '12 AM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['1 PM'],
                mode='lines',
                name='1 PM',
                line=dict(width=3, color='#000000'),
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['1 PM']] + '<br>'
                + '<b>Hour</b>: ' + '1 PM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['2 PM'],
                mode='lines',
                name='2 PM',
                line=dict(width=3, color='#00FF00'),
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['2 PM']] + '<br>'
                + '<b>Hour</b>: ' + '2 PM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['3 PM'],
                mode='lines',
                name='3 PM',
                line=dict(width=3, color='#00FFFF'), #cyan
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['3 PM']] + '<br>'
                + '<b>Hour</b>: ' + '3 PM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['4 PM'],
                mode='lines',
                name='4 PM',
                line=dict(width=3, color='#008080'), #teal
                hoverinfo='text',
                #visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['4 PM']] + '<br>'
                + '<b>Hour</b>: ' + '4 PM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['5 PM'],
                mode='lines',
                name='5 PM',
                line=dict(width=3, color='#000080'), #navy
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['5 PM']] + '<br>'
                + '<b>Hour</b>: ' + '5 PM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['6 PM'],
                mode='lines',
                name='6 PM',
                line=dict(width=3, color='#A52A2A'),#brown
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['6 PM']] + '<br>'
                + '<b>Hour</b>: ' + '6 PM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['7 PM'],
                mode='lines',
                name='7 PM',
                line=dict(width=3, color='#FF7F50'),#coral
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['7 PM']] + '<br>'
                + '<b>Hour</b>: ' + '7 PM' + '<br>'


            ),
            go.Scatter(
                x=covid_data_21['index'],
                y=covid_data_21['8 PM'],
                mode='lines',
                name='8 PM',
                line=dict(width=3, color='#FFD700'),#gold
                hoverinfo='text',
                visible='legendonly',
                hovertext=
                '<b>Date</b>: ' + covid_data_21['index'].astype(str) + '<br>' +
                '<b>Daily Traffic</b>: ' + [f'{x:,.0f}' for x in covid_data_21['8 PM']] + '<br>'
                + '<b>Hour</b>: ' + '8 PM' + '<br>'


            )
            
            ],

        'layout': go.Layout(
            title={'text': 'Year to date Daily Patron Traffic: ' + (w_countries),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Daily Patron Traffic</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       )


        )
    }
    ##
@app.callback(Output('map_chart1', 'figure'),
              [Input('w_countries1','value')])
def update_graph(w_countries1):
    circulationjcb_3 = circulationjcb.groupby(['Trans Stat Station Library','Trans Stat Date', 'Trans Stat Itype'])['Trans Stat Id'].count().reset_index()
    both = circulationjcb_3[circulationjcb_3['Trans Stat Station Library'] == w_countries1][['Trans Stat Itype','Trans Stat Station Library', 'Trans Stat Date', 'Trans Stat Id']]#.reset_index()
    chromebook = both[both['Trans Stat Itype'] == 'EQ-ECFCB']
    hotspot = both[both['Trans Stat Itype'] == 'EQ-ECFHOT']
    
    

    return {
        'data': [go.Scatter(
            x=chromebook['Trans Stat Date'],
            y=chromebook['Trans Stat Id'],
            mode='lines',
            name='Chromebooks',
            marker=dict(color='orange'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + chromebook['Trans Stat Date'].astype(str) + '<br>' +
            '<b>Daily Chromebook Numbers</b>: ' + [f'{x:,.0f}' for x in chromebook['Trans Stat Id']] + '<br>' 
            #+ '<b>Hour</b>: ' + '9 AM' + '<br>'


        ),
        go.Scatter(
            x=hotspot['Trans Stat Date'],
            y=hotspot['Trans Stat Id'],
            mode='lines',
            name='ECF-Hotspots',
            marker=dict(color='blue'),
            hoverinfo='text',
            hovertext=
            '<b>Date</b>: ' + hotspot['Trans Stat Date'].astype(str) + '<br>' +
            '<b>Daily Hotspots Numbers</b>: ' + [f'{x:,.0f}' for x in hotspot['Trans Stat Id']] + '<br>'


        )
        ],

        'layout': go.Layout(
            # title={'text': 'Year to date Daily Patron Traffic: ' + (w_countries),
            title={'text': 'Year to date Daily ECF-Chromebooks and ECF-Hotspots checkouts: ' + (w_countries1),
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',
                       color = 'white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Daily Chromebook</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       )


        )
    }
    ##

if __name__ == '__main__':
    app.run_server(debug=True)

