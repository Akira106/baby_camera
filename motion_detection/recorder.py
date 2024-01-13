import datetime
import subprocess
import os
import logging

# 保存先
OUTDIR = os.environ["OUTDIR"]

logger = logging.getLogger(__name__)


class Recorder():
    """映像を録画するクラス
    """
    def __init__(self):
        self.cmd = "ffmpeg -loglevel warning -i rtsp://127.0.0.1:8554/baby_camera -codec copy %s"

        self.proc = None

    def start(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        filename = OUTDIR + "/babycamera_" + now + ".mp4"
        cmd = self.cmd % filename
        self.proc = subprocess.Popen("exec " + cmd, shell=True)
        logger.info("start recording to %s", filename)

    def stop(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc = None
            logger.info("stop recording")
