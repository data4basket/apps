import numpy as np
import pandas as pd
import streamlit as st

import plotly.graph_objects as go
import plotly.express as px

import boto3 
from boto3.dynamodb.conditions import Key, Attr



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
            width: 23% !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def buscarCompeticiones(_dynamoDB):
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

@st.cache_data
def buscarEquipos(_dynamoDB, selected_liga_id):
    table = dynamoDB.Table('teams')
    try:
        response = table.query(
                IndexName="team-index",
            KeyConditionExpression=Key("key_competition").eq(selected_liga_id),
            )

        list_keys_out = response['Items']
        df_out = pd.DataFrame(list_keys_out)
        df_out = df_out[['id_team', 'team_name', 'image']]
    except:
        list_keys_out = []
        df_out = pd.DataFrame(list_keys_out)
    return df_out

@st.cache_data
def buscarStatFives(_dynamoDB, team):
    table = dynamoDB.Table('jFives')
#try:
    response = table.query( KeyConditionExpression=Key('id_team').eq(team))
    list_keys_out = response['Items']      
    df_out = pd.DataFrame(list_keys_out)
    if True:
        while response.get("LastEvaluatedKey"):
            response = table.query(
                ExclusiveStartKey=response.get("LastEvaluatedKey"),
                #IndexName="five_indexTeam",
                KeyConditionExpression=Key("id_team").eq(team),     
                #ProjectionExpression= "num_players, name_player1, name_player2, name_player3, name_player4, name_player5, name_five",
            )
            list_keys_out = response['Items']      
            df_outWhile = pd.DataFrame(list_keys_out)
            df_out = pd.concat([df_out, df_outWhile])
       
    df_out = df_out[df_out['num_players']==5]
#except:
#    list_keys_out = []
#    df_out = pd.DataFrame(list_keys_out)
    return df_out



# SIDEBAR
colSide1, colSide2= st.sidebar.columns([2, 5])
with colSide1:
    st.image('in/logo_data4basket.jpg')
with colSide2:
    htmlTittleSide='''
    <p style="font-type: Buffalo; margin-left: 20px; margin-top: 15px; font-size: 28spx; color: #3A6743">DATA4BASKET</p>
    '''
    st.markdown(htmlTittleSide, unsafe_allow_html=True)


[obj_competitions, obj_editions] = buscarCompeticiones(dynamoDB)
list_ligas_disponiblesName = list(set(list(obj_competitions[key] for key in obj_competitions)))
list_years_disponiblesName = sorted(list(set(list(obj_editions[key] for key in obj_editions))), reverse=True)
list_years_disponiblesName = ['2023-24'] # Hardcodeado porque solo datos de quintetos de este año 

# Quinteto 1
st.sidebar.title('Quinteto 1:')
col1, col2 = st.sidebar. columns([5,4])
with col1:
    selected_liga1 = st.selectbox('Liga 1:', list_ligas_disponiblesName)
    selected_liga1_id = list(obj_competitions.keys())[list(obj_competitions.values()).index(selected_liga1)]

with col2:
    selected_year1 = st.selectbox('Año 1:', list_years_disponiblesName)
    selected_year1_id = list(obj_editions.keys())[list(obj_editions.values()).index(selected_year1)]
    key_competition_1 = str(selected_liga1_id) + '_' + str(selected_year1_id)

df_teams1 = buscarEquipos(dynamoDB, key_competition_1)
list_teams1 = []
dict_team1 = {}
dict_teamFoto1 = {}
for index, row in df_teams1.iterrows():
    list_teams1.append(row['team_name'])
    dict_team1[row['team_name']] = row['id_team']
    dict_teamFoto1[row['team_name']] = row['image']
list_teams1 = sorted(list_teams1)
selected_team1 = st.sidebar.selectbox('Equipo 1:', list_teams1)
team1 = dict_team1[selected_team1]
teamFoto1 = dict_teamFoto1[selected_team1]

df_statFives_team1 = buscarStatFives(dynamoDB, team1)

