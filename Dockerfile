FROM ubuntu:22.04

# 共通で必要なライブラリのインストール
ENV TZ=Asia/Tokyo
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt -y install \
    tzdata \
    v4l-utils \
    alsa-utils \
    ffmpeg

# 映像配信サーバー(mediamtx)
RUN apt -y install software-properties-common \
    && add-apt-repository ppa:longsleep/golang-backports \
    && apt -y install golang-go git
WORKDIR /home/babycam
RUN git clone -b v1.4.1 https://github.com/bluenviron/mediamtx.git
COPY webrtc/static mediamtx/internal/servers/webrtc/static
COPY webrtc/*.go mediamtx/internal/servers/webrtc/
COPY webrtc/*.html mediamtx/internal/servers/webrtc/
RUN cd mediamtx && go build

# 動体検知
RUN apt -y install \
    libopencv-dev=4.5.4+dfsg-9ubuntu4 \
    python3-pip
RUN pip3 install \
    numpy==1.26.3 \
    opencv-python==4.5.4.60
COPY motion_detection /home/babycam/motion_detection

# v4l2loopback
COPY v4l2loopback /home/babycam/v4l2loopback

# エンコーダー
COPY encoder /home/babycam/encoder

# YouTubeライブ
COPY youtube_live /home/babycam/youtube_live

# 共通ライブラリ
COPY utils/* /home/babycam/v4l2loopback
COPY utils/* /home/babycam/encoder
COPY utils/* /home/babycam/motion_detection
COPY utils/* /home/babycam/youtube_live
