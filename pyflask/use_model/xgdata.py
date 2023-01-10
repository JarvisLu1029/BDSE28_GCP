import numpy as np
import pandas as pd 
from scipy import spatial
import openpyxl
from datetime import datetime,timedelta
import requests , json
import pickle
import pytz

stream = pd.read_csv('110.csv', low_memory=False)
stream['總計_流量(PCU)'] = stream['總計_流量(PCU)'].str.findall('\d').str.join('').astype(int)
stream['ID']=stream['年份'].astype(str)+stream['調查站_座標_經度'].astype(str)+stream['調查站_座標_緯度'].astype(str)
stream = stream.groupby('ID').mean()
KDTree_stream = spatial.KDTree(stream[['調查站_座標_經度','調查站_座標_緯度']])

def population(county_dist , coo):
    df_den = pd.read_excel('11109density.xlsx')
    if len(df_den[df_den['地區']== county_dist ]['人口密度']):
        density = float(df_den[df_den['地區']== county_dist ]['人口密度'])
    else:
        density = 0

    tz = pytz.timezone('Asia/Taipei')
    # 取得當前日期
    today = datetime.now(tz)
    
    # 計算隔天日期
    # tomorrow = today + datetime.timedelta(days=1)

    dic = {'year' : f'{today.year}', 
        'month' : f'{today.month}',
        'day' : f'{today.day}',
        'hour' : f'{today.hour}',
        'long' : f'{coo[1]}',
        'lat' : f'{coo[0]}',
        'pop' : f'{density}'}
    return dic