team1_listNames_player1 = df_statFives_team1['name_player1'].to_list()
team1_listNames_player2 = df_statFives_team1['name_player2'].to_list()
team1_listNames_player3 = df_statFives_team1['name_player3'].to_list()
team1_listNames_player4 = df_statFives_team1['name_player4'].to_list()
team1_listNames_player5 = df_statFives_team1['name_player5'].to_list()
team1_listNames_players = sorted(list(set(team1_listNames_player1 + team1_listNames_player2 + team1_listNames_player3 + team1_listNames_player4 + team1_listNames_player5)))

selected_team1_players_in = st.sidebar.multiselect('Jugadores dentro del quinteto 1:', team1_listNames_players)
selected_team1_players_out = st.sidebar.multiselect('Jugadores fuera del quinteto 1:', team1_listNames_players)

if len(selected_team1_players_in) > 0:
    for selected_player in selected_team1_players_in:
        df_statFives_team1 = df_statFives_team1[df_statFives_team1['name_five'].str.contains(selected_player)]
else:
    selected_team1_players_in.append('-')
TextPlayersIn_team1 = " - ".join(str(element) for element in selected_team1_players_in)

if len(selected_team1_players_out) > 0:
    for selected_player in selected_team1_players_out:
        df_statFives_team1 = df_statFives_team1[~df_statFives_team1['name_five'].str.contains(selected_player)]
else:
    selected_team1_players_out.append('-')
TextPlayersOut_team1 = " - ".join(str(element) for element in selected_team1_players_out)

GAMES_PLAYED_TEAM1 = len(pd.unique(df_statFives_team1['id_match']))
MINUTES_PLAYED_TEAM1 = (df_statFives_team1['second_gameOut'].sum() - df_statFives_team1['second_gameIn'].sum()) / 60
T2IN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 't2in'].shape[0]
T2OUT_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 't2out'].shape[0]
T3IN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 't3in'].shape[0]
T3OUT_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 't3out'].shape[0]
T1IN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 't1in'].shape[0]
T1OUT_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 't1out'].shape[0]
TURN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'turn'].shape[0]
REB_OF_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'rebO'].shape[0]
RIVAL_T2IN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_t2in'].shape[0]
RIVAL_T3IN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_t3in'].shape[0]
RIVAL_T1IN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_t1in'].shape[0]
RIVAL_T2OUT_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_t2out'].shape[0]
RIVAL_T3OUT_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_t3out'].shape[0]
RIVAL_T1OUT_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_t1out'].shape[0]
RIVAL_TURN_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_turn'].shape[0]
RIVAL_REB_OF_TEAM1 = df_statFives_team1[df_statFives_team1['id_playbyplaytype'] == 'r_rebO'].shape[0]
POS_TEAM1 = 0.96*((T2IN_TEAM1+T2OUT_TEAM1+T3IN_TEAM1+T3OUT_TEAM1) + TURN_TEAM1 + 0.44*(T1IN_TEAM1+T1OUT_TEAM1-REB_OF_TEAM1))
RIVAL_POS_TEAM1 = 0.96*((RIVAL_T2IN_TEAM1+RIVAL_T2OUT_TEAM1+RIVAL_T3IN_TEAM1+RIVAL_T3OUT_TEAM1) + RIVAL_TURN_TEAM1 + 0.44*(RIVAL_T1IN_TEAM1+RIVAL_T1OUT_TEAM1-RIVAL_REB_OF_TEAM1))
OFF_EF_TEAM1 = 100*((2*T2IN_TEAM1 + 3*T3IN_TEAM1 + T1IN_TEAM1)/POS_TEAM1)
DEF_EF_TEAM1 = -100*((2*RIVAL_T2IN_TEAM1 + 3*RIVAL_T3IN_TEAM1 + RIVAL_T1IN_TEAM1)/RIVAL_POS_TEAM1)
NET_EF_TEAM1 = OFF_EF_TEAM1 + DEF_EF_TEAM1
RITMO_TEAM1 = POS_TEAM1/float(MINUTES_PLAYED_TEAM1)*40 if MINUTES_PLAYED_TEAM1>0 else 0
MINUTES_PLAYED_TEAM1 = round(MINUTES_PLAYED_TEAM1, 0)


