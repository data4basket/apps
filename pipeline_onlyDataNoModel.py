import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
import torch.nn.functional as F

class BasketballDataPipeline:
    def __init__(self):
        self.duracion_cuarto = 600
        self.typesPlays_toCount = [
            't2in', 't3in', 'r_t2in', 'r_t3in'  , 't1in', 'r_t1in', 'startG', 'end','subsIn', 'subsOut','r_subsIn', 'r_subsOut','ast', 'r_ast', 'rebD', 'rebO', 'r_rebD', 'r_rebO'
        ]
        self.typesPlays_notToCount = [
        '415', 'ajustesEspeciales', 'end', 'endG', 'firma', 'IR','jumpWin', 'jumpLost', 'publico', 'start', 'startG','subsIn', 'subsOut', 'timeOut',
        'r_415', 'r_ajustesEspeciales', 'r_end', 'r_endG', 'r_firma', 'r_IR','r_jumpWin', 'r_jumpLost', 'r_publico', 'r_start', 'r_startG','r_subsIn', 'r_subsOut', 'r_timeOut']

    def preprocess_df(self, df_events):
        # Transformaciones en los datos
        df_events['id_team'] = df_events['id_team']
        df_events['id_rivalTeam'] = df_events['id_rivalTeam']
        df_events['id_teamEjecutor'] = df_events['id_teamEjecutor']
        df_events['id_playerEjecutor'] = df_events['id_playerEjecutor']
        df_events['differenceMoment'] = df_events['scoreTeam'] - df_events['scoreRivalTeam']
        df_events['id_event'] = df_events['id_event'].apply(lambda x: int(x.split('_E', -1)[1]))
        df_events['period'] = df_events['period'].apply(lambda x: 4 if x > 4 else x)
        df_events['tiempo'] = (self.duracion_cuarto * df_events['period']) - (df_events['minute'] * 60 + df_events['second'])
        df_events = df_events.dropna(subset=['tiempo'])
        #df_events = df_events[~df_events['id_playbyplaytype'].isin(self.typesPlays_notToCount)]
        df_events = df_events[df_events['id_playbyplaytype'].isin(self.typesPlays_toCount)]
        df_events['result'] = df_events['result'].apply(lambda x: 1 if x == 1 else 0)

        return df_events

    def create_sequences(self, df_events):
        list_all_games = df_events['id_match'].unique()

        for game in list_all_games:
            df_game = df_events[df_events['id_match'] == game]
            teams_in_game = df_game['id_team'].unique()

            for team in teams_in_game:
                df_team_game = df_game[df_game['id_team'] == team].sort_values(by=['id_event'])
        df_team_game = df_team_game.reset_index(drop=True)
        return df_team_game


def prepare_dataloader(df_events):
    
    pipeline = BasketballDataPipeline()
    df_processed = pipeline.preprocess_df(df_events)
    df_team_game = pipeline.create_sequences(df_processed)
    
    return df_team_game



