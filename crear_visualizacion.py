import matplotlib
#matplotlib.use('Agg')  # Usa un backend no interactivoimport matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import MaxNLocator



def create_vis_resumenPartido(obj_info,selected_game):

    event_times = obj_info['event_times']
    diff_scores = obj_info['diff_scores']
    scoreTeamA = obj_info['scoreTeamA']
    scoreTeamB = obj_info['scoreTeamB']
    teams_images = obj_info['teams_images']
    key_events = obj_info['key_events']
    event_types = obj_info['event_types']
    event_descriptions = obj_info['event_descriptions']
    key_event_images = obj_info['key_event_images']
    quarter_times = obj_info['quarter_times']
    teams_colors = obj_info['teams_colors']
    teams_names = obj_info['teams_names']
    teams_namesFull = obj_info['teams_namesFull']
    partial_starts = obj_info['partial_starts']
    partial_ends = obj_info['partial_ends']
    racha_starts = obj_info['racha_starts']
    racha_ends = obj_info['racha_ends']
    type_play = obj_info['type_play']
    impactoPlayer_starts = obj_info['impactoPlayer_starts']
    impactoPlayer_ends = obj_info['impactoPlayer_ends']


    def hex_to_rgb(hex_color):
        # Convertir de hexadecimal a RGB
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def get_text_color(hex_color):
        # Convertir a RGB
        rgb = hex_to_rgb(hex_color)

        # Desempaquetar los valores RGB
        r, g, b = rgb
        
        # Calcular la luminancia con la fórmula ponderada
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Umbral para determinar si el color es oscuro (recomendado ~128)
        return 'white' if luminance < 128 else 'black'
    

    def is_color_similar_to_color2(hex_color1, hex_color2):
        # Color dorado en RGB aproximado
        rgb1 = hex_to_rgb(hex_color1)
        rgb2 = hex_to_rgb(hex_color2)

        # Calcular la distancia euclidiana entre el color y el color dorado
        distance = ((rgb1[0] - rgb2[0]) ** 2 + 
                    (rgb1[1] - rgb2[1]) ** 2 + 
                    (rgb1[2] - rgb2[2]) ** 2) ** 0.5

        # Definir un umbral de cercanía (ajustable según la precisión deseada)
        threshold = 60
        return distance > threshold
    
    text_teamColors = [get_text_color(teams_colors[0]), get_text_color(teams_colors[1])]
    text_colors_inGoldStar = ["gold" if is_color_similar_to_color2(teams_colors[0], "#FFD700") else "black", "gold" if is_color_similar_to_color2(teams_colors[1], "#FFD700") else "black"]
    text_colors_inOrangeBall = [teams_colors[0] if is_color_similar_to_color2(teams_colors[0], "#ffa500") else "black", teams_colors[1] if is_color_similar_to_color2(teams_colors[1], "#ffa500") else "black"]

    # Para que un numero siempre tenga 2 digitos
    def format_number(num): 
        return str(num).zfill(2)

    quarter_labels = ["1º Cuarto", "Descanso", "3º Cuarto", "Final"] 

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(12, 8)) #(12, 8)
    ax.set_xlim(0, max(event_times))
    x_center = (ax.get_xlim()[1] + ax.get_xlim()[0]) / 2
    x_quarter = x_center / 2
    x_tercio =  x_center/ 3
    x_haciaAfuera = (ax.get_xlim()[1] + ax.get_xlim()[0]) / 12
    ymin = -max(abs(min(diff_scores)), abs(max(diff_scores)))
    ymax = max(diff_scores) + 1
    ymin = int(ymin + ymin*0.1)
    ymax = int(ymax + ymax*0.1)
    # Barra por encima del grafico para parciales: 
    y_max_evol = ymax + (4*(ymax - ymin)/4)
    y_div_rachas_parcial = ymax + 0.55*(y_max_evol - ymax)
    y_center = (ax.get_ylim()[1] + ax.get_ylim()[0]) / 2
    y_total_center = y_max_evol - 0.02*(y_max_evol-ymin)
    ax.set_ylim(ymin, y_max_evol)  # Centrar en 0
    # Configurar etiquetas y título
    ax.set_xlabel("Tiempo (s)", fontsize=12)
    #ax.set_ylabel("Diferencia de Puntos", fontsize=12)
    #ax.set_title("Diferencia de Puntos en el Tiempo - Simulación de Partido de Baloncesto", fontsize=14)
    ax.set_xticks([])  # Quita las etiquetas del eje x
    ax.set_xlabel('')  # Quita el título del eje x
    ax.yaxis.set_major_locator(MaxNLocator(nbins=14))
    ## posicionar labels de posesiones y jugadores calientes:
    ax.text(-x_haciaAfuera, ymax + 0.2*ymax, "blanco \n blanco \n blanco \n blanco \n blanco \n blanco \n blanco", color="white", fontsize=24, ha="center", bbox=dict(facecolor="white", edgecolor='white', alpha=1), zorder=2)
    ax.text(-x_haciaAfuera, ymax +(y_max_evol - ymax)*0.55/2, "Momentum \n Equipos", color="black", fontsize=14, va="center", ha="center", bbox=dict(facecolor="white", edgecolor='white', alpha=1), zorder=2)
    if len(impactoPlayer_starts) == 0:
        text_titulo_up = "Jugadores \n Calientes"
    else:
        text_titulo_up = "Impacto \n Jugador"
    ax.text(-x_haciaAfuera, y_max_evol -(y_max_evol - ymax)*0.45/2, text_titulo_up, color="black", fontsize=14, va="center", ha="center", bbox=dict(facecolor="white", edgecolor='white', alpha=1), zorder=2)
    ax.text(-x_haciaAfuera, y_center, "Evolución \n Partido", color="black", fontsize=14, va="center", ha="center", bbox=dict(facecolor="white", edgecolor='white', alpha=1), zorder=2)

    # Configuración de la cancha
    ax.set_facecolor('#d9d9d9')  # Color de fondo más suave
    ax.grid(True, which='both', linestyle='--', lw=0.5, color="white")

    # Línea de referencia en y=0
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, zorder=1)  # Línea en el fondo
    ax.axhline(y=ymax, color='black', linestyle='-', linewidth=3, zorder=1)  # Línea en el fondo
    ax.axhline(y=y_div_rachas_parcial, color='black', linestyle='-', linewidth=2, zorder=1)  # Línea en el fondo

    # Crear líneas verticales con etiquetas para cada cuarto
    for i, (q_time, label) in enumerate(zip(quarter_times, quarter_labels)):
        ax.axvline(x=q_time, color='black', linestyle='-', linewidth=1.75, alpha=1)
        ax.text(q_time, ymax - 0.02*(y_max_evol-ymin), label,
                 ha='center', va='top', bbox=dict(facecolor='white', edgecolor='grey', alpha=0.6))
        ax.text(q_time, ax.get_ylim()[0] - 0.02*(y_max_evol-ymin), label,
                 ha='center', va='top', bbox=dict(facecolor='white', edgecolor='grey', alpha=0.6))


    # Crear una línea de diferencia de puntos
    line, = ax.plot([], [], lw=2, zorder=2)

    # Inicialización de los elementos del gráfico
    def init():
        line.set_data([], [])
        return line,

    # Añadir imágenes en eventos clave
    annotation_boxes = []  # Lista para manejar las cajas de anotación de imágenes
    annotation_boxes_teamA = []  # Lista para manejar las cajas de anotación de imágenes
    annotation_boxes_teamB = []  # Lista para manejar las cajas de anotación de imágenes
    annotation_boxes_periodo = []  
    annotation_boxes_tiempo = [] 
    fill_areas = []  # Lista para almacenar las áreas coloreada
    fill_areas_parciales = []
    fill_areas_parciales_info = {}
    fill_areas_rachas = []
    fill_areas_rachas_info = {}
    fill_areas_impactoPlayer = []
    fill_areas_impactoPlayer_info = {}

    def add_scoreTeamsTittle(ax, scores_teams, teams_images, teams_colors, teams_names, info_tiempo, zoom=0.05):
        y_pos = ax.get_ylim()[1] + 0.06*(ax.get_ylim()[1]-ax.get_ylim()[0])
        imgA = teams_images[0]
        """Función para añadir una imagen al gráfico en las coordenadas especificadas."""
        if imgA is not None:  # Verificar si la imagen se cargó correctamente
            imagebox_teamAlogo = OffsetImage(imgA, zoom=zoom)
            # Obtener las coordenadas del centro del gráfico
            x_pos = (ax.get_xlim()[1] + ax.get_xlim()[0]) * 4/16
            ab_teamAlogo = AnnotationBbox(imagebox_teamAlogo, (x_pos, y_pos), frameon=False)
            ax.add_artist(ab_teamAlogo)
        imgB = teams_images[1]
        """Función para añadir una imagen al gráfico en las coordenadas especificadas."""
        if imgB is not None:  # Verificar si la imagen se cargó correctamente
            imagebox_teamBlogo = OffsetImage(imgB, zoom=zoom)
            # Obtener las coordenadas del centro del gráfico
            x_pos = (ax.get_xlim()[1] + ax.get_xlim()[0]) * 12/16
            ab_teamBlogo = AnnotationBbox(imagebox_teamBlogo, (x_pos, y_pos), frameon=False)
            ax.add_artist(ab_teamBlogo)

        x_pos_teamNameA = (ax.get_xlim()[1] + ax.get_xlim()[0]) * 2/16
        x_pos_teamNameB = (ax.get_xlim()[1] + ax.get_xlim()[0]) * 14/16
        ax.text(x_pos_teamNameA, y_pos, teams_names[0], color=teams_colors[0], fontsize=28, fontweight='bold', ha='center', va='center', zorder=3)
        ax.text(x_pos_teamNameB, y_pos, teams_names[1], color=teams_colors[1], fontsize=28, fontweight='bold', ha='center', va='center', zorder=3) 

        periodo = info_tiempo["periodo"]
        minutos = info_tiempo["minutos"]
        segundos = info_tiempo["segundos"]
        tiempo = minutos + " : " + segundos
        y_pos_marcador = y_pos + 0.03*(ax.get_ylim()[1]-ax.get_ylim()[0])   
        y_pos_tiempo = y_pos - 0.03*(ax.get_ylim()[1]-ax.get_ylim()[0])   
        periodo_text = ax.text(x_center, y_pos_marcador, periodo, color="purple", fontsize=18, fontweight='bold', ha='center', va='center', zorder=3)
        annotation_boxes_periodo.append(periodo_text)
        tiempo_text = ax.text(x_center, y_pos_tiempo, tiempo, color="purple", fontsize=20, fontweight='bold', ha='center', va='center', zorder=3)
        annotation_boxes_tiempo.append(tiempo_text)

        x_pos_scoreA = (ax.get_xlim()[1] + ax.get_xlim()[0]) * 5/16
        x_pos_scoreB = (ax.get_xlim()[1] + ax.get_xlim()[0]) * 11/16
        text_scoreA = ax.text(x_pos_scoreA, y_pos, scores_teams[0], color=teams_colors[0], fontsize=28, fontweight='bold', ha='center', va='center', zorder=3)
        annotation_boxes_teamA.append(text_scoreA)
        text_scoreB = ax.text(x_pos_scoreB, y_pos, scores_teams[1], color=teams_colors[1], fontsize=28, fontweight='bold', ha='center', va='center', zorder=3)
        annotation_boxes_teamB.append(text_scoreB)

    def update_scoreTeamsTittle(ax, scores_teams, info_tiempo):
        for ab in annotation_boxes_teamA:
            ab.set_text('')
            ab.set_text(scores_teams[0])
        for ab in annotation_boxes_teamB:
            ab.set_text('')
            ab.set_text(scores_teams[1])
        periodo = info_tiempo["periodo"]
        minutos = info_tiempo["minutos"]
        segundos = info_tiempo["segundos"]
        tiempo = minutos + " : " + segundos
        for ab in annotation_boxes_periodo:
            ab.set_text('')
            ab.set_text(periodo)
        for ab in annotation_boxes_tiempo:
            ab.set_text('')
            ab.set_text(tiempo)


    def add_image(ax, img, zoom=0.75):
        """Función para añadir una imagen al gráfico en las coordenadas especificadas."""
        if img is not None:  # Verificar si la imagen se cargó correctamente
            imagebox = OffsetImage(img, zoom=zoom)
            # Obtener las coordenadas del centro del gráfico
            ab = AnnotationBbox(imagebox, (x_quarter, y_center - 0.02*(ymax-ymin)), frameon=False)
            ax.add_artist(ab)
            annotation_boxes.append(ab)  # Añadir la imagen a la lista para el control en 'init'
    
    def add_image_circular(ax, img, x,y, zoom):
        if img is not None:  # Verificar si la imagen se cargó correctamente
            #zoom = 1
            #img_resized = np.resize(img, (50, 50, img.shape[2]))
            # Recortar la imagen según coordenadas especificadas
            imagebox = OffsetImage(img, zoom=zoom)
            # Obtener las coordenadas del centro del gráfico
            ab = AnnotationBbox(imagebox, (x, y), frameon=False)
            ax.add_artist(ab)

    def delete_image():
        # Eliminar imágenes antiguas si las hay
        for ab in annotation_boxes:
            ab.remove()  # Remover las imágenes anteriores
        annotation_boxes.clear()  # Vaciar la lista para nuevas imágenes

    def colorear_areas_parciales(x_fin_temp):
        for ab in fill_areas_parciales:
            ab.remove()
        fill_areas_parciales.clear()
        for key in fill_areas_parciales_info:
            x_init = fill_areas_parciales_info[key]['time_init']
            color = fill_areas_parciales_info[key]['color']
            if fill_areas_parciales_info[key]['estado'] == "running":
                x_fin = x_fin_temp
            elif fill_areas_parciales_info[key]['estado'] == "finish":
                x_fin = fill_areas_parciales_info[key]['time_finish']
            area_parcial = ax.fill_betweenx([ymax, y_div_rachas_parcial], x_init, x_fin, color = color, alpha=0.3, zorder=0)
            fill_areas_parciales.append(area_parcial)

    def colorear_areas_rachas(x_fin_temp):
        for ab in fill_areas_rachas:
            ab.remove()
        fill_areas_rachas.clear()
        for key in fill_areas_rachas_info:
            x_init = fill_areas_rachas_info[key]['time_init']
            color = fill_areas_rachas_info[key]['color']
            if fill_areas_rachas_info[key]['estado'] == "running":
                x_fin = x_fin_temp
            elif fill_areas_rachas_info[key]['estado'] == "finish":
                x_fin = fill_areas_rachas_info[key]['time_finish']
            area_racha = ax.fill_betweenx([y_div_rachas_parcial, y_max_evol], x_init, x_fin, color = color, alpha=0.3, zorder=0)
            fill_areas_rachas.append(area_racha)

    def colorear_areas_impactoPlayer(x_fin_temp):
        for ab in fill_areas_impactoPlayer:
            ab.remove()
        fill_areas_impactoPlayer.clear()
        for key in fill_areas_impactoPlayer_info:
            x_init = fill_areas_impactoPlayer_info[key]['time_init']
            color = fill_areas_impactoPlayer_info[key]['color']
            if fill_areas_impactoPlayer_info[key]['estado'] == "running":
                x_fin = x_fin_temp
            elif fill_areas_impactoPlayer_info[key]['estado'] == "finish":
                x_fin = fill_areas_impactoPlayer_info[key]['time_finish']
            area_impactoPlayer = ax.fill_betweenx([y_div_rachas_parcial, y_max_evol], x_init, x_fin, color = color, alpha=0.3, zorder=0)
            fill_areas_impactoPlayer.append(area_impactoPlayer)


    # Función para actualizar el gráfico
    def animate(i):
        
        # Mostrar la diferencia de puntos hasta el tiempo actual
        x = event_times[:i+1]
        y = diff_scores[:i+1]

        tiempo = x[-1]
        if tiempo < quarter_times[0]:
            periodo = str(1)
            minutos = str(format_number(10 - int(tiempo / 60)))
            segundos = str(format_number(int(tiempo - int(tiempo / 60) * 60)))
        elif tiempo < quarter_times[1]:
            periodo = str(2)
            minutos = str(format_number(20 - int(tiempo / 60)))
            segundos = str(format_number(int(tiempo - int(tiempo / 60) * 60)))
        elif tiempo < quarter_times[2]:
            periodo = str(3)
            minutos = str(format_number(30 - int(tiempo / 60)))
            segundos = str(format_number(int(tiempo - int(tiempo / 60) * 60)))
        elif tiempo < quarter_times[3]:
            periodo = str(4)
            minutos = str(format_number(40 - int(tiempo / 60)))
            segundos = str(format_number(int(tiempo - int(tiempo / 60) * 60)))
        else:
            periodo = str(4)
            minutos = str(format_number(40 - int(tiempo / 60)))
            segundos = str(format_number(int(tiempo - int(tiempo / 60) * 60)))
            print("Estamos fuera en tiempo: ", tiempo)
        info_tiempo = {
                            "periodo": periodo,
                            "minutos": minutos,
                            "segundos": segundos
                        }
        
        # Mostrar el marcador arriba
        score_x = scoreTeamA[i]
        score_y = scoreTeamB[i]
        scores_teams = [score_x, score_y]

        if i == 0:
            add_scoreTeamsTittle(ax, scores_teams, teams_images, teams_colors, teams_names, info_tiempo)
        else:
            update_scoreTeamsTittle(ax, scores_teams, info_tiempo)
        
        # Graficar cada segmento de la línea con el color correspondiente
        for j in range(1, len(x)):
            if y[j] > y[j - 1]:
                color = teams_colors[0] #'green'
            elif y[j] < y[j - 1]:
                color = teams_colors[1] #'red'
            else:
                color = 'grey'
            ax.plot(x[j - 1:j + 1], y[j - 1:j + 1], color=color, lw=2, zorder=2)



        # Área por encima y por debajo de la línea y=0
        # Limpiar áreas anteriores
        for area in fill_areas:
            area.remove()
        fill_areas.clear()
        area_above = ax.fill_between(x, 0, np.maximum(y, 0), color=teams_colors[0], alpha=0.3, zorder=0)  # Área verde '#c8fcc7'
        area_below = ax.fill_between(x, 0, np.minimum(y, 0), color=teams_colors[1], alpha=0.3, zorder=0)  # Área roja '#fab6b4'
        fill_areas.extend([area_above, area_below])  # Almacena las áreas en la lista


        # Añadir símbolos de inicio y fin de parciales y rachas
        ###################     PARCIALES  ########################################             
        for start_partial_time in partial_starts:
            if start_partial_time == event_times[i]:  # Solo si el inicio del parcial está en el tiempo actual
                color = partial_starts[start_partial_time]['color']
                text_color = get_text_color(color)
                tiempo_fin = partial_starts[start_partial_time]['tiempo_fin']
                ax.plot(start_partial_time, diff_scores[i], '*', color=color, markersize=8, markeredgecolor='gold')
                #parcial_text = ax.text(x_center, y_center, texto, color=text_color, fontsize=20, ha="center", bbox=dict(facecolor=color, alpha=0.8))                
                ax.axvline(x=start_partial_time, color=color, linestyle='--', linewidth=0.5, alpha=0.5, zorder=5)
                # Reproducir el texto 
                #parcial_text.remove()
                fill_areas_parciales_info[start_partial_time] = {
                                                                "estado": "running",
                                                                "color": color,
                                                                "text_color": text_color,
                                                                "time_init": start_partial_time,
                                                                "time_finish": tiempo_fin
                                                            }

        for end_partial_time in partial_ends:
            if end_partial_time == event_times[i]:  # Solo si el final del parcial está en el tiempo actual
                color = partial_ends[end_partial_time]['color']
                text_color = get_text_color(color)
                indice_inicio = partial_ends[end_partial_time]['indice_inicio']
                tiempo_inicio = partial_ends[end_partial_time]['tiempo_inicio']
                texto_fijo1 = partial_ends[end_partial_time]['texto_fijo1']
                texto_fijo2 = partial_ends[end_partial_time]['texto_fijo2']
                foto_equipo = partial_ends[end_partial_time]['foto_equipo']
                if fill_areas_parciales_info[indice_inicio]["estado"] != "finish":
                    ax.plot(end_partial_time, diff_scores[i], '*', color=color, markersize=8, markeredgecolor='gold')          
                    ax.axvline(x=end_partial_time, color=color, linestyle='--', linewidth=0.5, alpha=0.5)
                    colorear_areas_rachas(event_times[i])
                    fill_areas_parciales_info[indice_inicio]["estado"] = "finish"                  
                    ax.text(tiempo_inicio + (end_partial_time-tiempo_inicio)/2, y_max_evol - 0.54*(y_max_evol-ymax), texto_fijo1, color="black", fontsize=12, va="center", ha="center", zorder=7)
                    add_image_circular(ax, foto_equipo, tiempo_inicio + (end_partial_time-tiempo_inicio)/2, y_max_evol - 0.7*(y_max_evol-ymax), 1)                  
                    ax.text(tiempo_inicio + (end_partial_time-tiempo_inicio)/2, y_max_evol - 0.91*(y_max_evol-ymax), texto_fijo2, color="black", fontsize=12, va="center", ha="center", zorder=7)

        colorear_areas_parciales(event_times[i])

        ###################   FIN  PARCIALES  ########################################  

        if len(impactoPlayer_starts) == 0:
            ###################       RACHAS      ########################################  
            for start_racha_time in racha_starts:
                if start_racha_time == event_times[i]:  # Solo si el inicio del parcial está en el tiempo actual
                    color = racha_starts[start_racha_time]['color']
                    text_color = get_text_color(color)
                    tiempo_fin = racha_starts[start_racha_time]['tiempo_fin']
                    ax.plot(start_racha_time, diff_scores[i], 'o', color=color, markersize=8, markeredgecolor='gold')
                    #parcial_text = ax.text(x_center, y_center, texto, color=text_color, fontsize=20, ha="center", bbox=dict(facecolor=color, alpha=0.8))                
                    ax.axvline(x=start_racha_time, color=color, linestyle='--', linewidth=0.5, alpha=0.5, zorder=5)
                    # Reproducir el texto 
                    #parcial_text.remove()
                    fill_areas_rachas_info[start_racha_time] = {
                                                                    "estado": "running",
                                                                    "color": color,
                                                                    "text_color": text_color,
                                                                    "time_init": start_racha_time,
                                                                    "time_finish": tiempo_fin
                                                                }

            for end_racha_time in racha_ends:
                if end_racha_time == event_times[i]:  # Solo si el final del parcial está en el tiempo actual
                    color = racha_ends[end_racha_time]['color']
                    text_color = get_text_color(color)
                    indice_inicio = racha_ends[end_racha_time]['indice_inicio']
                    foto_cara_jugador = racha_ends[end_racha_time]['foto_cara_jugador']
                    tiempo_inicio = racha_ends[end_racha_time]['tiempo_inicio']
                    texto_fijo = racha_ends[end_racha_time]['texto_fijo']
                    if fill_areas_rachas_info[indice_inicio]["estado"] != "finish":
                        ax.plot(end_racha_time, diff_scores[i], 'o', color=color, markersize=8, markeredgecolor='gold')
                        ax.axvline(x=end_racha_time, color=color, linestyle='--', linewidth=0.5, alpha=0.5)
                        colorear_areas_rachas(event_times[i])
                        fill_areas_rachas_info[indice_inicio]["estado"] = "finish"
                        # Mostrar la imagen circular en la animación
                        add_image_circular(ax, foto_cara_jugador, tiempo_inicio + (end_racha_time-tiempo_inicio)/2, y_max_evol - 0.085*(y_max_evol-ymax), 0.27)
                        ax.text(tiempo_inicio + (end_racha_time-tiempo_inicio)/2, y_max_evol - 0.315*(y_max_evol-ymax), texto_fijo, color="black", fontsize=12, va="center", ha="center", zorder=7)
            
            
            ###################   FIN  RACHAS  ########################################  


        else:

            ###################       IMPACTO PLAYERS      ########################################  
            for start_impactoPlayer_time in impactoPlayer_starts:
                if start_impactoPlayer_time == event_times[i]:  # Solo si el inicio del parcial está en el tiempo actual Y pintarTexto (duracion > 2mins)
                    color = impactoPlayer_starts[start_impactoPlayer_time]['color']
                    text_color = "black"
                    tiempo_fin = impactoPlayer_starts[start_impactoPlayer_time]['tiempo_fin']
                    ax.plot(start_impactoPlayer_time, diff_scores[i], 'o', color=color, markersize=8, markeredgecolor='gold')
                    #parcial_text = ax.text(x_center, y_center, texto, color=text_color, fontsize=20, ha="center", bbox=dict(facecolor=color, alpha=0.8))                
                    ax.axvline(x=start_impactoPlayer_time, color=color, linestyle='-', linewidth=1, alpha=0.75, zorder=5)
                    # Reproducir el texto 
                    #parcial_text.remove()
                    fill_areas_impactoPlayer_info[start_impactoPlayer_time] = {
                                                                    "estado": "running",
                                                                    "color": color,
                                                                    "text_color": text_color,
                                                                    "time_init": start_impactoPlayer_time,
                                                                    "time_finish": tiempo_fin
                                                                }

            for end_impactoPlayer_time in impactoPlayer_ends:
                if end_impactoPlayer_time == event_times[i]:  # Solo si el final del parcial está en el tiempo actual
                    color = impactoPlayer_starts[start_impactoPlayer_time]['color']
                    indice_inicio = impactoPlayer_ends[end_impactoPlayer_time]['indice_inicio']
                    tiempo_inicio = impactoPlayer_ends[end_impactoPlayer_time]['tiempo_inicio']
                    texto_fijo = impactoPlayer_ends[end_impactoPlayer_time]['texto_fijo']
                    if fill_areas_impactoPlayer_info[indice_inicio]["estado"] != "finish":
                        ax.plot(end_impactoPlayer_time, diff_scores[i], 'x', color=color, markersize=8, markeredgecolor='gold')
                        ax.axvline(x=end_impactoPlayer_time, color=color, linestyle='-', linewidth=1, alpha=0.75)
                        colorear_areas_rachas(event_times[i])
                        fill_areas_impactoPlayer_info[indice_inicio]["estado"] = "finish"
                        if impactoPlayer_ends[end_impactoPlayer_time]['pintarTexto']:
                            ax.text(tiempo_inicio + (end_impactoPlayer_time-tiempo_inicio)/2, y_max_evol - 0.22*(y_max_evol-ymax), texto_fijo, color="black", fontsize=12, va="center", ha="center", zorder=7)
                   
             ###################   FIN  IMPACTO PLAYERS  ########################################  

                    
        colorear_areas_rachas(event_times[i])
        colorear_areas_impactoPlayer(event_times[i])

        

        ### Finales de cuarto/partido
        if type_play[i] == "end":
            scoreA = str(scoreTeamA[i])
            scoreB = str(scoreTeamB[i])
            if periodo == '2':
                ax.text(quarter_times[0]- 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreA, color=teams_colors[0], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                ax.text(quarter_times[0], ymax - 0.075*(y_max_evol-ymin), '-', color='black', fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                ax.text(quarter_times[0]+ 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreB, color=teams_colors[1], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
            elif periodo == '3':
                ax.text(quarter_times[1]- 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreA, color=teams_colors[0], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                ax.text(quarter_times[1], ymax - 0.075*(y_max_evol-ymin), '-', color='black', fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                ax.text(quarter_times[1]+ 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreB, color=teams_colors[1], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
            elif periodo == '4':
                if i != len(event_times)-1:
                    ax.text(quarter_times[2]- 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreA, color=teams_colors[0], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                    ax.text(quarter_times[2], ymax - 0.075*(y_max_evol-ymin), '-', color='black', fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                    ax.text(quarter_times[2]+ 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreB, color=teams_colors[1], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                else:
                    ax.text(quarter_times[3]- 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreA, color=teams_colors[0], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                    ax.text(quarter_times[2], ymax - 0.075*(y_max_evol-ymin), '-', color='black', fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')
                    ax.text(quarter_times[3]+ 0.05*(x_center), ymax - 0.075*(y_max_evol-ymin), scoreB, color=teams_colors[1], fontsize=12, va="center", ha="center", zorder=7, fontweight='bold')


        return line,

    # Crear la animación
    ani = animation.FuncAnimation(fig, animate, frames=len(event_times), init_func=init,
                                blit=True, interval=1, repeat=False)
    
    # Guardar el último cuadro después de la animación
    ani.save('temp/animacion.gif', writer='pillow', fps=1)  # Guarda la animación completa en GI

    # Guardar la animación como MP4
    if len(impactoPlayer_starts) == 0:
        fig.savefig('temp/'+selected_game+'.png') 
    else:
        fig.savefig('temp/'+selected_game+'_player.png') 

    plt.close(fig)

    # Detener la música cuando termine la animación
    #pygame.mixer.music.stop()