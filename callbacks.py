from app import app
from layouts import fd_plot,sfd_plot,tp_plot
from vdplot import*
import pandas as pd
from datetime import datetime
from dash.dependencies import Output, Input, State



day, DB = [], vdplot()
for i in pd.date_range(start="2020-11-01",end="2020-11-30"):
    d = datetime.strftime(i,'%Y-%m-%d').replace('-','')
    day.append(d)
    data = vdload(d,'5',path='data')
    DB.add(data)

def search_dayofweek(sd,ed,wd):
    find = []
    days = pd.date_range(start=sd,end=ed).to_series().to_list()
    s = pd.date_range(start=sd,end=ed).to_series().dt.weekday.to_list()
    temp = {}
    for i in range(len(days)):
        temp[days[i]] = s[i]
    #search for selected days of week in selected date range
    for key,value in temp.items():
        if value in wd:
            find.append(key)
    for i in range(len(find)):
        find[i] = datetime.strftime(find[i],'%Y-%m-%d').replace('-','')
    return find

@app.callback(
    [Output("graphs", "children"),
    Output('update-button', 'n_clicks')],
    [Input("graphtabs", "value")])
def render_graph_content(gtab):
    if gtab == "Fundamental-Diagram":
        return [fd_plot], 1
    elif gtab == "Speed-Flow-Diagram":
        return [sfd_plot], 1
    elif gtab == "Hour-of-Day-Traffic-Pattern":
        return [tp_plot], 1

@app.callback(
    [Output('location-dropdown', 'value'),
    Output('location-dropdown-active', 'data')],
    [Input('location-dropdown', 'value'),
    State('location-dropdown-active', 'data')],)
def update_loc_none_options(value,active):
    if len(value) < 1:
        return active, active
    else:
        return value, value

@app.callback(
    [Output('weekdays', 'value'),
    Output('weekdays-active', 'data')],
    [Input('weekdays', 'value'),
    State('weekdays-active','data')])
def update_wee_none_options(value,active):
    if len(value) < 1:
        return active, active
    else:
        return value, value

@app.callback(
    [Output(component_id='fundamental_d',component_property='figure')],
    [Input(component_id='update-button', component_property='n_clicks'),
    State(component_id='date-picker',component_property='start_date'),
    State(component_id='date-picker',component_property='end_date'),
    State(component_id='location-dropdown',component_property='value'),
    State(component_id='time-slider',component_property='value'),
    State(component_id='weekdays',component_property='value'),]
)
def update_fd_graph(n_clicks,sdate,edate,loc,time_r,weekdays):
    if n_clicks > 0:
        find = search_dayofweek(sdate,edate,weekdays)
        stime, etime = time_r[0]*12, time_r[1]*12

        loc = [loc[i].split('-')[0] for i in range(len(loc))]

        return [DB.plot_fundamental_d(loc,find, stime, etime)]

@app.callback(
    [Output(component_id='speedflow_d',component_property='figure')],
    [Input(component_id='update-button', component_property='n_clicks'),
    State(component_id='date-picker',component_property='start_date'),
    State(component_id='date-picker',component_property='end_date'),
    State(component_id='location-dropdown',component_property='value'),
    State(component_id='time-slider',component_property='value'),
    State(component_id='weekdays',component_property='value')]
)
def update_sf_graph(n_clicks,sdate,edate,loc,time_r,weekdays):
    if n_clicks > 0:
        find = search_dayofweek(sdate,edate,weekdays)
        stime, etime = time_r[0]*12, time_r[1]*12
        loc = [loc[i].split('-')[0] for i in range(len(loc))]

        return [DB.plot_speedflow_d(loc,find, stime, etime)]

@app.callback(
    [Output(component_id='trafficpattern',component_property='figure')],
    [Input(component_id='update-button', component_property='n_clicks'),
    State(component_id='date-picker',component_property='start_date'),
    State(component_id='date-picker',component_property='end_date'),
    State(component_id='location-dropdown',component_property='value')]
)
def update_tf_graph(n_clicks,sdate,edate,loc):
    if n_clicks > 0:
        find = pd.date_range(start=sdate,end=edate).to_series().to_list()
        for i in range(len(find)):
            find[i] = datetime.strftime(find[i],'%Y-%m-%d').replace('-','')
        loc = [loc[i].split('-')[0] for i in range(len(loc))]
        fig = DB.plot_traffic_pattern()
        DB.plot_time_series_flow(loc,find,fig)
        DB.plot_speed_heatmap(find,fig)
        return [fig]