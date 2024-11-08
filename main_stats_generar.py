import pandas as pd
import numpy as np
import requests
from PIL import Image
from io import BytesIO

from conexiones_bbdd import *
from pipeline_onlyDataNoModel import *




# Para que un numero siempre tenga 2 digitos
def format_number(num): 
    return str(num).zfill(2)

def hex_to_rgb(hex_color):
    # Convertir de hexadecimal a RGB
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
def is_color_similar_to_color(hex_color1, hex_color2):
    # Color dorado en RGB aproximado
    rgb1 = hex_to_rgb(hex_color1)
    rgb2 = hex_to_rgb(hex_color2)

    # Calcular la distancia euclidiana entre el color y el color dorado
    distance = ((rgb1[0] - rgb2[0]) ** 2 + 
                (rgb1[1] - rgb2[1]) ** 2 + 
                (rgb1[2] - rgb2[2]) ** 2) ** 0.5

    # Definir un umbral de cercanía (ajustable según la precisión deseada)
    threshold = 60
    return distance < threshold


# Ejemplo de carga de imágenes desde URLs
def load_image_from_url(url, recorteBool, recorte_izq=0, recorte_sup=0, recorte_der=0, recorte_inf=0):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP no exitosos
        if 'image' in response.headers['Content-Type']:
            image = Image.open(BytesIO(response.content))
            if recorteBool:
                image = image.crop((recorte_izq, recorte_sup, recorte_der, recorte_inf))
            else:
                image = image.resize((50, 50), Image.Resampling.LANCZOS)
            return np.array(image)
        else:
            print(f"El contenido de {url} no es una imagen.")
            return None
    except Exception as e:
        print(f"Error al cargar la imagen de {url}: {e}")
        return None

def obtener_statsPosibles_equiposComparar():
    list_stats_basicas = ["Nº POS", "PTS","RT", "AST", "REC", "PERD", "VAL", "+-"]
    list_stats_basicas_rival = ["Nº POS rival", "PTS rival","RT rival", "AST rival", "REC rival", "PERD rival", "VAL rival", "+-"]

    list_stats_ofensivas = ["Nº POS", "PTS/POS","%EFG", "EF.OF", "%REB.OF", "%AST", "%PERD", "AST/PERD", "FREC.TL", "%PLAY"]
    list_stats_defensivas = ["Nº POS", "PTS/POS rival","%EFG rival", "EF.DEF", "%REB.DEF", "%AST rival", "%REC", "AST/PERD rival", "%TAP", "FREC.TL rival", "%PLAY rival"]
    list_stats_avanzadas = ["Nº POS", "RITMO","%EFG", "EF.OF", "EF.DEF", "EF.NETA", "%REB", "%REB.DEF", "%REB.OF", "%AST", "%REC", "%PERD", "AST/PERD"]
    list_PosibleStats_personalizadas =  list(set(list_stats_basicas + list_stats_basicas_rival + list_stats_ofensivas + list_stats_defensivas + list_stats_avanzadas))

    list_stats_a40mins = ["Nº POS", "PTS", "T2A", "T2I", "%T2", "T3A", "T3I", "%T3", "TLA", "TLI", "%TL", "RD", "RO","RT", "AST", "REC", "PERD", "TF", "TC", "FC", "FR", "VAL",  "+-", "Nº POS rival", "PTS rival","RT rival", "AST rival", "REC rival", "PERD rival", "VAL rival"]

    list_stats_inversas = ["PERD", "TC", "FR", "PTS rival","RT rival", "AST rival", "REC rival", "VAL rival", "%PERD", "PTS/POS rival","%EFG rival", "%AST rival", "AST/PERD rival", "FREC.TL rival", "%PLAY rival"]

    return list_stats_basicas, list_stats_basicas_rival, list_stats_ofensivas, list_stats_defensivas, list_stats_avanzadas, list_PosibleStats_personalizadas, list_stats_a40mins, list_stats_inversas

def crearBucleFor_teams_fromEvents(DF_Boxscores, list_selected_stats, list_teams_df):
    PJ = len(pd.unique(DF_Boxscores['id_match']))
    MIN = (DF_Boxscores['second_gameOut'].sum() - DF_Boxscores['second_gameIn'].sum()) / 60
    T2A = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 't2in'].shape[0]
    T2O = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 't2out'].shape[0]
    T3A = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 't3in'].shape[0]
    T3O= DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 't3out'].shape[0]
    TLA = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 't1in'].shape[0]
    TLO = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 't1out'].shape[0]
    AST = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'ast'].shape[0]
    REC = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'stl'].shape[0]
    PER = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'turn'].shape[0]
    RD = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'rebD'].shape[0]
    RO = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'rebO'].shape[0]
    TF = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'block'].shape[0]
    TC = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'blockAgainst'].shape[0]
    FC = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'foul'].shape[0]
    FR = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'foulR'].shape[0]
    r_T2A = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_t2in'].shape[0]
    r_T2O = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_t2out'].shape[0]
    r_T3A = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_t3in'].shape[0]
    r_T3O= DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_t3out'].shape[0]
    r_TLA = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_t1in'].shape[0]
    r_TLO = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_t1out'].shape[0]
    r_AST = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_ast'].shape[0]
    r_REC = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_stl'].shape[0]
    r_PER = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_turn'].shape[0]
    r_RD = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_rebD'].shape[0]
    r_RO = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_rebO'].shape[0]
    r_TF = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_block'].shape[0]
    r_TC = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_blockAgainst'].shape[0]
    r_FC = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_foul'].shape[0]
    r_FR = DF_Boxscores[DF_Boxscores['id_playbyplaytype'] == 'r_foulR'].shape[0]
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

    obj_variableValue_to_stats = {
                "MIN":MIN, "Nº POS":POSESIONES, "PTS":PTS, "T2A":T2A, "T2I":T2I, "%T2":T2_PORC, "T3A":T3A, "T3I":T3I, "%T3":T3_PORC, "TLA":TLA, "TLI":TLI, "%TL":TL_PORC, "RD":RD, "RO":RO,"RT":RT, "AST":AST, "REC":REC, "PERD":PER, "TF":TF, "TC":TC, "FC":FC, "FR":FR, "VAL":VAL, "+-": DIF_PTS,
                "PTS/TIRO": PTS_TIRO, "PTS/POS": PTS_POS,"%EFG": EFG, "EF.OF": OFF_EF, "%REB.OF": REBO_P, "%AST": AST_P, "%PERD": PERD_P, "AST/PERD": AST_PERD, "FREC.TL": FREC_TL, "%PLAY": PLAY_P,
                "Nº POS rival": r_POSESIONES, "PTS rival": r_PTS,"RT rival": r_RT, "AST rival": r_AST, "REC rival": r_REC, "PERD rival": r_PER, "VAL rival": r_VAL,
                "PTS/POS rival": r_PTS_POS,"%EFG rival": r_EFG, "EF.DEF": DEF_EF, "%REB.DEF": REBD_P, "%AST rival": r_AST_P, "%PERD rival": r_PERD_P, "AST/PERD rival": r_AST_PERD, "FREC.TL rival": r_FREC_TL, "%PLAY rival": r_PLAY_P, "%REC": REC_P, "%TAP": TAP_P, "RITMO": RITMO, "EF.NETA": NET_EF, "%REB": REB_P
            }

    list_team_out = []
    for stat in list_selected_stats:
        statValue = obj_variableValue_to_stats[stat]
        list_team_out.append(statValue)

    list_teams_df.append(list_team_out)

    return list_teams_df

