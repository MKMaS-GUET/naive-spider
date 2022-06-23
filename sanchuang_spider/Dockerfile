FROM python:3.8

COPY . /usr/src/sanchuang_spider/
WORKDIR /usr/src/sanchuang_spider


RUN pip install --default-timeout=100 -i https://pypi.douban.com/simple -r requirements.txt

CMD ["python", "HttpsServer.py"]