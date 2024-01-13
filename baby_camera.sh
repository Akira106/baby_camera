#!/bin/bash

# 実行時にEmail入力画面が出て止まってしまわないように、空のEmailを設定する
mkdir -p ~/.streamlit/
echo "[general]"  > ~/.streamlit/credentials.toml
echo "email = \"\""  >> ~/.streamlit/credentials.toml
# 実行
/usr/local/bin/streamlit run baby_camera.py