def crearBucleFor_teams_fromBoxscore(isRow, DF_Boxscores, list_selected_stats, list_teams_df):
    if isRow:
        MIN = int(DF_Boxscores["time_played"]/(60*5))
        PTS = DF_Boxscores["points"]
        T2A = DF_Boxscores["pt2_success"]
        T2I = DF_Boxscores["pt2_tried"]
        T3A = DF_Boxscores["pt3_success"]
        T3I= DF_Boxscores["pt3_tried"]
        TLA = DF_Boxscores["pt1_success"]
        TLI = DF_Boxscores["pt1_tried"]
        AST = DF_Boxscores["assists"]
        REC = DF_Boxscores["steals"]
        PER = DF_Boxscores["turnovers"]
        RD = DF_Boxscores["deffensive_rebound"]
        RO = DF_Boxscores["offensive_rebound"]
        TF = DF_Boxscores["blocks"]
        TC = DF_Boxscores["received_blocks"]
        FC = DF_Boxscores["personal_fouls"]
        FR = DF_Boxscores["received_fouls"]
        r_PTS = DF_Boxscores["rival_points"]
        r_T2A = DF_Boxscores["rival_2pt_success"]
        r_T2I = DF_Boxscores["rival_2pt_tried"]
        r_T3A = DF_Boxscores["rival_3pt_success"]
        r_T3I= DF_Boxscores["rival_3pt_tried"]
        r_TLA = DF_Boxscores["rival_1pt_success"]
        r_TLI = DF_Boxscores["rival_1pt_tried"]
        r_AST = DF_Boxscores["rival_assists"]
        r_REC = DF_Boxscores["rival_steals"]
        r_PER = DF_Boxscores["rival_turnovers"]
        r_RD = DF_Boxscores["rival_deffensive_rebound"]
        r_RO = DF_Boxscores["rival_offensive_rebound"]
        r_TF = DF_Boxscores["blocks"]
        r_TC = DF_Boxscores["received_blocks"]
        r_FC = DF_Boxscores["received_fouls"]
        r_FR = DF_Boxscores["personal_fouls"]
    else:
        MIN = int(DF_Boxscores["time_played"].mean()/(60*5))
        PTS = DF_Boxscores["points"].mean()
        T2A = DF_Boxscores["pt2_success"].mean()
        T2I = DF_Boxscores["pt2_tried"].mean()
        T3A = DF_Boxscores["pt3_success"].mean()
        T3I= DF_Boxscores["pt3_tried"].mean()
        TLA = DF_Boxscores["pt1_success"].mean()
        TLI = DF_Boxscores["pt1_tried"].mean()
        AST = DF_Boxscores["assists"].mean()
        REC = DF_Boxscores["steals"].mean()
        PER = DF_Boxscores["turnovers"].mean()
        RD = DF_Boxscores["deffensive_rebound"].mean()
        RO = DF_Boxscores["offensive_rebound"].mean()
        TF = DF_Boxscores["blocks"].mean()
        TC = DF_Boxscores["received_blocks"].mean()
        FC = DF_Boxscores["personal_fouls"].mean()
        FR = DF_Boxscores["received_fouls"].mean()
        r_PTS = DF_Boxscores["rival_points"].mean()
        r_T2A = DF_Boxscores["rival_2pt_success"].mean()
        r_T2I = DF_Boxscores["rival_2pt_tried"].mean()
        r_T3A = DF_Boxscores["rival_3pt_success"].mean()
        r_T3I= DF_Boxscores["rival_3pt_tried"].mean()
        r_TLA = DF_Boxscores["rival_1pt_success"].mean()
        r_TLI = DF_Boxscores["rival_1pt_tried"].mean()
        r_AST = DF_Boxscores["rival_assists"].mean()
        r_REC = DF_Boxscores["rival_steals"].mean()
        r_PER = DF_Boxscores["rival_turnovers"].mean()
        r_RD = DF_Boxscores["rival_deffensive_rebound"].mean()
        r_RO = DF_Boxscores["rival_offensive_rebound"].mean()
        r_TF = DF_Boxscores["blocks"].mean()
        r_TC = DF_Boxscores["received_blocks"].mean()
        r_FC = DF_Boxscores["received_fouls"].mean()
        r_FR = DF_Boxscores["personal_fouls"].mean()
    T2O = T2I - T2A
    r_T2O = r_T2I - r_T2A
    T2_PORC = round(T2A/T2I,2) if T2I > 0 else 0
    r_T2_PORC = round(r_T2A/r_T2I,2) if r_T2I > 0 else 0
    T3O = T3I - T3A
    r_T3O = r_T3I - r_T3A
    T3_PORC = round(T3A/T3I,2) if T3I > 0 else 0
    r_T3_PORC = round(r_T3A/r_T3I,2) if T3I > 0 else 0
    TLO = TLI - TLA
    r_TLO = r_TLI - r_TLA
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

    obj_variableValue_to_stats = {
                "MIN":MIN, "Nº POS":POSESIONES, "PTS":PTS, "T2A":T2A, "T2I":T2I, "%T2":T2_PORC, "T3A":T3A, "T3I":T3I, "%T3":T3_PORC, "TLA":TLA, "TLI":TLI, "%TL":TL_PORC, "RD":RD, "RO":RO,"RT":RT, "AST":AST, "REC":REC, "PERD":PER, "TF":TF, "TC":TC, "FC":FC, "FR":FR, "VAL":VAL, "+-": DIF_PTS,
                "PTS/TIRO": PTS_TIRO, "PTS/POS": PTS_POS,"%EFG": EFG, "EF.OF": OFF_EF, "%REB.OF": REBO_P, "%AST": AST_P, "%PERD": PERD_P, "AST/PERD": AST_PERD, "FREC.TL": FREC_TL, "%PLAY": PLAY_P,
                "Nº POS rival": r_POSESIONES, "PTS rival": r_PTS,"RT rival": r_RT, "AST rival": r_AST, "REC rival": r_REC, "PERD rival": r_PER, "VAL rival": r_VAL,
                "PTS/POS rival": r_PTS_POS,"%EFG rival": r_EFG, "EF.DEF": DEF_EF, "%REB.DEF": REBD_P, "%AST rival": r_AST_P, "%PERD rival": r_PERD_P, "AST/PERD rival": r_AST_PERD, "FREC.TL rival": r_FREC_TL, "%PLAY rival": r_PLAY_P, "%REC": REC_P, "%TAP": TAP_P, "RITMO": RITMO, "EF.NETA": NET_EF, "%REB": REB_P
            }

    list_team_out = []
    for stat in list_selected_stats:
        statValue = obj_variableValue_to_stats[stat]
        list_team_out.append(statValue)

    list_teams_df.append(list_team_out)

    return list_teams_df


