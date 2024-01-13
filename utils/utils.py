import signal
import logging
from logging import StreamHandler, Formatter


def init_logger():
    """ロガーの初期化
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(Formatter("%(asctime)s,%(levelname)s,%(lineno)d,%(message)s"))
    logger.addHandler(handler)


# シグナルハンドラの設定
class SignalException(Exception):
    pass


def handler(signum, frame):
    raise SignalException


def set_signal():
    signal.signal(signal.SIGALRM, handler)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGQUIT, handler)