# Quinteto 2
st.sidebar.title('Quinteto 2:')
col1, col2 = st.sidebar. columns([5,4])
with col1:
    selected_liga2 = st.selectbox('Liga 2:', list_ligas_disponiblesName)
    selected_liga2_id = list(obj_competitions.keys())[list(obj_competitions.values()).index(selected_liga2)]

with col2:
    selected_year2 = st.selectbox('Año 2:', list_years_disponiblesName)
    selected_year2_id = list(obj_editions.keys())[list(obj_editions.values()).index(selected_year2)]
    key_competition_2 = str(selected_liga2_id) + '_' + str(selected_year2_id)

df_teams2 = buscarEquipos(dynamoDB, key_competition_2)
list_teams2 = []
dict_team2 = {}
dict_teamFoto2 = {}
for index, row in df_teams2.iterrows():
    list_teams2.append(row['team_name'])
    dict_team2[row['team_name']] = row['id_team']
    dict_teamFoto2[row['team_name']] = row['image']
list_teams2 = sorted(list_teams2)
selected_team2 = st.sidebar.selectbox('Equipo 2:', list_teams2)
team2 = dict_team2[selected_team2]
teamFoto2 = dict_teamFoto2[selected_team2]

df_statFives_team2 = buscarStatFives(dynamoDB, team2)

team2_listNames_player1 = df_statFives_team1['name_player1'].to_list()
team2_listNames_player2 = df_statFives_team2['name_player2'].to_list()
team2_listNames_player3 = df_statFives_team2['name_player3'].to_list()
team2_listNames_player4 = df_statFives_team2['name_player4'].to_list()
team2_listNames_player5 = df_statFives_team2['name_player5'].to_list()
team2_listNames_players = sorted(list(set(team2_listNames_player1 + team2_listNames_player2 + team2_listNames_player3 + team2_listNames_player4 + team2_listNames_player5)))

selected_team2_players_in = st.sidebar.multiselect('Jugadores dentro del quinteto 2:', team2_listNames_players)
selected_team2_players_out = st.sidebar.multiselect('Jugadores fuera del quinteto 2:', team2_listNames_players)

if len(selected_team2_players_in) > 0:
    for selected_player in selected_team2_players_in:
        df_statFives_team2 = df_statFives_team2[df_statFives_team2['name_five'].str.contains(selected_player)]
else:
    selected_team2_players_in.append('-')
TextPlayersIn_team2 = " - ".join(str(element) for element in selected_team2_players_in)

if len(selected_team2_players_out) > 0:
    for selected_player in selected_team2_players_out:
        df_statFives_team2 = df_statFives_team2[~df_statFives_team2['name_five'].str.contains(selected_player)]
else:
    selected_team2_players_out.append('-')
TextPlayersOut_team2 = " - ".join(str(element) for element in selected_team2_players_out)

