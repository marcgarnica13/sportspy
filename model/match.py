import os
import time
import numpy as np

from model.footballpy.fs.loader import dfl

class Match:
    def __init__(self, data, logger):
        logger.info('Starting Match instance')
        self.data_folder = data
        self.current_match = ""
        self.lg = logger

    def load_match(self, logger_tag, match_pos, match_info):
        self.tag = logger_tag
        if match_pos != self.current_match:
            self.lg.debug("{} > Loading new match {}".format(self.tag, match_pos))
            self.current_match = match_pos
            self.current_info = match_info

            if not os.path.exists(os.path.join(self.data_folder, match_pos)):
                self.lg.error("{} > Match pos file does not exist".format(self.tag))
                self.correct = False
                return False
            if not os.path.exists(os.path.join(self.data_folder, match_info)):
                self.lg.error("{} > Match info file does not exist".format(self.tag))
                self.correct = False
                return False
            self.lg.debug('{} > Match pos and info files exist'.format(self.tag))
            self.correct = True
            self.lg.debug("{} > Starting footballpy loading functionality.".format(self.tag))
            t_before = time.time()
            self.pdata, self.teams, self.match = dfl.get_df_from_files(os.path.join(self.data_folder, match_info), os.path.join(self.data_folder, match_pos))
            self.lg.debug("{} > footballpy loaded the data in {} seconds".format(self.tag, time.time() - t_before))
            return True

        return self.correct

    def set_test(self, frame_s_pre, frame_e_pre, frame_s_post, frame_e_post, location):
        self.lg.debug('{} > Setting new test from #{} to #{} and from #{} to #{}'.format(self.tag, frame_s_pre, frame_e_pre, frame_s_post, frame_e_post))
        self.lg.debug('{} > Location value: {}'.format(self.tag, location))
        self.frame_pre = {'start': int(frame_s_pre), 'end': int(frame_e_pre)}
        self.frame_post = {'start': int(frame_s_post), 'end': int(frame_e_post)}
        self.location = location

    def set_substitution(self, player_out, player_in):
        self.lg.debug('{} > {} player out | {} player in'.format(self.tag, player_out, player_in))
        self.player_out = player_out
        self.player_in = player_in

    def run_test(self):
        self.lg.info('{} > Starting test execution'.format(self.tag))
        result_centroid = []
        result_distance = []
        result_team_mesures = []
        result_stretch = []
        result_distance_centroid = []
        result_dyadic = []
        result_distance_opp = []

        if self.location == 1:
            indexes = [0,1,4]
        else:
            indexes = [2,3,4]

        for frame, player in [(self.frame_pre, self.player_out), (self.frame_post, self.player_in)]:
            self.lg.debug('{} > Testing {} frame'.format(self.tag, frame))
            first_slice = self.pdata.loc[frame['start']:frame['end'], :]
            home_players_list, h_factor = self._list_players(first_slice, 'home')
            guest_players_list, g_factor = self._list_players(first_slice, 'guest')
            first_slice = first_slice[first_slice['game_state'] == 1]
            start_time = time.time()
            result_centroid += [v for index, v in enumerate(self.team_centroid(first_slice[home_players_list], h_factor, first_slice[guest_players_list], g_factor)) if index in indexes]
            centroid_time = time.time()
            result_distance.append(self.distance_nearest_opp_ind(player, [first_slice[home_players_list], first_slice[guest_players_list]], self.location))
            distance_ind_time = time.time()
            result_team_mesures += self.team_length_width(first_slice[home_players_list if self.location == 1 else guest_players_list])
            team_mesures_time = time.time()
            result_stretch.append(self.stretch_index(first_slice[home_players_list if self.location == 1 else guest_players_list]))
            stretch_time = time.time()
            result_distance_centroid.append(self.distance_centroid(player, first_slice[home_players_list if self.location == 1 else guest_players_list]))
            distance_centroid_time = time.time()
            result_dyadic.append(self.dyadic_distance(first_slice[home_players_list if self.location == 1 else guest_players_list]))
            dyadic_time = time.time()
            result_distance_opp.append((self.distance_nearest_opp([first_slice[home_players_list], first_slice[guest_players_list]], self.location)))
            distance_opp_time = time.time()

            self.lg.debug('{} > Positional data indicators metrics: '.format(self.tag))
            self.lg.debug('{} > - Team centroid: {} seconds'.format(self.tag, centroid_time - start_time))
            self.lg.debug('{} > - Player distance to nearest opponent: {} seconds'.format(self.tag, distance_ind_time - centroid_time))
            self.lg.debug('{} > - Team measures (width/length): {} seconds'.format(self.tag, team_mesures_time - distance_ind_time))
            self.lg.debug('{} > - Team stretch: {} seconds'.format(self.tag, stretch_time - team_mesures_time))
            self.lg.debug('{} > - Team distance to centroid: {} seconds'.format(self.tag, distance_centroid_time - stretch_time))
            self.lg.debug('{} > - Team dyadic distance: {} seconds'.format(self.tag, dyadic_time - distance_centroid_time))
            self.lg.debug('{} > - Team collective distance to nearest opponent: {} seconds'.format(self.tag, distance_opp_time - dyadic_time))

            for e in [first_slice['possession'] == self.location, first_slice['possession'] != self.location]:
                self.lg.debug('{} > Testing with possession'.format(self.tag))
                poss_filtered = first_slice[e]
                result_centroid += [v for index, v in enumerate(self.team_centroid(poss_filtered[home_players_list], h_factor, poss_filtered[guest_players_list], g_factor)) if index in indexes]
                result_distance.append(self.distance_nearest_opp_ind(player, [poss_filtered[home_players_list], poss_filtered[guest_players_list]], self.location))
                result_team_mesures += self.team_length_width(poss_filtered[home_players_list if self.location == 1 else guest_players_list])
                result_stretch.append(self.stretch_index(poss_filtered[home_players_list if self.location == 1 else guest_players_list]))
                result_distance_centroid.append(self.distance_centroid(player, poss_filtered[home_players_list if self.location == 1 else guest_players_list]))
                result_dyadic.append(self.dyadic_distance(poss_filtered[home_players_list if self.location == 1 else guest_players_list]))
                result_distance_opp.append((self.distance_nearest_opp([poss_filtered[home_players_list], poss_filtered[guest_players_list]], self.location)))

        return result_centroid + result_distance + result_team_mesures + result_stretch + result_distance_centroid + result_dyadic + result_distance_opp

    def _list_players(self, data_slice, team):
        self.lg.debug('{} > _list_players function'.format(self.tag))
        lista = []
        factor = 1
        for player in self.teams[team]:
            if player['position'] != 'TW':
                if player['id'] + '_x' in data_slice:
                    lista.append(player['id'] + '_x')
                    lista.append(player['id'] + '_y')
            else:
                mean_x_gk = np.nanmean(data_slice[player['id'] + '_x'])
                if mean_x_gk < 0:
                    factor = 1
                if mean_x_gk > 0:
                    factor = -1
        return lista, factor

    def team_centroid(self, pdata1, factor1, pdata2, factor2):
        self.lg.info('{} > Computing team centroid'.format(self.tag))
        x_centroid1 = np.nanmean(pdata1.iloc[:, 0::2], 1, keepdims=True)
        y_centroid1 = np.nanmean(pdata1.iloc[:, 1::2], 1, keepdims=True)
        x_centroid2 = np.nanmean(pdata2.iloc[:, 0::2], 1, keepdims=True)
        y_centroid2 = np.nanmean(pdata2.iloc[:, 1::2], 1, keepdims=True)

        return (np.mean(x_centroid1) * factor1, np.mean(y_centroid1) * factor1,
            np.mean(x_centroid2) * factor2, np.mean(y_centroid2)* factor2,
            np.mean(np.sqrt((x_centroid1 - x_centroid2) ** 2 +
                            (y_centroid1 - y_centroid2) ** 2)))

    # Función distancia de un jugador al oponente más cercano#
    # player must play in pdata1
    def distance_nearest_opp_ind(self, player_id, list_of_slices, loc):
        self.lg.info('{} > Computing individual distance to nearest opponent'.format(self.tag))
        pdata1 = list_of_slices[loc - 1]
        pdata2 = list_of_slices[loc % 2]
        player = []
        player.append(player_id + '_x')
        player.append(player_id + '_y')
        pdata_ind = pdata1[player]
        pdata_ind = pdata_ind.to_numpy()
        pdata2 = pdata2.to_numpy()
        no_player = pdata2.shape[1] // 2
        no_frames = pdata2.shape[0]
        distances_all = np.zeros((no_frames, no_player))
        for f in np.arange(no_frames):
            for p in np.arange(no_player):
                distances_all[f, p] = np.sqrt(np.sum((pdata_ind[f, :] - pdata2[f, (p * 2):((p + 1) * 2)]) ** 2))
        distances_min = np.nanmin(distances_all[:, :], axis=1)
        return np.mean(distances_min)

    # Función team length, width and lg/W Ratio#
    def team_length_width(self, pdata):
        self.lg.info('{} > Computing team mesures'.format(self.tag))
        length = np.max(pdata.iloc[:, 0::2], 1) - np.min(pdata.iloc[:, 0::2], 1)
        width = np.max(pdata.iloc[:, 1::2], 1) - np.min(pdata.iloc[:, 1::2], 1)
        return [np.mean(length), np.mean(width),
                (np.mean(length / width))]

    # Stretch index, distancia media de todos los jugadores al team centroid#
    def stretch_index(self, pdata):
        self.lg.info('{} > Computing team stretch index'.format(self.tag))
        pdata = pdata.to_numpy()
        no_frames, no_player = pdata.shape
        no_player = no_player // 2
        x_centroid = np.nanmean(pdata[:, 0::2], 1, keepdims=True)
        y_centroid = np.nanmean(pdata[:, 1::2], 1, keepdims=True)
        matriz_centroid = np.hstack((x_centroid, y_centroid))
        tmp = np.zeros((no_frames, no_player))
        for p in np.arange(no_player):
            tmp[:, p] = np.sqrt(np.sum((pdata[:, (p * 2):((p + 1) * 2)] - matriz_centroid) ** 2, axis=1))
        si = np.nanmean(tmp, axis=1)
        si.shape = (no_frames, 1)
        return np.mean(si)

    def distance_centroid(self, player_id, pdata):
        self.lg.info('{} > Computing team centroid distance'.format(self.tag))
        player = []
        player.append(player_id + '_x')
        player.append(player_id + '_y')
        pdata_ind = pdata[player]
        x_centroid = np.nanmean(pdata.iloc[:, 0::2], 1, keepdims=True)
        y_centroid = np.nanmean(pdata.iloc[:, 1::2], 1, keepdims=True)
        matriz_centroid = np.hstack((x_centroid, y_centroid))
        distance = np.sqrt(
            (pdata_ind.iloc[:, 0] - matriz_centroid[:, 0]) ** 2 + (pdata_ind.iloc[:, 1] - matriz_centroid[:, 1]) ** 2)
        return np.mean(distance)

    def dyadic_distance(self, pdata):
        self.lg.info('{} > Computing team dyadic distance'.format(self.tag))
        pdata = pdata.to_numpy()
        no_player = pdata.shape[1] // 2
        distances = np.zeros((no_player, no_player))
        for p in np.arange(no_player):
            for o in np.arange(no_player):
                distances[p, o] = np.mean(
                    np.sqrt(np.sum((pdata[:, (p * 2):((p + 1) * 2)] - pdata[:, (o * 2):((o + 1) * 2)]) ** 2, axis=1)))
        distances[distances == 0] = ['nan']
        return np.nanmean(distances)

    # Distance to nearest opponent#
    def distance_nearest_opp(self, list_of_slices, loc):
        self.lg.info('{} > Computing team distance to nearest opponents'.format(self.tag))
        pdata1 = list_of_slices[loc - 1]
        pdata2 = list_of_slices[loc % 2]

        pdata1 = pdata1.to_numpy()
        pdata2 = pdata2.to_numpy()
        no_player1 = pdata1.shape[1] // 2
        no_player2 = pdata2.shape[1] // 2
        no_frames = pdata1.shape[0]
        distances_all = np.zeros((no_player1, no_frames, no_player2))
        for p in np.arange(no_player1):
            for f in np.arange(no_frames):
                for o in np.arange(no_player2):
                    distances_all[p, f, o] = np.sqrt(
                        np.sum((pdata1[f, (p * 2):((p + 1) * 2)] - pdata2[f, (o * 2):((o + 1) * 2)]) ** 2))
        distances_min = np.zeros((no_frames, no_player1))
        for p in np.arange(no_player1):
            distances_min[:, p] = np.nanmin(distances_all[p, :, :], axis=1)
        return np.nanmean(distances_min)





