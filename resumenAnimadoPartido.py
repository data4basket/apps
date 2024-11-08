import pandas as pd


import os
import streamlit as st

from crear_visualizacion import *
from main_stats_generar import *
from conexiones_bbdd import *
from main_graphics_creations import *



# Inject custom CSS to set the width of the sidebar
st.markdown(
    """
    <style>
        .stMainBlockContainer {
            max-width: 90rem !important;
            padding: 10rem 10rem 10rem !important;
        section[data-testid="stSidebar"] {
            width: 23% !important; # Set the width to your desired value
        }
        h1 {
            text-align: center
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Caracteristicas de Jugadores


df_players = buscarJugadoresInfo()
obj_players_name = {x['id_player']: x['name_nick'] for index, x in df_players.iterrows() }
obj_players_image = {x['id_player']: x['image'] for index, x in df_players.iterrows() }
obj_players_image2 = {x['id_player']: x['image_2'] for index, x in df_players.iterrows() }
###############################



df_teams = buscarEquiposInfo()
obj_teams_img = {x['id_team']: x['image_2'] for index, x in df_teams.iterrows() }
obj_teams_name = {x['id_team']: x['abrev_name'] for index, x in df_teams.iterrows() }
obj_teams_nameFull = {x['id_team']: x['team_name'] for index, x in df_teams.iterrows() }
obj_teams_color = {x['id_team']: x['primary_color'] for index, x in df_teams.iterrows() }
obj_teams_color2 = {x['id_team']: x['secondary_color'] for index, x in df_teams.iterrows() }
###############################





def PROCESAR():
    st.session_state.disabled = True

    # Inject custom CSS to set the width of the sidebar
    st.markdown(
        """
        <style>
            .stMainBlockContainer {
                max-width: 90rem !important;
                padding: 10rem 10rem 10rem !important;
            section[data-testid="stSidebar"] {
                width: 23% !important; # Set the width to your desired value
            }
            h1 {
                text-align: center
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.procesado = True

# PRINCIPAL PAGE

HEADER = "ANÁLISIS DE PARTIDOS: "
st.title(HEADER)

st.text("")

st.header("SELECCIONAR PARTIDO:")
colM1, colM2, colM3= st.columns([1, 1, 1])
with colM1:
    selected_liga = st.selectbox("COMPETICIÓN: ", ["LIGA ENDESA 2024/25"])
with colM2:
    DF_JORNADAS = obtener_jornadas()
    lista_jornadas = DF_JORNADAS.columns.to_list()[1:]
    selected_jornada = st.selectbox("JORNADA: ", lista_jornadas, index=len(lista_jornadas)-1)
with colM3:
    obj_games, obj_teams_in_Game = buscar_selected_games(DF_JORNADAS, selected_jornada, obj_teams_nameFull)
    lista_games = list(obj_games.values())
    selected_gameNombre = st.selectbox("Selecciona el partido: ", lista_games)
    selected_game = [clave for clave, valor in obj_games.items() if valor == selected_gameNombre][0]
    list_teams = obj_teams_in_Game[selected_game]
    list_teamsNames = [obj_teams_nameFull[list_teams[0]], obj_teams_nameFull[list_teams[1]]]

st.text("")

analisis_option = st.select_slider(
    "Opción de Análisis",
    options=[
        "Generar Resumen Gráfico",
        "Comparar Equipos",
        "4 Factors",
        "Impacto Jugador en Partido"
    ]
)





st.text("")

if analisis_option == "Generar Resumen Gráfico":
    pass
elif analisis_option == "Comparar Equipos":
    list_stats_basicas, _, list_stats_ofensivas, list_stats_defensivas, list_stats_avanzadas, _, list_stats_a40mins, list_stats_inversas = obtener_statsPosibles_equiposComparar()
    list_PosibleStats_personalizadas =  list(set(list_stats_basicas + list_stats_ofensivas + list_stats_defensivas + list_stats_avanzadas))

    obj_type_stats = {
                        '***Básicas Equipo***': list_stats_basicas,
                        '***Ofensivas***': list_stats_ofensivas,
                        '***Avanzadas***': list_stats_avanzadas,
                        '***Personalizadas*** :movie_camera:': list_PosibleStats_personalizadas
                    }

    colMain1, colMain2= st.columns([1, 1])
    with colMain1:
        selected_type_stats = st.radio(
                                "SELECCIONA LAS MÉTRICAS A COMPARAR",
                                ["***Básicas Equipo***", "***Ofensivas***", "***Avanzadas***", "***Personalizadas*** :movie_camera:"],
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

elif analisis_option == "4 Factors":
    pass
elif analisis_option == "Impacto Jugador en Partido":
    colMain1, colMain2= st.columns([1, 1])
    with colMain1:
        selected_teamImpacto = st.selectbox(
                                "¿DE QUÉ EQUIPO ES EL JUGADOR QUE QUIERES ANALIZAR SU IMPACTO?",
                                list_teamsNames              
                            )
        id_teamImpacto = [clave for clave, valor in obj_teams_nameFull.items() if valor == selected_teamImpacto][0]


    with colMain2:
        df_playerNames_enPartido_equipo = buscarPlayers_dePartido_de1Equipo(selected_game, id_teamImpacto)
        df_playerNames_enPartido_equipo = pd.merge(how='left', left=df_playerNames_enPartido_equipo, left_on="id_player", right=df_players, right_on="id_player")
        obj_players_name_enPartido_equipo = {x['id_player']: x['name_nick'] for index, x in df_playerNames_enPartido_equipo.iterrows() }
        list_playerNames_enPartido_equipo = list(obj_players_name_enPartido_equipo.values())
        selected_playerImpacto = st.selectbox(
                                "SELECCIONA EL JUGADOR:",
                                list_playerNames_enPartido_equipo              
                            )
        selected_IdPlayerImpacto = [clave for clave, valor in obj_players_name_enPartido_equipo.items() if valor == selected_playerImpacto][0]
        objJugadorImpacto = {}
        objJugadorImpacto[selected_IdPlayerImpacto] = id_teamImpacto
        playerImpacto_image = obj_players_image[selected_IdPlayerImpacto]

    list_stats_basicas, _, list_stats_ofensivas, list_stats_defensivas, list_stats_avanzadas, _, list_stats_a40mins, list_stats_inversas = obtener_statsPosibles_equiposComparar()
    list_PosibleStats_personalizadas =  list(set(list_stats_basicas + list_stats_ofensivas + list_stats_defensivas + list_stats_avanzadas))

    obj_type_stats = {
                        '***Básicas Equipo***': list_stats_basicas,
                        '***Ofensivas***': list_stats_ofensivas,
                        '***Avanzadas***': list_stats_avanzadas,
                        '***Personalizadas*** :movie_camera:': list_PosibleStats_personalizadas
                    }

    colMainSB1, colMainSB2= st.columns([1, 1])
    with colMainSB1:
        selected_type_stats = st.radio(
                                "SELECCIONA LAS MÉTRICAS A COMPARAR",
                                ["***Básicas Equipo***", "***Ofensivas***", "***Avanzadas***", "***Personalizadas*** :movie_camera:"],
                                index=2,               
                            )
        list_posible_stats = obj_type_stats[selected_type_stats]  


    with colMainSB2:
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


colMainB1, colMainB2, colMainB3= st.columns([2, 8, 2])
with colMainB1:
    pass
with colMainB2:
    procesar_button = st.button("PROCESAR...", type="primary", icon="🔥", key = 'procesar_button', disabled = st.session_state.get("disabled", False), use_container_width=True, on_click=PROCESAR)
with colMainB3:
    pass


if st.session_state.get("procesado", False):
    st.session_state.procesado = False

    teams_colors = [obj_teams_color[list_teams[0]], 
                    obj_teams_color2[list_teams[1]] if is_color_similar_to_color(obj_teams_color[list_teams[0]], obj_teams_color[list_teams[1]]) else obj_teams_color[list_teams[1]]]

    if analisis_option == "Generar Resumen Gráfico":
        
        # Ejecutar la animación completa y guardar el último cuadro
        if os.path.exists('temp/'+selected_game+'.png'):
            pass
        else:     
            with st.spinner("Generando Análisis Partido..."):
                objJugadorImpacto = {}
                obj_info = crear_resumenAnimadoInfo(objJugadorImpacto,selected_game, list_teams, obj_teams_img, obj_teams_name, obj_teams_nameFull, obj_players_name, teams_colors, obj_players_image,obj_players_image2)
                create_vis_resumenPartido(obj_info,selected_game)

        
        # Cargar y mostrar el video
        if True:
            st.image('temp/'+selected_game+'.png', caption="Resumen "+ selected_gameNombre, use_column_width=True)
        else:
            video_file = open("animacion.mp4", "rb")
            video_bytes = video_file.read()

            st.video(video_bytes)
    elif analisis_option == "Comparar Equipos":
        DF_STATS_COMPARE_TEAMS = generar_stats_for_teams_fromBoxscore(selected_game, list_selected_stats, list_teamsNames, list_teams)

        list_variables = DF_STATS_COMPARE_TEAMS.index.to_list()
        DF_STATS_COMPARE_TEAMS.index = list_variables

        H1 = selected_jornada + " - " + selected_liga + ":\n"
        st.title(H1)
        st.title(list_teamsNames[0] + " - " + list_teamsNames[1])

        if H1:
            colMain1, colMain2= st.columns([1, 1])
            with colMain1:
                        
                st.dataframe(DF_STATS_COMPARE_TEAMS.style.apply(make_maxHighland, axis=1)
                            .apply(make_minHighland, axis=1)
                            .format(precision=1, thousands=".", decimal=","),
                            #.apply(make_pretty, axis=1),
                                #.highlight_max(axis=1, color = '#a7fcb5')
                                #.highlight_min(axis=1, color = '#fca7a7'),
                            # .set_properties(**{'text-align': 'center'}),
                            height= int(35.2*(DF_STATS_COMPARE_TEAMS.shape[0]+1)) ,
                            column_config = {'width': 'small'},
                            use_container_width = True)
                
            with colMain2:
                DF_DROP = DF_STATS_COMPARE_TEAMS.copy()
                DF_PLOT= DF_DROP.T

                ## Mover la 1º columna con valores distintos al principio
                for index, row in DF_DROP.iterrows():
                    unique_values = row.unique()
                    if len(unique_values) >1:
                        break
                DF_PLOT = DF_PLOT[[index] + [col for col in DF_PLOT.columns if col != index]]
                DF_DROP= DF_PLOT.T

                DF_PLOT.columns = list_variables

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
                radar = ComplexRadar(fig1, list_variables, ranges)

                k= 0
                for index, row in DF_PLOT.iterrows():
                    legend = index
                    data = []
                    for var in list_variables:
                        data.append(row[var])
                    radar.plot(data, legend, 2, color=teams_colors[k])
                    radar.fill(data, alpha=0.2, color=teams_colors[k])
                    k = k+1
                
                st.pyplot(fig1, use_container_width=True)
                st.text("")

        H2 = list_teamsNames[0]
        st.title(H2)
        st.title("promedio Liga VS en partido")

        if H2:
            colMain1, colMain2= st.columns([1, 1])
            with colMain1:
                DF_STATS_COMPARE_TEAMS = generar_stats_for_SameTeam_fromBoxscore(selected_game, list_selected_stats, list_teamsNames[0], list_teams[0])

                list_variables = DF_STATS_COMPARE_TEAMS.index.to_list()
                DF_STATS_COMPARE_TEAMS.index = list_variables

                st.dataframe(DF_STATS_COMPARE_TEAMS.style.apply(make_maxHighland, axis=1)
                            .apply(make_minHighland, axis=1)
                            .format(precision=1, thousands=".", decimal=","),
                            #.apply(make_pretty, axis=1),
                                #.highlight_max(axis=1, color = '#a7fcb5')
                                #.highlight_min(axis=1, color = '#fca7a7'),
                            # .set_properties(**{'text-align': 'center'}),
                            height= int(35.2*(DF_STATS_COMPARE_TEAMS.shape[0]+1)) ,
                            column_config = {'width': 'small'},
                            use_container_width = True)
                
            with colMain2:
                DF_DROP = DF_STATS_COMPARE_TEAMS.copy()
                DF_PLOT= DF_DROP.T

                ## Mover la 1º columna con valores distintos al principio
                for index, row in DF_DROP.iterrows():
                    unique_values = row.unique()
                    if len(unique_values) >1:
                        break
                DF_PLOT = DF_PLOT[[index] + [col for col in DF_PLOT.columns if col != index]]
                DF_DROP= DF_PLOT.T

                DF_PLOT.columns = list_variables

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
                radar = ComplexRadar(fig1, list_variables, ranges)

                teams_colors = [obj_teams_color[list_teams[0]], 
                    obj_teams_color2[list_teams[0]]]
                
                k=0

                for index, row in DF_PLOT.iterrows():
                    legend = index
                    data = []
                    for var in list_variables:
                        data.append(row[var])
                    radar.plot(data, legend, 2, color=teams_colors[k])
                    radar.fill(data, alpha=0.2, color=teams_colors[k])
                    k = k+1
                
                st.pyplot(fig1, use_container_width=True)
                st.text("")


        H3 = list_teamsNames[1]
        st.title(H3)
        st.title("promedio Liga VS en partido")

        if H3:
            colMain1, colMain2= st.columns([1, 1])
            with colMain1:
                DF_STATS_COMPARE_TEAMS = generar_stats_for_SameTeam_fromBoxscore(selected_game, list_selected_stats, list_teamsNames[1], list_teams[1])

                list_variables = DF_STATS_COMPARE_TEAMS.index.to_list()
                DF_STATS_COMPARE_TEAMS.index = list_variables

                st.dataframe(DF_STATS_COMPARE_TEAMS.style.apply(make_maxHighland, axis=1)
                            .apply(make_minHighland, axis=1)
                            .format(precision=1, thousands=".", decimal=","),
                            #.apply(make_pretty, axis=1),
                                #.highlight_max(axis=1, color = '#a7fcb5')
                                #.highlight_min(axis=1, color = '#fca7a7'),
                            # .set_properties(**{'text-align': 'center'}),
                            height= int(35.2*(DF_STATS_COMPARE_TEAMS.shape[0]+1)) ,
                            column_config = {'width': 'small'},
                            use_container_width = True)
                
            with colMain2:
                DF_DROP = DF_STATS_COMPARE_TEAMS.copy()
                DF_PLOT= DF_DROP.T

                ## Mover la 1º columna con valores distintos al principio
                for index, row in DF_DROP.iterrows():
                    unique_values = row.unique()
                    if len(unique_values) >1:
                        break
                DF_PLOT = DF_PLOT[[index] + [col for col in DF_PLOT.columns if col != index]]
                DF_DROP= DF_PLOT.T

                DF_PLOT.columns = list_variables

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
                radar = ComplexRadar(fig1, list_variables, ranges)

                teams_colors = [obj_teams_color[list_teams[1]], 
                    obj_teams_color2[list_teams[1]]]

                k= 0
                for index, row in DF_PLOT.iterrows():
                    legend = index
                    data = []
                    for var in list_variables:
                        data.append(row[var])
                    radar.plot(data, legend, 2, color=teams_colors[k])
                    radar.fill(data, alpha=0.2, color=teams_colors[k])
                    k = k+1
                
                st.pyplot(fig1, use_container_width=True)
                st.text("")
    
    elif analisis_option == "Impacto Jugador en Partido":
        with st.spinner("Generando Análisis Partido con impacto player..."):
                obj_info = crear_resumenAnimadoInfo(objJugadorImpacto,selected_game, list_teams, obj_teams_img, obj_teams_name, obj_teams_nameFull, obj_players_name, teams_colors, obj_players_image,obj_players_image2)
                create_vis_resumenPartido(obj_info,selected_game)

        st.title("Impacto de " + selected_playerImpacto)
        st.title(selected_gameNombre)
        # Cargar y mostrar el video
        if True:
            st.image('temp/'+selected_game+'_player.png', caption="Resumen "+ selected_gameNombre, use_column_width=True)

            st.title(selected_gameNombre)
            colMainSB3, colMainSB4= st.columns([1, 1])
            with colMainSB3:
                DF_STATS_COMPARE_TEAMS = generar_stats_for_Team_playerImpacto(selected_game, list_selected_stats, list_teamsNames[0], list_teams[0], selected_playerImpacto, selected_IdPlayerImpacto)

                list_variables = DF_STATS_COMPARE_TEAMS.index.to_list()
                DF_STATS_COMPARE_TEAMS.index = list_variables

                st.dataframe(DF_STATS_COMPARE_TEAMS.style.apply(make_maxHighland, axis=1)
                            .apply(make_minHighland, axis=1)
                            .format(precision=1, thousands=".", decimal=","),
                            #.apply(make_pretty, axis=1),
                                #.highlight_max(axis=1, color = '#a7fcb5')
                                #.highlight_min(axis=1, color = '#fca7a7'),
                            # .set_properties(**{'text-align': 'center'}),
                            height= int(35.2*(DF_STATS_COMPARE_TEAMS.shape[0]+1)) ,
                            column_config = {'width': 'small'},
                            use_container_width = True)
                
            with colMainSB4:
                DF_DROP = DF_STATS_COMPARE_TEAMS.copy()
                DF_PLOT= DF_DROP.T

                ## Mover la 1º columna con valores distintos al principio
                for index, row in DF_DROP.iterrows():
                    unique_values = row.unique()
                    if len(unique_values) >1:
                        break
                DF_PLOT = DF_PLOT[[index] + [col for col in DF_PLOT.columns if col != index]]
                DF_DROP= DF_PLOT.T

                DF_PLOT.columns = list_variables

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
                radar = ComplexRadar(fig1, list_variables, ranges)

                teams_colors = [obj_teams_color[list_teams[0]], 
                    obj_teams_color2[list_teams[0]]]
                
                k=0

                for index, row in DF_PLOT.iterrows():
                    legend = index
                    data = []
                    for var in list_variables:
                        data.append(row[var])
                    radar.plot(data, legend, 2, color=teams_colors[k])
                    radar.fill(data, alpha=0.2, color=teams_colors[k])
                    k = k+1
                
                st.pyplot(fig1, use_container_width=True)
                st.text("")

            


    st.session_state.disabled = False
