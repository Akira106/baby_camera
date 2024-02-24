import subprocess

import streamlit as st


def shutdown_sidebar():
    # サイドバーに電源オフのボタンをつける
    shutdown = st.sidebar.button("シャットダウン")
    if shutdown:
        cmd = "shutdown -h now"
        st.sidebar.markdown("シャットダウンします...")
        subprocess.check_output(cmd, shell=True).decode().rstrip()
