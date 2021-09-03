#!/usr/bin/env python
# coding: utf-8
# --------------------------------
# 0. setting
# --------------------------------

import pandas as pd
from haversine import haversine
import folium
from tqdm import tqdm

# --------------------------------
# 1. Preprocessing Data
# --------------------------------

# officetels and infra data
opt = pd.read_csv('docs/datasets/bundag_officetels.csv')
laundry = pd.read_csv('docs/datasets/bundag_laundry.csv')
fitness = pd.read_csv('docs/datasets/bundag_fitness.csv')
macdonalds = pd.read_csv('docs/datasets/bundag_MacDonalds.csv')
convenience = pd.read_csv('docs/datasets/bundag_convenience.csv')
elec = pd.read_csv('docs/datasets/bundag_elec_charge.csv')
clinic = pd.read_csv('docs/datasets/bundag_clinic_Orth.csv')

# inplace '-'
fitness.drop(index=fitness[fitness['위도'] == '-'].index, inplace=True)
fitness = fitness.reset_index(drop=True)
convenience.drop(index=convenience[convenience['위도'] == '-'].index, inplace=True)
convenience = convenience.reset_index(drop=True)

# rename columns
opt.rename(columns={'오피스텔명':'Officetels_Name',
                    '위도':'LAT', '경도':'LNG'}, inplace=True)

infra = [laundry, fitness, macdonalds, convenience, elec, clinic]
for i in range(len(infra)):
    infra[i].rename(columns={'위도':'LAT', '경도':'LNG'}, inplace=True)


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
d1 = DISTANCE(opt['LAT'], opt['LNG'], laundry['LAT'], laundry['LNG'])
d2 = DISTANCE(opt['LAT'], opt['LNG'], fitness['LAT'], fitness['LNG'])
d3 = DISTANCE(opt['LAT'], opt['LNG'], macdonalds['LAT'], macdonalds['LNG'])
d4 = DISTANCE(opt['LAT'], opt['LNG'], convenience['LAT'], convenience['LNG'])
d5 = DISTANCE(opt['LAT'], opt['LNG'], elec['LAT'], elec['LNG'])
d6 = DISTANCE(opt['LAT'], opt['LNG'], clinic['LAT'], clinic['LNG'])

md = {'Officetels_Name':opt.iloc[:,0],
      'LAT':opt.iloc[:,2], 'LNG':opt.iloc[:,3],
      'LAUNDRY':d1, 'FITNESS':d2, 'MACDONALDS':d3,
      'CONVENIENCE':d4, 'ELEC_CHARGE':d5, 'CLINIC_OS':d6}

tmp_df = pd.DataFrame(md)
tmp_df.head()


# --------------------------------
# 3. Scoring & Adding Weight
# --------------------------------

tier_1 = int(len(tmp_df) * 0.2)
tier_2 = int(len(tmp_df) * 0.4)
tier_3 = int(len(tmp_df) * 0.6)
tier_4 = int(len(tmp_df) * 0.8)

infra_columns = ['LAUNDRY', 'FITNESS', 'MACDONALDS', 'CONVENIENCE', 'ELEC_CHARGE' ,'CLINIC_OS']
score_columns = ['LAUN_Score', 'FIT_Score', 'MAC_Score', 'CONV_Score', 'ELEC_Score', 'CLINIC_Score']

# scoring
for i in range(len(infra_columns)):
    tmp_df.loc[tmp_df['Officetels_Name'].isin(tmp_df.sort_values(by=infra_columns[i])[:tier_1]['Officetels_Name']), score_columns[i]] = 5
    tmp_df.loc[tmp_df['Officetels_Name'].isin(tmp_df.sort_values(by=infra_columns[i])[tier_1:tier_2]['Officetels_Name']), score_columns[i]] = 4
    tmp_df.loc[tmp_df['Officetels_Name'].isin(tmp_df.sort_values(by=infra_columns[i])[tier_2:tier_3]['Officetels_Name']), score_columns[i]] = 3
    tmp_df.loc[tmp_df['Officetels_Name'].isin(tmp_df.sort_values(by=infra_columns[i])[tier_3:tier_4]['Officetels_Name']), score_columns[i]] = 2
    tmp_df.loc[tmp_df['Officetels_Name'].isin(tmp_df.sort_values(by=infra_columns[i])[tier_4:]['Officetels_Name']), score_columns[i]] = 1
