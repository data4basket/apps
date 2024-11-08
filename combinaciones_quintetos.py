import numpy as np
import pandas as pd
import streamlit as st

import numpy as np
import matplotlib.pyplot as plt

from crear_visualizacion import *
from main_stats_generar import *
from conexiones_bbdd import *
from main_graphics_creations import *



# Inject custom CSS to set the width of the sidebar
st.markdown(
    """
    <style>
        .stJson{
            display: none !important;
        }
        .stMainBlockContainer {
            max-width: 70rem !important;
            padding: 1rem 1rem 10rem !important;
        }
        section[data-testid="stSidebar"] {
            width: 23% !important; # Set the width to your desired value
        }
        button {
            background-color: #00FF00;
        }
        h1 {
            text-align: center
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# SIDEBAR
colSide1, colSide2= st.sidebar.columns([2, 5])
with colSide1:
    st.image('in/logo_data4basket.png')
with colSide2:
    htmlTittleSide='''
    <p style="font-type: Buffalo; margin-top: 15px; font-size: 30px; color: #3A6743; text-align: center">DATA4BASKET</p>
    '''
    st.markdown(htmlTittleSide, unsafe_allow_html=True)

list_colors = ['blue', '#fa07e6', '#ccc902', '#03fcf4', '#8406ba']
obj_colors_background = {'Quinteto 1': '#b1bffa', 'Quinteto 2': '#fcc7f8', 'Quinteto 3': '#f0efa8', 'Quinteto 4': '#b3f5f3', 'Quinteto 5': '#e9c6f7'}

df_competiciones = buscarCompeticiones()
list_ligas_disponiblesName = list(set(df_competiciones['name'].to_list()))
list_years_disponiblesName = list(set(df_competiciones['year'].to_list()))
list_years_disponiblesName.sort(reverse=True)

# Configuración
selected_number_quintetos = st.sidebar.slider('Número de quintetos a comparar:', 
                                         min_value=1, max_value=5, value=2, step=1)



LIST_QUINTETOS_TODOS = []

for i in range(selected_number_quintetos):
    OBJ_QUINTETO = {}
    n_quinteto = i + 1
    st.sidebar.title('Quinteto ' + str(n_quinteto) + ':')
    col1, col2 = st.sidebar. columns([5,4])
    with col1:
        selected_liga = st.selectbox('Liga:', list_ligas_disponiblesName, key='Liga_'+ str(n_quinteto))
        selected_liga_id = df_competiciones[df_competiciones['name'] == selected_liga].reset_index()['id_competition'][0]

    with col2:
        selected_year = st.selectbox('Año:', list_years_disponiblesName, key='Año_'+ str(n_quinteto))
        selected_year_id = df_competiciones[df_competiciones['year'] == selected_year].reset_index()['id_edition'][0]

    df_teams = buscarEquipos(selected_liga_id, selected_year_id)
    list_teams = sorted(df_teams['team_name'].to_list())
    selected_team = st.sidebar.selectbox('Equipo:', list_teams, index=n_quinteto, key='Equipo_'+ str(n_quinteto))
    id_team = df_teams[df_teams['team_name'] == selected_team].reset_index()['id_team'][0]
    teamFoto = df_teams[df_teams['id_team'] == id_team].reset_index()['image'][0]
    # Buscar Jugadores del Quinteto:
    df_team_players = buscarJugadores(id_team)
    team_listNames_players = df_team_players['name_nick'].to_list()

    selected_team_players_in = st.sidebar.multiselect('Jugadores IN quinteto:', team_listNames_players, key='IN_'+ str(n_quinteto))
    selected_team_players_out = st.sidebar.multiselect('Jugadores OUT quinteto:', team_listNames_players, key='OUT_'+ str(n_quinteto))

    OBJ_QUINTETO = {
                        'id_competition': selected_liga_id,
                        'competition_name': selected_liga,
                        'id_edition': selected_year_id,
                        'year': selected_year,
                        'id_team': id_team,
                        'team_name': selected_team,
                        'team_image': teamFoto,
                        'players_IN': selected_team_players_in,
                        'players_OUT': selected_team_players_out       
                    }
    LIST_QUINTETOS_TODOS.append(OBJ_QUINTETO)
    #inicio = time.time()
    #df_statFives_team = buscarStatFives(id_team)
    #fin = time.time()
    #st.sidebar.text(str(fin-inicio))


      

def PROCESAR():
    st.session_state.disabled = True

    # Inject custom CSS to set the width of the sidebar
    st.markdown(
        """
        <style>
            .stMainBlockContainer {
                max-width: 70rem !important;
            padding: 1rem 1rem 10rem !important;
            }
            section[data-testid="stSidebar"] {
                width: 23% !important; # Set the width to your desired value
            }
            button {
                background-color: #00FF00;
            }
            h1 {
                text-align: center
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    list_fives_df = []
    list_index_fives_df = []
    for j in range(selected_number_quintetos):
        df_statFives_team = buscarStatFives(LIST_QUINTETOS_TODOS[j]['id_team'], LIST_QUINTETOS_TODOS[j]['players_IN'], LIST_QUINTETOS_TODOS[j]['players_OUT'])

        TextPlayersIn_team1 = " - ".join(str(element) for element in LIST_QUINTETOS_TODOS[j]['players_IN'])
        TextPlayersOut_team1 = " - ".join(str(element) for element in LIST_QUINTETOS_TODOS[j]['players_OUT'])

        list_five_out = []
        list_five_out = crearBucleFor_teams_fromEvents(df_statFives_team, list_selected_stats, list_five_out, modo_metricas, list_stats_a40mins)[0]

        players_in_string = ''
        for p_in in range(len(LIST_QUINTETOS_TODOS[j]['players_IN'])):
            if p_in == 0:
                players_in_string = players_in_string + LIST_QUINTETOS_TODOS[j]['players_IN'][p_in]
            else:
                players_in_string = players_in_string + " + " + LIST_QUINTETOS_TODOS[j]['players_IN'][p_in]
        players_out_string = ''
        for p_out in range(len(LIST_QUINTETOS_TODOS[j]['players_OUT'])): 
            if p_out == 0:
                players_out_string = players_out_string + LIST_QUINTETOS_TODOS[j]['players_OUT'][p_out]
            else:
                players_out_string = players_out_string + " + " + LIST_QUINTETOS_TODOS[j]['players_OUT'][p_out]

        list_five_out.insert(0, players_out_string)
        list_five_out.insert(0, players_in_string)
        list_five_out.insert(0, LIST_QUINTETOS_TODOS[j]["team_name"]+" "+LIST_QUINTETOS_TODOS[j]["year"][2:])

        list_fives_df.append(list_five_out)
        list_index_fives_df.append('Quinteto ' + str(j+1))


    list_selected_stats.insert(0, "JUG. OUT")
    list_selected_stats.insert(0, "JUG. IN")
    list_selected_stats.insert(0, "EQUIPO")

    DF =  pd.DataFrame(list_fives_df,
                        columns = list_selected_stats,
                        index = list_index_fives_df)
    

    st.session_state.procesado = True
    st.session_state.results = DF.transpose()


    
# PRINCIPAL PAGE

HEADER = "COMPARADOR RENDIMIENTO DE QUINTETOS: "
st.title(HEADER)

st.text("")

list_stats_basicas = ["PJ", "MIN", "Nº POS", "PTS","RT", "AST", "REC", "PERD", "VAL", "+-"]
list_stats_basicas_rival = ["PJ", "MIN", "Nº POS rival", "PTS rival","RT rival", "AST rival", "REC rival", "PERD rival", "VAL rival", "+-"]

list_stats_ofensivas = ["PJ", "MIN", "Nº POS", "PTS/POS","%EFG", "EF.OF", "%REB.OF", "%AST", "%PERD", "AST/PERD", "FREC.TL", "%PLAY"]
list_stats_defensivas = ["PJ", "MIN", "Nº POS", "PTS/POS rival","%EFG rival", "EF.DEF", "%REB.DEF", "%AST rival", "%REC", "AST/PERD rival", "%TAP", "FREC.TL rival", "%PLAY rival"]
list_stats_avanzadas = ["PJ", "MIN", "Nº POS", "RITMO","%EFG", "EF.OF", "EF.DEF", "EF.NETA", "%REB", "%REB.DEF", "%REB.OF", "%AST", "%REC", "%PERD", "AST/PERD"]
list_PosibleStats_personalizadas =  list(set(list_stats_basicas + list_stats_basicas_rival + list_stats_ofensivas + list_stats_defensivas + list_stats_avanzadas))

list_stats_a40mins = ["Nº POS", "PTS", "T2A", "T2I", "%T2", "T3A", "T3I", "%T3", "TLA", "TLI", "%TL", "RD", "RO","RT", "AST", "REC", "PERD", "TF", "TC", "FC", "FR", "VAL",  "+-", "Nº POS rival", "PTS rival","RT rival", "AST rival", "REC rival", "PERD rival", "VAL rival"]

list_stats_inversas = ["PERD", "TC", "FR", "PTS rival","RT rival", "AST rival", "REC rival", "VAL rival", "%PERD", "PTS/POS rival","%EFG rival", "%AST rival", "AST/PERD rival", "FREC.TL rival", "%PLAY rival"]


obj_type_stats = {
                    '***Básicas Equipo***': list_stats_basicas,
                    '***Básicas Recibidas***': list_stats_basicas_rival,
                    '***Ofensivas***': list_stats_ofensivas,
                    '***Defensivas***': list_stats_defensivas,
                    '***Avanzadas***': list_stats_avanzadas,
                    '***Personalizadas*** :movie_camera:': list_PosibleStats_personalizadas
                }

colMain1, colMain2= st.columns([1, 1])
with colMain1:
    selected_type_stats = st.radio(
                            "SELECCIONA LAS MÉTRICAS A COMPARAR",
                            ["***Básicas Equipo***", "***Básicas Recibidas***", "***Ofensivas***", "***Defensivas***", "***Avanzadas***", "***Personalizadas*** :movie_camera:"],
                            index=2,               
                        )
    list_posible_stats = obj_type_stats[selected_type_stats]  

with colMain2:
    if selected_type_stats != "***Personalizadas*** :movie_camera:": 
        list_selected_stats = st.multiselect(
                                    "MÉTRICAS SELECCIONADAS: ",
                                    list_posible_stats,
                                    list_posible_stats,
                                    disabled=True
                                )
    else:
        if st.session_state.get("list_selected_stats", False):
            list_selected_statsAnt = st.session_state.list_selected_stats
        else:
            list_selected_statsAnt = list_posible_stats
        list_selected_stats = st.multiselect(
                                    "MÉTRICAS SELECCIONADAS: ",
                                    list_posible_stats,
                                    list_selected_statsAnt,
                                    disabled=False
                                )
    st.session_state.list_selected_stats = list_selected_stats.copy()

    modo_metricas = st.radio("***MODO MÉTRICAS***",
                                              options=[
                                                        "Totales",
                                                        "A 40 minutos de juego (por partido)"
                                                    ])

st.text("")

colMainB1, colMainB2, colMainB3= st.columns([2, 8, 2])
with colMainB1:
    st.text("")
with colMainB2:
    procesar_button = st.button("PROCESAR...", type="primary", icon="🔥", key = 'procesar_button', disabled = st.session_state.get("disabled", False), use_container_width=True, on_click=PROCESAR)
with colMainB3:
    st.text("")


def make_maxHighland(s):
    if s.name in ["EQUIPO", "JUG. IN", "JUG. OUT"]: 
        is_max = [False for _ in range(s.shape[0])] 
    else: 
        if s.name in list_stats_inversas:
            is_max = s == s.min()
        else:
            is_max = s == s.max()
    if s.max() == s.min():
        return ['' if cell else '' for cell in is_max] 
    else:
        return ['background-color: lightgreen' if cell else '' for cell in is_max] 

def make_minHighland(s):
    if s.name in ["EQUIPO", "JUG. IN", "JUG. OUT"]: 
        return ['background-color: ' + obj_colors_background[s[s == cell].index[0]] if cell != '' else '' for cell in s]
    else: 
        if s.name in list_stats_inversas:
            is_min = s == s.max()
        else:
            is_min = s == s.min()
        if s.max() == s.min():
            return ['' if cell else '' for cell in is_min] 
        else:
            return ['background-color: #fabbb1' if cell else '' for cell in is_min] 



if st.session_state.get("procesado", False):
    st.session_state.procesado = False
    DF = st.session_state.results

    list_variables = DF.index.to_list()
    if modo_metricas != 'Totales':
            list_variables_a40mins = []
            for met in range(len(list_variables)):
                if list_variables[met] in list_stats_a40mins:
                    new_name_a40mins = list_variables[met] + " por 40'"
                else:
                    new_name_a40mins = list_variables[met]
                list_variables_a40mins.append(new_name_a40mins)
    else:
        list_variables_a40mins = list_variables
    DF.index = list_variables_a40mins

    colMain1, colMain2= st.columns([1, 1])
    with colMain1:
                
        st.dataframe(DF.style.apply(make_maxHighland, axis=1)
                     .apply(make_minHighland, axis=1)
                     .format(precision=1, thousands=".", decimal=","),
                     #.apply(make_pretty, axis=1),
                        #.highlight_max(axis=1, color = '#a7fcb5')
                        #.highlight_min(axis=1, color = '#fca7a7'),
                       # .set_properties(**{'text-align': 'center'}),
                    height= int(35.2*(DF.shape[0]+1)) ,
                    column_config = {'width': 'small'},
                    use_container_width = True)
        
    with colMain2:
        DF_DROP = DF.copy()
        DF_DROP.drop(['EQUIPO','JUG. IN','JUG. OUT'], axis=0, inplace=True)
        DF_PLOT= DF_DROP.T

        ## Mover la 1º columna con valores distintos al principio
        for index, row in DF_DROP.iterrows():
            unique_values = row.unique()
            if len(unique_values) >1:
                break
        DF_PLOT = DF_PLOT[[index] + [col for col in DF_PLOT.columns if col != index]]
        DF_DROP= DF_PLOT.T

        list_variables = DF_PLOT.columns.to_list()
        if modo_metricas != 'Totales':
            list_variables_a40mins = []
            for met in range(len(list_variables)):
                if list_variables[met] in list_stats_a40mins:
                    new_name_a40mins = list_variables[met] + " por 40'"
                else:
                    new_name_a40mins = list_variables[met]
                list_variables_a40mins.append(new_name_a40mins)
        else:
            list_variables_a40mins = list_variables
        DF_PLOT.columns = list_variables_a40mins

        ranges = []
        for index, row in DF_DROP.iterrows():
            max = row.max()
            min = row.min()
            media = abs(0.1*max)        
            if index in list_stats_inversas:
                ranges.append((max +media, min -media))
            else:
                ranges.append((min -media, max +media))

        fig1 = plt.figure(figsize=(6, 6))
        #fig1.suptitle('NonUniformImage class', fontsize='large')
        radar = ComplexRadar(fig1, list_variables_a40mins, ranges)


        k= 0
        for index, row in DF_PLOT.iterrows():
            JUG_IN = DF[index]['JUG. IN']
            JUG_OUT = DF[index]['JUG. OUT']
            txt_JUG_IN = '     * IN: ' + JUG_IN if JUG_IN != '' else ''
            txt_JUG_OUT = '     * OUT: ' + JUG_OUT if JUG_OUT != '' else ''
            legend = DF[index]['EQUIPO']   + " : " + txt_JUG_IN + txt_JUG_OUT
            data = []
            for var in list_variables_a40mins:
                data.append(row[var])
            radar.plot(data, legend, selected_number_quintetos, color=list_colors[k])
            radar.fill(data, alpha=0.2, color=list_colors[k])
            k = k+1
        
        st.pyplot(fig1, use_container_width=True)

        
st.session_state.disabled = False
