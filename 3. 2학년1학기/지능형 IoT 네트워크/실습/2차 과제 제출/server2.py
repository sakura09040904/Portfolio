# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    print("Received Data:", data)  # 온도 데이터 출력
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # PC의 IP 주소와 포트 설정
    app.run(host='172.30.1.66',
            port=15002)