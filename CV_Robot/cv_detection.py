import cv2
import mediapipe as mp
import math

# Configuración de MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    # Calcula el ángulo entre 3 puntos (hombro, codo, muñeca)
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

    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    # Coordenadas Y
    lw_y = left_wrist.y
    rw_y = right_wrist.y
    ls_y = left_shoulder.y
    rs_y = right_shoulder.y
    nose_y = nose.y

    # Gestos
    if lw_y < nose_y and rw_y < nose_y:
        return "forward"
    if lw_y > ls_y and rw_y > rs_y:
        return "backward"
    if left_wrist.x < left_shoulder.x and rw_y > rs_y:
        return "left"
    if right_wrist.x > right_shoulder.x and lw_y > ls_y:
        return "right"
    if left_wrist.x > right_shoulder.x and right_wrist.x < left_shoulder.x:
        return "stop"

    # "Strong pose" = ángulo de codo muy cerrado
    left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
    if left_angle < 60 and right_angle < 60:
        return "strong"

    return "idle"

# Captura de video
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Procesamiento
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(frame_rgb)

    if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark
        gesture = detect_gesture(landmarks)

        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.putText(frame, f'Gesture: {gesture}', (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)

        # Aquí iría el envío al ESP32, por ejemplo:
        # send_to_esp32(gesture)

    cv2.imshow("Pose Control", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