def generar_stats_for_teams_fromBoxscore(selected_game, list_selected_stats, list_teamsNames, list_teams):
    DF_Boxscores = buscarBoxscore(selected_game)
    list_teams_df = []
    for index, row in DF_Boxscores.iterrows():
        crearBucleFor_teams_fromBoxscore(True, row, list_selected_stats, list_teams_df)

    DF_OUT =  pd.DataFrame(list_teams_df,
                        columns = list_selected_stats,
                        index = list_teamsNames).T
    
    return DF_OUT



def generar_stats_for_SameTeam_fromBoxscore(selected_game, list_selected_stats, teamsName, id_team):
    DF_BoxscoresPromedioTeam = buscarBoxscorePromedioTeam(id_team, selected_game)
    DF_BoxscoresGame = buscarBoxscore(selected_game)
    DF_BoxscoresGame = DF_BoxscoresGame[DF_BoxscoresGame['id_team'] == id_team]
    list_teams_df = []
    list_teams_df = crearBucleFor_teams_fromBoxscore(False, DF_BoxscoresPromedioTeam, list_selected_stats, list_teams_df)
    list_teams_df = crearBucleFor_teams_fromBoxscore(False, DF_BoxscoresGame, list_selected_stats, list_teams_df)
        
    index1 = teamsName + " promedio Liga"
    index2 = teamsName + " en partido"

    DF_OUT =  pd.DataFrame(list_teams_df,
                        columns = list_selected_stats,
                        index = [index1, index2]).T
    
    return DF_OUT

def generar_stats_for_Team_playerImpacto(selected_game, list_selected_stats, teamsName, id_team, playerName, id_player):
    DF_BoxscoresWithPlayer = buscarEventosGameWithPlayer(selected_game, id_team, id_player)
    DF_BoxscoresWithoutPlayer = buscarEventosGameWithoutPlayer(selected_game, id_team, id_player)
    list_teams_df = []
    list_teams_df = crearBucleFor_teams_fromEvents(DF_BoxscoresWithPlayer, list_selected_stats, list_teams_df)
    list_teams_df = crearBucleFor_teams_fromEvents(DF_BoxscoresWithoutPlayer, list_selected_stats, list_teams_df)
        
    index1 = teamsName + " CON " + playerName
    index2 = teamsName + " SIN " + playerName

    DF_OUT =  pd.DataFrame(list_teams_df,
                        columns = list_selected_stats,
                        index = [index1, index2]).T
    
    return DF_OUT



################################
####    CALCULAR PARCIALES #####
################################

