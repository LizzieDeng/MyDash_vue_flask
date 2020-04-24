from flask import Flask, render_template, jsonify, request
from random import *
from flask_cors import CORS
import requests
import os
import logging
from flask_caching import Cache
import numpy as np
import IMU_Vis
import json

CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200  # should be equal to maximum number of active users
}

app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app, supports_credentials=False, resources={r"/api/*": {"origins": "*"}})
# 设置上传文件路径
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')
# 创建缓存
cache = Cache()
cache.init_app(app, config=CACHE_CONFIG)

# log文件
logging.basicConfig(level=logging.DEBUG, filename='log/log.txt', filemode='w',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    # response.setHeader("Access-Control-Allow-Origin", "*")
    if request.method == 'POST':
        # 获取文件名
        filestorage = request.files['file']
        uuid = request.form.get('uuid')
        filename = filestorage.filename
        temp_dir = app.config['UPLOAD_PATH']
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)
        # 将文件保存至本地目录
        try:
            path_name = os.path.join(app.config['UPLOAD_PATH'], filename)
            path_rename = os.path.join(app.config['UPLOAD_PATH'], uuid)
            filestorage.save(path_name)
            # 重命名
            os.rename(path_name, path_rename)
        except Exception as e:
            logging.DEBUG('at upload function, save file failed, exception {0}'.format(e))
            jsonify({'success': False, 'message': e, 'data': filename})
    return jsonify({'success': True})


@cache.memoize()
def generate_path_gesture_data(filename):
    # np.genfromtxt 处理缺失值NAN
    data = np.genfromtxt(open(filename, 'rb'), delimiter=',', missing_values=None, filling_values=0.0)[1:, :]
    header = np.genfromtxt(open(filename, 'rb'), delimiter=',', dtype="str")[0, :]
    Vis = IMU_Vis.Vis(data, header, trim_all_zero_row=True)
    Vis.gen_gesture_on_path(num=100)
    gesture_data = Vis.get_path_gesture_data()
    return gesture_data


@app.route('/api/getopt', methods=['GET', 'POST'])
def getOptions():
    if request.method == 'POST':
        try:
            data = request.get_data()
            data1 = json.loads(data.decode('utf-8'))
            uuid = data1.get('uuid')
            filename = os.path.join(app.config['UPLOAD_PATH'], uuid)
            data = generate_path_gesture_data(filename)
            data_length = len(data)
            max_frames = 500
            frames_step = int(data_length / max_frames)
            if frames_step > 1000:
                frames_step = round(frames_step, -3)
            elif frames_step > 100:
                frames_step = round(frames_step, -2)
            else:
                frames_step = round(frames_step, -1)
            options = [{'label': frames_step * i, 'value': frames_step * i} for i in range(1, 10, 2)]
            success = True
            message = "successfully"
        except Exception as e:
            logging.DEBUG('at getOptions function, save file failed, exception {0}'.format(e))
            success = False
            options = None
            message = e
            # jsonify({'success': False, 'message': e, 'data': uuid})
        return jsonify({'success': success, 'options': options, 'message': message})


@app.route('/api/getpath', methods=['GET', 'POST'])
def getPathdata():   
     if request.method == 'POST':
        try:
            data = request.get_data()
            data1 = json.loads(data.decode('utf-8'))
            uuid = data1.get('uuid')
            filename = os.path.join(app.config['UPLOAD_PATH'], uuid)
            data = generate_path_gesture_data(filename)
            x = list(data[:, 0])
            y = list(data[:, 1])
            z = list(data[:, 2])
            path_data = {'x': x, 'y': y, 'z': z}
            success = True
            message = "successfully"
            print("getpathdata", path_data)
        except Exception as e: 
            logging.DEBUG('at getPathdata function, get data failed, exception {0}'.format(e))   
            success = False
            path_data = None
            message = e
        return jsonify({'success': success, 'data': path_data, 'message': message})




@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8081/{}'.format(path)).text
    return render_template("index.html")

import pandas as pd
if __name__== "__main__":
    app.run(debug=True)