GAMES_PLAYED_TEAM2 = len(pd.unique(df_statFives_team2['id_match']))
MINUTES_PLAYED_TEAM2 = (df_statFives_team2['second_gameOut'].sum() - df_statFives_team2['second_gameIn'].sum()) / 60
T2IN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 't2in'].shape[0]
T2OUT_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 't2out'].shape[0]
T3IN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 't3in'].shape[0]
T3OUT_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 't3out'].shape[0]
T1IN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 't1in'].shape[0]
T1OUT_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 't1out'].shape[0]
TURN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'turn'].shape[0]
REB_OF_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'rebO'].shape[0]
RIVAL_T2IN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_t2in'].shape[0]
RIVAL_T3IN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_t3in'].shape[0]
RIVAL_T1IN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_t1in'].shape[0]
RIVAL_T2OUT_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_t2out'].shape[0]
RIVAL_T3OUT_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_t3out'].shape[0]
RIVAL_T1OUT_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_t1out'].shape[0]
RIVAL_TURN_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_turn'].shape[0]
RIVAL_REB_OF_TEAM2 = df_statFives_team2[df_statFives_team2['id_playbyplaytype'] == 'r_rebO'].shape[0]
POS_TEAM2 = 0.96*((T2IN_TEAM2+T2OUT_TEAM2+T3IN_TEAM2+T3OUT_TEAM2) + TURN_TEAM2 + 0.44*(T1IN_TEAM2+T1OUT_TEAM2-REB_OF_TEAM2))
RIVAL_POS_TEAM2 = 0.96*((RIVAL_T2IN_TEAM2+RIVAL_T2OUT_TEAM2+RIVAL_T3IN_TEAM2+RIVAL_T3OUT_TEAM2) + RIVAL_TURN_TEAM2 + 0.44*(RIVAL_T1IN_TEAM2+RIVAL_T1OUT_TEAM2-RIVAL_REB_OF_TEAM2))
OFF_EF_TEAM2 = 100*((2*T2IN_TEAM2 + 3*T3IN_TEAM2 + T1IN_TEAM2)/POS_TEAM2)
DEF_EF_TEAM2 = -100*((2*RIVAL_T2IN_TEAM2 + 3*RIVAL_T3IN_TEAM2 + RIVAL_T1IN_TEAM2)/RIVAL_POS_TEAM2)
NET_EF_TEAM2 = OFF_EF_TEAM2 + DEF_EF_TEAM2
RITMO_TEAM2 = POS_TEAM2/float(MINUTES_PLAYED_TEAM2)*40 if MINUTES_PLAYED_TEAM2>0 else 0
MINUTES_PLAYED_TEAM2 = round(MINUTES_PLAYED_TEAM2, 0)


DF =  pd.DataFrame([[selected_team1, TextPlayersIn_team1, TextPlayersOut_team1, GAMES_PLAYED_TEAM1, MINUTES_PLAYED_TEAM1, OFF_EF_TEAM1, DEF_EF_TEAM1, NET_EF_TEAM1, RITMO_TEAM1],
                    [selected_team2, TextPlayersIn_team2, TextPlayersOut_team2, GAMES_PLAYED_TEAM2, MINUTES_PLAYED_TEAM2, OFF_EF_TEAM2, DEF_EF_TEAM2, NET_EF_TEAM2, RITMO_TEAM2]],
                    columns = ['TEAM', 'IN', 'OUT', 'PJ', 'MINS', 'OFF RATING', 'DEF RATING', 'NET RATING', 'RITMO'],
                    index = ['Q1', 'Q2'])

# PRINCIPAL PAGE
    
colMain1, colMain2= st.columns([6, 2])
with colMain1:
    htmlTittleMain='''
    <p style="font-type: Buffalo; margin-left: 60px; margin-top: 25px; font-size: 60px; color: #3A6743">DATA4BASKET</p>
    '''
    st.markdown(htmlTittleMain, unsafe_allow_html=True)
with colMain2:
    st.image('in/logo_data4basket.jpg')

HEADER = "COMBINACIÓN DE JUGADORES: "
st.title(HEADER)

#list_stats = []
#selected_stats = st.sidebar.multiselect('Estadísticas a comparar: ', list_stats)


colMain1_1, colMain1_2= st.columns([1, 1])

with colMain1_1:
    st.title('Quinteto 1:')
    Text1_team1 = 'Equipo: ' + str(selected_team1)
    st.text(Text1_team1)
    sub1_colMain1_1, sub2_colMain1_1= st.columns([1, 1])
    with sub1_colMain1_1:
        st.image(teamFoto1)
    st.text('Jugadores dentro del quinteto: ')
    #html_PlayersIn_team1='<p style="font-weight: bold; margin-left: auto; margin-right: 0; font-size: 60px; color: black">'+ TextPlayersIn_team1 +'</p>'
    st.subheader(TextPlayersIn_team1)
    st.text('Jugadores fuera del quinteto: ')
    st.subheader(TextPlayersOut_team1)

