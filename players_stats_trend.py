import numpy as np
import pandas as pd
import streamlit as st

import plotly.figure_factory as ff
import plotly.express as px
import boto3 
from boto3.dynamodb.conditions import Key, Attr


#@st.cache

def conectar_AWS(Access_WS):
    Access_key = Access_WS['Access_key']
    Secret_Access_key = Access_WS['Secret_Access_key']
    region_name = Access_WS['region_name']
    dynamodb = boto3.resource('dynamodb',aws_access_key_id=Access_key, aws_secret_access_key=Secret_Access_key, region_name=region_name)
    return(dynamodb)

def conectar_AWS_client(Access_WS):
    Access_key = Access_WS['Access_key']
    Secret_Access_key = Access_WS['Secret_Access_key']
    region_name = Access_WS['region_name']
    dynamodb = boto3.client('dynamodb',aws_access_key_id=Access_key, aws_secret_access_key=Secret_Access_key, region_name=region_name)
    return(dynamodb)


#AWS_keys = pd.read_csv('in/read_only_streamlit_accessKeys.csv')
Access_key = st.secrets["AWS_ACCESS_KEY_ID"] #AWS_keys['Access key ID'][0]
Secret_Access_key = st.secrets["AWS_SECRET_ACCESS_KEY"] #AWS_keys['Secret access key'][0]
region_name = st.secrets["AWS_DEFAULT_REGION"]
Access_WS = {'Access_key': Access_key, 'Secret_Access_key': Secret_Access_key, 'region_name': region_name}

dynamoDB = conectar_AWS(Access_WS)

# Inject custom CSS to set the width of the sidebar
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 33% !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def buscarCompeticiones(dynamoDB):
    table = dynamoDB.Table('competition')
    obj_competitions = {}
    obj_editions = {}
    try:
        response = table.scan(
        )
        items = response['Items']
        for key in items:
            obj_competitions[key['id_competition']] = key['name']
            obj_editions[key['id_edition']] = key['year']
    except:
        True
    return [obj_competitions, obj_editions]

def buscarJugadores(dynamoDB, selected_liga_id):
    table = dynamoDB.Table('p_players')
    try:
        response = table.query(
            IndexName="player_index",
            KeyConditionExpression=Key("key_competition").eq(selected_liga_id),
            )

        list_keys_out = response['Items']
        df_out = pd.DataFrame(list_keys_out)
        df_out = df_out[['id_player', 'name']]
    except:
        list_keys_out = []
        df_out = pd.DataFrame(list_keys_out)
    return df_out

def buscarEstadisticas(dynamoDB, player, stat):
    table = dynamoDB.Table('j_playerstats')
    try:
        response = table.query(
            IndexName="player_index",
            KeyConditionExpression=Key("id_player").eq(player),
            )

        list_keys_out = response['Items']      
        df_out = pd.DataFrame(list_keys_out)
        df_out = df_out[df_out['period']==0]
        df_out['start_date'] = pd.to_datetime(df_out['start_date'], format='%d-%m-%Y - %H:%M')
        df_out = df_out[['start_date', stat, 'rival_team_name']].sort_values(by='start_date', ascending=True)
        df_out[stat] = df_out[stat].astype(float)
        if stat == 'time_played':
            df_out[stat] = df_out[stat]/60 #df_out.stat.apply(lambda x:x/60)
    except:
        list_keys_out = []
        df_out = pd.DataFrame(list_keys_out)
    return df_out



# SIDEBAR
colSide1, colSide2= st.sidebar.columns([2, 5])
with colSide1:
    st.image('in/logo_data4basket.jpg')
with colSide2:
    htmlTittleSide='''
    <p style="font-type: Buffalo; margin-left: 35px; margin-top: 25px; font-size: 40px; color: #3A6743">DATA4BASKET</p>
    '''
    st.markdown(htmlTittleSide, unsafe_allow_html=True)


