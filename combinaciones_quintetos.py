import numpy as np
import pandas as pd
import streamlit as st

import mysql.connector
import numpy as np
import matplotlib.pyplot as plt

DB_user = st.secrets["DB_user"] 
DB_host = st.secrets["DB_host"] 
DB_password = st.secrets["DB_password"]
DB_database = st.secrets["DB_database"]
DB_port = st.secrets["DB_port"]
Access_DB = {'DB_user': DB_user, 'DB_host': DB_host, 'DB_password': DB_password, 'DB_database': DB_database, 'DB_port': DB_port}

##############################################################################################################################################
##############################################################   RADAR CHART   ###############################################################
##############################################################################################################################################

def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])


def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    """
    for r in ranges:
        x1, x2 = r
        if x1 != x2:
            break """
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d - y1) / (y2 - y1)
                     * (x2 - x1) + x1 if (y2 - y1) != 0 else d)
    return sdata


class ComplexRadar():
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=6):
        angles = np.arange(0, 360, 360. / len(variables))

        axes = [fig.add_axes([0.05, 0.05, 0.9, 0.9], polar=True,
                             label="axes{}".format(i))
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles,
                                         labels=variables,
                                         fontsize=14,
                                         rotation=angles[1],#-90,
                                         color='purple'
                                         )

        [txt.set_position((-0.05, -0.05)) for txt, angle in zip(text, angles)]
        [txt.set_rotation(angle - 90) for txt, angle in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i],
                               num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x, 2))
                         for x in grid]
            '''
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1]  # hack to invert grid
                # gridlabels aren't reversed
            '''
            for gL in range(len(gridlabel)):
                if (gL != len(gridlabel)-1):
                    gridlabel[gL] = ""  # clean up origin
                else:
                    gridlabel[gL] = int(float(gridlabel[gL]))

            ax.set_rgrids(grid, labels=gridlabel,
                          angle=angles[i])
            ax.spines["polar"].set_visible(True)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]

    def plot(self, data, legend, n_quintetos, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], label=legend, marker='o', ms=3, linewidth=1.5, alpha=0.5, *args, **kw)
        for an in range(len(data)):
            txt = str(data[an]) if type(data[an]) == "<class 'float'>" else str(round(data[an],1))
            self.ax.annotate(txt, xy = (self.angle[an], np.r_[sdata[an], sdata[0]][0]+sdata[0]*0.025), annotation_clip=True, *args, **kw )
        self.ax.legend(ncols=1, bbox_to_anchor=(0, 1.11 +0.05*n_quintetos),
              loc='upper left', fontsize='large')

    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)

##############################################################################################################################################
##############################################################   RADAR CHART   ###############################################################
##############################################################################################################################################


#@st.cache_resource
def conectar_BDD():
    conexion = mysql.connector.connect(user=Access_DB['DB_user'], password=Access_DB['DB_password'],
                              host=Access_DB['DB_host'],
                              database=Access_DB['DB_database'], port=Access_DB['DB_port'],
                              auth_plugin='mysql_native_password')
    cursor = conexion.cursor()
    return(conexion, cursor)


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


@st.cache_data
def buscarCompeticiones():
    [conexion, _]= conectar_BDD()
    query = "SELECT id_competition, name, id_edition, year FROM competition ORDER BY year DESC"
    df_out = pd.read_sql(query,conexion).drop_duplicates()
    conexion.close()
    return df_out

@st.cache_data
def buscarEquipos(selected_liga_id, selected_year_id):
    [conexion, _]= conectar_BDD()
    query = "SELECT id_team, team_name, image FROM teams WHERE id_competition = '"+ selected_liga_id+"' and id_edition = '"+selected_year_id+"'"
    df_out = pd.read_sql(query,conexion)
    conexion.close()
    return df_out

@st.cache_data
def buscarJugadores(id_team):
    [conexion, _]= conectar_BDD()
    query = "SELECT id_player, name_nick, image FROM p_players WHERE id_team = '" + id_team + "'"
    df_out = pd.read_sql(query,conexion)
    conexion.close()
    return df_out

