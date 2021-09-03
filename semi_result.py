# -*- coding: utf-8 -*-
# --------------------------------
# 0. setting
# --------------------------------

import pandas as pd
from haversine import haversine
import folium
from tqdm import tqdm
import matplotlib.pyplot as plt
%matplotlib inline

from google.colab import drive
drive.mount('/content/drive')

# --------------------------------
# 1. Preprocessing Data
# --------------------------------

# officetel
opt = pd.read_excel('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/목록화_부동산/오피스텔목록_샘플_분당직장인중점/분당_오피스텔_시트.xlsx')
opt = opt.drop(columns=['Unnamed: 0'])

# laundry
laundry = pd.read_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/2030라이프스타일/세탁/분당_세탁소.csv')
laundry = laundry.drop(columns=['Unnamed: 0'])

# fitness center
fitness = pd.read_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/2030라이프스타일/운동시설/헬스장/분당_헬스장.csv')
fitness.rename(columns={'WGS84위도':'위도', 'WGS84경도':'경도'}, inplace=True)
fitness = fitness.drop(columns=['Unnamed: 0'])

# MacDonald's
macdonalds = pd.read_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/2030라이프스타일/패스트푸드/패스트푸드_맥도날드/분당_맥도날드.csv')
macdonalds = macdonalds.drop(columns=['Unnamed: 0'])

# convenience
convenience = pd.read_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/2030라이프스타일/편의점/분당_편의점.csv')
convenience = convenience.drop(columns=['Unnamed: 0'])
convenience.drop(index=convenience[convenience['위도'] == '-'].index, inplace=True)
convenience = convenience.reset_index(drop=True)

# electric vehicle charging station
elec = pd.read_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/2030라이프스타일/전기차충전소/분당_전기차충전소.csv')
elec.rename(columns={'WGS84위도':'위도', 'WGS84경도':'경도'}, inplace=True)
elec = elec.drop(columns=['Unnamed: 0'])

# clinic for Orthopedics
clinic = pd.read_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/2030라이프스타일/병원/정형외과/분당_정형외과.csv')
clinic.rename(columns={'WGS84위도':'위도', 'WGS84경도':'경도'}, inplace=True)
clinic = clinic.drop(columns=['Unnamed: 0'])


# --------------------------------
# 2. Measuring Distance
# --------------------------------

# function of measuring minimum distance
def DISTANCE(x_1, y_1, x_2, y_2):
  min_list = []

  for i in range(len(x_1)):
    start = (float(x_1[i]), float(y_1[i]))
    haver = []
    for i2 in range(len(x_2)):
      goal = (float(x_2[i2]), float(y_2[i2]))
      haver.append(haversine(start, goal, unit='m'))

    min_list.append(min(haver))
  return min_list

# measure minimum distance
d1 = DISTANCE(opt['위도'], opt['경도'], laundry['위도'], laundry['경도'])
d2 = DISTANCE(opt['위도'], opt['경도'], fitness['위도'], fitness['경도'])
d3 = DISTANCE(opt['위도'], opt['경도'], macdonalds['위도'], macdonalds['경도'])
d4 = DISTANCE(opt['위도'], opt['경도'], convenience['위도'], convenience['경도'])
d5 = DISTANCE(opt['위도'], opt['경도'], elec['위도'], elec['경도'])
d6 = DISTANCE(opt['위도'], opt['경도'], clinic['위도'], clinic['경도'])

md = {'오피스텔명':opt.iloc[:,0], '위도':opt.iloc[:,2], '경도':opt.iloc[:,3],'세탁소':d1, '헬스장':d2, '맥도날드':d3, '편의점':d4, '전기차충전소':d5, '정형외과':d6}
tmp_df = pd.DataFrame(md)


# --------------------------------
# 3. Scoring & Adding Weight
# --------------------------------

tier_1 = int(len(tmp_df) * 0.2)
tier_2 = int(len(tmp_df) * 0.4)
tier_3 = int(len(tmp_df) * 0.6)
tier_4 = int(len(tmp_df) * 0.8)

