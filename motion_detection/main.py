import time
import os
import logging

import cv2

from recorder import Recorder
from motion_detector import MotionDetector
from utils import init_logger, SignalException, set_signal


# 高速化のための解像度リサイズ
RESIZE_SHAPE = (640, 360)

# 映像の設定
VIDEO_DEVICE = int(os.environ["VIDEO_DEVICE"])

# フレームスキップ
FRAME_SKIP_RATIO = int(os.environ.get("FRAME_SKIP_RATIO", 5))

# 閾値
DIFF_THRESHOLD = int(os.environ.get("DIFF_THRESHOLD", 30))
SIZE_THRESHOLD = int(os.environ.get("SIZE_THRESHOLD", 1000))

# この設定値以上、動体を連続して検知できなかった場合、録画を終了する
RECORD_STOP_SEC = float(os.environ.get("RECORD_STOP_SEC", 5))


logger = logging.getLogger(__name__)


def detect_and_record():
    """動体検知を実行し、検知したら録画を開始する
    """
    cap = cv2.VideoCapture(VIDEO_DEVICE)
    recorder = None
    not_detected_start_time = time.time()  # 動体を検知しなくなった時刻

    try:
        md = MotionDetector(RESIZE_SHAPE, DIFF_THRESHOLD, SIZE_THRESHOLD)
        counter = -1
        while True:
            # 1フレームずつ取得する
            ret, frame = cap.read()
            if ret is False:
                return

            # フレームスキップ
            counter += 1
            if counter % FRAME_SKIP_RATIO != 0:
                continue
            else:
                counter = 0

            ret = md.detect(frame)
            # 検知
            if ret is True:
                if not_detected_start_time is not None:
                    not_detected_start_time = None
                # 録画開始
                if recorder is None:
                    recorder = Recorder()
                    recorder.start()
            # 非検知
            else:
                if recorder is not None:
                    if not_detected_start_time is None:
                        not_detected_start_time = time.time()
                    # 録画終了
                    elif time.time() - not_detected_start_time > RECORD_STOP_SEC:
                        recorder.stop()
                        recorder = None

    finally:
        cap.release()
        if recorder is not None:
            recorder.stop()


if __name__ == "__main__":
    # ロガーの初期化
    init_logger()
    # シグナルハンドラの設定
    set_signal()

    recv_signal = False
    while True:
        try:
            detect_and_record()
        except SignalException:
            logger.info("detection stop")
            recv_signal = True
            break
        except Exception as e:
            logger.exception(e)
        finally:
            if recv_signal is False:
                retry_sec = 3
                logger.info("Retry after %s sec", retry_sec)
                time.sleep(retry_sec)
