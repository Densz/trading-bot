FROM python:3.8

RUN mkdir /bot
WORKDIR /bot

# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
ENV LD_LIBRARY_PATH /usr/local/lib
RUN pip3 install ta-lib

RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

COPY requirements.txt .
COPY ./tradingbot ./tradingbot

RUN pip install -r requirements.txt