# tmp_df.head()

# adding weight
survey = pd.read_csv('survey_result.csv')
w = survey / 5

tmp_df[['LAUN_Score_w', 'FIT_Score_w',
        'MAC_Score_w', 'CONV_Score_w',
        'ELEC_Score_w', 'CLINIC_Score_w']] = tmp_df[['LAUN_Score', 'FIT_Score',
                                                     'MAC_Score', 'CONV_Score',
                                                     'ELEC_Score', 'CLINIC_Score']] * w.values

# sum & avg
tmp_df['Total_Score_w'] = tmp_df['LAUN_Score_w'] + tmp_df['FIT_Score_w'] + tmp_df['MAC_Score_w'] + tmp_df['ELEC_Score_w'] + tmp_df['CLINIC_Score_w']
tmp_df['AVG_Score_w'] = round((tmp_df['Total_Score_w'] / 6), 2)

# result
score = tmp_df[['Officetels_Name', 'LAT', 'LNG',
                'LAUN_Score_w', 'FIT_Score_w',
                'MAC_Score_w', 'CONV_Score_w',
                'ELEC_Score_w', 'CLINIC_Score_w',
                'Total_Score_w', 'AVG_Score_w']]
result = score.sort_values(by='AVG_Score_w', ascending=False).reset_index(drop=True).head(5)
# result.head()


# --------------------------------
# 4. Visualizing
# --------------------------------

# funtion of marker
def make_marker(map, x, y,z):
  for i in range(len(x)):
    folium.Marker([float(x[i]), float(y[i])], popup=z[i]).add_to(map)

# visualize the result on a map
map = folium.Map(location=[result['LAT'][0], result['LNG'][0]], zoom_start=12)
make_marker(map, result['LAT'], result['LNG'],result['Officetels_Name'])
# map


# --------------------------------
# 5. Appendix
# --------------------------------

lat = [laundry['LAT'], fitness['LAT'], macdonalds['LAT'],
       convenience['LAT'], elec['LAT'], clinic['LAT']]
lon = [laundry['LNG'], fitness['LNG'], macdonalds['LNG'],
       convenience['LNG'], elec['LNG'], clinic['LNG']]

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

# funtion of counting infra
def COUNT_INFRA(lat, lon):
  global df
  for i in tqdm(range(len(opt))):
    li_500 = []
    li_1000 = []
    li_2000 = []
    li_3000 = []
    li_4000 = []

    for i2 in range(len(lat)):
      sd = ALL_DISTANCE(opt['LAT'], opt['LNG'], lat[i2], lon[i2])
      sd_df = pd.DataFrame(sd[i], columns=['DX'])

      d_500 = sd_df[sd_df['DX'] < 500].count().values[0]
      d_1000 = sd_df[(sd_df['DX'] >= 500) & (sd_df['DX'] < 1000)].count().values[0]
      d_2000 = sd_df[(sd_df['DX'] >= 1000) & (sd_df['DX'] < 2000)].count().values[0]
      d_3000 = sd_df[(sd_df['DX'] >= 2000) & (sd_df['DX'] < 3000)].count().values[0]
      d_4000 = sd_df[sd_df['DX'] >= 3000 & (sd_df['DX'] < 4000)].count().values[0]

      li_500.append(d_500)
      li_1000.append(d_1000)
      li_2000.append(d_2000)
      li_3000.append(d_3000)
      li_4000.append(d_4000)

    index = ['Laundry', 'Fitness', 'MacDonalds',
             'Convenience', 'Elec_Charge', 'Clinic_OS']
    df = pd.DataFrame(index=index)
    df['under 500m'] = li_500
    df['500m ~ 1km'] = li_1000
    df['1km ~ 2km'] = li_2000
    df['2km ~ 3km'] = li_3000
    df['3km ~ 5km'] = li_4000

    df.to_csv('docs/table/' + opt['Officetels_Name'][i] + '.csv')

  return df

# count infra in distance conditions
cnt = COUNT_INFRA(lat, lon)
# cnt
