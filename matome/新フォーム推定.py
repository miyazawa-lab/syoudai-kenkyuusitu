import cv2
import mediapipe as mp
import json
import os
import math
import time





# 角度を計算する関数

def calculate_angle(a, b, c):

    angle = math.degrees(
        math.atan2(c.y - b.y, c.x - b.x)
        -
        math.atan2(a.y - b.y, a.x - b.x)
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle



# JSONファイルを読み込む

base_dir = os.path.dirname(__file__)
json_path = os.path.join(base_dir, "squat.json")

with open(json_path, "r", encoding="utf-8") as f:
    config = json.load(f)

print("読み込んだ設定:")
print(config)



# JSONから設定を取得

left_target_angle = config["angles"]["left_knee"]
right_target_angle = config["angles"]["right_knee"]

tolerance = config["tolerance"]

print("左膝の理想角度:", left_target_angle)
print("右膝の理想角度:", right_target_angle)
print("許容誤差:", tolerance)



# MediaPipeの準備
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils


pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

total_processing_time = 0
frame_count = 0


while True:

    
    # カメラから画像を取得
    
    start_time = time.perf_counter()

    ret, frame = cap.read()

    if not ret:
        print("カメラから映像を取得できません")
        break


   
    # BGR → RGB
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    
    # 姿勢推定
    
    results = pose.process(rgb)


    
    # 人体が検出された場合
    
    if results.pose_landmarks:

        # 骨格を画面に表示
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )


        
        # 左側の関節座標を取得
       
        left_hip = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.LEFT_HIP
        ]

        left_knee = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.LEFT_KNEE
        ]

        left_ankle = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.LEFT_ANKLE
        ]


       
        # 右側の関節座標を取得
        

        right_hip = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.RIGHT_HIP
        ]

        right_knee = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.RIGHT_KNEE
        ]

        right_ankle = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.RIGHT_ANKLE
        ]


        
        # 左膝の角度を計算
        

        left_knee_angle = calculate_angle(
            left_hip,
            left_knee,
            left_ankle
        )


        # 右膝の角度を計算
       
        right_knee_angle = calculate_angle(
            right_hip,
            right_knee,
            right_ankle
        )


        
        # 理想角度との差を計算
        

        left_difference = abs(
            left_knee_angle - left_target_angle
        )

        right_difference = abs(
            right_knee_angle - right_target_angle
        )


        
        # 左膝のフォーム判定
        
        if left_difference <= tolerance:
            left_feedback = "左膝：良好"
        elif left_knee_angle > left_target_angle:
            left_feedback = "左膝：もう少し曲げてください"
        else:
            left_feedback = "左膝：少し伸ばしてください"


        
        # 右膝のフォーム判定
        
        if right_difference <= tolerance:
            right_feedback = "右膝：良好"
        elif right_knee_angle > right_target_angle:
            right_feedback = "右膝：もう少し曲げてください"
        else:
            right_feedback = "右膝：少し伸ばしてください"


       
        # ターミナルに結果を表示
        

        print(
            "左膝:",
            round(left_knee_angle, 1),
            "度",
            "差:",
            round(left_difference, 1),
            "度",
            left_feedback
        )

        print(
            "右膝:",
            round(right_knee_angle, 1),
            "度",
            "差:",
            round(right_difference, 1),
            "度",
            right_feedback
        )


        
        # カメラ画面に左膝角度を表示
        cv2.putText(
       frame,
        f"Left Knee: {left_knee_angle:.1f} deg",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
        )


        
        # カメラ画面に右膝角度を表示
        
        cv2.putText(
            frame,
            f"Right Knee: {right_knee_angle:.1f} deg",
            (30, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )



          
          # 処理時間・FPS計測
         

        end_time = time.perf_counter()

        processing_time = end_time - start_time

        total_processing_time += processing_time
        frame_count += 1

        fps = 1 / processing_time





        
        # フォーム判定を表示
        

        cv2.putText(
            frame,
            left_feedback,
            (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            right_feedback,
            (30, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    
    # カメラ映像を表示
    

    cv2.imshow("Pose Detection", frame)


    
    # qで終了
   
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break



# 終了処理

if frame_count > 0:
    average_time = total_processing_time / frame_count
    average_time_ms = average_time * 1000
    average_fps = 1 / average_time

    print("=========================")
    print("処理フレーム数:", frame_count)
    print("平均処理時間:", round(average_time_ms, 2), "ms")
    print("平均FPS:", round(average_fps, 2), "fps")
    print("=========================")

cap.release()
cv2.destroyAllWindows()
pose.close()