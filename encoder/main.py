import subprocess
import time
import os
import logging

from utils import init_logger, SignalException, set_signal

# 映像の設定
FPS = os.environ["FPS"]
H264ENCODER = os.environ["H264ENCODER"]
GOP_SIZE = os.environ["GOP_SIZE"]
VIDEO_DEVICE = os.environ["VIDEO_DEVICE"]
AUDIO_CARD_NUM = os.environ["AUDIO_CARD_NUM"]
AUDIO_DEVICE = os.environ["AUDIO_DEVICE"]
VIDEO_BITRATE = os.environ.get("VIDEO_BITRATE", "2.4M")
AUDIO_BITRATE = os.environ.get("AUDIO_BITRATE", "128k")

logger = logging.getLogger(__name__)


def encode():
    """映像を取得してエンコードし、mediamtxサーバーに送信する関数
    """
    cmd = \
        'ffmpeg -loglevel warning ' + \
        '-f v4l2 -thread_queue_size 8192 -r %s -i %s ' % (FPS, VIDEO_DEVICE) + \
        '-f alsa -thread_queue_size 8192 -i hw:%s,%s ' % (AUDIO_CARD_NUM, AUDIO_DEVICE) + \
        '-c:v %s -bsf:v h264_mp4toannexb -preset fast -g %s -b:v %s ' % (H264ENCODER, GOP_SIZE, VIDEO_BITRATE) + \
        '-c:a libopus -b:a %s -af "afftdn=nf=-25,highpass=f=200,lowpass=f=3000" ' % AUDIO_BITRATE + \
        '-f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/baby_camera'

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

    logger.info("video_device=%s", VIDEO_DEVICE)
    logger.info("bitrate=%s,%s", VIDEO_BITRATE, AUDIO_BITRATE)
    logger.info("encode start")

    recv_signal = False
    while True:
        try:
            encode()
        except SignalException:
            logger.info("encode stop")
            recv_signal = True
            break
        except Exception as e:
            logger.exception(e)
        finally:
            if recv_signal is False:
                retry_sec = 3
                logger.info("Retry after %s sec", retry_sec)
                time.sleep(retry_sec)
