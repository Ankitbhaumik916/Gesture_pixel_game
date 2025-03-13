import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# Use DroidCam (Change IP if needed)
DROIDCAM_IP = "192.168.1.100"  # Replace with your actual IP
cap = cv2.VideoCapture(0)  # Uses USB connection as default webcam


# Push-up tracking variables
pushup_count = 0
pushup_state = "UP"  # 'UP' means user is at the top, 'DOWN' means at the bottom

def calculate_angle(a, b, c):
    """Calculate angle between three points using cosine rule."""
    a = np.array(a)  # First point
    b = np.array(b)  # Middle point (joint)
    c = np.array(c)  # Last point

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))  # Clip to avoid errors
    return np.degrees(angle)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Check DroidCam connection!")
        break

    # Convert image to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        # Extract landmark points
        landmarks = results.pose_landmarks.landmark

        # Get required points (shoulder, elbow, wrist)
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        # Calculate elbow angle
        angle = calculate_angle(shoulder, elbow, wrist)

        # Push-up detection logic
        if angle < 60:  # Arms bent → Down position
            if pushup_state == "UP":
                pushup_state = "DOWN"
        
        if angle > 160:  # Arms straight → Up position
            if pushup_state == "DOWN":
                pushup_state = "UP"
                pushup_count += 1  # Count only when moving up

        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Display push-up count
        cv2.putText(frame, f"Push-ups: {pushup_count}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    # Show live feed
    cv2.imshow("Push-Up Counter", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