with colMain1_2:
    st.title('Quinteto 2:')
    Text1_team2 = 'Equipo: ' + str(selected_team2)
    st.text(Text1_team2)
    sub1_colMain1_2, sub2_colMain1_2= st.columns([1, 1])
    with sub2_colMain1_2:
        st.image(teamFoto2)
    st.text('Jugadores dentro del quinteto: ')
    st.subheader(TextPlayersIn_team2)
    st.text('Jugadores fuera del quinteto: ')
    st.subheader(TextPlayersOut_team2)

HEADER1 = "COMPARACIÓN"
st.header(HEADER1)

range_PJ = DF['PJ'].max()
range_Minutos = DF['MINS'].max()
range_Ritmo = DF['RITMO'].max()
range_Off_rating = DF['OFF RATING'].max()
range_Def_rating = DF['DEF RATING'].min()
range_Net_rating = DF['NET RATING'].max()


def color_PJ(val):
    color = 'green' if val>=range_PJ  else 'red'
    return f'color: {color}'

def color_Minutos(val):
    color = 'green' if val>=range_Minutos  else 'red'
    return f'color: {color}'

def color_Ritmo(val):
    color = 'green' if val>=range_Ritmo  else 'red'
    return f'color: {color}'

def color_Off_rating(val):
    color = 'green' if val>=range_Off_rating  else 'red'
    return f'color: {color}'

def color_Def_rating(val):
    color = 'red' if val<=range_Def_rating  else 'green'
    return f'color: {color}'

def color_Net_rating(val):
    color = 'green' if val>=range_Net_rating  else 'red'
    return f'color: {color}'


st.dataframe(DF
             .style.format({"OFF RATING": "{:.2f}".format, "DEF RATING": "{:.2f}".format, "NET RATING": "{:.2f}".format, "POS": "{:.0f}".format})
             .applymap(color_PJ, subset=['PJ'])
             .applymap(color_Minutos, subset=['MINS'])
             .applymap(color_Ritmo, subset=['RITMO'])
             .applymap(color_Off_rating, subset=['OFF RATING'])
             .applymap(color_Def_rating, subset=['DEF RATING'])
             .applymap(color_Net_rating, subset=['NET RATING'])
            )

range_Ritmo = round(range_Ritmo, 1)
range_Off_rating = round(range_Off_rating, 2)
range_Def_rating = round(range_Def_rating, 2)
range_Net_rating = round(range_Net_rating, 2)

categories = [f'Eficiencia Ofensiva ({range_Off_rating})', f'Eficiencia Defensiva ({range_Def_rating})', f'Eficiencia Neta ({range_Net_rating})', f'Partidos Jugados ({range_PJ})', f'Minutos ({range_Minutos})', f'Ritmo ({range_Ritmo})']

range_Net_rating = range_Net_rating +100
ranges = [range_Off_rating, range_Def_rating, range_Net_rating, range_PJ, range_Minutos, range_Ritmo]

