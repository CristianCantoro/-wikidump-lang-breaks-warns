FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
RUN python3.8 -m pip install pip
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-setuptools
RUN python3.8 -m pip install pip --upgrade pip
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
