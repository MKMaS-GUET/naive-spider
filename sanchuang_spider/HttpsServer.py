from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import time
from run import imme_crawl, crawl_with_cycle
import threading
import json
from ctypes import *

REQUEST_METHOD_MAP = {'GET': 'args', 'POST': 'form'}
executors = {
    'default': ThreadPoolExecutor(10)
}


def _params_covert(val):
    val = val[0] if isinstance(val, list) else val
    try:
        val = json.loads(val)
    except (ValueError, TypeError):
        pass
    return val


def _get_request_params():
    params = request.json or {}
    for k, v in dict(getattr(request, REQUEST_METHOD_MAP.get(request.method))).items():
        params[k] = _params_covert(v)
    return params
app = Flask(__name__)
scheduler = BlockingScheduler(executors=executors)
CORS(app)


def get_params(key):
    if request.method == "GET":
        val = request.args.get(key)
        return val
    if request.method == "POST":
        if request.content_type.startswith('application/json'):
            val = request.json.get(key)
        elif request.content_type.startswith('multipart/form-data'):
            val = request.form.get(key)
        else:
            val = request.values.get(key)
        return val

class MyThread(threading.Thread):
    def __init__(self, keywords="", sort_type=0, spiderName="", type="", day_of_week="", hour=0, minute=0, second=0, running_time=0):
        threading.Thread.__init__(self)
        self.keywords = keywords
        self.sort_type = sort_type
        self.spiderName = spiderName
        self.type = type
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute
        self.second = second
        self.ThreadID = 'spider {0}'.format(time.ctime())
        self.Running = running_time

    def run(self):
        if self.type == 'imme':
            try:
                message = imme_crawl(self.keywords, self.sort_type, self.spiderName, self.Running)
            except Exception as e:
                print(e)
                print("爬虫启动失败")
                return None
            return message
        elif self.type == 'cycle':
            try:
                crawl_with_cycle(self.keywords, self.sort_type, self.spiderName, self.day_of_week, self.hour,
                                           self.minute, self.second, self.Running)
            except Exception as e:
                print(e)
                print("爬虫定时设定失败")


@app.route('/spider/immediately', methods=['POST', 'GET'])
def imme_run():
    t = MyThread(keywords=get_params('keywords'), sort_type=get_params('sort_type'), spiderName=get_params('spiderName')
                 , type='imme', running_time=get_params('running_time'))
    t.start()
    return jsonify(code=1, message="immediately spider running successfully")


@app.route('/spider/timed_spider')
def cycle_run_modify():
    Date = dict(
        Monday=0,
        Tuesday=1,
        Wednesday=2,
        Thursday=3,
        Friday=4,
        Saturday=5,
        Sunday=6,
    )

    t1 = MyThread(keywords=get_params('keywords'), sort_type=get_params('sort_type'), spiderName=get_params('spiderName'), type='cycle',
                  day_of_week=Date[get_params('day_of_week')], hour=get_params('hour'), minute=get_params('minute'), second=get_params('second'), running_time=get_params('running_time'))
    t1.start()
    return jsonify(code=1, message="timed spider running successfully")

@app.route('/spider/stop_spider')
def stop_spider():
    request.environ.get('')
    return jsonify(code=1, message="stop spider running")


app.run(host='0.0.0.0', port=5000, debug=True)