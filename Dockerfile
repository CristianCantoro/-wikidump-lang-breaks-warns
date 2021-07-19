# Docker image
FROM python:3.8.0
# Work directory
WORKDIR /usr/src/app
# Installing brew
RUN apt-get update && \
  apt-get install -y -q --allow-unauthenticated \
  build-essential \
  procps \
  curl \
  file \
  git \
  gzip \
  tar \
  p7zip-full \
  sudo
RUN useradd -m -s /bin/zsh linuxbrew && \
  usermod -aG sudo linuxbrew &&  \
  mkdir -p /home/linuxbrew/.linuxbrew && \
  chown -R linuxbrew: /home/linuxbrew/.linuxbrew
USER linuxbrew
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
# Add brew to PATH
ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"
# Installing parallel
RUN brew install parallel
# Creating folders, and files
USER root
COPY . .
# Installing dependencies
RUN pip install -r requirements.txt
# Making the run.sh executable
RUN chmod +x run.sh
# run the run.sh script
CMD ./run.sh