lista_estadisticas = ['Puntos', 'Rebotes', 'Asistencias', 'Minutos', 'Valoración', '+-', 'Recuperaciones', 'Pérdidas', 'Tapones a Favor', 'Tapones en Contra', 'Rebotes Defensivos', 'Rebotes Ofensivos', 'Faltas Cometidas', 'Faltas Recibidas', 'Puntos al Contrataque', 'Puntos en la Zona', 'Puntos en 2º Oportunidad', 'Puntos tras Asistencia', 'Puntos tras Robo', 'Mates', 'Tiros de 2 puntos Anotados', 'Tiros de 2 puntos Intentados', '% Tiros de 2 puntos', 'Triples Anotados', 'Triples Intentados', '% Triples', 'Tiros Libres Anotados', 'Tiros Libres Intentados', '% Tiros Libres', 'Titular', 'Finaliza partido en campo']

dict_estadisticas = {'Puntos': 'points', 'Rebotes': 'total_rebound', 'Asistencias': 'assists', 'Minutos': 'time_played', 'Valoración': 'val', '+-': 'differencePlayer', 'Recuperaciones': 'steals', 'Pérdidas': 'turnovers', 'Tapones a Favor': 'blocks', 'Tapones en Contra': 'received_blocks', 'Rebotes Defensivos': 'deffensive_rebound', 'Rebotes Ofensivos': 'offensive_rebound', 'Faltas Cometidas': 'personal_fouls', 'Faltas Recibidas': 'received_fouls', 'Puntos al Contrataque': 'points_fast_break', 'Puntos en la Zona': 'points_in_the_paint', 'Puntos en 2º Oportunidad': 'points_second_chance', 'Puntos tras Asistencia': 'points_afterassist', 'Puntos tras Robo': 'points_aftersteal', 'Mates': 'dunks', 'Tiros de 2 puntos Anotados': 'pt2_success', 'Tiros de 2 puntos Intentados': 'pt2_tried', '% Tiros de 2 puntos': 'pt2_percentage', 'Triples Anotados': 'pt3_success', 'Triples Intentados': 'pt3_tried', '% Triples': 'pt3_percentage', 'Tiros Libres Anotados': 'pt1_success', 'Tiros Libres Intentados': 'pt1_tried', '% Tiros Libres': 'pt3_percentage', 'Titular': 'starting', 'Finaliza partido en campo': 'finishing'}

st.sidebar.header('Estadística')
selected_stat= st.sidebar.selectbox('',lista_estadisticas)
#selected_stat = 'Minutos'
stat = dict_estadisticas[selected_stat]


col1, col2, col3 = st.sidebar. columns([5,4,6])
[obj_competitions, obj_editions] = buscarCompeticiones(dynamoDB)
list_ligas_disponiblesName = list(set(list(obj_competitions[key] for key in obj_competitions)))
list_years_disponiblesName = sorted(list(set(list(obj_editions[key] for key in obj_editions))), reverse=True)

list_players_selected = []
hist_data = []
df_data = []
color_list = []

with col1:
   st.header('Jugador 1')
   selected_liga1 = st.selectbox('Liga 1', list_ligas_disponiblesName)
   selected_liga1_id = list(obj_competitions.keys())[list(obj_competitions.values()).index(selected_liga1)]
   st.header('Jugador 2')
   selected_liga2 = st.selectbox('Liga 2', list_ligas_disponiblesName)
   selected_liga2_id = list(obj_competitions.keys())[list(obj_competitions.values()).index(selected_liga2)]
   st.header('Jugador 3')
   check_player3 = st.checkbox('Jugador 3')
   if check_player3:
       selected_liga3 = st.selectbox('Liga 3', list_ligas_disponiblesName)
       selected_liga3_id = list(obj_competitions.keys())[list(obj_competitions.values()).index(selected_liga3)]
   st.header('Jugador 4')
   check_player4 = st.checkbox('Jugador 4')
   if check_player4:
       selected_liga4 = st.selectbox('Liga 4', list_ligas_disponiblesName)
       selected_liga4_id = list(obj_competitions.keys())[list(obj_competitions.values()).index(selected_liga4)]
       