def calcular_parciales_potentes(df, umbral_potencia=0.6, tiempo_minimo = 90, diferencia_puntos_minima = 7, tiempo_maximo= 500):
    parciales = []
    
    # Iteramos por cada posible inicio de parcial
    for i in range(len(df)):
        play_type_i = df.loc[i, 'id_playbyplaytype']
        if ('t1in' not in play_type_i) and ('t2in' not in play_type_i) and ('t3in' not in play_type_i):
            continue
        equipo_anotador_inicio_parcial = df.loc[i, 'id_teamEjecutor']
        marcador_inicial_eq1 = df.loc[i, 'scoreTeam']
        marcador_inicial_eq2 = df.loc[i, 'scoreRivalTeam']
        cuarto_inicio = df.loc[i, 'period']
        tiempo_inicio = df.loc[i, 'tiempo']
        tiempo_anterior_inicio = df.loc[i-1, 'tiempo'] # en el grafico, el parcial hay que ponerlovisualmente cuando va a empezar, no despues de simar la primera canasta
            
        jugadores_anotadores = {}
        
        # Variables para llevar el control del parcial
        puntos_eq1 = 0
        puntos_eq2 = 0
        max_puntaje = 0  # Inicializar el puntaje máximo para este parcial en 0
        parciales_dentro_este_parcial = []
        entroBucle = False
        # Buscamos hasta donde se puede extender el parcial dentro del límite de tiempo
        for j in range(i, len(df)):
            play_type_j = df.loc[j, 'id_playbyplaytype']
            if ('t1in' not in play_type_j) and ('t2in' not in play_type_j) and ('t3in' not in play_type_j):
                continue
            equipo_anotador = df.loc[j, 'id_teamEjecutor']
            if 't1in' in play_type_j:
                puntos = 1
            elif 't2in' in play_type_j:
                puntos = 2
            elif 't3in' in play_type_j:
                puntos = 3 

            cuarto = df.loc[j, 'period']
            tiempo = df.loc[j, 'tiempo']
            tiempo_fin_posterior = df.loc[j+1, 'tiempo'] # en el grafico, el parcial hay que ponerlo visualmente cuando termina, no despues anotar tu la ultima

            # Calcular el tiempo transcurrido
            tiempo_transcurrido = tiempo - tiempo_inicio
            
            # Actualizar puntos y jugadores según el equipo anotador
            if equipo_anotador == equipo_anotador_inicio_parcial:
                puntos_eq1 += puntos
            else:
                puntos_eq2 += puntos
            
            if (equipo_anotador== equipo_anotador_inicio_parcial):
                if (df.loc[j, 'id_playerEjecutor'] in jugadores_anotadores):
                    jugadores_anotadores[df.loc[j, 'id_playerEjecutor']] = jugadores_anotadores[df.loc[j, 'id_playerEjecutor']] + puntos
                else:
                    jugadores_anotadores[df.loc[j, 'id_playerEjecutor']] = puntos

            # Calcular la diferencia de puntos y el puntaje
            diferencia = puntos_eq1 - puntos_eq2
            puntos_en_contra = puntos_eq2#min(puntos_eq1, puntos_eq2)  # Puntos del equipo rival
            puntaje = diferencia * (1 / (1.05*np.sqrt(tiempo_transcurrido + 1))) * (1 + 1 / (1 + puntos_en_contra))
            
            # Terminar el bucle si el puntaje cae por debajo del umbral de potencia o disminuye significativamente
            if entroBucle or (diferencia >= diferencia_puntos_minima and tiempo_transcurrido > tiempo_minimo) or tiempo_transcurrido > tiempo_maximo:
                entroBucle = True
                if tiempo_transcurrido > tiempo_maximo and max_puntaje == 0:
                    break
                else:
                    if puntaje < umbral_potencia or (max_puntaje > 0 and puntaje < max_puntaje * 0.7) :
                        break
                    else:
                        parciales_dentro_este_parcial.append({
                            'equipo_iniciador': equipo_anotador_inicio_parcial,
                            'puntaje': puntaje,
                            'diferencia_puntos': diferencia,
                            'tiempo_transcurrido': tiempo_transcurrido,
                            'cuarto_inicio': cuarto_inicio,
                            'tiempo_inicio': tiempo_anterior_inicio,
                            'puntos_eq1': puntos_eq1,
                            'puntos_eq2': puntos_eq2,
                            'jugadores': jugadores_anotadores,
                            'tiempo_fin': tiempo_fin_posterior
                        })

                    # Actualizar el puntaje máximo alcanzado en este parcial
                    max_puntaje = max(max_puntaje, puntaje)

        # Convertir parciales a DataFrame y ordenar por la diferencia de puntos
        parciales_dentro_este_parcial_df = pd.DataFrame(parciales_dentro_este_parcial)

        if parciales_dentro_este_parcial_df.shape[0] > 0:
            parciales_dentro_este_parcial_df = parciales_dentro_este_parcial_df.sort_values(by='puntaje', ascending=False).reset_index(drop=True)

            # Calcular diferencia de puntos y puntaje parcial
            tiempo_transcurrido = parciales_dentro_este_parcial_df.loc[0, 'tiempo_transcurrido']
            diferencia = parciales_dentro_este_parcial_df.loc[0, 'diferencia_puntos']

            # Guardar el parcial si cumple con los criterios
            if diferencia >= diferencia_puntos_minima and tiempo_transcurrido > tiempo_minimo:
                parciales.append({
                    'equipo_iniciador': parciales_dentro_este_parcial_df.loc[0, 'equipo_iniciador'],
                    'puntaje': parciales_dentro_este_parcial_df.loc[0, 'puntaje'],
                    'diferencia_puntos': diferencia,
                    'tiempo_transcurrido': tiempo_transcurrido,
                    'cuarto_inicio': parciales_dentro_este_parcial_df.loc[0, 'cuarto_inicio'],
                    'tiempo_inicio': parciales_dentro_este_parcial_df.loc[0, 'tiempo_inicio'],
                    'puntos_eq1': parciales_dentro_este_parcial_df.loc[0, 'puntos_eq1'],
                    'puntos_eq2': parciales_dentro_este_parcial_df.loc[0, 'puntos_eq2'],
                    'jugadores': parciales_dentro_este_parcial_df.loc[0, 'jugadores'],
                    'tiempo_fin': parciales_dentro_este_parcial_df.loc[0, 'tiempo_fin']
                })
    
    # Convertir parciales a DataFrame y ordenar por la diferencia de puntos
    parciales_df = pd.DataFrame(parciales)
    #parciales_df = parciales_df.sort_values(by='diferencia_puntos', ascending=False).reset_index(drop=True)
    parciales_df = parciales_df.sort_values(by='puntaje', ascending=False)

    return parciales_df


