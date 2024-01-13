import subprocess
import time
import os
import logging

from utils import init_logger, SignalException, set_signal

# 映像の設定
INPUT_VIDEO_DEVICE = os.environ["INPUT_VIDEO_DEVICE"]
OUTPUT_VIDEO_DEVICE_1 = os.environ["OUTPUT_VIDEO_DEVICE_1"]
OUTPUT_VIDEO_DEVICE_2 = os.environ["OUTPUT_VIDEO_DEVICE_2"]
WIDTH = os.environ["WIDTH"]
HEIGHT = os.environ["HEIGHT"]
FPS = os.environ["FPS"]

logger = logging.getLogger(__name__)


def loopback():
    """仮想デバイスに映像を流す
    """
    cmd = \
        'ffmpeg -loglevel error ' + \
        '-f v4l2 -s %sx%s -r %s ' % (WIDTH, HEIGHT, FPS) + \
        '-i %s ' % INPUT_VIDEO_DEVICE + \
        '-f v4l2 -vcodec copy %s ' % OUTPUT_VIDEO_DEVICE_1 + \
        '-f v4l2 -vcodec copy %s ' % OUTPUT_VIDEO_DEVICE_2
    try:
        proc = subprocess.Popen("exec " + cmd, shell=True)
        proc.wait()
    finally:
        proc.terminate()


if __name__ == "__main__":
    # ロガーの初期化
    init_logger()
    # シグナルハンドラの設定
    set_signal()

    logger.info("input_video_device=%s", INPUT_VIDEO_DEVICE)
    logger.info("output_video_device_1=%s", OUTPUT_VIDEO_DEVICE_1)
    logger.info("output_video_device_2=%s", OUTPUT_VIDEO_DEVICE_2)
    logger.info("width,height,fps=%s,%s,%s", WIDTH, HEIGHT, FPS)
    logger.info("loopback start")

    recv_signal = False
    while True:
        try:
            loopback()
        except SignalException:
            logger.info("loopback stop")
            recv_signal = True
            break
        except Exception as e:
            logger.exception(e)
        finally:
            if recv_signal is False:
                retry_sec = 3
                logger.info("Retry after %s sec", retry_sec)
                time.sleep(retry_sec)
