import pygame
import random
import cv2
import mediapipe as mp
import time
import math

# Initialize pygame & sound
pygame.init()
pygame.mixer.init()

# Load sound effects
jump_sound = pygame.mixer.Sound("jump.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")

# Game Constants
WIDTH, HEIGHT = 500, 600
PLAYER_SIZE = 50
ENEMY_SIZE = 50
BASE_SPEED = 3
JUMP_VELOCITY = -15
GRAVITY = 5
POWERUP_DURATION = 5000  # Milliseconds (5 seconds)
SPEED_INCREMENT_TIME = 10000  # Milliseconds (10 seconds)
FLOOR_Y = HEIGHT - PLAYER_SIZE - 10

# Colors
WHITE, RED, BLUE, GREEN = (255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 255, 0)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture-Controlled AI Enemy Game")

# Player
player = pygame.Rect(WIDTH // 2, FLOOR_Y, PLAYER_SIZE, PLAYER_SIZE)
player_velocity, is_jumping = 0, False

# Enemies
enemies = [pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), random.randint(-300, -50), ENEMY_SIZE, ENEMY_SIZE) for _ in range(3)]

# Power-up Variables
powerup_active, powerup_start_time = False, 0
speed, last_speed_increase_time = BASE_SPEED, pygame.time.get_ticks()

# Initialize OpenCV and MediaPipe Hands
mp_hands, mp_draw = mp.solutions.hands, mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()

    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Reset gesture flags
    jump_detected, powerup_detected = False, False

    # If hand detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x  
            player.x = max(0, min(WIDTH - PLAYER_SIZE, int(index_finger_x * WIDTH) - PLAYER_SIZE // 2))

            # Jump Detection (Thumbs-up)
            if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].y:
                jump_detected = True

            # Power-up Detection (Open Palm)
            fingers_up = sum(hand_landmarks.landmark[i * 4].y < hand_landmarks.landmark[i * 4 + 2].y for i in range(5))
            powerup_detected = fingers_up >= 4

            # Draw Hand Landmarks (Optional)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Jump Logic
    if jump_detected and not is_jumping:
        player_velocity, is_jumping = JUMP_VELOCITY, True
        jump_sound.play()

    # Apply Gravity
    player.y += player_velocity
    player_velocity += GRAVITY

    # Prevent Player from Falling Below Floor
    if player.y >= FLOOR_Y:
        player.y, is_jumping = FLOOR_Y, False

    # Activate Power-up
    if powerup_detected and not powerup_active:
        powerup_active, powerup_start_time = True, current_time
        powerup_sound.play()

    # Deactivate Power-up after Time
    if powerup_active and current_time - powerup_start_time > POWERUP_DURATION:
        powerup_active = False

    # Increase enemy speed every SPEED_INCREMENT_TIME
    if current_time - last_speed_increase_time > SPEED_INCREMENT_TIME:
        speed += 1
        last_speed_increase_time = current_time

    # Move AI Enemies toward Player
    for enemy in enemies:
        enemy.x += math.copysign(speed, player.x - enemy.x)  # Move towards player
        enemy.y += speed

        # Respawn enemy if it goes off screen
        if enemy.y > HEIGHT:
            enemy.y, enemy.x = random.randint(-300, -50), random.randint(0, WIDTH - ENEMY_SIZE)

        # Collision Detection (Disabled if Power-up Active)
        if not powerup_active and player.colliderect(enemy):
            running = False

    # Draw Player & Enemies
    pygame.draw.rect(screen, GREEN if powerup_active else BLUE, player)
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
