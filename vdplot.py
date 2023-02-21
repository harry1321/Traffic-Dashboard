import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import copy
class vdload:
    def __init__(self, date, interval, path='D:/dashboard/data'):
        self.date = date
        self.interval = interval
        self.path = path
        self.section = 'all'
        self.flow = pd.read_csv(self.path+"/%s/%s_flow_vd_5min.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
        self.speed = pd.read_csv(self.path+"/%s/%s_speed_vd_5min.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
        self.occ = pd.read_csv(self.path+"/%s/%s_occ_vd_5min.csv"%(self.date,self.date), index_col=0, encoding = 'big5')

class vdplot:
    def __init__(self):
        self.db = {'flow':pd.DataFrame(),'speed':pd.DataFrame(),'occ':pd.DataFrame()}
        self.count = 0
        self.palette = ['#007bff','#6610f2','#6f42c1','#e83e8c','#dc3545','#fd7e14','#ffc107','#28a745','#20c997','#17a2b8']   
        vd_id = pd.read_csv("D:/HYYANG_MS_THESIS/VD_data/vd_static_mainline.csv")
        self.vd_id = [vd_id.iloc[i,0].split('-')[3] for i in range(vd_id.shape[0])]
        self.width = 1344
        self.height = 1008

    def add(self, obj):
        temp = copy.deepcopy(obj)
        temp.flow.loc[:,'date'] = [temp.date for _ in range(temp.flow.shape[0])]
        temp.flow.loc[:,'time'] = [i for i in range(temp.flow.shape[0])]
        temp.flow.set_index(keys=['date','time'],inplace=True)
        temp.speed.loc[:,'date'] = [temp.date for _ in range(temp.speed.shape[0])]
        temp.speed.loc[:,'time'] = [i for i in range(temp.speed.shape[0])]
        temp.speed.set_index(keys=['date','time'],inplace=True)
        temp.occ.loc[:,'date'] = [temp.date for _ in range(temp.occ.shape[0])]
        temp.occ.loc[:,'time'] = [i for i in range(temp.occ.shape[0])]
        temp.occ.set_index(keys=['date','time'],inplace=True)
        
        self.db['flow'] = pd.concat([self.db['flow'],temp.flow])
        self.db['speed'] = pd.concat([self.db['speed'],temp.speed])
        self.db['occ'] = pd.concat([self.db['occ'],temp.occ])
        self.count += 1

    def settime(self, start, end):
        if start != None:
            stime = int(start/100)*12 + int((start%100)/5)
        else: stime = 0
        if end != None:
            etime = int(end/100)*12 + int((end%100)/5) - 1
        else: etime = 287
        return stime,etime

    def plot_ind_fundamental_d(self,xdata,ydata,name,mo='markers',legend_group='VD',show_legend=False,color='#007bff',ms=4):
        return go.Scatter(
                x=xdata,
                y=ydata,
                mode=mo,
                marker= dict(
                    size=ms,
                    color=color
                    #,symbol = 'pentagon'
                ),
                name='VD '+name+' K',
                legendgroup=legend_group,
                showlegend=show_legend
            )

    def data_preparation(self, location, date, stime, etime):
        plot_flow = self.db['flow'][(self.db['flow'] != 0) & (self.db['speed'] != 0)]
        plot_speed = self.db['speed'][(self.db['flow'] != 0) & (self.db['speed'] != 0)]
        plot_occ = self.db['occ'][(self.db['flow'] != 0) & (self.db['speed'] != 0)]

        plot_flow = plot_flow.loc[date,:]
        plot_speed = plot_speed.loc[date,:]
        plot_occ = plot_occ.loc[date,:]
        
        data = pd.concat([plot_speed.query('%i<=time<=%i'%(stime,etime)).loc[:,location].reset_index(drop=True)\
                        ,plot_flow.query('%i<=time<=%i'%(stime,etime)).loc[:,location].reset_index(drop=True)\
                        ,plot_occ.query('%i<=time<=%i'%(stime,etime)).loc[:,location].reset_index(drop=True)],axis=1)
        data.columns = ['speed', 'flow', 'occ']

        return data.loc[:,'flow'], data.loc[:,'speed'], data.loc[:,'occ']

    def plot_fundamental_d(self, location, date, stime, etime):
        fig = make_subplots(
            rows=2, cols=2, 
            specs=[[{}, {}],
                    [{}, None]],
            horizontal_spacing=0.1,
            vertical_spacing=0.1,
            subplot_titles=('Speed-Occupany Diagram',
                            'Speed-Flow Diagram',
                            'Flow-Occuoancy Diagram'),
        )
        if len(location) > 1:
            for l in location:
                #data preparation
                X,Y,Z = self.data_preparation(l, date, stime, etime)
                c = self.palette[location.index(l)%11]
                #Plotly graph object
                sod = self.plot_ind_fundamental_d(Y,Z,l,show_legend=True,color=c)
                sfd = self.plot_ind_fundamental_d(X,Y,l,color=c)
                fod = self.plot_ind_fundamental_d(Z,X,l,color=c)

                fig.add_trace(sod,row=1,col=1)
                fig.add_trace(sfd,row=1,col=2)
                fig.add_trace(fod,row=2,col=1)
            
            fig.update_layout(
                autosize=False,
                width=self.width,
                height=self.height,
                # set fig, x and y axis tiltles & font
                title='Multi VD Comparison Fundemental Diagram',
                xaxis_title="Flow (veh/hr)",
                yaxis_title="Speed (km/hr)",
                font=dict(
                    #family="Courier New, monospace",
                    size=16,
                    #color="RebeccaPurple",
                    color="#411530"
                ),
                showlegend = True,
                legend_title_text='VD Location'
            )
        else:
            #data preparation
            X,Y,Z = self.data_preparation(location, date, stime, etime)

            #Plotly graph object
            sod = self.plot_ind_fundamental_d(Y,Z,location[0])
            sfd = self.plot_ind_fundamental_d(X,Y,location[0])
            fod = self.plot_ind_fundamental_d(Z,X,location[0])

            fig.add_trace(sod,row=1,col=1)
            fig.add_trace(sfd,row=1,col=2)
            fig.add_trace(fod,row=2,col=1)
        
            fig.update_layout(
                autosize=False,
                width=self.width,
                height=self.height,
                # set fig, x and y axis tiltles & font
                title='VD '+location[0]+' K Fundemental Diagram',
                xaxis_title="Flow (veh/hr)",
                yaxis_title="Speed (km/hr)",
                font=dict(
                    #family="Courier New, monospace",
                    size=16,
                    #color="RebeccaPurple",
                    color="#411530"
                ),
                showlegend = False
            )

        # Update yaxis properties
        fig.update_yaxes(
            title_text="Speed (km/hr)", 
            range=[0, 100],
            minor=dict(ticklen=6, tickcolor="black", showgrid=True), 
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=1)
        fig.update_yaxes(
            title_text="Speed (km/hr)",
            range=[0, 100],
            minor=dict(ticklen=6, tickcolor="black", showgrid=True),
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=2)
        fig.update_yaxes(
            title_text="Flow (veh/hr)",
            range=[0, 3500],
            minor=dict(ticklen=6, tickcolor="black", showgrid=True),
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)

        # Update xaxis properties
        fig.update_xaxes(
            title_text="Occupany (%)",
            range=[0, 100],
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=1)
        fig.update_xaxes(
            title_text="Flow (veh/hr)",
            range=[0, 3500],minor=dict(ticklen=6, tickcolor="black", showgrid=True),
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=2)
        fig.update_xaxes(
            title_text="Occupany (%)",
            range=[0, 100],
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)

        return fig

    def plot_speedflow_d(self, location, date, stime, etime):
        col_num = 4
        if len(location)%col_num == 0:row_num = (len(location)//col_num)
        else:row_num = ((len(location)//col_num)+1)
        fig = make_subplots(
            rows=row_num, cols=col_num,
            specs=[[
                {"rowspan": 1,"colspan": 1},
                {"rowspan": 1,"colspan": 1},
                {"rowspan": 1,"colspan": 1},
                {"rowspan": 1,"colspan": 1}] for x in range(row_num)],
            subplot_titles=['VD '+l+' K' for l in location],
            shared_yaxes=True
        )
        rcount, ccount = 1, 1
        for l in location:
            X,Y,Z = self.data_preparation(l, date, stime, etime)
            fig.add_trace(self.plot_ind_fundamental_d(X,Y,l),row=rcount,col=ccount)
            if ccount%4 == 0: 
                ccount=1
                rcount+=1
            else: ccount += 1
        
        fig.update_layout(
            autosize=False,
            height=400*row_num,
            width=(self.width/4)*col_num,
            # set fig, x and y axis tiltles & font
            title=' Speed-Flow Diagram',
            font=dict(
                #family="Courier New, monospace",
                size=16,
                #color="RebeccaPurple",
                color="#411530"
            ),
            showlegend = False
        )
        fig.for_each_xaxis(lambda x: x.update(range=[0,3500]))
        fig.for_each_yaxis(lambda x: x.update(range=[0,100]))
        return fig

    def plot_traffic_pattern(self):
        row_num, col_num = 3,1
        fig = make_subplots(
            rows=row_num, cols=col_num,
            specs=[[{}],[{"rowspan": 2}],[None]],
            subplot_titles=['Hour of Day Flow Pattern','Speed Heat Map over Time & Spatial']
        )
        fig.update_layout(
            autosize=False,
            width=self.width,
            height=1080,
            # set fig, x and y axis tiltles & font
            title='Day by Day Trffic Pattern',
            font=dict(
                #family="Courier New, monospace",
                size=16,
                #color="RebeccaPurple",
                color="#411530"
            )
        )
        return fig

    def plot_time_series_flow(self, location, date, fig):
        if len(location) > 1:
            for l in location:
                #data preparation
                X,Y,Z = self.data_preparation(l, date, 0, 287)
                c = self.palette[location.index(l)%11]
                if date[0]==date[-1]:
                    temp = [str(datetime.now()), str(datetime.now() + timedelta(days=1))]
                    temp = [i.split(' ')[0] for i in temp]
                    temp = pd.date_range(start=temp[0], end=temp[1], freq='5min')
                    x=[]
                    for dt in temp:
                        x.append(dt.replace(year=int(date[0][:4]),month=int(date[0][4:6]),day=int(date[0][6:])))
                    x = np.array(x)
                else:
                    x = np.array(pd.date_range(start=date[0], end=date[-1], freq='5min'))           
                #Plotly graph object
                trace = self.plot_ind_fundamental_d(x,X,l,mo='lines+markers',show_legend=True,color=c)
                fig.add_trace(trace,row=1,col=1)
        else:
            #data preparation
            X,Y,Z = self.data_preparation(location, date, 0, 287)
            if date[0]==date[-1]:
                temp = [str(datetime.now()), str(datetime.now() + timedelta(days=1))]
                temp = [i.split(' ')[0] for i in temp]
                temp = pd.date_range(start=temp[0], end=temp[1], freq='5min')
                x=[]
                for dt in temp:
                    x.append(dt.replace(year=int(date[0][:4]),month=int(date[0][4:6]),day=int(date[0][6:])))
                x = np.array(x)
            else:
                x = np.array(pd.date_range(start=date[0], end=date[-1], freq='5min'))
            #Plotly graph object
            trace = self.plot_ind_fundamental_d(x,X,location[0],mo='lines+markers')
            fig.add_trace(trace,row=1,col=1)
        # Update yaxis properties
        fig.update_yaxes(
            title_text="Flow (veh/hr)", 
            range=[0, 3500],
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=1, col=1)
        return 

    def plot_speed_heatmap(self, date, fig):
        #data preparation
        data = self.db['speed'].drop(columns=['29.600'])
        temp = self.db['flow'].drop(columns=['29.600'])
        
        data = data.fillna(90)
        data[(data == 0) & (temp == 0)] = 90
        Z = pd.DataFrame()
        for d in date:
            temp = data.loc[d,:].reset_index(drop=True)
            temp = temp.T
            Z = pd.concat([Z,temp],axis=1)
        str_vd_id = [i+' K' for i in self.vd_id]
        str_vd_id.remove('29.600 K')
        #Plotly graph object
        Z = Z[::-1]#reverse row order
        str_vd_id.reverse()
        X = np.array(pd.date_range(start=date[0], end=date[-1], freq='5min'))
        trace = go.Heatmap(z=Z,x=X,y=str_vd_id,
                   hoverongaps = False,
                   colorscale='portland',
                   #reverse color bar
                   reversescale=True,
                   colorbar=dict(
                       title="Speed",
                       thicknessmode="pixels", thickness=30,
                       lenmode="pixels", len=self.height*0.67,
                       #set color position base on top side
                       yanchor="top",y=0.7,
                       ticks="outside", ticksuffix=" (km/hr)",
                       dtick=20))
        fig.add_trace(trace,row=2,col=1)
        fig.update_yaxes(
            title_text="VD Location (veh/hr)", 
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)
        fig.update_xaxes(
            title_text="Time",
            title_font=dict(
                size=14,
                color="#411530"
            ),
            row=2, col=1)
        return 