def dataFill(dic):
    
    year = dic['year']
    month = dic['month']
    day = dic['day']
    hour = dic['hour']
    long = dic['long']
    lat = dic['lat']
    pop = dic['pop']
    
    
    input_columns = ['發生年度','發生月份', '發生日期', '發生時間', '經度', '緯度',  'population_density']
    columns = ['dow', 'doy', '元旦', '春節', '二二八', '兒童清明', '端午', '中秋', '雙十', '發生年度','發生月份', '發生日期', '發生時間', '經度', '緯度', '氣溫(℃)_x', '測站氣壓(hPa)_x','相對溼度(%)_x', '降水量(mm)_x', '風向(360degree)_x', '風速(m/s)_x', 'population_density', '流量加權']

    input_data = pd.DataFrame(columns=input_columns, index=[1]); input_data.iloc[0,:] = [year, month, day, hour, long, lat,pop]; input_data.astype(str)
    df = pd.DataFrame(columns = columns, index=[i for i in range(24)])

    df.經度 = long
    df.緯度 = lat
    df.population_density = pop

    datetime = input_data.apply((lambda x: x.發生年度+'-'+ x.發生月份+'-'+x.發生日期+' '+x.發生時間+':00:00'), axis = 1)
    time = pd.datetime.strptime(datetime[1], '%Y-%m-%d %H:%M:%S')
    time_range = pd.date_range(start=time, periods=24, freq='H')
    time_strings = time_range.strftime('%Y-%m-%d %H:%M:%S')

    df['dow'] = time_range.dayofweek
    df['doy'] = time_range.dayofyear
    df['發生年度'] = time_range.year
    df['發生月份'] = time_range.month
    df['發生日期'] = time_range.day
    df['發生時間'] = time_range.hour

    def taiwan_festival(x: int) -> pd.Series:

        sr = pd.Series([0,0,0,0,0,0,0],index=['元旦','春節','二二八','兒童清明','端午','中秋','雙十'])

        def _2018( x, sr):
            if x == 20180101:
                sr['元旦'] = 1
            elif 20180215 <= x <= 20180220:
                sr['春節'] = 1
            elif x == 20180228:
                sr['二二八'] = 1
            elif 20180404 <= x <= 20180408:
                sr['兒童清明'] = 1
            elif 20180616 <= x <= 20180618:
                sr['端午'] = 1
            elif 20180922 <= x <= 20180924:
                sr['中秋'] = 1
            elif x == 20181010:
                sr['雙十'] = 1
            elif 20181229 <= x <= 20181231:
                sr['元旦'] = 1
            return sr

        def _2019( x, sr):
            if x == 20190101:
                sr['元旦'] = 1
            elif 20190202 <= x <= 20190210:
                sr['春節'] = 1
            elif 20190228 <= x <= 20190303:
                sr['二二八'] = 1
            elif 20190404 <= x <= 20190407:
                sr['兒童清明'] = 1
            elif 20190607 <= x <= 20190609:
                sr['端午'] = 1
            elif 20190913 <= x <= 20190915:
                sr['中秋'] = 1
            elif 20191010 <= x <= 20191013:
                sr['雙十'] = 1
            return sr


        def _2020( x, sr):
            if x == 20200101:
                sr['元旦'] = 1
            elif 20200123 <= x <= 20200129:
                sr['春節'] = 1
            elif 20200228 <= x <= 20200301:
                sr['二二八'] = 1
            elif 20200402 <= x <= 20200405:
                sr['兒童清明'] = 1
            elif 20200625 <= x <= 20200628:
                sr['端午'] = 1
            elif 20201001 <= x <= 20201004:
                sr['中秋'] = 1
            elif 20201009 <= x <= 20201011:
                sr['雙十'] = 1
            return sr

        def _2021( x, sr):
            if 20210101 <= x <= 20210103:
                sr['元旦'] = 1
            elif 20210210  <= x <= 20210216:
                sr['春節'] = 1
            elif 20210227 <= x <= 20210301:
                sr['二二八'] = 1
            elif 20210402 <= x <= 20210405:
                sr['兒童清明'] = 1
            elif 20210612 <= x <= 20210614:
                sr['端午'] = 1
            elif 20210918 <= x <= 20210921:
                sr['中秋'] = 1
            elif 20211009 <= x <= 20211011:
                sr['雙十'] = 1
            elif x == 20211231:
                sr['元旦'] = 1
            return sr

        def _2022( x, sr):
            if 20220101 <= x <= 20220102:
                sr['元旦'] = 1
            elif 20220129 <= x <= 20220206:
                sr['春節'] = 1
            elif 20220226 <= x <= 20220228:
                sr['二二八'] = 1
            elif 20220402 <= x <= 20220405:
                sr['兒童清明'] = 1
            elif 20220603 <= x <= 20220605:
                sr['端午'] = 1
            elif 20220909 <= x <= 20220911:
                sr['中秋'] = 1
            elif 20221008 <= x <= 20221010:
                sr['雙十'] = 1
            elif x == 20221231:
                sr['元旦'] = 1
            return sr

        def _2023( x, sr):
            if 20230101 <= x <= 20230102:
                sr['元旦'] = 1
            elif 20230120 <= x <= 20230129:
                sr['春節'] = 1
            elif 20230225 <= x <= 20230228:
                sr['二二八'] = 1
            elif 20230401 <= x <= 20230405:
                sr['兒童清明'] = 1
            elif 20230622 <= x <= 20230625:
                sr['端午'] = 1
            elif 20230929 <= x <= 20231001:
                sr['中秋'] = 1
            elif 20231007 <= x <= 20231010:
                sr['雙十'] = 1
            elif 20231230 <= x <= 20231231:
                sr['元旦'] = 1
            return sr

        year = x // 10000

        if year == 2018:
            sr = _2018(x, sr)
        elif year == 2019:
            sr = _2019(x, sr)
        elif year == 2020:
            sr = _2020(x, sr)
        elif year == 2021:
            sr = _2021(x, sr)
        elif year == 2022:
            sr = _2022(x, sr)
        elif year == 2023:
            sr = _2023(x, sr)

        return sr

    date_int = df.發生年度.astype(int)*10000 + df.發生月份.astype(int)*100 + df.發生日期.astype(int)
    df[['元旦', '春節', '二二八', '兒童清明', '端午', '中秋', '雙十']] = date_int.apply((taiwan_festival))

    def nearest(x: pd.DataFrame):
        distance = KDTree_stream.query((x.經度, x.緯度),k=3)[0]
        index = KDTree_stream.query((x.經度, x.緯度),k=3)[1]
        df = stream.iloc[index,:]
        df['與事故點距離'] = pd.Series(distance,index=df.index)
        df = df[['調查站_座標_經度','調查站_座標_緯度','與事故點距離','總計_流量(PCU)']]
        df = pd.concat([df.iloc[0,],df.iloc[1,],df.iloc[2,]])
        return df

    stream_data = df.apply(nearest, axis=1)
    stream_data.columns = ['調查站1_座標_經度','調查站1_座標_緯度','調查站1與事故點距離','調查站1總計_流量(PCU)','調查站2_座標_經度','調查站2_座標_緯度','調查站2與事故點距離','調查站2總計_流量(PCU)','調查站3_座標_經度','調查站3_座標_緯度','調查站3與事故點距離','調查站3總計_流量(PCU)']

    stream_data['流量加權'] = stream_data['調查站1總計_流量(PCU)']*(1/(stream_data.調查站1與事故點距離))/(1/(stream_data.調查站1與事故點距離)+1/(stream_data.調查站2與事故點距離)+1/(stream_data.調查站3與事故點距離)) +\
                stream_data['調查站2總計_流量(PCU)']*(1/(stream_data.調查站2與事故點距離))/(1/(stream_data.調查站1與事故點距離)+1/(stream_data.調查站2與事故點距離)+1/(stream_data.調查站3與事故點距離)) +\
                stream_data['調查站3總計_流量(PCU)']*(1/(stream_data.調查站3與事故點距離))/(1/(stream_data.調查站1與事故點距離)+1/(stream_data.調查站2與事故點距離)+1/(stream_data.調查站3與事故點距離))

    df.流量加權 = stream_data.流量加權
    
    return df


