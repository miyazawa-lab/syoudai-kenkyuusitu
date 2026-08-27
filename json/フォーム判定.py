import cv2
import mediapipe as mp
import json
import os
import math


# =========================
# 角度を計算する関数
# =========================

def calculate_angle(a, b, c):

    # a→b と c→b の角度を計算
    angle = math.degrees(
        math.atan2(c.y - b.y, c.x - b.x)
        -
        math.atan2(a.y - b.y, a.x - b.x)
    )

    # マイナスになった場合は正の値にする
    angle = abs(angle)

    # 180度を超えた場合の調整
    if angle > 180:
        angle = 360 - angle

    return angle


base_dir = os.path.dirname(__file__)
json_path = os.path.join(base_dir, "squat.json")

with open(json_path, "r", encoding="utf-8") as f:
    config = json.load(f)

    print(config)

# =========================
# JSONから理想角度を取得
# =========================

target_angle = config["angles"]["left_knee"]

# 許容誤差
tolerance = config["tolerance"]

print("左膝の理想角度:", target_angle)
print("許容誤差:", tolerance)


mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose()

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

         # -------------------------
        # 関節座標の取得
        # -------------------------

        # 左腰
        left_hip = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.LEFT_HIP
        ]

        # 左膝
        left_knee = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.LEFT_KNEE
        ]

        # 左足首
        left_ankle = results.pose_landmarks.landmark[
            mp_pose.PoseLandmark.LEFT_ANKLE
        ]

        # 座標を表示
        print(
            "左腰:",
            left_hip.x,
            left_hip.y,
            left_hip.z
        )

        print(
            "左膝:",
            left_knee.x,
            left_knee.y,
            left_knee.z
        )

        print(
            "左足首:",
            left_ankle.x,
            left_ankle.y,
            left_ankle.z
        )

        # =========================
# 左膝の角度を計算
# =========================

        left_knee_angle = calculate_angle(
        left_hip,
        left_knee,
        left_ankle
)

print("左膝の角度:", left_knee_angle)

 # =========================
        # 理想角度との差を計算
        # =========================

        difference = abs(
            left_knee_angle - target_angle
        )


        # =========================
        # フォームを評価
        # =========================

        if difference <= tolerance:

            feedback = "フォームは良好です"

        else:

            feedback = "左膝の角度を調整してください"


        # =========================
        # 結果をターミナルに表示
        # =========================

        print(
            "左膝:",
            round(left_knee_angle, 1),
            "度",
            "差:",
            round(difference, 1),
            "度",
            feedback
        )


        # =========================
        # 画面に表示
        # =========================

        cv2.putText(
            frame,
            f"Left Knee: {left_knee_angle:.1f} deg",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            feedback,
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        cv2.imshow("Pose Detection", frame

            if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()