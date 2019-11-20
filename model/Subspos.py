# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:12:45 2019
@author: Miguel
"""
import pylab
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
#%%
#Cargar las funciones de Robert para importar el partido#
from model.footballpy.fs.loader import dfl
#%%
#Importar el partido#
fpos = "DFL_04_02_positions_raw_DFL-COM-000001_DFL-MAT-0027AF.xml"
fmatch = "DFL_02_01_matchinformation_DFL-COM-000001_DFL-MAT-0027AF.xml"
pdata, teams, match = dfl.get_df_from_files(fmatch, fpos)
#%%
#Seleccionar una parte del partido#
half2 = pdata[pdata['half'] == 2]
#%%
#Seleccionar los intervalos en frames antes y depués de la sub#
pre = pdata.loc[100001:133326,:]
post = pdata.loc[133327:146721,:]
#%%
#Plotear posiciones de todo el equipo#
from statistics import mean
def plot_positions(pdata, location):
    for player in teams[location]:
        print(player['name'])
        print(player['id'])
        print(player['position'])
        x_name = player['id'] + '_x'
        y_name = player['id'] + '_y'
        if x_name in pdata:
            x = mean(pdata[x_name])
            y = mean(pdata[y_name])
            plt.scatter(x, y, marker='o', color='blue')
            plt.text(x+0.2, y, player['name'], fontsize=14)
            plt.text(x+2, y-3, player['position'], fontsize=14)
    plt.show()
#%%
#Plotear posiciones home or guest para un corte#
plot_positions(team1_pre, 'home')
#%%
#Plotear un jugador#
plt.plot(team2_post['DFL-OBJ-000280_x'], team2_post['DFL-OBJ-000280_y'])
#%%
#Exportar como csv#
def export_csv(abbrepartido_team_sub):
    pre.to_csv(abbrepartido_team_sub + '_pre')
    post.to_csv(abbrepartido_team_sub + '_post')
export_csv('ingo_hoff_team2_1')
#%%
#CALCULAR CENTROIDES AUTOMATIZADO#
#1.Eliminar columnas de los porteros#
def delete_gk(location):
    for player in teams [location]:
        if player['position'] == 'TW':
            x_gk = player['id'] + '_x'
            y_gk = player['id'] + '_y'
            del pre[x_gk]
            del pre[y_gk]
            del post[x_gk]
            del post[y_gk]
delete_gk('home')
delete_gk('guest')
#2.Hacer los cortes para cada equipo pre y post substitucion#
corte_pre = pre[pre['game_state'] == 1]
corte_post = post[post['game_state'] == 1]
corte_pre_poss1 = corte_pre[corte_pre['possession'] == 1]
corte_pre_poss2 = corte_pre[corte_pre['possession'] == 2]
corte_post_poss1 = corte_post[corte_post['possession'] == 1]
corte_post_poss2 = corte_post[corte_post['possession'] == 2]
#3.Lista de jugadores pre y post para cada equipo#
def list_players(pdata, location):
    lista = []
    for player in teams [location]:
        if player ['id']+'_x' in pdata:
            lista.append(player['id']+ '_x')
            lista.append(player['id']+ '_y')
    return (lista)
list_home_pre = list_players(pre, 'home')
list_home_post = list_players(post, 'home')
list_guest_pre = list_players(pre, 'guest')
list_guest_post = list_players(post, 'guest')
#4.Cortes para cada equipo en función de la posesión#
team1_pre = corte_pre[list_home_pre]
team2_pre = corte_pre[list_guest_pre]
team1_post = corte_post[list_home_post]
team2_post = corte_post[list_guest_post]
team1_pre_a = corte_pre_poss1[list_home_pre]
team1_pre_d = corte_pre_poss2[list_home_pre]
team2_pre_a = corte_pre_poss2[list_guest_pre]
team2_pre_d = corte_pre_poss1[list_guest_pre]
team1_post_a = corte_post_poss1[list_home_post]
team1_post_d = corte_post_poss2[list_home_post]
team2_post_a = corte_post_poss2[list_guest_post]
team2_post_d = corte_post_poss1[list_guest_post]
#5.Función team_centroid para los dos equipos y distancia entre centroides#
def team_centroid(pdata1, pdata2):
    x_centroid1 = np.nanmean(pdata1.iloc[:,0::2],1, keepdims = True)
    y_centroid1 = np.nanmean(pdata1.iloc[:,1::2],1, keepdims = True)
    x_centroid2 = np.nanmean(pdata2.iloc[:,0::2],1, keepdims = True)
    y_centroid2 = np.nanmean(pdata2.iloc[:,1::2],1, keepdims = True)
    return (np.mean(x_centroid1), np.mean(y_centroid1), 
            np.mean(x_centroid2), np.mean(y_centroid2),
            np.mean(np.sqrt((x_centroid1 - x_centroid2)**2 + 
                            (y_centroid1 - y_centroid2)**2)))
#Calcular team_centroid usando la función#
centroid_pre = team_centroid(team1_pre, team2_pre)
centroid_pre_poss1 = team_centroid(team1_pre_a, team2_pre_d)
centroid_pre_poss2 = team_centroid(team1_pre_d, team2_pre_a)
centroid_post = team_centroid(team1_post, team2_post)
centroid_post_poss1 = team_centroid(team1_post_a, team2_post_d)
centroid_post_poss2 = team_centroid(team1_post_d, team2_post_a)
#%%
#FALTA METERLO EN UNA FUNCIÓN Y TERMINARLO#
for player in teams ['guest']:
        if player['position'] == 'TW':
            x_gk = player['id'] + '_x'
            pos_gk = np.nanmean(pre[x_gk])
            if pos_gk < 0:
                print (centroid_pre[0])
            if pos_gk > 0:
                print (centroid_pre[0]*-1)
#%%
#Función team length, width and lg/W Ratio#
def team_length_width(pdata):
    length = np.max(pdata.iloc[:,0::2],1) - np.min(pdata.iloc[:,0::2],1)
    width = np.max(pdata.iloc[:,1::2],1) - np.min(pdata.iloc[:,1::2],1)
    return (np.mean(length), np.mean(width), 
            (np.mean(length) / np.mean(width)))
#%%
#Calcular length and width usando la función#
team_length_width(team2_post_d)
#%%
#Función distancia de un jugador al team centroid#
def distance_centroid(player_id, pdata):
    player = []
    player.append(player_id + '_x')
    player.append(player_id + '_y')
    pdata_ind = pdata[player]
    x_centroid = np.nanmean(pdata.iloc[:,0::2],1, keepdims = True)
    y_centroid = np.nanmean(pdata.iloc[:,1::2],1, keepdims = True)
    matriz_centroid = np.hstack((x_centroid, y_centroid))
    no_frames = team1_pre.shape[0]
    distance = np.zeros((no_frames))
    distance = np.sqrt((pdata_ind.iloc[:,0] - matriz_centroid[:,0])**2 + (pdata_ind.iloc[:,1] - matriz_centroid[:,1])**2)
    return distance
player_dis_centroid = distance_centroid('DFL-OBJ-0027AG', team1_pre)
np.mean(player_dis_centroid)
#%%
#Stretch index, distancia media de todos los jugadores al team centroid#
def stretch_index(pdata):
    pdata = pdata.to_numpy()
    no_frames, no_player = pdata.shape
    no_player = no_player // 2
    x_centroid = np.nanmean(pdata[:,0::2],1, keepdims = True)
    y_centroid = np.nanmean(pdata[:,1::2],1, keepdims = True)
    matriz_centroid = np.hstack((x_centroid, y_centroid))
    tmp = np.zeros((no_frames, no_player))
    for p in np.arange(no_player):
        tmp[:,p] = np.sqrt(np.sum((pdata[:,(p*2):((p+1)*2)] - matriz_centroid)**2, axis=1))
    si = np.nanmean(tmp, axis=1)
    si.shape = (no_frames, 1)
    return si, np.mean(si)
si = stretch_index(team1_pre)
#%%
#Dyadic distance#
def dyadic_distance(pdata):
    pdata = pdata.to_numpy()
    no_player = pdata.shape[1] // 2
    distances = np.zeros((no_player, no_player))
    for p in np.arange(no_player):
        for o in np.arange(no_player):
            distances[p,o] = np.mean(np.sqrt(np.sum((pdata[:,(p*2):((p+1)*2)] - pdata[:,(o*2):((o+1)*2)])**2, axis=1)))
    return distances
distances = dyadic_distance(team2_pre)
distances[distances==0]=['nan']
np.nanmean(distances)