@st.cache_data
def buscarStatFives(id_team, list_players_in, list_player_out):
    SQL_PLAYERS_IN = ""
    for player in list_players_in:
        SQL_PLAYERS_IN = SQL_PLAYERS_IN + "AND name_five like '%" + player + "%'"
    SQL_PLAYERS_OUT = ""
    for player in list_player_out:
        SQL_PLAYERS_OUT = SQL_PLAYERS_OUT + "AND name_five not like '%" + player + "%'"
        
    [conexion, _] = conectar_BDD()
    query = "SELECT * FROM j_fives WHERE num_players = 5 AND id_team = '" + id_team + "' " + SQL_PLAYERS_IN + SQL_PLAYERS_OUT
    df_out = pd.read_sql(query,conexion)
    conexion.close()
    return df_out



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

        PJ = len(pd.unique(df_statFives_team['id_match']))
        MIN = (df_statFives_team['second_gameOut'].sum() - df_statFives_team['second_gameIn'].sum()) / 60
        T2A = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 't2in'].shape[0]
        T2O = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 't2out'].shape[0]
        T3A = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 't3in'].shape[0]
        T3O= df_statFives_team[df_statFives_team['id_playbyplaytype'] == 't3out'].shape[0]
        TLA = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 't1in'].shape[0]
        TLO = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 't1out'].shape[0]
        AST = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'ast'].shape[0]
        REC = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'stl'].shape[0]
        PER = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'turn'].shape[0]
        RD = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'rebD'].shape[0]
        RO = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'rebO'].shape[0]
        TF = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'block'].shape[0]
        TC = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'blockAgainst'].shape[0]
        FC = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'foul'].shape[0]
        FR = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'foulR'].shape[0]
        r_T2A = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_t2in'].shape[0]
        r_T2O = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_t2out'].shape[0]
        r_T3A = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_t3in'].shape[0]
        r_T3O= df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_t3out'].shape[0]
        r_TLA = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_t1in'].shape[0]
        r_TLO = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_t1out'].shape[0]
        r_AST = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_ast'].shape[0]
        r_REC = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_stl'].shape[0]
        r_PER = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_turn'].shape[0]
        r_RD = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_rebD'].shape[0]
        r_RO = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_rebO'].shape[0]
        r_TF = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_block'].shape[0]
        r_TC = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_blockAgainst'].shape[0]
        r_FC = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_foul'].shape[0]
        r_FR = df_statFives_team[df_statFives_team['id_playbyplaytype'] == 'r_foulR'].shape[0]
        PTS = 2*T2A + 3*T3A + TLA
        r_PTS = 2*r_T2A + 3*r_T3A + r_TLA
        T2I = T2A + T2O
        r_T2I = r_T2A + r_T2O
        T2_PORC = round(T2A/T2I,2) if T2I > 0 else 0
        r_T2_PORC = round(r_T2A/r_T2I,2) if r_T2I > 0 else 0
        T3I = T3A + T3O
        r_T3I = r_T3A + r_T3O
        T3_PORC = round(T3A/T3I,2) if T3I > 0 else 0
        r_T3_PORC = round(r_T3A/r_T3I,2) if T3I > 0 else 0
        TLI = TLA + TLO
        r_TLI = r_TLA + r_TLO
        TL_PORC = round(TLA/TLI,2) if TLI > 0 else 0
        r_TL_PORC = round(r_TLA/r_TLI,2) if r_TLI > 0 else 0
        RT = RD +RO
        r_RT = r_RD +r_RO
        VAL = PTS - T2O - T3O - TLO + RT + AST + REC - PER + TF - TC + FR -FC
        r_VAL = r_PTS - r_T2O - r_T3O - r_TLO + r_RT + r_AST + r_REC - r_PER + r_TF - r_TC + r_FR - r_FC
        DIF_PTS = PTS - r_PTS
        POSESIONES = 0.96*((T2A+T2O+T3A+T3O) + PER + 0.44*(TLA+TLO-RO))
        r_POSESIONES = 0.96*((r_T2A+r_T2O+r_T3A+r_T3O) + r_PER + 0.44*(r_TLA+r_TLO-r_RO))
        OFF_EF = 100*((PTS)/POSESIONES) if POSESIONES > 0 else 0
        DEF_EF = -100*((r_PTS)/r_POSESIONES) if r_POSESIONES > 0 else 0
        NET_EF = OFF_EF + DEF_EF
        RITMO = POSESIONES/float(MIN)*40 if MIN>0 else 0

        PTS_TIRO = PTS / (T2I + T3I) if (T2I + T3I) > 0 else 0
        r_PTS_TIRO = r_PTS / (r_T2I + r_T3I) if (r_T2I + r_T3I) > 0 else 0
        PTS_POS = PTS / POSESIONES if POSESIONES > 0 else 0
        r_PTS_POS = r_PTS / r_POSESIONES if r_POSESIONES > 0 else 0
        EFG = 100*((T2A + T3A) + 0.5*T3A)/(T2I + T3I) if (T2I + T3I) > 0 else 0
        r_EFG = 100*((r_T2A + r_T3A) + 0.5*r_T3A)/(r_T2I + r_T3I) if (r_T2I + r_T3I) > 0 else 0
        REBO_P = 100*RO / (RO + r_RD) if (RO + r_RD) > 0 else 0
        REBD_P = 100*RD / (RD + r_RO) if (RD + r_RO) > 0 else 0
        REB_P = 100*(RO+RD) / (RO+RD+r_RO+r_RD) if (RO+RD+r_RO+r_RD) > 0 else 0
        AST_P = 100*AST / POSESIONES if POSESIONES > 0 else 0
        r_AST_P = 100*r_AST / r_POSESIONES if r_POSESIONES > 0 else 0
        REC_P = 100*REC / r_POSESIONES if r_POSESIONES > 0 else 0
        TAP_P = 100*TF / r_POSESIONES if r_POSESIONES > 0 else 0
        PERD_P = 100*PER / POSESIONES if POSESIONES > 0 else 0
        r_PERD_P = 100*r_PER / r_POSESIONES if r_POSESIONES > 0 else 0
        AST_PERD =AST / PER if PER >0 else 0
        r_AST_PERD =r_AST / r_PER if r_PER >0 else 0
        FREC_TL = 100*TLI / (T2I + T3I) if (T2I + T3I) > 0 else 0
        r_FREC_TL = 100*r_TLI / (r_T2I + r_T3I) if (r_T2I + r_T3I) > 0 else 0
        PLAY_P = 100*(T2A + T3A)/(T2I+T3I+RO+PER) if (T2I+T3I+RO+PER) > 0 else 0
        r_PLAY_P = 100*(r_T2A + r_T3A)/(r_T2I+r_T3I+r_RO+r_PER) if (r_T2I+r_T3I+r_RO+r_PER) > 0 else 0
            
        POSESIONES = int(POSESIONES)
        r_POSESIONES = int(r_POSESIONES)

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

        obj_variableValue_to_stats = {
                    "PJ":PJ, "MIN":MIN, "Nº POS":POSESIONES, "PTS":PTS, "T2A":T2A, "T2I":T2I, "%T2":T2_PORC, "T3A":T3A, "T3I":T3I, "%T3":T3_PORC, "TLA":TLA, "TLI":TLI, "%TL":TL_PORC, "RD":RD, "RO":RO,"RT":RT, "AST":AST, "REC":REC, "PERD":PER, "TF":TF, "TC":TC, "FC":FC, "FR":FR, "VAL":VAL, "+-": DIF_PTS,
                    "PTS/TIRO": PTS_TIRO, "PTS/POS": PTS_POS,"%EFG": EFG, "EF.OF": OFF_EF, "%REB.OF": REBO_P, "%AST": AST_P, "%PERD": PERD_P, "AST/PERD": AST_PERD, "FREC.TL": FREC_TL, "%PLAY": PLAY_P,
                    "Nº POS rival": r_POSESIONES, "PTS rival": r_PTS,"RT rival": r_RT, "AST rival": r_AST, "REC rival": r_REC, "PERD rival": r_PER, "VAL rival": r_VAL,
                    "PTS/POS rival": r_PTS_POS,"%EFG rival": r_EFG, "EF.DEF": DEF_EF, "%REB.DEF": REBD_P, "%AST rival": r_AST_P, "%PERD rival": r_PERD_P, "AST/PERD rival": r_AST_PERD, "FREC.TL rival": r_FREC_TL, "%PLAY rival": r_PLAY_P, "%REC": REC_P, "%TAP": TAP_P, "RITMO": RITMO, "EF.NETA": NET_EF, "%REB": REB_P,
                    "EQUIPO": LIST_QUINTETOS_TODOS[j]["team_name"]+" "+LIST_QUINTETOS_TODOS[j]["year"][2:], "JUG. IN": players_in_string, "JUG. OUT": players_out_string
                }

        list_five_out = []
        for stat in list_selected_stats:
            statValue = obj_variableValue_to_stats[stat]
            if (modo_metricas != 'Totales') and (stat in list_stats_a40mins):
                statValue = round(statValue/MIN*40 if MIN>0 else 0, 1)
            list_five_out.append(statValue)

        list_fives_df.append(list_five_out)
        list_index_fives_df.append('Quinteto ' + str(j+1))



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
    list_selected_stats.insert(0, "JUG. OUT")
    list_selected_stats.insert(0, "JUG. IN")
    list_selected_stats.insert(0, "EQUIPO")

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
            legend = DF[index]['EQUIPO'] + ': ' + txt_JUG_IN + txt_JUG_OUT
            data = []
            for var in list_variables_a40mins:
                data.append(row[var])
            radar.plot(data, legend, selected_number_quintetos, color=list_colors[k])
            radar.fill(data, alpha=0.2, color=list_colors[k])
            k = k+1
        
        st.pyplot(fig1, use_container_width=True)

        
st.session_state.disabled = False
