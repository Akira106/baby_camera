import glob
import os
import base64
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from shutdown_sidebar import shutdown_sidebar


VIDEOS = "./recorded_videos/"


def main():
    # ページの設定
    st.set_page_config(
        page_title="赤ちゃんカメラ",
        page_icon=":baby_symbol:",
        layout="wide",  # wideレイアウトを指定
    )

    # タイトル
    st.title("録画した映像を見る")
    st.divider()

    # サイドバーに電源オフのボタンをつける
    shutdown_sidebar()


    # 録画した映像を撮影日で分ける
    list_video_path = sorted(glob.glob(VIDEOS + "*.mp4"), reverse=True)
    dict_year_month_video = {}
    for video_path in list_video_path:
        dt = parse_video_path(video_path)
        if dt is None:
            st.warning("%sの読み込みに失敗しました。" % video_path)
        else:
            year = str(dt.year) + "年"
            month = str(dt.month) + "月"
            if year not in dict_year_month_video:
                dict_year_month_video[year] = {}
            if month not in dict_year_month_video[year]:
                dict_year_month_video[year][month] = []
            dict_year_month_video[year][month].append((dt, video_path))

    # 画面に一覧を表示
    list_years = list(dict_year_month_video.keys())
    if len(list_years) == 0:
        st.warning("録画した映像はありません。")
    else:
        year_tabs = st.tabs(list_years)
        for i, year_tab in enumerate(year_tabs):
            year = list_years[i]
            with year_tab:
                list_month = list(dict_year_month_video[year].keys())
                month_tabs = st.tabs(list_month)
                for j, month_tab in enumerate(month_tabs):
                    with st.container(height=500):
                        for k, (dt, video_path) in enumerate(dict_year_month_video[year][month]):
                            with st.container(border=True):
                                st.write("%s月%s日%s時%s分%s秒" % (dt.month, dt.day, dt.hour, dt.minute, dt.second))
                                st.video(video_path, format="video/mp4", start_time=1)
                                # ダウンロードボタン
                                dl_button = st.button("ダウンロード", key="dl_button_%s_%s_%s" % (i, j, k))
                                if dl_button:
                                    html_dl = trigger_download(video_path, video_path[len(VIDEOS):])
                                    components.html(html=html_dl, height=0, width=0)

                                # 削除ボタン(確認ボタンつき)
                                # button in buttonは、セッションを使ってボタンの状態を記憶する
                                key = "rm_button_%s_%s_%s" % (i, j, k)
                                key_save = key + "_"
                                rm_button = st.button("削除", key=key)
                                if st.session_state.get(key_save) is not True:
                                    st.session_state[key_save] = rm_button
                                if st.session_state.get(key_save) is True:
                                    st.warning("本当に削除しますか?")
                                    yes_col, no_col = st.columns([1, 5])
                                    yes_button = yes_col.button("はい", key="yes_button_%s_%s_%s" % (i, j, k))
                                    no_button = no_col.button("いいえ", key="no_button_%s_%s_%s" % (i, j, k))
                                    if yes_button:
                                        os.remove(video_path)
                                    if yes_button or no_button:
                                        st.session_state[key_save] = False
                                        st.rerun()


def parse_video_path(video_path):
    """ファイル名のパース

    ファイル名をパースして撮影日を返す

    Args:
        video_path (str):
            ファイル名

    Returns:
        DateTime: 撮影日
    """
    try:
        template = VIDEOS + "babycamera_%Y-%m-%d_%H.%M.%S.mp4"
        dt = datetime.strptime(video_path, template)
        return dt
    except Exception:
        return None


def trigger_download(video_path, filename):
    """
    ダウンロードのトリガー

    Args:
        video_path (str):
            ダウンロードする動画ファイルのパス
        filename (str):
            ユーザーがダウンロードした時のファイル名

    Returns:
        str: ダウンロード機能が入ったHTML
    """
    with open(video_path, "rb") as f:
        data = f.read()

    b64 = base64.b64encode(data).decode()
    dl_link = f"""
                <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
                <script>
                $('<a href="data:application/octet-stream;base64,{b64}" download="{filename}">')[0].click()
                </script>
                """
    return dl_link


if __name__ == "__main__":
    main()