all_averages_team1 = [OFF_EF_TEAM1, DEF_EF_TEAM1, (NET_EF_TEAM1+100), GAMES_PLAYED_TEAM1, MINUTES_PLAYED_TEAM1, RITMO_TEAM1]
all_averages_team2 = [OFF_EF_TEAM2, DEF_EF_TEAM2, (NET_EF_TEAM2+100), GAMES_PLAYED_TEAM2, MINUTES_PLAYED_TEAM2, RITMO_TEAM2]
for idx, value in enumerate(ranges):
    if idx == 0: # Offensive Rating
        if all_averages_team1[idx] > all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = (all_averages_team2[idx] - (ranges[idx]-(all_averages_team2[idx] - 15)))/ranges[idx]
            #print('A1: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
        elif all_averages_team1[idx] == all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
        else:
            all_averages_team1[idx] = (all_averages_team1[idx] - (ranges[idx]-(all_averages_team1[idx] - 15)))/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
            #print('A2: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
    elif idx == 1: # Deffensive Rating
        if all_averages_team1[idx] > all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = (all_averages_team2[idx] - (ranges[idx]-(all_averages_team2[idx] + 15)))/ranges[idx]
            #print('B1: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
        elif all_averages_team1[idx] == all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
        else:
            all_averages_team1[idx] = (all_averages_team1[idx] - (ranges[idx]-(all_averages_team1[idx] + 15)))/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
            #print('B2: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
    elif idx == 2: # Net Rating
        if all_averages_team1[idx] > all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = (all_averages_team2[idx] - (ranges[idx]-(all_averages_team2[idx] - 15)))/ranges[idx]
            #print('C1: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
        elif all_averages_team1[idx] == all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
        else:
            all_averages_team1[idx] = (all_averages_team1[idx] - (ranges[idx]-(all_averages_team1[idx] - 15)))/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
            #print('C2: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
    elif idx == 5: # Ritmo
        if all_averages_team1[idx] > all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = (all_averages_team2[idx] - (ranges[idx]-(all_averages_team2[idx] - 15)))/ranges[idx]
            #print('C1: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
        elif all_averages_team1[idx] == all_averages_team2[idx]:
            all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
        else:
            all_averages_team1[idx] = (all_averages_team1[idx] - (ranges[idx]-(all_averages_team1[idx] - 15)))/ranges[idx]
            all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]
            #print('C2: ', all_averages_team1[idx], ' - ', all_averages_team2[idx])
    else:
        all_averages_team1[idx] = all_averages_team1[idx]/ranges[idx]
        all_averages_team2[idx] = all_averages_team2[idx]/ranges[idx]

fig = go.Figure()

name_quinteto1 ='Quinteto 1. IN:' + TextPlayersIn_team1 + '.  OUT: ' + TextPlayersOut_team1
fig.add_trace(go.Scatterpolar(
      r=all_averages_team1,
      theta=categories,
      fill='toself',
      name=name_quinteto1,
      marker_color = 'blue'
))

name_quinteto2 ='Quinteto 2. IN:' + TextPlayersIn_team2 + '.  OUT: ' + TextPlayersOut_team2
fig.add_trace(go.Scatterpolar(
      r=all_averages_team2,
      theta=categories,
      fill='toself',
      name=name_quinteto2,
      marker_color = 'orange'
))
fig.update_polars(radialaxis=dict(visible=False,range=[0, 1]))

st.plotly_chart(fig, use_container_width=True)



