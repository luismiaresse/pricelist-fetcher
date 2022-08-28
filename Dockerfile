FROM python:3.10
RUN apt update && apt upgrade -y
RUN useradd -m -s /bin/bash -G sudo luismi
COPY . /home/luismi/pricelist-fetcher
# Install latest Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install ./google-chrome*.deb -y && rm ./google-chrome*.deb
# Work with non-root user
USER luismi
WORKDIR /home/luismi/pricelist-fetcher
# Run tests and open a terminal
CMD pip3 install -r requirements.txt pytest && python3 -m pytest && /bin/bash