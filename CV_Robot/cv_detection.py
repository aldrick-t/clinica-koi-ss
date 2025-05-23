import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt

# Configuración MQTT
BROKER = "localhost"
PORT = 1883
TOPIC = "car/control"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# Configuración MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Tamaño del frame (se actualizará)
ancho_frame = 0
alto_frame = 0

# Definición de zonas (se actualizarán)
zonas = {
    "stop": None,
    "forward": None,
    "backward": None,
    "left": None,
    "right": None
}

def dibujar_zonas(frame):
    """Dibuja las zonas con estilo cuadricular y textos en español"""
    for nombre_zona, rect_zona in zonas.items():
        if rect_zona:
            # Configuración de colores y estilos
            color = (0, 255, 0)  # Verde para la mayoría
            grosor = 2
            
            if nombre_zona == "stop":
                color = (0, 0, 255)  # Rojo para stop
                grosor = 3
            
            # Dibujar rectángulo de zona
            cv2.rectangle(frame, rect_zona[0], rect_zona[1], color, grosor)
            
            # Dibujar fondo semitransparente para el texto
            texto_tam = cv2.getTextSize(nombre_zona.upper(), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(frame, 
                         (rect_zona[0][0], rect_zona[0][1] - texto_tam[1] - 10),
                         (rect_zona[0][0] + texto_tam[0] + 10, rect_zona[0][1]),
                         color, -1)
            
            # Dibujar texto en mayúsculas
            cv2.putText(frame, nombre_zona.upper(), 
                       (rect_zona[0][0] + 5, rect_zona[0][1] - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def inicializar_zonas():
    """Inicializa las zonas en disposición cuadricular"""
    global zonas
    
    margen = 20
    ancho_zona = int(ancho_frame * 0.2)
    alto_zona = int(alto_frame * 0.3)
    
    # Disposición cuadricular de 3x2
    zonas["forward"] = [  # Arriba left
        (int(ancho_frame/2 - ancho_zona/2), margen),
        (int(ancho_frame/2 + ancho_zona/2), margen + alto_zona)
    ]
    
    zonas["stop"] = [  # Centro centro
        (int(ancho_frame/2 - ancho_zona/2), int(alto_frame/2 - (alto_zona*.95)/2)),
        (int(ancho_frame/2 + ancho_zona/2), int(alto_frame/2 + (alto_zona*.95)/2))
    ]
 
    
    zonas["backward"] = [  # Abajo centro
        (int(ancho_frame/2 - ancho_zona/2), alto_frame - margen - alto_zona),
        (int(ancho_frame/2 + ancho_zona/2), alto_frame - margen)
    ]

        
    zonas["left"] = [  # Centro left
        (margen, int(alto_frame/2 - (alto_zona*.95)/2)),
        (margen + ancho_zona, int(alto_frame/2 + (alto_zona*.95)/2))
    ]
    
    zonas["right"] = [  # Abajo right
        (ancho_frame - margen - ancho_zona, int(alto_frame/2 - (alto_zona*.95)/2)),
        (ancho_frame - margen, int(alto_frame/2 + (alto_zona*.95)/2))
    ]

def mano_en_zona(pos_mano, zona):
    """Determina si una mano está dentro de una zona"""
    if zona is None or pos_mano is None:
        return False
    x, y = pos_mano
    return (zona[0][0] <= x <= zona[1][0]) and (zona[0][1] <= y <= zona[1][1])

def detectar_gesto(landmarks):
    """Detecta en qué zona está cada mano"""
    if not landmarks:
        return "sin_persona"

    lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    
    # Convertir coordenadas normalizadas a píxeles
    pos_mano_izq = (int(lw.x * ancho_frame), int(lw.y * alto_frame))
    pos_mano_der = (int(rw.x * ancho_frame), int(rw.y * alto_frame))
    
    # Verificar manos en zonas
    for nombre_zona, rect_zona in zonas.items():
        if mano_en_zona(pos_mano_izq, rect_zona) or mano_en_zona(pos_mano_der, rect_zona):
            return nombre_zona
    
    return "inactivo"

# Bucle principal
cap = cv2.VideoCapture(0)
ultimo_comando = ""
cv2.namedWindow("Control por Gestos", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Control por Gestos", 1280, 960)  # Ancho, Alto
while cap.isOpened():
    exito, frame = cap.read()
    if not exito:
        break
    frame = cv2.resize(frame, (1280,960))  # Antes de procesarlo
    # espejear imagen
    frame = cv2.flip(frame, 1)  # Espejear horizontalmente
    # Actualizar tamaño del frame
    alto_frame, ancho_frame = frame.shape[:2]
    if zonas["stop"] is None or zonas["stop"][1][0] > ancho_frame:
        zonas = {k: None for k in zonas}  # Reiniciar zonas si el tamaño cambió
        inicializar_zonas()

    # Procesamiento de pose
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = pose.process(rgb)

    if resultado.pose_landmarks:
        landmarks = resultado.pose_landmarks.landmark
        gesto = detectar_gesto(landmarks)

        # Dibujar elementos
        mp_drawing.draw_landmarks(frame, resultado.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        dibujar_zonas(frame)
        
        # Mostrar comando actual
        cv2.putText(frame, f'Comando: {gesto.upper()}', (30, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        if gesto == "inactivo":
            gesto = "stop"

        # Enviar comando si cambió
        if gesto != ultimo_comando:
            client.publish(TOPIC, gesto)
            print(f"Comando enviado: {gesto}")
            ultimo_comando = gesto
        

    # Mostrar frame
    cv2.imshow("Control por Gestos", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break


# Liberar recursos
cap.release()
cv2.destroyAllWindows()
client.disconnect()