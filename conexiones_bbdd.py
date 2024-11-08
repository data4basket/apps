import pandas as pd

import mysql.connector
from sqlalchemy import create_engine
import streamlit as st




DB_user = st.secrets["DB_user"] 
DB_host = st.secrets["DB_host"] 
DB_password = st.secrets["DB_password"]
DB_database = st.secrets["DB_database"]
DB_port = st.secrets["DB_port"]
DB_URI = st.secrets["DB_URI"] 
Access_DB = {'DB_user': DB_user, 'DB_host': DB_host, 'DB_password': DB_password, 'DB_database': DB_database, 'DB_port': DB_port, 'DB_URI': DB_URI}


def conectar_BDD(conn = True):
    if conn:
        engine = create_engine(Access_DB['DB_URI'])
        return(engine)
    else:
        conexion = mysql.connector.connect(user=Access_DB['DB_user'], password=Access_DB['DB_password'],host=Access_DB['DB_host'],database=Access_DB['DB_database'], port=Access_DB['DB_port'],auth_plugin='mysql_native_password')
        cursor = conexion.cursor()
        return (conexion, cursor)
    

@st.cache_data
def buscarJugadoresInfo():
    engine= conectar_BDD()
    query = "SELECT id_player, id_person, name_nick, image, image_2 from p_players order by id_edition desc" # where id_team = '" + id_team + "'"
    df_players = pd.read_sql(query, con=engine).drop_duplicates(subset=['id_person'])
    return df_players

# Caracteristicas de Equipos
st.cache_data
def buscarEquiposInfo():
    engine= conectar_BDD()
    query = "SELECT id_team, team_name, abrev_name, primary_color, secondary_color, image_2 from teams order by id_edition desc"
    df_teams = pd.read_sql(query, con=engine)
    return df_teams


@st.cache_data
def obtener_infoPartidos(list_games):
    engine= conectar_BDD()
    query = "SELECT id_match, id_localteam, id_visitorteam FROM j_matches WHERE id_match in " + str(tuple(list_games))
    df_out = pd.read_sql(query, con=engine)
    return df_out

@st.cache_data
def obtener_jornadas():
    DF = pd.read_excel("in/partidos.xlsx")
    return(DF)

@st.cache_data
def buscar_selected_games(DF_JORNADAS, selected_jornada, obj_teams_nameFull):
    list_games = DF_JORNADAS[selected_jornada].to_list()
    DF_GAMES= obtener_infoPartidos(list_games)
    obj_games = {x['id_match']: obj_teams_nameFull[x['id_localteam']] + "  -  " + obj_teams_nameFull[x['id_visitorteam']] for index, x in DF_GAMES.iterrows() }
    list_teams = {x['id_match']:[x['id_localteam'], x['id_visitorteam']] for index, x in DF_GAMES.iterrows()}
    return obj_games, list_teams

# Partido ejemplo:
@st.cache_data
def buscarPartidosEvents(game, id_team):
    engine= conectar_BDD()
    query = "SELECT id_match, id_event, period, minute, second, id_team, id_rivalTeam, scoreTeam, scoreRivalTeam, id_teamEjecutor, id_playerEjecutor, id_playbyplaytype, result, difference from j_fives WHERE id_match = '" + game + "' and id_team = '" + id_team + "'"
    df_events = pd.read_sql(query, con=engine)
    return df_events

#@st.cache_data
def buscarBoxscore(game):
    engine= conectar_BDD()
    query = "SELECT * from j_teamstats WHERE id_match = '" + game + "' and period = 0"
    df_events = pd.read_sql(query, con=engine).sort_values(by='lado', ascending=True)
    return df_events

def buscarBoxscorePromedioTeam(id_team, game):
    engine= conectar_BDD()
    query = "SELECT * from j_teamstats WHERE id_team = '" + id_team + "' and id_match < '" + game + "' and period = 0"
    df_events = pd.read_sql(query, con=engine).sort_values(by='lado', ascending=True)
    return df_events

def buscarPlayers_dePartido_de1Equipo(selected_game, selected_teamImpacto):
    engine= conectar_BDD()
    query = "SELECT id_player from j_playerstats WHERE id_team = '" + selected_teamImpacto + "' and id_match = '" + selected_game + "' and period = 0"
    df_events = pd.read_sql(query, con=engine)
    return df_events

def buscarEventosGameWithPlayer(selected_game, selected_teamImpacto, selected_playerImpacto):
    [conexion, _] = conectar_BDD(False)
    query =  "SELECT * FROM j_fives WHERE id_match = '" + selected_game + "' AND num_players = 5 AND id_team = '" + selected_teamImpacto + "' AND id_five like '%" + selected_playerImpacto + "%'"
    df_events = pd.read_sql(query, conexion)
    conexion.close()
    return df_events

def buscarEventosGameWithoutPlayer(selected_game, selected_teamImpacto, selected_playerImpacto):
    [conexion, _] = conectar_BDD(False)
    query =  "SELECT * FROM j_fives WHERE id_match = '" + selected_game + "' AND num_players = 5 AND id_team = '" + selected_teamImpacto + "' AND id_five not like '%" + selected_playerImpacto + "%'"
    df_events = pd.read_sql(query, conexion)
    conexion.close()
    return df_events
