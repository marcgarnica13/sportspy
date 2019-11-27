# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:12:45 2019
@author: Miguel
"""
import numpy as np

#A partir de un pdata limpiar las columnas que sobran#
def clean_for_space_control(pdata):
    del pdata['half']
    del pdata['ball_x']
    del pdata['ball_y']
    del pdata['possession']
    del pdata['game_state']
    del pdata['time']
#Obtener la posición media del portero para saber la dirección de ataque#
def pitch_half_to_team(pdata):
    for player in teams ['home']:
        if player['position'] == 'TW':
            x_gk = player['id'] + '_x'
            pos_gk = np.nanmean(pdata[x_gk])
    return pos_gk
#%%
#SPACE CONTROL - VORONOI#
#1.Cálculo de las distancias a cada celda y asignación del player index más cercano#
#2.Cálculo del número de celdas controladas por cada jugador y por zonas del campo#
def calc_space_control(pdata, n_ver_cells, n_hor_cells):
    #width, length please
    no_frames = pdata.shape[0]
    no_players = pdata.shape[1]//2
    cells_to_players = np.zeros((2, no_frames, n_ver_cells, n_hor_cells))
    cells_to_players[0,:,:,:] = np.sqrt((n_ver_cells+n_hor_cells)**2)
    players_index = {}
    for f in range(no_frames):
        for i in range(n_hor_cells):
            for j in range(n_ver_cells):
                for p in range(no_players):
                    player = pdata.columns[p*2]
                    player_id = player.split('_')[0]
                    distance = np.sqrt(((i-52) - pdata.iloc[f,(p*2)])**2 + ((j-33.5) - pdata.iloc[f,(p*2+1)])**2)
                    if distance < cells_to_players[0,f,j,i]:
                        cells_to_players[0,f,j,i] = distance
                        cells_to_players[1,f,j,i] = p
                        players_index[player_id] = p
    num_cells_per_player = np.zeros((6, no_frames, no_players))
    for f in range(no_frames):
        for p in range(no_players):
            num_cells_per_player[0,f,p] = np.count_nonzero(cells_to_players[1,f,:,:] == p)
            num_cells_per_player[1,f,p] = np.count_nonzero(cells_to_players[1,f,:,:53] == p)
            num_cells_per_player[2,f,p] = np.count_nonzero(cells_to_players[1,f,:,52:] == p)
            num_cells_per_player[3,f,p] = np.count_nonzero(cells_to_players[1,f,:,:35] == p)
            num_cells_per_player[4,f,p] = np.count_nonzero(cells_to_players[1,f,:,35:70] == p)
            num_cells_per_player[5,f,p] = np.count_nonzero(cells_to_players[1,f,:,70:] == p)
    return num_cells_per_player, players_index
#%%

#Obtener listas de jugadores (solo su x)#
def list_players_space_control(pdata, teams):
    lista_all = []
    lista_home = []
    for headers in pdata.iloc[:,0::2]:
        lista_all.append(headers)
        for player in teams['home']:
            player_home = player['id'] + '_x'
            if player_home in headers:
                lista_home.append(player_home)
    return lista_all, lista_home
#%%
#Sumatorio del número de celdas controladas por cada equipo para cada frame#
def sum_functions(num_cells_per_player, lista, factor):
    nplayer = len(lista[1])
    space_control_home, space_control_away = np.sum(num_cells_per_player[0,:,:nplayer], axis = 1), np.sum(num_cells_per_player[0,:,nplayer:], axis = 1)
    if factor == 1:
        space_control_pitch_half1_h, space_control_pitch_half1_a = np.sum(num_cells_per_player[1,:,:nplayer], axis = 1), np.sum(num_cells_per_player[1,:,nplayer:], axis = 1)
        space_control_pitch_half2_h, space_control_pitch_half2_a = np.sum(num_cells_per_player[2,:,:nplayer], axis = 1), np.sum(num_cells_per_player[2,:,nplayer:], axis = 1)
        space_control_pitch_third1_h, space_control_pitch_third1_a = np.sum(num_cells_per_player[3,:,:nplayer], axis = 1), np.sum(num_cells_per_player[3,:,nplayer:], axis = 1)
        space_control_pitch_third2_h, space_control_pitch_third2_a = np.sum(num_cells_per_player[4,:,:nplayer], axis = 1), np.sum(num_cells_per_player[4,:,nplayer:], axis = 1)
        space_control_pitch_third3_h, space_control_pitch_third3_a = np.sum(num_cells_per_player[5,:,:nplayer], axis = 1), np.sum(num_cells_per_player[5,:,nplayer:], axis = 1)
    elif factor == -1:
        space_control_pitch_half2_h, space_control_pitch_half2_a = np.sum(num_cells_per_player[1,:,:nplayer], axis = 1), np.sum(num_cells_per_player[1,:,nplayer:], axis = 1)
        space_control_pitch_half1_h, space_control_pitch_half1_a = np.sum(num_cells_per_player[2,:,:nplayer], axis = 1), np.sum(num_cells_per_player[2,:,nplayer:], axis = 1)
        space_control_pitch_third3_h, space_control_pitch_third3_a = np.sum(num_cells_per_player[3,:,:nplayer], axis = 1), np.sum(num_cells_per_player[3,:,nplayer:], axis = 1)
        space_control_pitch_third2_h, space_control_pitch_third2_a = np.sum(num_cells_per_player[4,:,:nplayer], axis = 1), np.sum(num_cells_per_player[4,:,nplayer:], axis = 1)
        space_control_pitch_third1_h, space_control_pitch_third1_a = np.sum(num_cells_per_player[5,:,:nplayer], axis = 1), np.sum(num_cells_per_player[5,:,nplayer:], axis = 1)

    return [np.mean(space_control_home), np.mean(space_control_away), np.mean(space_control_pitch_half1_h), np.mean(space_control_pitch_half1_a), np.mean(space_control_pitch_half2_h), np.mean(space_control_pitch_half2_a), np.mean(space_control_pitch_third1_h), np.mean(space_control_pitch_third1_a), np.mean(space_control_pitch_third2_h), np.mean(space_control_pitch_third2_a), np.mean(space_control_pitch_third3_h), np.mean(space_control_pitch_third3_a)]

def sum_ind_function(num_cells_per_player, player_id, players_index):
    space_control = np.mean(num_cells_per_player[0,:,players_index[player_id]])
    return space_control

def run(pdata, width, length, teams, player, factor):
    pdata_onesecond = pdata[::10000]
    clean_for_space_control(pdata_onesecond)
    players_matrix, player_index = calc_space_control(pdata_onesecond, width, length)
    team_space_control = sum_functions(players_matrix, list_players_space_control(pdata, teams), factor)
    ind_space_control = sum_ind_function(players_matrix, player, player_index)
    return team_space_control + [ind_space_control]