with col2:
   html='''
    <p style="visibility: hidden; font-size: 25px">.</p>
    '''
   html_small='''
    <p style="visibility: hidden">.</p>
    '''
   st.markdown(html, unsafe_allow_html=True)
   selected_year1 = st.selectbox('Año 1', list_years_disponiblesName)
   selected_year1_id = list(obj_editions.keys())[list(obj_editions.values()).index(selected_year1)]
   key_competition_1 = str(selected_liga1_id) + '_' + str(selected_year1_id)
   st.markdown(html, unsafe_allow_html=True)
   selected_year2 = st.selectbox('Año 2', list_years_disponiblesName)
   selected_year2_id = list(obj_editions.keys())[list(obj_editions.values()).index(selected_year2)]
   key_competition_2 = str(selected_liga2_id) + '_' + str(selected_year2_id)
   st.markdown(html, unsafe_allow_html=True)
   if check_player3:
       st.markdown(html_small, unsafe_allow_html=True)
       selected_year3 = st.selectbox('Año 3', list_years_disponiblesName)
       selected_year3_id = list(obj_editions.keys())[list(obj_editions.values()).index(selected_year3)]
       key_competition_3 = str(selected_liga3_id) + '_' + str(selected_year3_id)
   st.markdown(html, unsafe_allow_html=True)
   if check_player4:
       st.markdown(html_small, unsafe_allow_html=True)
       selected_year4 = st.selectbox('Año 4', list_years_disponiblesName)
       selected_year4_id = list(obj_editions.keys())[list(obj_editions.values()).index(selected_year4)]
       key_competition_4 = str(selected_liga4_id) + '_' + str(selected_year4_id)

with col3:
    st.markdown(html, unsafe_allow_html=True)
    df_players1 = buscarJugadores(dynamoDB, key_competition_1)
    list_jugadores1 = []
    dict_players1 = {}
    for index, row in df_players1.iterrows():
        list_jugadores1.append(row['name'])
        dict_players1[row['name']] = row['id_player']
    list_jugadores1 = sorted(list_jugadores1)
    selected_player1 = st.selectbox('Jugador 1', list_jugadores1)
    player1 = dict_players1[selected_player1]

    st.markdown(html, unsafe_allow_html=True)
    df_players2 = buscarJugadores(dynamoDB, key_competition_2)
    list_jugadores2 = []
    dict_players2 = {}
    for index, row in df_players2.iterrows():
        list_jugadores2.append(row['name'])
        dict_players2[row['name']] = row['id_player']
    list_jugadores2 = sorted(list_jugadores2)
    selected_player2 = st.selectbox('Jugador 2', list_jugadores2)
    player2 = dict_players2[selected_player2]

    st.markdown(html, unsafe_allow_html=True)
    if check_player3:
        st.markdown(html_small, unsafe_allow_html=True)
        df_players3 = buscarJugadores(dynamoDB, key_competition_3)
        list_jugadores3 = []
        dict_players3 = {}
        for index, row in df_players3.iterrows():
            list_jugadores3.append(row['name'])
            dict_players3[row['name']] = row['id_player']
        list_jugadores3 = sorted(list_jugadores3)
        selected_player3 = st.selectbox('Jugador 3', list_jugadores3)
        player3 = dict_players3[selected_player3]

    st.markdown(html, unsafe_allow_html=True)
    if check_player4:
        st.markdown(html_small, unsafe_allow_html=True)
        df_players4 = buscarJugadores(dynamoDB, key_competition_4)
        list_jugadores4 = []
        dict_players4 = {}
        for index, row in df_players4.iterrows():
            list_jugadores4.append(row['name'])
            dict_players4[row['name']] = row['id_player']
        list_jugadores4 = sorted(list_jugadores4)
        selected_player4 = st.selectbox('Jugador 4', list_jugadores4)
        player4 = dict_players4[selected_player4]






if selected_player1:
    stringPlayer1 = str(selected_player1) + " (" + str(selected_liga1) + " " + str(selected_year1) + ")"
    list_players_selected.append(stringPlayer1)

    df_results_player1 = buscarEstadisticas(dynamoDB, player1, stat)
    resultsList_player1 = df_results_player1[stat].to_list() # Estadistica
    rivalesList_player1 = df_results_player1['rival_team_name'].to_list() # Rival

    hist_data.append(resultsList_player1)
    for n in range(len(resultsList_player1)):
        estadistica = resultsList_player1[n]
        rivalTeam = rivalesList_player1[n]
        df_data.append({'jugador': stringPlayer1, str(selected_stat): estadistica, 'rival': rivalTeam, 'nº partido': n+1})
    color_list.append("#D62728")


