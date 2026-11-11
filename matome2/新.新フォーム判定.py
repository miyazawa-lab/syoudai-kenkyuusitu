import cv2
import mediapipe as mp
import json
import os
import math
from PIL import Image, ImageDraw, ImageFont


def calculate_angle(a, b, c):
    """3つのランドマークから関節角度を計算。"""
    angle = math.degrees(
        math.atan2(c.y - b.y, c.x - b.x)
        - math.atan2(a.y - b.y, a.x - b.x)
    )
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle
    return angle


def put_japanese_text(frame, text, position, color, size=25):
    """Pillowを使用して日本語を描画。"""
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(
        "C:/Windows/Fonts/meiryo.ttc",
        size
    )

    draw.text(position, text, font=font, fill=color)

    return cv2.cvtColor(
        __import__("numpy").array(img),
        cv2.COLOR_RGB2BGR
    )


def load_config():
    """JSONを読み込む。"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filename = input(
        "JSONファイル名を入力してください "
        "(squat.json / benchpress.json / pushup.json / armcurl.json): "
    ).strip()

    if not filename.lower().endswith(".json"):
        filename += ".json"

    json_path = os.path.join(base_dir, filename)

    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not config.get("angles"):
        raise ValueError("JSONの angles に評価項目がありません。")

    return config


def calculate_evaluations(
    landmarks,
    evaluations,
    mp_pose,
    default_tolerance=10
):
    """JSONの評価項目を処理し、角度と個別判定を返す。"""
    results = []

    for evaluation in evaluations:
        point_ids = [
            getattr(mp_pose.PoseLandmark, point_name)
            for point_name in evaluation["points"]
        ]

        a = landmarks[point_ids[0].value]
        b = landmarks[point_ids[1].value]
        c = landmarks[point_ids[2].value]

        angle = calculate_angle(a, b, c)
        target = float(evaluation["target"])
        difference = abs(angle - target)

        # 項目ごとのtoleranceがあれば優先し、なければJSON全体の値を使用
        tolerance = float(
            evaluation.get("tolerance", default_tolerance)
        )

        results.append({
            "name": evaluation["name"],
            "angle": angle,
            "difference": difference,
            "within_range": difference <= tolerance,
            "feedback": evaluation.get(
                "feedback",
                "角度を調整してください"
            )
        })

    return results


def judge_overall(evaluation_results):
    """すべての評価項目が許容範囲内か判定する。"""
    if not evaluation_results:
        return "未判定", False

    all_within_range = all(
        item["within_range"] for item in evaluation_results
    )

    if all_within_range:
        return "総合判定：基準範囲内", True

    return "総合判定：要確認", False


def main():
    config = load_config()
    tolerance = float(config.get("tolerance", 10))
    evaluations = config["angles"]

    print("読み込んだ種目:", config.get("exercise", "未設定"))
    print("共通評価処理を開始します。")
    print("評価項目数:", len(evaluations))

    mp_pose = mp.solutions.pose
    mp_draw = mp.solutions.drawing_utils

    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("カメラを開けませんでした。カメラ接続を確認してください。")
        pose.close()
        return

    previous_overall = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("カメラから映像を取得できません")
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                landmarks = results.pose_landmarks.landmark

                #  個別判定
                evaluation_results = calculate_evaluations(
                    landmarks,
                    evaluations,
                    mp_pose,
                    tolerance
                )

                for i, item in enumerate(evaluation_results):
                    y = 30 + i * 35
                    status = (
                        "Within range"
                        if item["within_range"]
                        else "Adjust"
                    )
                    color = (
                        (0, 255, 0)
                        if item["within_range"]
                        else (0, 0, 255)
                    )

                    cv2.putText(
                        frame,
                        f'{item["name"]}: {item["angle"]:.1f} deg',
                        (20, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 0),
                        2
                    )
                    cv2.putText(
                        frame,
                        status,
                        (350, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        color,
                        2
                    )

                # 総合判定
                overall_text, overall_ok = judge_overall(
                    evaluation_results
                )

                # Pillowの色指定はRGB形式
                overall_color = (
                    (0, 180, 0)
                    if overall_ok
                    else (255, 0, 0)
                )

                frame = put_japanese_text(
                    frame,
                    overall_text,
                    (20, 30 + len(evaluation_results) * 35 + 10),
                    overall_color,
                    25
                )

                # 判定が変わった時だけ表示
                if overall_text != previous_overall:
                    print(overall_text)
                    previous_overall = overall_text

            cv2.imshow("Pose Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        pose.close()


if __name__ == "__main__":
    main()

    