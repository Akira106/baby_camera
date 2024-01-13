import cv2
import numpy as np


class MotionDetector():
    """動体検知をするクラス

    以下のコードを参考にしています
    https://piccalog.net/python/detect-airplane-opencv
    """
    def __init__(self, resize_shape, diff_threshold, size_threshold):
        """コンストラクタ

        Args:
            device_num (int):
                映像デバイスの番号
            resize_shape (tuple(int, int)):
                リサイズ後の解像度(width, height)
            diff_threshold (int):
                画素値の差分の閾値
            size_threshold (int):
                動体サイズの閾値
        """
        self.resize_shape = resize_shape
        self.diff_threshold = diff_threshold
        self.size_threshold = size_threshold

        # 比較対象のフレーム
        self.frame_old = None

    def detect(self, frame):
        """動体検知

        Args:
            frame (ndarray((height, width, 3), dtype=np.uint8)):
                入力フレーム

        Returns:
            bool: 動体の有無
        """
        # リサイズ
        frame = cv2.resize(frame, self.resize_shape)
        # グレースケールに変換
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 比較用のフレームを取得する
        if self.frame_old is None:
            self.frame_old = gray.astype("float")
            return False

        # ブラーを掛けてノイズを軽減する
        blur = cv2.GaussianBlur(gray, (1, 1), 1)
        # 現在のフレームと移動平均との差を計算
        cv2.accumulateWeighted(blur, self.frame_old, 0.5)
        frameDelta = cv2.absdiff(blur, self.frame_old.astype(np.uint8))
        # デルタ画像を閾値処理を行う
        thresh = cv2.threshold(frameDelta, self.diff_threshold, 255, cv2.THRESH_BINARY)[1]
        # 画像の閾値に輪郭線を入れる
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        for i in range(0, len(contours)):
            if len(contours[i]) > 0:
                # しきい値より小さい領域は無視する
                if cv2.contourArea(contours[i]) < self.size_threshold:
                    continue
                else:
                    # 動体を検知
                    return True

        return False
