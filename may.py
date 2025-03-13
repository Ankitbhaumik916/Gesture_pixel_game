import pygame
import random
import cv2
import mediapipe as mp

# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 500, 600
PLAYER_SIZE = 50
ENEMY_SIZE = 50
SPEED = 5

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture-Controlled Dodge Game")

# Player
player = pygame.Rect(WIDTH // 2, HEIGHT - PLAYER_SIZE - 10, PLAYER_SIZE, PLAYER_SIZE)

# Enemy List
enemies = []
for _ in range(5):
    x_pos = random.randint(0, WIDTH - ENEMY_SIZE)
    enemies.append(pygame.Rect(x_pos, random.randint(-300, -50), ENEMY_SIZE, ENEMY_SIZE))

# Initialize OpenCV and MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hand tracking
    results = hands.process(rgb_frame)

    # If hand detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get x-coordinate of index finger tip
            index_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x  
            
            # Map hand x-position to game screen width
            player.x = int(index_finger_x * WIDTH) - PLAYER_SIZE // 2

            # Draw hand landmarks (optional)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Move Enemies
    for enemy in enemies:
        enemy.y += SPEED
        if enemy.y > HEIGHT:
            enemy.y = random.randint(-300, -50)
            enemy.x = random.randint(0, WIDTH - ENEMY_SIZE)

        # Collision Detection
        if player.colliderect(enemy):
            running = False

    # Draw Player and Enemies
    pygame.draw.rect(screen, BLUE, player)
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

    pygame.display.flip()
    clock.tick(30)  # FPS

    # Show webcam feed
    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