def filtrar_parciales_solapados(parciales_df):
    parciales_filtrados = []
    
    # Ordenar los parciales por tiempo de inicio y puntaje para priorizar parciales fuertes
    parciales_df = parciales_df.sort_values(by=['diferencia_puntos', 'puntaje'], ascending=[False, False])
    
    for idx, parcial in parciales_df.iterrows():
        # Comprobar si este parcial se solapa con algún parcial ya guardado
        solapado = False
        for parcial_filtrado in parciales_filtrados:
            # Verificar si el parcial actual comienza después y termina antes o al mismo tiempo que un parcial ya guardado
            if ((parcial['tiempo_fin'] >= parcial_filtrado['tiempo_inicio'] and parcial['tiempo_fin'] <= parcial_filtrado['tiempo_fin']) or 
                (parcial['tiempo_inicio'] >= parcial_filtrado['tiempo_inicio'] and parcial['tiempo_inicio'] <= parcial_filtrado['tiempo_fin']) or 
                (parcial['tiempo_inicio'] <= parcial_filtrado['tiempo_inicio'] and parcial['tiempo_fin'] >= parcial_filtrado['tiempo_fin']) or 
                (parcial['tiempo_inicio'] >= parcial_filtrado['tiempo_inicio'] and parcial['tiempo_fin'] <= parcial_filtrado['tiempo_fin'])):
                solapado = True
                break
        
        # Solo agregar el parcial si no se solapa
        if not solapado:
            parciales_filtrados.append(parcial)

    # Convertir la lista de parciales filtrados a DataFrame
    parciales_df_noSolapados = pd.DataFrame(parciales_filtrados).sort_values(by='puntaje', ascending=False)
    return parciales_df_noSolapados

################################
###  FIN CALCULAR PARCIALES ####
################################

#######################################
####    CALCULAR RACHAS JUGADORES #####
#######################################
def calcular_jugadoresCalientes(df, tiempo_min_transcurrido = 120, puntos_min_acumulados = 6, puntos_min_por_minuto = 2.5):

    # Inicializamos variables para almacenar rachas
    rachas = []

    # Buscamos rachas para cada jugador
    for jugador in df['id_playerEjecutor'].unique():
        acciones = df[df['id_playerEjecutor'] == jugador].reset_index(drop=True)

        for i in range(len(acciones)):
            play_type_i = acciones.loc[i, 'id_playbyplaytype']
            if ('t1in' not in play_type_i) and ('t2in' not in play_type_i) and ('t3in' not in play_type_i):
                continue
            puntos_acumulados = 0
            tiempo_inicial = acciones.loc[i, 'tiempo']

            for j in range(i, len(acciones)):
                play_type_j = acciones.loc[j, 'id_playbyplaytype']
                if ('t1in' not in play_type_j) and ('t2in' not in play_type_j) and ('t3in' not in play_type_j):
                    continue
                equipo_anotador = acciones.loc[j, 'id_teamEjecutor']
                if 't1in' in play_type_j:
                    puntos = 1
                if 't2in' in play_type_j:
                    puntos = 2
                if 't3in' in play_type_j:
                    puntos = 3 
                tiempo_actual = acciones.loc[j, 'tiempo']
                puntos_acumulados += puntos
                
                tiempo_transcurrido = tiempo_actual - tiempo_inicial
                puntos_por_minuto = puntos_acumulados / (0.75*(tiempo_transcurrido / 60)) if tiempo_transcurrido > 0 else puntos_min_por_minuto
                
                # Criterios de racha: mínimo de 6 puntos en 90 segundos y eficiencia de al menos 1.5 puntos/min
                if tiempo_transcurrido >= tiempo_min_transcurrido and puntos_acumulados >= puntos_min_acumulados and puntos_por_minuto >= puntos_min_por_minuto:
                    racha = {
                        'jugador': jugador,
                        'puntos_acumulados': puntos_acumulados,
                        'tiempo_inicio': tiempo_inicial,
                        'tiempo_fin': tiempo_actual,
                        'puntos_por_minuto': puntos_por_minuto,
                        'equipo_anotador': equipo_anotador
                    }
                    rachas.append(racha)
                    
                # Salir de la racha si la eficiencia cae por debajo del umbral o si pasa el límite de tiempo
                if puntos_por_minuto*1.5 < puntos_min_por_minuto or tiempo_transcurrido > 600:
                    break

    # Crear dataframe con las rachas detectadas
    df_rachas = pd.DataFrame(rachas)
    if len(rachas) > 0:
        df_rachas['tiempo_transcurrido'] = df_rachas['tiempo_fin'] - df_rachas['tiempo_inicio']  # Duración en segundos

    return(df_rachas)


def filtrar_jugadoresCalientes(df_rachas):
    rachas_filtrados = []
    
    # Ordenar los parciales por tiempo de inicio y puntaje para priorizar parciales fuertes
    df_rachas = df_rachas.sort_values(by=['puntos_por_minuto', 'puntos_acumulados'], ascending=[False, False])
    
    for idx, racha in df_rachas.iterrows():
        # Comprobar si este parcial se solapa con algún parcial ya guardado
        solapado = False
        for racha_filtrado in rachas_filtrados:
            # Verificar si el parcial actual comienza después y termina antes o al mismo tiempo que un parcial ya guardado
            if ((racha['tiempo_fin'] >= racha_filtrado['tiempo_inicio'] and racha['tiempo_fin'] <= racha_filtrado['tiempo_fin']) or 
                (racha['tiempo_inicio'] >= racha_filtrado['tiempo_inicio'] and racha['tiempo_inicio'] <= racha_filtrado['tiempo_fin']) or 
                (racha['tiempo_inicio'] <= racha_filtrado['tiempo_inicio'] and racha['tiempo_fin'] >= racha_filtrado['tiempo_fin']) or 
                (racha['tiempo_inicio'] >= racha_filtrado['tiempo_inicio'] and racha['tiempo_fin'] <= racha_filtrado['tiempo_fin'])):
                solapado = True
                break
        
        # Solo agregar el parcial si no se solapa
        if not solapado:
            rachas_filtrados.append(racha)

    # Convertir la lista de parciales filtrados a DataFrame
    df_rachas_noSolapados = pd.DataFrame(rachas_filtrados).sort_values(by='puntos_por_minuto', ascending=False)
    return df_rachas_noSolapados


#######################################
#### FIN CALCULAR RACHAS JUGADORES ####
#######################################


