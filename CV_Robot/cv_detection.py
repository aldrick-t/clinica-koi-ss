import cv2
import mediapipe as mp
import math
import paho.mqtt.client as mqtt

# MQTT Config
BROKER = "localhost"  # Cambia por la IP de tu ESP32/MQTT broker
PORT = 1883
TOPIC = "car/control"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# MediaPipe config
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a = [a.x, a.y]
    b = [b.x, b.y]
    c = [c.x, c.y]
    ab = [a[0]-b[0], a[1]-b[1]]
    cb = [c[0]-b[0], c[1]-b[1]]
    dot = ab[0]*cb[0] + ab[1]*cb[1]
    norm_ab = math.hypot(*ab)
    norm_cb = math.hypot(*cb)
    return math.degrees(math.acos(dot / (norm_ab * norm_cb)))

def detect_gesture(landmarks):
    if not landmarks:
        return "no_person"

    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    le = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    re = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    # Brazo cruzado
    if lw.x > rs.x and rw.x < ls.x:
        return "stop" # Cuando curce el brazo izquierdo hacia la derecha y el derecho hacia la izquierda
    
    if lw.y < nose.y and rw.y < nose.y:
        return "forward" # Cuando ambos brazos están arriba de la cabeza
    if lw.y > ls.y and rw.y > rs.y:
        return "backward"
    if lw.x < ls.x and rw.y > rs.y:
        return "left"
    if rw.x > rs.x and lw.y > ls.y:
        return "right"
    
    left_angle = calculate_angle(ls, le, lw)
    right_angle = calculate_angle(rs, re, rw)
    if left_angle < 60 and right_angle < 60:
        return "light_on"

    return "idle"

# Webcam loop
cap = cv2.VideoCapture(0)
last_command = ""

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark
        gesture = detect_gesture(landmarks)

        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.putText(frame, f'Gesture: {gesture}', (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)

        if gesture != last_command and gesture not in ["idle", "no_person"]:
            client.publish(TOPIC, gesture)
            print(f"Sent command: {gesture}")
            last_command = gesture

    cv2.imshow("Pose Control", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client.disconnect()
