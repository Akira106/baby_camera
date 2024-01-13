import subprocess

import streamlit as st


# カメラ(WebRTC)へのリンク
CAMERA_LINK = "http://raspberrypi.local:8889/baby_camera/"

# 各サービス名を表す文字列
SERVICE_CAMERA = "camera"
SERVICE_MOTION_DETECTION = "motion_detection"
SERVICE_YOUTUBE_LIVE = "youtube_live"

# 各サービスのdocker-composeファイルのファイル名
DICT_COMPOSE_FILE = {
    SERVICE_CAMERA: "docker-compose.yml",
    SERVICE_MOTION_DETECTION: "docker-compose_motion_detection.yml",
    SERVICE_YOUTUBE_LIVE: "docker-compose_youtube_live.yml"
}


def main():
    # ページの設定
    st.set_page_config(
        page_title="赤ちゃんカメラ",
        page_icon=":baby_symbol:",
        layout="wide",  # wideレイアウトを指定
    )

    # サービスの起動・停止状態の初期化
    list_service = [
        # (サービス, コンテナ数)
        (SERVICE_CAMERA, 3),
        (SERVICE_MOTION_DETECTION, 1),
        (SERVICE_YOUTUBE_LIVE, 1)
    ]
    for service, ncontainer in list_service:
        if service not in st.session_state:
            if count_active_container(DICT_COMPOSE_FILE[service]) == ncontainer:
                st.session_state[service] = True
            else:
                st.session_state[service] = False

    # ページ
    st.title("赤ちゃんカメラ")
    st.divider()

    # サイドバーに電源オフのボタンをつける
    shutdown = st.sidebar.button("シャットダウン")
    if shutdown:
        cmd = "shutdown -h now"
        st.sidebar.markdown("シャットダウンします...")
        subprocess.check_output(cmd, shell=True).decode().rstrip()

    st.markdown("### カメラ")
    # カメラ起動済みならリンクをはる
    if st.session_state[SERVICE_CAMERA] is True:
        st.markdown("[映像を確認する](%s)" % CAMERA_LINK)
    col1_cam, col2_cam = st.columns([1, 3])
    bt_cam_on = col1_cam.button(
        '起動', key='bt1_1', disabled=st.session_state[SERVICE_CAMERA])
    bt_cam_off = col2_cam.button(
        '停止', key='bt1_2', disabled=not st.session_state[SERVICE_CAMERA])

    st.divider()
    st.markdown("### 動体検知 & 録画")
    col1_md, col2_md = st.columns([1, 3])
    bt_md_on = col1_md.button(
        '起動', key='bt2_1',
        disabled=(st.session_state[SERVICE_MOTION_DETECTION] or (not st.session_state[SERVICE_CAMERA])))
    bt_md_off = col2_md.button(
        '停止', key='bt2_2', disabled=(not st.session_state[SERVICE_MOTION_DETECTION]))

    st.divider()
    st.markdown("### YouTube Live")
    col1_yt, col2_yt = st.columns([1, 3])
    bt_yt_on = col1_yt.button(
        '起動', key='bt3_1',
        disabled=(st.session_state[SERVICE_YOUTUBE_LIVE] or (not st.session_state[SERVICE_CAMERA])))
    bt_yt_off = col2_yt.button(
        '停止', key='bt3_2', disabled=(not st.session_state[SERVICE_YOUTUBE_LIVE]))

    # ボタンの動作の実装
    def on(col, service):
        """起動ボタンの動作

        Args:
            col (st.columns): カラムオブジェクト
            services (str): サービス名
        """
        col.markdown("起動中です。  \nしばらくお待ちください...")
        activate_container(DICT_COMPOSE_FILE[service])
        st.session_state[service] = True

    def off(col, service):
        """停止ボタンの動作

        Args:
            col (st.columns): カラムオブジェクト
            services (str): サービス名
        """
        col.markdown("停止中です。  \nしばらくお待ちください...")
        deactivate_container(DICT_COMPOSE_FILE[service])
        st.session_state[service] = False

    if bt_cam_on:
        on(col1_cam, SERVICE_CAMERA)
        st.rerun()
    if bt_cam_off:
        # 動体検知やYouTube Liveが起動していれば、先にオフにする
        if st.session_state[SERVICE_YOUTUBE_LIVE] is True:
            off(col2_yt, SERVICE_YOUTUBE_LIVE)
        if st.session_state[SERVICE_MOTION_DETECTION] is True:
            off(col2_md, SERVICE_MOTION_DETECTION)
        off(col2_cam, SERVICE_CAMERA)
        st.rerun()

    if bt_md_on:
        on(col1_md, SERVICE_MOTION_DETECTION)
        st.rerun()
    if bt_md_off:
        off(col2_md, SERVICE_MOTION_DETECTION)
        st.rerun()

    if bt_yt_on:
        on(col1_yt, SERVICE_YOUTUBE_LIVE)
        st.rerun()
    if bt_yt_off:
        off(col2_yt, SERVICE_YOUTUBE_LIVE)
        st.rerun()


def count_active_container(compose_file="docker-compose.yml"):
    """docker-compose.ymlで定義したコンテナのうちアクティブなものの数を数える

    Args:
        compose_file (str): docker-composeファイルのファイル名

    Returns:
        int: コンテナ数
    """
    cmd = 'docker-compose -f %s ps --services --filter "status=running"' % compose_file
    ret = subprocess.check_output(cmd, shell=True).decode().rstrip()
    if ret == "":
        return 0
    else:
        return len(ret.split("\n"))


def activate_container(compose_file="docker-compose.yml"):
    """docker-compose.ymlで定義したコンテナを起動する

    Args:
        compose_file (str): docker-composeファイルのファイル名

    Returns:
        なし
    """
    cmd = "docker-compose -f %s up -d" % compose_file
    subprocess.check_output(cmd, shell=True).decode().rstrip()


def deactivate_container(compose_file="docker-compose.yml"):
    """docker-compose.ymlで定義したコンテナを停止する

    Args:
        compose_file (str): docker-composeファイルのファイル名

    Returns:
        なし
    """
    cmd = "docker-compose -f %s down" % compose_file
    subprocess.check_output(cmd, shell=True).decode().rstrip()


if __name__ == "__main__":
    main()
