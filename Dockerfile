FROM python:3.10
RUN apt update && apt upgrade -y
COPY . /pricelist-fetcher
# Install latest Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install ./google-chrome*.deb -y && rm ./google-chrome*.deb
WORKDIR /pricelist-fetcher
# Run tests
CMD pip3 install -r requirements.txt pytest && python3 -m pytest