# laundry
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='세탁소')[:tier_1]['오피스텔명']), 'LAUNDRY_Score'] = 5
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='세탁소')[tier_1:tier_2]['오피스텔명']), 'LAUNDRY_Score'] = 4
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='세탁소')[tier_2:tier_3]['오피스텔명']), 'LAUNDRY_Score'] = 3
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='세탁소')[tier_3:tier_4]['오피스텔명']), 'LAUNDRY_Score'] = 2
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='세탁소')[tier_4:]['오피스텔명']), 'LAUNDRY_Score'] = 1

# electric vehicle charging station
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='전기차충전소')[:tier_1]['오피스텔명']), 'ELEC_Score'] = 5
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='전기차충전소')[tier_1:tier_2]['오피스텔명']), 'ELEC_Score'] = 4
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='전기차충전소')[tier_2:tier_3]['오피스텔명']), 'ELEC_Score'] = 3
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='전기차충전소')[tier_3:tier_4]['오피스텔명']), 'ELEC_Score'] = 2
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='전기차충전소')[tier_4:]['오피스텔명']), 'ELEC_Score'] = 1

# convenience
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='편의점')[:tier_1]['오피스텔명']), 'CONV_Score'] = 5
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='편의점')[tier_1:tier_2]['오피스텔명']), 'CONV_Score'] = 4
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='편의점')[tier_2:tier_3]['오피스텔명']), 'CONV_Score'] = 3
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='편의점')[tier_3:tier_4]['오피스텔명']), 'CONV_Score'] = 2
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='편의점')[tier_4:]['오피스텔명']), 'CONV_Score'] = 1

# MacDonald's
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='맥도날드')[:tier_1]['오피스텔명']), 'MAC_Score'] = 5
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='맥도날드')[tier_1:tier_2]['오피스텔명']), 'MAC_Score'] = 4
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='맥도날드')[tier_2:tier_3]['오피스텔명']), 'MAC_Score'] = 3
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='맥도날드')[tier_3:tier_4]['오피스텔명']), 'MAC_Score'] = 2
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='맥도날드')[tier_4:]['오피스텔명']), 'MAC_Score'] = 1

# fitness center
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='헬스장')[:tier_1]['오피스텔명']), 'FITNESS_Score'] = 5
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='헬스장')[tier_1:tier_2]['오피스텔명']), 'FITNESS_Score'] = 4
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='헬스장')[tier_2:tier_3]['오피스텔명']), 'FITNESS_Score'] = 3
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='헬스장')[tier_3:tier_4]['오피스텔명']), 'FITNESS_Score'] = 2
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='헬스장')[tier_4:]['오피스텔명']), 'FITNESS_Score'] = 1

# clinic for Orthopedics
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='정형외과')[:tier_1]['오피스텔명']), 'CLINIC_Score'] = 5
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='정형외과')[tier_1:tier_2]['오피스텔명']), 'CLINIC_Score'] = 4
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='정형외과')[tier_2:tier_3]['오피스텔명']), 'CLINIC_Score'] = 3
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='정형외과')[tier_3:tier_4]['오피스텔명']), 'CLINIC_Score'] = 2
tmp_df.loc[tmp_df['오피스텔명'].isin(tmp_df.sort_values(by='정형외과')[tier_4:]['오피스텔명']), 'CLINIC_Score'] = 1

# survey
survey = pd.read_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/직장인 A 설문지(응답).csv', encoding='utf-8')
survey = survey.iloc[:, 1:]

# weight of importance
w = survey / 5

# add weight
tmp_df[['LAUNDRY_Score_w', 
        'ELEC_Score_w',
        'CONV_Score_w',
        'MAC_Score_w',
        'FITNESS_Score_w',
        'CLINIC_Score_w']] = tmp_df[['LAUNDRY_Score',
                                     'ELEC_Score',
                                     'CONV_Score',
                                     'MAC_Score',
                                     'FITNESS_Score',
                                     'CLINIC_Score']] * w.values

