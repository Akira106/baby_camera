import subprocess
import time
import os

import logging

from utils import init_logger, SignalException, set_signal


# ストリーム設定
STREAM_URL = os.environ["STREAM_URL"]
STREAM_KEY = os.environ["STREAM_KEY"]


logger = logging.getLogger(__name__)


def youtube_live():
    # YouTubeの音声コーデックはOPUSに対応していないので、AACに変換する
    cmd = \
        'ffmpeg -loglevel warning ' + \
        '-i rtsp://127.0.0.1:8554/baby_camera -vcodec copy -acodec aac ' + \
        '-f flv %s/%s' % (STREAM_URL, STREAM_KEY)
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

    logger.info("live start")
    recv_signal = False
    while True:
        try:
            youtube_live()
        except SignalException:
            logger.info("live stop")
            recv_signal = True
            break
        except Exception as e:
            logger.exception(e)
        finally:
            if recv_signal is False:
                retry_sec = 3
                logger.info("Retry after %s sec", retry_sec)
                time.sleep(retry_sec)