if selected_team1 == selected_team2:
    HEADER3 = "COMBINACIONES POR PARTIDO"
    st.header(HEADER3)

    list_games = list(set(df_statFives_team1['start_date'].to_list() + df_statFives_team2['start_date'].to_list()))

    obj_team1 = {}
    obj_team2 = {}
    for date in list_games:
        date_only = date[0:10]

        df_game1 = df_statFives_team1[df_statFives_team1['start_date'] == date]
        MINUTES_PLAYED_TEAM1 = (df_game1['second_gameOut'].sum() - df_game1['second_gameIn'].sum()) / 60
        T2IN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 't2in'].shape[0]
        T2OUT_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 't2out'].shape[0]
        T3IN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 't3in'].shape[0]
        T3OUT_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 't3out'].shape[0]
        T1IN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 't1in'].shape[0]
        T1OUT_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 't1out'].shape[0]
        TURN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'turn'].shape[0]
        REB_OF_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'rebO'].shape[0]
        RIVAL_T2IN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_t2in'].shape[0]
        RIVAL_T3IN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_t3in'].shape[0]
        RIVAL_T1IN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_t1in'].shape[0]
        RIVAL_T2OUT_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_t2out'].shape[0]
        RIVAL_T3OUT_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_t3out'].shape[0]
        RIVAL_T1OUT_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_t1out'].shape[0]
        RIVAL_TURN_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_turn'].shape[0]
        RIVAL_REB_OF_TEAM1 = df_game1[df_game1['id_playbyplaytype'] == 'r_rebO'].shape[0]
        POS_TEAM1 = 0.96*((T2IN_TEAM1+T2OUT_TEAM1+T3IN_TEAM1+T3OUT_TEAM1) + TURN_TEAM1 + 0.44*(T1IN_TEAM1+T1OUT_TEAM1-REB_OF_TEAM1))
        RIVAL_POS_TEAM1 = 0.96*((RIVAL_T2IN_TEAM1+RIVAL_T2OUT_TEAM1+RIVAL_T3IN_TEAM1+RIVAL_T3OUT_TEAM1) + RIVAL_TURN_TEAM1 + 0.44*(RIVAL_T1IN_TEAM1+RIVAL_T1OUT_TEAM1-RIVAL_REB_OF_TEAM1))
        OFF_EF_TEAM1 = 100*((2*T2IN_TEAM1 + 3*T3IN_TEAM1 + T1IN_TEAM1)/POS_TEAM1) if POS_TEAM1 > 0 else 0
        DEF_EF_TEAM1 = -100*((2*RIVAL_T2IN_TEAM1 + 3*RIVAL_T3IN_TEAM1 + RIVAL_T1IN_TEAM1)/RIVAL_POS_TEAM1) if RIVAL_POS_TEAM1 > 0 else 0
        NET_EF_TEAM1 = OFF_EF_TEAM1 + DEF_EF_TEAM1
        RITMO_TEAM1 = POS_TEAM1/float(MINUTES_PLAYED_TEAM1)*40 if MINUTES_PLAYED_TEAM1>0 else 0
        MINUTES_PLAYED_TEAM1 = round(MINUTES_PLAYED_TEAM1, 0)

        obj_team1[date_only] = {
                            'MINS': MINUTES_PLAYED_TEAM1,
                            'RITMO': RITMO_TEAM1,
                            'OFF RATING': OFF_EF_TEAM1,
                            'DEF RATING': DEF_EF_TEAM1,
                            'NET RATING': NET_EF_TEAM1,
                            'DATE': date_only
                           }
        
        df_game2 = df_statFives_team2[df_statFives_team2['start_date'] == date]
        MINUTES_PLAYED_TEAM2 = (df_game2['second_gameOut'].sum() - df_game2['second_gameIn'].sum()) / 60
        T2IN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 't2in'].shape[0]
        T2OUT_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 't2out'].shape[0]
        T3IN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 't3in'].shape[0]
        T3OUT_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 't3out'].shape[0]
        T1IN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 't1in'].shape[0]
        T1OUT_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 't1out'].shape[0]
        TURN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'turn'].shape[0]
        REB_OF_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'rebO'].shape[0]
        RIVAL_T2IN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_t2in'].shape[0]
        RIVAL_T3IN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_t3in'].shape[0]
        RIVAL_T1IN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_t1in'].shape[0]
        RIVAL_T2OUT_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_t2out'].shape[0]
        RIVAL_T3OUT_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_t3out'].shape[0]
        RIVAL_T1OUT_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_t1out'].shape[0]
        RIVAL_TURN_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_turn'].shape[0]
        RIVAL_REB_OF_TEAM2 = df_game2[df_game2['id_playbyplaytype'] == 'r_rebO'].shape[0]
        POS_TEAM2 = 0.96*((T2IN_TEAM2+T2OUT_TEAM2+T3IN_TEAM2+T3OUT_TEAM2) + TURN_TEAM2 + 0.44*(T1IN_TEAM2+T1OUT_TEAM2-REB_OF_TEAM2))
        RIVAL_POS_TEAM2 = 0.96*((RIVAL_T2IN_TEAM2+RIVAL_T2OUT_TEAM2+RIVAL_T3IN_TEAM2+RIVAL_T3OUT_TEAM2) + RIVAL_TURN_TEAM2 + 0.44*(RIVAL_T1IN_TEAM2+RIVAL_T1OUT_TEAM2-RIVAL_REB_OF_TEAM2))
        OFF_EF_TEAM2 = 100*((2*T2IN_TEAM2 + 3*T3IN_TEAM2 + T1IN_TEAM2)/POS_TEAM2) if POS_TEAM2 > 0 else 0
        DEF_EF_TEAM2 = -100*((2*RIVAL_T2IN_TEAM2 + 3*RIVAL_T3IN_TEAM2 + RIVAL_T1IN_TEAM2)/RIVAL_POS_TEAM2) if RIVAL_POS_TEAM2 > 0 else 0
        NET_EF_TEAM2 = OFF_EF_TEAM2 + DEF_EF_TEAM2
        RITMO_TEAM2 = POS_TEAM2/float(MINUTES_PLAYED_TEAM2)*40 if MINUTES_PLAYED_TEAM2>0 else 0
        MINUTES_PLAYED_TEAM2 = round(MINUTES_PLAYED_TEAM2, 0)

        obj_team2[date_only] = {
                            'MINS': MINUTES_PLAYED_TEAM2,
                            'RITMO': RITMO_TEAM2,
                            'OFF RATING': OFF_EF_TEAM2,
                            'DEF RATING': DEF_EF_TEAM2,
                            'NET RATING': NET_EF_TEAM2,
                            'DATE': date_only
                           }
        
    DF_teamEvoluting_1 = pd.DataFrame(obj_team1).transpose()
    DF_teamEvoluting_1['start_date'] = pd.to_datetime(DF_teamEvoluting_1['DATE'], format='%d-%m-%Y')
    DF_teamEvoluting_1 = DF_teamEvoluting_1.sort_values(by='start_date', ascending=True)
    DF_teamEvoluting_1['start_date_inversed'] = pd.to_datetime(DF_teamEvoluting_1['DATE'], format='%Y-%m-%d')
    DF_teamEvoluting_2 = pd.DataFrame(obj_team2).transpose()
    DF_teamEvoluting_2['start_date'] = pd.to_datetime(DF_teamEvoluting_2['DATE'], format='%d-%m-%Y')
    DF_teamEvoluting_2 = DF_teamEvoluting_2.sort_values(by='start_date', ascending=True)
    DF_teamEvoluting_2['start_date_inversed'] = pd.to_datetime(DF_teamEvoluting_2['DATE'], format='%Y-%m-%d')
    list_game_dates = list(set(DF_teamEvoluting_1['DATE'].to_list()+DF_teamEvoluting_2['DATE'].to_list()))
    list_resultsTeams = []
    list_stat_a_visualizar = ['NET RATING', 'OFF RATING', 'DEF RATING', 'MINS', 'POS',]
    selected_stat_a_visualizar = st.selectbox('Estadística a visualizar: ', list_stat_a_visualizar)
    for date in list_game_dates:
        date_inversed1 = 0    
        DF_teamEvoluting_1alone = DF_teamEvoluting_1[DF_teamEvoluting_1['DATE'] == date].reset_index()
        if DF_teamEvoluting_1alone.shape[0] > 0:
            value_team1 = round(DF_teamEvoluting_1alone[selected_stat_a_visualizar][0], 1)
            date_inversed1 = DF_teamEvoluting_1alone['start_date_inversed'][0]
        else:
            value_team1 = 0

        DF_teamEvoluting_2alone = DF_teamEvoluting_2[DF_teamEvoluting_2['DATE'] == date].reset_index()
        if DF_teamEvoluting_2alone.shape[0] > 0:
            value_team2 = round(DF_teamEvoluting_2alone[selected_stat_a_visualizar][0], 1)
            if date_inversed1 != 0:
                date_inversed = date_inversed1
            else:
                date_inversed = DF_teamEvoluting_2alone['start_date_inversed'][0]
        else:
            value_team2 = 0
        list_resultsTeams.append([date, value_team1, name_quinteto1, date_inversed])
        list_resultsTeams.append([date, value_team2, name_quinteto2, date_inversed])
    DF_teamEvoluting = pd.DataFrame(list_resultsTeams, columns = ['PARTIDOS', selected_stat_a_visualizar, 'Quintetos', 'date_inversed']).sort_values(by='PARTIDOS',ascending=True)

    fig = px.line(DF_teamEvoluting, x="PARTIDOS", y=selected_stat_a_visualizar, color='Quintetos', text=selected_stat_a_visualizar)
    fig.update_traces(textposition="bottom right")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)