# sum & avg
tmp_df['Total_Score_w'] = tmp_df['ELEC_Score_w'] + tmp_df['CONV_Score_w'] + tmp_df['MAC_Score_w'] + tmp_df['FITNESS_Score_w'] + tmp_df['CLINIC_Score_w']
tmp_df['AVG_Score_w'] = round((tmp_df['Total_Score_w'] / 6), 2)

# result
score = tmp_df[['오피스텔명', '위도', '경도', 'LAUNDRY_Score_w', 'ELEC_Score_w', 'CONV_Score_w', 'MAC_Score_w', 'FITNESS_Score_w', 'CLINIC_Score_w', 'Total_Score_w', 'AVG_Score_w']]
result = score.sort_values(by='AVG_Score_w', ascending=False).reset_index(drop=True).head(5)


# --------------------------------
# 4. Visualizing
# --------------------------------

# funtion of marker
def make_marker(map, x, y,z):
  for i in range(len(x)):
    folium.Marker([float(x[i]), float(y[i])], popup=z[i]).add_to(map)

# visualize the result on a map
map = folium.Map(location=[result['위도'][0], result['경도'][0]], zoom_start=12)
make_marker(map, result['위도'], result['경도'],result['오피스텔명'])
# print(map


# --------------------------------
# 5. Appendix
# --------------------------------

lat = [laundry['위도'], fitness['위도'], macdonalds['위도'], convenience['위도'], elec['위도'], clinic['위도']]
lon = [laundry['경도'], fitness['경도'], macdonalds['경도'], convenience['경도'], elec['경도'], clinic['경도']]

# function of all distance
def ALL_DISTANCE(x_1, y_1, x_2, y_2):
  all_list = []

  for i in range(len(x_1)):
    start = (float(x_1[i]), float(y_1[i]))
    haver = []
    for i2 in range(len(x_2)):
      goal = (float(x_2[i2]), float(y_2[i2]))
      haver.append(haversine(start, goal, unit='m'))

    all_list.append(haver)
  return all_list

# count infra in distance conditions
def COUNT_INFRA(lat, lon):
  for i in tqdm(range(len(opt))):
    li_500 = []
    li_1000 = []
    li_2000 = []
    li_3000 = []
    li_4000 = []


    for i2 in range(len(lat)):
      sd = ALL_DISTANCE(opt['위도'], opt['경도'], lat[i2], lon[i2])    
      sd_df = pd.DataFrame(sd[i], columns=['거리'])

      d_500 = sd_df[sd_df['거리'] < 500].count().values[0]
      d_1000 = sd_df[(sd_df['거리'] >= 500) & (sd_df['거리'] < 1000)].count().values[0]
      d_2000 = sd_df[(sd_df['거리'] >= 1000) & (sd_df['거리'] < 2000)].count().values[0]
      d_3000 = sd_df[(sd_df['거리'] >= 2000) & (sd_df['거리'] < 3000)].count().values[0]
      d_4000 = sd_df[sd_df['거리'] >= 3000 & (sd_df['거리'] < 4000)].count().values[0]


      li_500.append(d_500)
      li_1000.append(d_1000)
      li_2000.append(d_2000)
      li_3000.append(d_3000)
      li_4000.append(d_4000)

    index = ['세탁소', '헬스장', '맥도날드', '편의점', '전기차충전소', '정형외과']
    df = pd.DataFrame(index=index)
    df['500m 미만'] = li_500
    df['500m ~ 1km'] = li_1000
    df['1km ~ 2km'] = li_2000
    df['2km ~ 3km'] = li_3000
    df['3km ~ 5km'] = li_4000

    df.to_csv('/content/drive/MyDrive/양재AI허브교육_코드9조대_프로젝트/최종코드(깃헙업로드)/오피스텔 시설 카운팅/' + opt['오피스텔명'][i] + '.csv')

  return df
