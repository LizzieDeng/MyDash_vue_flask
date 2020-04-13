from flask import Flask, render_template, jsonify, request
from random import *
from flask_cors import CORS
import requests
import os
import logging
app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app, supports_credentials=False, resources={r"/api/*": {"origins": "*"}})
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')

# log文件
logging.basicConfig(level=logging.DEBUG, filename='log/log.txt', filemode='w',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    # response.setHeader("Access-Control-Allow-Origin", "*")
    if request.method == 'POST':
        # print("get request:", request.files['file'], type(request.files['file']))
        # 获取文件名
        filestorage = request.files['file']
        filename = filestorage.filename
        temp_dir = app.config['UPLOAD_PATH']
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)
        # 将文件保存至本地目录
        try:
            filestorage.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        except Exception as e:
            logging.DEBUG('at upload function, save file failed, exception {0}'.format(e))
            jsonify({'success': False, 'message': e, 'data': filename})
    return jsonify({'success': True})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8081/{}'.format(path)).text
    return render_template("index.html")


if __name__== "__main__":
    app.run()