#######################################
####    CALCULAR JUGADOR IN      ######
#######################################
def calcular_jugadoresImpactoIn(df, jugador, team):

    # Inicializamos variables para almacenar rachas
    jugadorInParciales = []
 
    for i in range(len(df)):
        puntos_parcial = 0
        rebotes_parcial = 0
        asistencias_parcial = 0
        diferencia_parcial = 0
        play_type_i = df.loc[i, 'id_playbyplaytype']
        if play_type_i in ['subsIn', 'r_subsIn']:
            tiempo_inicial = df.loc[i, 'tiempo']
            for j in range(i, len(df)):
                tiempo_actual = df.loc[j, 'tiempo']
                play_type_j = df.loc[j, 'id_playbyplaytype']
                if play_type_j in ['subsOut', 'r_subsOut']:
                    inParcial = {
                        'jugador': jugador,
                        'puntos_parcial': puntos_parcial,
                        'tiempo_inicio': tiempo_inicial,
                        'tiempo_fin': tiempo_actual,
                        'rebotes_parcial': rebotes_parcial,
                        'asistencias_parcial': asistencias_parcial,
                        'diferencia_parcial': diferencia_parcial
                    }
                    jugadorInParciales.append(inParcial)
                    break
                if jugador == df.loc[j, 'id_playerEjecutor']:
                    if 't1in' in play_type_j:
                        puntos_parcial += 1
                    elif 't2in' in play_type_j:
                        puntos_parcial += 2
                    elif 't3in' in play_type_j:
                        puntos_parcial += 3 
                    elif 'reb' in play_type_j:
                        rebotes_parcial += 1
                    elif 'ast' in play_type_j:
                        asistencias_parcial += 1
                
                if ('t1in' in play_type_j) or ('t2in' in play_type_j) or ('t3in' in play_type_j):
                    equipo_anotador = df.loc[j, 'id_teamEjecutor']
                    if 't1in' in play_type_j:
                        puntos = 1
                    elif 't2in' in play_type_j:
                        puntos = 2
                    elif 't3in' in play_type_j:
                        puntos = 3 
                    if team == equipo_anotador:
                        diferencia_parcial += puntos
                    else:
                        diferencia_parcial -= puntos

    # Crear dataframe con las rachas detectadas
    df_jugadorInParciales = pd.DataFrame(jugadorInParciales)
    if len(jugadorInParciales) > 0:
        df_jugadorInParciales['tiempo_transcurrido'] = df_jugadorInParciales['tiempo_fin'] - df_jugadorInParciales['tiempo_inicio']  # Duración en segundos

    return(df_jugadorInParciales)

#######################################
######    FIN JUGADOR IN      ########
#######################################