# https://www.visualcrossing.com
def weatherAPI(df1):
    # 密鑰
#     key = '4KD3GK5WQ8HX23YXVEVS3ZYPM'
    key = 'NZKHHNNZV9ZXDRGDM4NJTT9YR'
    tz = pytz.timezone('Asia/Taipei')
    # 緯度，經度
    a1 = f"{df1.iloc[0,14]},{df1.iloc[0,13]}"
    # 時間
    t1 = f"{df1.iloc[0,9]}-{df1.iloc[0,10]}-{df1.iloc[0,11]}"
    # day = datetime.datetime.strptime(t1, '%Y-%m-%d')
    day1 = datetime.now(tz) + timedelta(days=1)
    t2 = day1.strftime('%Y-%m-%d')
    # 單位
    unitGroup = 'metric'
    # 語言
    lang = 'zh'
    # 需求資料
    include = 'hours'
    # 元素
    elements = 'datetime,pressure,humidity,temp,winddir,windspeed,precip'

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{a1}/{t1}/{t2}?key={key}&unitGroup={unitGroup}&lang={lang}&include={include}&elements={elements}"


    response = requests.get(url)
#     print(response.status_code)
    if response.status_code == 200:
        data = json.loads(response.text)
        a = pd.DataFrame(data['days'][0]['hours'])
        b = pd.DataFrame(data['days'][1]['hours'])
        c = pd.concat([a,b],axis=0)
        c.reset_index(drop=True, inplace=True)
        d = c.iloc[df1.發生時間[0]:df1.發生時間[0]+24,:]
        d.reset_index(drop=True, inplace=True)
        df1['氣溫(℃)_x'] = d['temp']
        df1['測站氣壓(hPa)_x'] = d['pressure']
        df1['相對溼度(%)_x'] = d['humidity']
        df1['降水量(mm)_x'] = d['precip']
        df1['風向(360degree)_x'] = d['winddir']
        df1['風速(m/s)_x'] = d['windspeed']*1000/3600
        df1 = df1.round({'風速(m/s)_x':1})
        return df1
    
    
def pred_loc(forxg):
    with open('model_best_xgb(無做特徵縮減).pkl','rb') as f:
        clf_load = pickle.load(f)
        prob = pd.DataFrame(clf_load.predict_proba(forxg)[:,1])
        
        def rank(x):
            
            if 0<=x < 0.1941:
                x = 'rank1'
            elif 0.1941<=x<0.2141:
                x = 'rank2'
            elif 0.2141 <= x <0.2546:
                x = 'rank3'
            elif 0.2546<= x<0.3274:
                x = 'rank4'
            elif 0.3274<= x <0.4806:
                x = 'rank5'
            elif 0.4806<=x <0.6800:
                x = 'rank6'
            elif 0.6800<=x <0.7526:
                x = 'rank7'
            elif 0.7526 <=x <0.8030:
                x = 'rank8'
            elif 0.8030<=x < 0.8130:
                x = 'rank9'
            elif 0.8130 <=x < 1:
                x = 'rank10'

            return x
        level = prob.iloc[:,0].astype(float).apply(rank)
        hour = forxg.iloc[:,12]
        
        # weather = forxg.iloc[:,-8:-2]
        # df = pd.concat([hour, weather, level],axis=1)
        df = pd.concat([hour,level],axis=1)
        df = df.rename(columns={0: 'rank'})
        
        return df