
from flask import Flask, render_template, Response
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import time
import random

app = Flask(__name__)
CORS(app)  # Now use CORS

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Define gestures
GESTURES = {"Rock": 0, "Paper": 1, "Scissors": 2}

# Initialize scores
player_score = 0
ai_score = 0
last_comparison_time = time.time()

# Function to classify hand gestures
def classify_hand_landmarks(landmarks):
    fingers = [False] * 5  # Thumb, Index, Middle, Ring, Pinky
    
    # Thumb: Compare tip to IP joint (folded or not)
    fingers[0] = landmarks[4].x > landmarks[3].x  # Adjusted for right hand
    
    # Other fingers: Tip should be higher than PIP joint
    for i, tip_idx in enumerate([8, 12, 16, 20]):
        fingers[i+1] = landmarks[tip_idx].y < landmarks[tip_idx - 2].y
    
    if all(not finger for finger in fingers):
        return "Rock"
    elif all(finger for finger in fingers[1:]):  # Index, middle, ring, pinky are open
        return "Paper"
    elif fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:  # Index and Middle open
        return "Scissors"
    else:
        return "Unknown"

# OpenCV Video Capture
cap = cv2.VideoCapture(0)

def generate_frames():
    global player_score, ai_score, last_comparison_time

    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        player_move = "Unknown"
        ai_move = "Unknown"
        result = "Waiting..."
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                player_move = classify_hand_landmarks(hand_landmarks.landmark)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Compare every 5 seconds
        if time.time() - last_comparison_time > 5:

            ai_move = random.choice(list(GESTURES.keys()))  # AI makes a move
            
            if player_move in GESTURES:
                if player_move == ai_move:
                    result = "Draw"
                elif (GESTURES[player_move] - GESTURES[ai_move]) % 3 == 1:
                    result = "Player Wins!"
                    player_score += 1
                else:
                    result = "AI Wins!"
                    ai_score += 1
            else:
                result = "Invalid Move"
            
            last_comparison_time = time.time()

        # Display results
        cv2.putText(frame, f"Detected: {player_move}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"AI: {ai_move}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"Result: {result}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Display Scores
        cv2.putText(frame, f"Player Score: {player_score}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"AI Score: {ai_score}", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

        # Encode frame for streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
      