def crear_resumenAnimadoInfo(objJugadorImpacto, selected_game, list_teams, obj_teams_img, obj_teams_name, obj_teams_nameFull, obj_players_name, teams_colors, obj_players_image,obj_players_image2):
    df_events = buscarPartidosEvents(selected_game, list_teams[0])

    quarter_times = [600, 1200, 1800, 2400]  # Final de cada cuarto (segundos en un juego de baloncesto)

    df_events = prepare_dataloader(df_events)

    
    list_subs_types = ['subsIn', 'subsOut','r_subsIn', 'r_subsOut','ast', 'r_ast', 'rebD', 'rebO', 'r_rebD', 'r_rebO']
    if len(objJugadorImpacto) == 1:
        jugadorImpacto = list(objJugadorImpacto.keys())[0]
        df_events = df_events[(~df_events['id_playbyplaytype'].isin(list_subs_types)) | (df_events['id_playerEjecutor'] == jugadorImpacto)].reset_index(drop=True)
        teamImpacto = objJugadorImpacto[jugadorImpacto]
        df_jugadorInParciales = calcular_jugadoresImpactoIn(df_events, jugadorImpacto, teamImpacto)
    else:
        df_events = df_events[(~df_events['id_playbyplaytype'].isin(list_subs_types))].reset_index(drop=True)
        df_jugadorInParciales = pd.DataFrame()

    event_times = []   # inicio partido
    diff_scores = []   # inicio partido
    scoreTeamA = []
    scoreTeamB = []
    type_play = []

    for index, row in df_events.iterrows():
        time = row['tiempo']
        event_times.append(time)
        diff = row['differenceMoment']
        diff_scores.append(diff)
        scoreA = row['scoreTeam']
        scoreTeamA.append(scoreA)
        scoreB = row['scoreRivalTeam']
        scoreTeamB.append(scoreB)
        play = row['id_playbyplaytype']
        type_play.append(play)

    teams_images = [load_image_from_url(obj_teams_img[df_events['id_team'][df_events.index.to_list()[-1]]], False), 
                    load_image_from_url(obj_teams_img[df_events['id_rivalTeam'][df_events.index.to_list()[-1]]], False)]
    teams_names = [obj_teams_name[df_events['id_team'][df_events.index.to_list()[-1]]], 
                    obj_teams_name[df_events['id_rivalTeam'][df_events.index.to_list()[-1]]]]
    teams_namesFull = [obj_teams_nameFull[df_events['id_team'][df_events.index.to_list()[-1]]], 
                    obj_teams_nameFull[df_events['id_rivalTeam'][df_events.index.to_list()[-1]]]]
    

    list_cuartos = list(set(df_events['period'].to_list()))

    obj_event_descriptions = {"t2in": "2 pts importantes", "t3in": "Triple importante", "t1in": "TL clave",
                            "r_t2in": "2 pts importantes", "r_t3in": "Triple importante", "r_t1in": "TL clave"}

    key_events = []
    event_types = {}
    event_descriptions = {}
    key_event_images = {}


    ##################  PARCIALES POTENTES  ########################################
    partial_starts = {}
    partial_ends = {}

    parciales_potentes = calcular_parciales_potentes(df_events)
    parciales_potentes = filtrar_parciales_solapados(parciales_potentes)

    top_partials_rows = parciales_potentes.head(10)
    top_partials_indices = top_partials_rows.index[:].tolist()
    for indice in top_partials_indices:
        cuarto_inicio = parciales_potentes.loc[indice, 'cuarto_inicio']
        cuarto_inicio_text = str(cuarto_inicio)
        tiempo_inicio = parciales_potentes.loc[indice, 'tiempo_inicio']
        if (600 * cuarto_inicio) - tiempo_inicio > 400:
            texto_cuarto = " a inicios del " + cuarto_inicio_text + "º cuarto"
        elif (600 * cuarto_inicio) - tiempo_inicio > 200:
            texto_cuarto = " a mitad del " + cuarto_inicio_text + "º cuarto"
        else:
            texto_cuarto = " a finales del " + cuarto_inicio_text + "º cuarto"
        team_name = obj_teams_name[parciales_potentes.loc[indice, 'equipo_iniciador']]
        team_nameFull = obj_teams_nameFull[parciales_potentes.loc[indice, 'equipo_iniciador']]
        texto_start = team_name + " inicia un parcial\n " + texto_cuarto

        obj_jugadores_points_inPartial = parciales_potentes.loc[indice, 'jugadores']
        # Encontrar el valor máximo
        jugador_points_inPartial_maximo = max(obj_jugadores_points_inPartial.values())
        # Filtrar las claves con el valor máximo
        claves_inPartial_maximo = [key for key, value in obj_jugadores_points_inPartial.items() if value == jugador_points_inPartial_maximo]
        if len(claves_inPartial_maximo) > 1:
            for clave in claves_inPartial_maximo:
                if clave == claves_inPartial_maximo[0]:
                    text_jugadoresInPartial = obj_players_name[clave]
                elif clave == claves_inPartial_maximo[-1]:
                    text_jugadoresInPartial = text_jugadoresInPartial + " y " + obj_players_name[clave]
                else:
                    text_jugadoresInPartial = text_jugadoresInPartial + ", " + obj_players_name[clave]
            text_jugadoresInPartial_full = text_jugadoresInPartial + " claves en el parcial con " + str(obj_jugadores_points_inPartial[claves_inPartial_maximo[0]]) + " puntos cada uno"
            text_jugadoresInPartial = text_jugadoresInPartial + " claves \n con " + str(obj_jugadores_points_inPartial[claves_inPartial_maximo[0]]) + " puntos cada uno."

        else:
            text_jugadoresInPartial = obj_players_name[claves_inPartial_maximo[0]] + " clave \n aportando " + str(obj_jugadores_points_inPartial[claves_inPartial_maximo[0]]) + " puntos"
            text_jugadoresInPartial_full = obj_players_name[claves_inPartial_maximo[0]] + " clave aportando " + str(obj_jugadores_points_inPartial[claves_inPartial_maximo[0]]) + " puntos en este parcial"
        text_jugadoresInPartial_fijo = obj_players_name[claves_inPartial_maximo[0]] +"\n" + str(obj_jugadores_points_inPartial[claves_inPartial_maximo[0]]) + " puntos"


        texto_startFull = team_nameFull + " inicia un parcial " + texto_cuarto

        partial_starts[top_partials_rows.tiempo_inicio[indice]] = {
                                    "team_name": team_name,
                                    "color": teams_colors[0] if team_name == teams_names[0] else teams_colors[1],
                                    "texto": texto_start,
                                    "textoFull": texto_startFull,
                                    "tiempo_fin": parciales_potentes.loc[indice, 'tiempo_fin']
                                }
        diferencia = str(parciales_potentes.loc[indice, 'diferencia_puntos'])
        puntos_favor = str(parciales_potentes.loc[indice, 'puntos_eq1'])
        puntos_contra = str(parciales_potentes.loc[indice, 'puntos_eq2'])
        tiempo_transcurrido = parciales_potentes.loc[indice, 'tiempo_transcurrido']
        minutos_trans = int(tiempo_transcurrido / 60)
        minutos_text = str(minutos_trans)
        segundos_trans = str(format_number(int(tiempo_transcurrido - minutos_trans*60)))
        texto_fin = "Parcial de "+ puntos_favor + "-" + puntos_contra + "\n en " + minutos_text + "':" + segundos_trans + "\"\n en favor de " + team_name + ". \n\n" + text_jugadoresInPartial
        texto_finFull = "Parcial de "+ puntos_favor + " a " + puntos_contra + " en " + minutos_text + " minutos " + segundos_trans + " segundos en favor de " + team_nameFull + " \n\n" + text_jugadoresInPartial_full
        texto_fijo1 = puntos_favor + "-" + puntos_contra + '\n' + "en " + minutos_text + "':" + segundos_trans + "\""
        texto_fijo2 = text_jugadoresInPartial_fijo
        foto_equipo = load_image_from_url(obj_teams_img[parciales_potentes.loc[indice, 'equipo_iniciador']], False)
        partial_ends[top_partials_rows.tiempo_fin[indice]] = {
                                    "team_name": team_name,
                                    "color": teams_colors[0] if team_name == teams_names[0] else teams_colors[1],
                                    "texto": texto_fin,
                                    "textoFull": texto_finFull,
                                    "tiempo_inicio": parciales_potentes.loc[indice, 'tiempo_inicio'],
                                    "indice_inicio": top_partials_rows.tiempo_inicio[indice],
                                    "texto_fijo1": texto_fijo1,
                                    "texto_fijo2": texto_fijo2,
                                    "foto_equipo": foto_equipo
                                }
    ##################  FIN PARCIALES POTENTES  ########################################

    ##################  RACHAS  ########################################
    racha_starts = {}
    racha_ends = {}

    df_rachas = calcular_jugadoresCalientes(df_events)
    df_rachas = filtrar_jugadoresCalientes(df_rachas)

    top_rachas_rows = df_rachas.head(10)
    top_rachas_indices = top_rachas_rows.index[:].tolist()
    for indice in top_rachas_indices:
        tiempo_inicio = df_rachas.loc[indice, 'tiempo_inicio']
        team_name = obj_teams_name[df_rachas.loc[indice, 'equipo_anotador']]
        team_nameFull = obj_teams_nameFull[df_rachas.loc[indice, 'equipo_anotador']]
        player_name = obj_players_name[df_rachas.loc[indice, 'jugador']]
        texto_start = player_name + " entra en racha."

        racha_starts[top_rachas_rows.tiempo_inicio[indice]] = {
                                    "team_name": team_name,
                                    "color": teams_colors[0] if team_name == teams_names[0] else teams_colors[1],
                                    "texto": texto_start,
                                    "tiempo_fin": df_rachas.loc[indice, 'tiempo_fin']
                                }
        puntos_acumulados = str(df_rachas.loc[indice, 'puntos_acumulados'])
        tiempo_transcurrido = df_rachas.loc[indice, 'tiempo_transcurrido']
        minutos_trans = int(tiempo_transcurrido / 60)
        minutos_text = str(minutos_trans)
        segundos_trans = str(format_number(int(tiempo_transcurrido - minutos_trans*60)))
        puntos_por_minuto = df_rachas.loc[indice, 'puntos_por_minuto']
        titular_texto = "Racha de " if puntos_por_minuto < 3.5 else "Momento caliente de "
        texto_fin = titular_texto + player_name + "\n con " + puntos_acumulados + " puntos \n\n en " + minutos_text + "':" + segundos_trans + "\" \n en favor de " + team_name
        texto_finFull = titular_texto + player_name + " con " + puntos_acumulados + " puntos en " + minutos_text + " minutos " + segundos_trans + " segundos en favor de " + team_nameFull
        foto_jugador = load_image_from_url(obj_players_image[df_rachas.loc[indice, 'jugador']], False)
        foto_cara_jugador = load_image_from_url(obj_players_image2[df_rachas.loc[indice, 'jugador']], True, 40, 25, 170, 140)
        texto_fijo = player_name + '\n' + puntos_acumulados + " puntos\nen " + minutos_text + "':" + segundos_trans + "\""
        racha_ends[top_rachas_rows.tiempo_fin[indice]] = {
                                    "team_name": team_name,
                                    "color": teams_colors[0] if team_name == teams_names[0] else teams_colors[1],
                                    "texto": texto_fin,
                                    "textoFull": texto_finFull,
                                    "tiempo_inicio": df_rachas.loc[indice, 'tiempo_inicio'],
                                    "indice_inicio": top_rachas_rows.tiempo_inicio[indice],
                                    "foto_jugador": foto_jugador,
                                    "foto_cara_jugador": foto_cara_jugador,
                                    "texto_fijo": texto_fijo
                                }

    ##################  FIN RACHAS ########################################

    ##################  IMPACTO JUGADOR  ########################################
    impactoPlayer_starts = {}
    impactoPlayer_ends = {}

    if len(objJugadorImpacto) == 1:
        top_impactoPlayer_rows = df_jugadorInParciales.head(10)
        top_impactoPlayer_indices = top_impactoPlayer_rows.index[:].tolist()
        for indice in top_impactoPlayer_indices:
            tiempo_inicio = df_jugadorInParciales.loc[indice, 'tiempo_inicio']
            tiempo_fin = df_jugadorInParciales.loc[indice, 'tiempo_fin']
            tiempo_transcurrido = df_jugadorInParciales.loc[indice, 'tiempo_fin']
            pintarTexto = True if tiempo_transcurrido >= 120 else False
            player_name = obj_players_name[df_jugadorInParciales.loc[indice, 'jugador']]
            color = "green" if df_jugadorInParciales.loc[indice, 'diferencia_parcial'] >= 0 else "red"
            impactoPlayer_starts[top_impactoPlayer_rows.tiempo_inicio[indice]] = {
                                        "player_name": player_name,
                                        "pintarTexto": pintarTexto,
                                        "tiempo_fin": tiempo_fin,
                                        "color": color
                                    }
            puntos_parcial = str(df_jugadorInParciales.loc[indice, 'puntos_parcial'])
            rebotes_parcial = str(df_jugadorInParciales.loc[indice, 'rebotes_parcial'])
            asistencias_parcial = str(df_jugadorInParciales.loc[indice, 'asistencias_parcial'])
            diferencia_parcial = str(df_jugadorInParciales.loc[indice, 'diferencia_parcial'])
            tiempo_transcurrido = df_jugadorInParciales.loc[indice, 'tiempo_transcurrido']
            minutos_trans = int(tiempo_transcurrido / 60)
            minutos_text = str(minutos_trans)
            segundos_trans = str(format_number(int(tiempo_transcurrido - minutos_trans*60)))
            diferencia_parcial_text = "+" if df_jugadorInParciales.loc[indice, 'diferencia_parcial'] >= 0 else ""
            texto_fijo = player_name + "\n" + puntos_parcial + " pts\n" + rebotes_parcial + " reb\n" + asistencias_parcial + " ast\n+-: " + diferencia_parcial_text + diferencia_parcial + "\nen " + minutos_text + "':" + segundos_trans + "\""
            impactoPlayer_ends[top_impactoPlayer_rows.tiempo_fin[indice]] = {
                                        "player_name": player_name,
                                        "tiempo_inicio": tiempo_inicio,
                                        "indice_inicio": top_impactoPlayer_rows.tiempo_inicio[indice],
                                        "texto_fijo": texto_fijo,
                                        "pintarTexto": pintarTexto,
                                        "color": color
                                    }

    ##################  FIN IMPACTO JUGADOR ########################################


    obj_info = {
                    'event_times': event_times,
                    'diff_scores': diff_scores,
                    'scoreTeamA': scoreTeamA,
                    'scoreTeamB': scoreTeamB,
                    'teams_images': teams_images,
                    'key_events': key_events,
                    'event_types': event_types,
                    'event_descriptions': event_descriptions,
                    'key_event_images': key_event_images,
                    'quarter_times': quarter_times,
                    'teams_names': teams_names,
                    'teams_namesFull': teams_namesFull,
                    'teams_colors': teams_colors,
                    'partial_starts': partial_starts,
                    'partial_ends': partial_ends,
                    'racha_starts': racha_starts,
                    'racha_ends': racha_ends,
                    'type_play': type_play,
                    'impactoPlayer_starts': impactoPlayer_starts,
                    'impactoPlayer_ends': impactoPlayer_ends

                }
    
    return obj_info
