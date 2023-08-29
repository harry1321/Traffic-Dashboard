import pandas as pd
import numpy as np
import os

def get_index_1(idx):
    if idx.empty:
        return False
    else:
        temp = {}
        for c in idx.index:
            if len(idx.loc[c])!=0:
                temp[c] = [i for i in idx.loc[c]]
        return temp

def get_index_2(data, mask):
    if mask.empty:
        return False
    else:
        temp = {}
        idx, idy = np.where(pd.isnull(mask))
        result = np.column_stack((data.index[idx], data.columns[idy]))
        #print(np.unique(result[:,1]))
        for c in np.unique(result[:,1]):
            temp[c] = [result[i,0] for i in range(result.shape[0]) if result[i,1] == c]
        return temp

class vddata:
    def __init__(self, date, interval, path='data'):
        self.date = date
        self.interval = interval
        self.path = path
        self.spath = "data"
        self.section = 'all'
        self.flow = pd.read_csv(self.path+"/%s/%s_flow_vd2.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
        self.speed = pd.read_csv(self.path+"/%s/%s_speed_vd2.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
        self.occ = pd.read_csv(self.path+"/%s/%s_occ_vd2.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
        self.psg = pd.read_csv(self.path+"/%s/%s_psg_vd2.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
        self.lag = pd.read_csv(self.path+"/%s/%s_lag_vd2.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
        self.tr = pd.read_csv(self.path+"/%s/%s_tr_vd2.csv"%(self.date,self.date), index_col=0, encoding = 'big5')
    
    def continuous_data(self,data):#檢查連續相同數據筆數是否超過6筆
        free_flow = get_index_2(data,data.mask((self.flow == 0) & (self.speed == 0) & (self.occ == 0), np.nan))
        
        temp_dict = {} #輸出之字典
        for c in data.columns:
            temp = [] #存放連續出現同數值之index
            count = 1
            for r in data.index:
                if r != data.index.to_list()[-1]: #非最後一筆資料
                    if data.loc[r,c] == data.loc[r+1,c]: #前筆資料等於下一筆資料計數加一
                        count += 1
                    else: #若上下筆資料不同則統計連續之序號
                        if count >= 6: #超過6筆相同資料才計入
                            temp = temp + [idx for idx in range(r-count+1,r+1)]
                        count = 1
            if c in free_flow:
                temp = list(set(temp) - set(free_flow[c]))#移除自由車流下狀況之異常值
            temp_dict[c] = temp
        return temp_dict
    
    def flow_concervation(self, data):#檢驗主線偵測器密度變化
        temp_dict = {} #輸出之字典
        mainline_id = pd.read_csv(self.path+"/vd_static_mainline.csv")
        mainline_id = [mainline_id.iloc[i,0] for i in range(mainline_id.shape[0])]
        data = data[mainline_id]
        vd = data.columns.tolist()
        for i in range(len(vd)):
            vd[i] = vd[i].split('-')[3]
        for r in data.index:
            for c in range(len(data.columns.to_list())):
                if c != 0:
                    v = data.columns.to_list()[c]
                    dis = float(vd[c]) - float(vd[c-1])
                    q_var = (data.loc[r,][c] - data.loc[r,][c-1])/60
                    if q_var < dis*(-8.82)*2*1.1 or q_var > dis*(8.82)*2*1.1:#密度變化
                        if v in temp_dict:
                            temp = temp_dict[v]
                        else:
                            temp_dict[v] = []
                            temp = temp_dict[v]
                        temp.append(r)
                        temp_dict[v] = temp
        return temp_dict

    def read_error_code(self, dictionary, dtype):
        #dict{error code:{vd: time index}} error dictionary 輸入格式
        #dict{vd:time index} 輸出格式
        temp_dict = {}
        error_count = 0
        error_rate = 0.0
        if dtype == 'speed':
            div = 1
        elif dtype == 'flow':
            div = 2
        elif dtype == 'occ':
            div =3
        else:
            return print('error in read_error_code dtype!!')
        for k, v in dictionary.items():
            if int(int(k)/100) == div:
                #print("processing error number: %s"%k)
                #print('\n========================')
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        if kk in temp_dict:
                            temp = temp_dict[kk]
                        else:
                            temp_dict[kk] = []
                            temp = temp_dict[kk]
                        temp = temp + vv
                        temp = list(set(temp))
                        temp.sort()
                        temp_dict[kk] = temp
                        error_count = len(temp)
                        error_rate = 100*error_count/(1439*65)
                        #print("processing vd number: %s"%kk)
        #print('Unique vd count: %i\t error rate:%.4f %%'%(len(temp_dict),error_rate))
        return temp_dict, error_rate

    #處理負值數據
    def imputation_data(self, data, dictionary, dtype):#移動平均方修正錯誤資料
        new_dictionary, rate = self.read_error_code(dictionary,dtype)
        for k, v in new_dictionary.items():
            #print('vd name: %s'%k)
            for i in v:
                if i >= 6:
                    #print('origin value: %i'%data.loc[:,k][i])
                    #print('MA: ',np.average(data.loc[:,k][i-6:i]))
                    data.loc[i,k] = np.average(data.loc[i-6:i,k])
        return data
    
    def detect_error_data(self):
        error_code={}
        #先對佔有率進行轉換，將速度流量不為0但佔有率為0之資料依據平均車長重新估計
        error_code['303'] = get_index_2(self.occ,self.occ.mask((self.occ == 0) & (self.flow != 0) & (self.speed != 0), np.nan))
        for k, v in error_code['303'].items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    for i in vv:
                        self.occ.loc[i,kk] = 0.6*self.flow.loc[i,kk]/self.speed.loc[i,kk]
        error_code['206'] = self.flow_concervation(self.flow)
        
        #uper limit speed
        idx = self.speed.apply(lambda x:np.array((x>200)).nonzero()[0][:].tolist())
        error_code['101'] = get_index_1(idx)
        #lower limit speed
        idx = self.speed.apply(lambda x:np.array((x<0)).nonzero()[0][:].tolist())
        error_code['102'] = get_index_1(idx)
        #speed=0,flow!=0,occ!=0
        error_code['103'] = get_index_2(self.speed,self.speed.mask((self.speed == 0) & (self.flow != 0) & (self.occ != 0), np.nan))
        #speed!=0,flow=0,occ=0
        error_code['104'] = get_index_2(self.speed,self.speed.mask((self.speed != 0) & (self.flow == 0) & (self.occ == 0), np.nan))
        error_code['105'] = self.continuous_data(self.speed)
        error_code['106'] = error_code['206']
        
        #uper limit flow
        idx = self.flow.apply(lambda x:np.array((x>6000)).nonzero()[0][:].tolist())
        error_code['201'] = get_index_1(idx)
        #lower limit flow
        idx = self.flow.apply(lambda x:np.array((x<0)).nonzero()[0][:].tolist())
        error_code['202'] = get_index_1(idx)
        #speed!=0,flow=0,occ!=0
        error_code['203'] = get_index_2(self.flow,self.flow.mask((self.flow == 0) & (self.speed != 0) & (self.occ != 0), np.nan))
        #speed=0,flow!=0,occ=0
        error_code['204'] = get_index_2(self.flow,self.flow.mask((self.flow != 0) & (self.speed == 0) & (self.occ == 0), np.nan))
        #檢查連續相同數據筆數是否超過6筆
        error_code['205'] = self.continuous_data(self.flow)
        

        #uper limit occ
        idx = self.occ.apply(lambda x:np.array((x>100)).nonzero()[0][:].tolist())
        error_code['301'] = get_index_1(idx)
        #lowe limit occ
        idx = self.occ.apply(lambda x:np.array((x<0)).nonzero()[0][:].tolist())
        error_code['302'] = get_index_1(idx)
        #speed!=0,flow!=0,occ=0
        error_code['303'] = get_index_2(self.occ,self.occ.mask((self.occ == 0) & (self.flow != 0) & (self.speed != 0), np.nan))
        #speed=0,flow=0,occ!=0
        error_code['304'] = get_index_2(self.occ,self.occ.mask((self.occ != 0) & (self.flow == 0) & (self.speed == 0), np.nan))
        error_code['305'] = self.continuous_data(self.occ)
        #
        error_code['306'] = error_code['206']
        
        '''for k, v in error_code.items():
            err_count = 0
            err_vd = 0
            if isinstance(v, dict):#檢查是否為字典
                for kk, vv in v.items():
                    err_vd += 1
                    err_count += len(vv)
            print('Error key : %s\terror vd count: %i\terror data count: %i'%(k,err_vd,err_count))'''
        return error_code

    def preprocess_data(self):
        error_code = self.detect_error_data()
        self.flow = self.imputation_data(self.flow, error_code, 'flow')
        self.psg = self.imputation_data(self.psg, error_code, 'flow')
        self.lag = self.imputation_data(self.lag, error_code, 'flow')
        self.tr = self.imputation_data(self.tr, error_code, 'flow')
        self.speed = self.imputation_data(self.speed, error_code, 'speed')
        self.occ = self.imputation_data(self.occ,error_code, 'occ')
        temp_dict, error_rate1 = self.read_error_code(error_code, 'flow')
        temp_dict, error_rate2 = self.read_error_code(error_code, 'speed')
        temp_dict, error_rate3 = self.read_error_code(error_code, 'occ')
        avg_rate = np.mean([error_rate1,error_rate2,error_rate3])
        return {'flow':error_rate1,'speed':error_rate2,'occ':error_rate3}

    def transform(self):
        if self.interval == '1':
            new_vddata = vddata(self.date,'5')
            new_vddata.flow = (self.flow/60).groupby(self.flow.index // 5).sum().round(0)*12
            new_vddata.speed = (self.speed*self.flow/60).groupby(self.speed.index // 5).sum()
            new_vddata.speed = (12*new_vddata.speed/new_vddata.flow).round(2)
            new_vddata.occ = (self.occ).groupby(self.occ.index // 5).mean().round(2)
            new_vddata.psg = (self.psg/60).groupby(self.psg.index // 5).sum().round(0)*12
            new_vddata.lag = (self.lag/60).groupby(self.lag.index // 5).sum().round(0)*12
            new_vddata.tr = (self.tr/60).groupby(self.tr.index // 5).sum().round(0)*12
            return new_vddata
        else:
            return print('Error: Can not transform 5 minutes data to 1 minute data.')
    
    def save(self):
        subdir = self.spath+'/%s'%(self.date)
        if os.path.isdir(subdir):
            print("Exists")
        else:
            os.mkdir(subdir)
        self.flow.to_csv(self.spath+'/%s/%s_flow_vd_5min.csv'%(self.date,self.date), sep=',', encoding = 'big5')
        self.speed.to_csv(self.spath+'/%s/%s_speed_vd_5min.csv'%(self.date,self.date), sep=',', encoding = 'big5')
        self.occ.to_csv(self.spath+'/%s/%s_occ_vd_5min.csv'%(self.date,self.date), sep=',', encoding = 'big5')

    def export(self, sec):
        if sec == 'mainline':
            new_vddata = vddata(self.date,self.interval)
            mainline_id = pd.read_csv(self.path+"/vd_static_mainline.csv")
            mainline_id = [mainline_id.iloc[i,0] for i in range(mainline_id.shape[0])]
            new_vddata.flow = self.flow[mainline_id]
            new_vddata.psg = self.psg[mainline_id]
            new_vddata.lag = self.lag[mainline_id]
            new_vddata.tr = self.tr[mainline_id]
            new_vddata.speed = self.speed[mainline_id]
            new_vddata.occ = self.occ[mainline_id]
            for i in range(len(mainline_id)):
                mainline_id[i] = mainline_id[i].split('-')[3]
            new_vddata.flow.columns = mainline_id
            new_vddata.psg.columns = mainline_id
            new_vddata.lag.columns = mainline_id
            new_vddata.tr.columns = mainline_id
            new_vddata.speed.columns = mainline_id
            new_vddata.occ.columns = mainline_id
            return new_vddata

        elif sec == 'ramp':
            new_vddata = vddata(self.date,self.interval)
            ramp_id = pd.read_csv(self.path+"/vd_static_ramp.csv", encoding = 'big5')
            ramp_name = [ramp_id.iloc[i,1] for i in range(ramp_id.shape[0])]
            ramp_id = [ramp_id.iloc[i,0] for i in range(ramp_id.shape[0])]
            new_vddata.flow = self.flow[ramp_id]
            new_vddata.flow.columns = ramp_name
            new_vddata.psg = self.psg[ramp_id]
            new_vddata.psg.columns = ramp_name
            new_vddata.lag = self.lag[ramp_id]
            new_vddata.lag.columns = ramp_name
            new_vddata.tr = self.tr[ramp_id]
            new_vddata.tr.columns = ramp_name
            new_vddata.speed = self.speed[ramp_id]
            new_vddata.speed.columns = ramp_name
            new_vddata.occ = self.occ[ramp_id]
            new_vddata.occ.columns = ramp_name
            return new_vddata

        elif sec == 'validation': # export 15K - 42K VD data
            new_vddata = vddata(self.date,self.interval)
            vd_id = pd.read_csv(self.path+"/vd_static_network_validate.csv")
            vd_id = [vd_id.iloc[i,0] for i in range(vd_id.shape[0])]
            new_vddata.flow = self.flow[vd_id]
            new_vddata.psg = self.psg[vd_id]
            new_vddata.lag = self.lag[vd_id]
            new_vddata.tr = self.tr[vd_id]
            new_vddata.speed = self.speed[vd_id]
            new_vddata.occ = self.occ[vd_id]
            for i in range(len(vd_id)):
                vd_id[i] = vd_id[i].split('-')[3]
            new_vddata.flow.columns = vd_id
            new_vddata.psg.columns = vd_id
            new_vddata.lag.columns = vd_id
            new_vddata.tr.columns = vd_id
            new_vddata.speed.columns = vd_id
            new_vddata.occ.columns = vd_id
            return new_vddata

        elif sec == 'tunnel': # export Xueshan tunnel VD data
            new_vddata = vddata(self.date,self.interval)
            vd_id = pd.read_csv(self.path+"/vd_static_tunnel.csv")
            vd_id = [vd_id.iloc[i,0] for i in range(vd_id.shape[0])]
            new_vddata.flow = self.flow[vd_id]
            new_vddata.psg = self.psg[vd_id]
            new_vddata.lag = self.lag[vd_id]
            new_vddata.tr = self.tr[vd_id]
            new_vddata.speed = self.speed[vd_id]
            new_vddata.occ = self.occ[vd_id]
            for i in range(len(vd_id)):
                vd_id[i] = vd_id[i].split('-')[3]
            new_vddata.flow.columns = vd_id
            new_vddata.psg.columns = vd_id
            new_vddata.lag.columns = vd_id
            new_vddata.tr.columns = vd_id
            new_vddata.speed.columns = vd_id
            new_vddata.occ.columns = vd_id
            return new_vddata