if selected_player2:
    stringPlayer2 = str(selected_player2) + " (" + str(selected_liga2) + " " + str(selected_year2) + ")"
    list_players_selected.append(stringPlayer2)

    df_results_player2 = buscarEstadisticas(dynamoDB, player2, stat)
    resultsList_player2 = df_results_player2[stat].to_list() # Estadistica
    rivalesList_player2 = df_results_player2['rival_team_name'].to_list() # Rival

    hist_data.append(resultsList_player2)
    for n in range(len(resultsList_player2)):
        estadistica = resultsList_player2[n]
        rivalTeam = rivalesList_player2[n]
        df_data.append({'jugador': stringPlayer2, str(selected_stat): estadistica, 'rival': rivalTeam, 'nº partido': n+1})
    color_list.append("#1F77B4")


if check_player3 and selected_player3:
    stringPlayer3 = str(selected_player3) + " (" + str(selected_liga3) + " " + str(selected_year3) + ")"
    list_players_selected.append(stringPlayer3)

    df_results_player3 = buscarEstadisticas(dynamoDB, player3, stat)
    resultsList_player3 = df_results_player3[stat].to_list() # Estadistica
    rivalesList_player3 = df_results_player3['rival_team_name'].to_list() # Rival

    hist_data.append(resultsList_player3)
    for n in range(len(resultsList_player3)):
        estadistica = resultsList_player3[n]
        rivalTeam = rivalesList_player3[n]
        df_data.append({'jugador': stringPlayer3, str(selected_stat): estadistica, 'rival': rivalTeam, 'nº partido': n+1})
    color_list.append("#2D952E")


if check_player4 and selected_player4:
    stringPlayer4 = str(selected_player4) + " (" + str(selected_liga4) + " " + str(selected_year4) + ")"
    list_players_selected.append(stringPlayer4)

    df_results_player4 = buscarEstadisticas(dynamoDB, player4, stat)
    resultsList_player4 = df_results_player4[stat].to_list() # Estadistica
    rivalesList_player4 = df_results_player4['rival_team_name'].to_list() # Rival

    hist_data.append(resultsList_player4)
    for n in range(len(resultsList_player4)):
        estadistica = resultsList_player4[n]
        rivalTeam = rivalesList_player4[n]
        df_data.append({'jugador': stringPlayer4, str(selected_stat): estadistica, 'rival': rivalTeam, 'nº partido': n+1})
    color_list.append("#FF7F0E")


# PRINCIPAL PAGE
    
colMain1, colMain2= st.columns([6, 2])
with colMain1:
    htmlTittleMain='''
    <p style="font-type: Buffalo; margin-left: 60px; margin-top: 25px; font-size: 60px; color: #3A6743">DATA4BASKET</p>
    '''
    st.markdown(htmlTittleMain, unsafe_allow_html=True)
with colMain2:
    st.image('in/logo_data4basket.jpg')


str_jugadores_seleccionados = " y ".join(list_players_selected)
# HISTÓRICO AÑOS

HEADER2 = "TENDENCIA DE: " + str(selected_stat).upper()
st.title(HEADER2)

TITLE2 = "- Gráfico con línea de tendencia de " + str(selected_stat) + " entre " + str_jugadores_seleccionados
st.markdown(TITLE2)
df = pd.DataFrame(df_data)

fig2 = px.scatter(
    df,
    x="nº partido",
    y=str(selected_stat),
    color="jugador",
    hover_name="rival",
    trendline="lowess",
    size_max=60, 
    color_discrete_sequence=color_list,
    title="TENDENCIA " + str(selected_stat).upper())

fig2.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ),
    xaxis_title="Partidos Jugados",
    yaxis_title= str(selected_stat)
    )

st.plotly_chart(fig2, use_container_width=True)



# DENSITY PLOT
HEADER1 = "DISTRIBUCIÓN DE: " + str(selected_stat).upper()
st.title(HEADER1)

TITLE1 = "- Gráfico de densidad midiendo en el eje Y la frecuencia de puntos entre " + str_jugadores_seleccionados
st.markdown(TITLE1)

fig = ff.create_distplot(
        hist_data, list_players_selected, show_hist=False, colors=color_list)

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ),
    xaxis_title=str(selected_stat),
    yaxis_title= "Frecuencia",
    title_text='GRÁFICO DENSIDAD: '+str(selected_stat).upper()
    )

st.plotly_chart(fig, use_container_width=True)


