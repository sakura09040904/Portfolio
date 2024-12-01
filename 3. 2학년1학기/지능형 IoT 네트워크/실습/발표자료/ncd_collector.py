import socket
import pymysql
import datetime
import requests
import time

# IN : NCD.io 수신기 ip주소 및 port번호
HOST = "192.168.99.110"
PORT = 2101
MAIN_SERVER_URL = "http://jusung1.iptime.org:5000/sensor/sensor_data"

def send_sensor_data(url, data):
    try:
        response = requests.get(url, params=data, timeout=5)
        print(response.text)
        # log_data(data)
    except Exception as e:
        print(e)

# 소켓 객체 생성(TCP 방식)
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            # 서버에 연결 시도
            client_socket.connect((HOST, PORT))
            print('Connect OK!')
            return client_socket
        except Exception as e:
            print(f"Connect failed: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)  # 5초 후에 재시도

def receive_data(client_socket):
    try:

        # 데이터를 받기 시도
        data = client_socket.recv(1024)
        
        # 만약 데이터가 없다면 연결이 끊어진 경우로 간주
        if not data:
            return None
        
        return data
    except Exception as e:
        # 예외 발생 시 소켓 오류로 간주하고 재연결을 시도
        print(f"Error while receiving data: {e}")
        return None

client_socket = connect_to_server()

conn = pymysql.connect(host='127.0.0.1', user='root', password='bizforce', db='ncd', charset='utf8')
cursor = conn.cursor()  # 커서 설정

tot = 0
result = []

def process_sensor_data(data, tot):
    # 29바이트 데이터를 처리 (전류 센서 데이터)
    if tot >= 29:
        data_chunk_29 = data[:29]  # 29바이트 데이터를 가져옴
        print("Received 29 bytes of data:", data_chunk_29)

        s_nodeid = data_chunk_29[15 + 1]  # 예시로 nodeid를 읽어오기
        s_volt = (data_chunk_29[15 + 3] * 256 + data_chunk_29[15 + 4]) * 0.00322  # 전압 계산
        s_type = data_chunk_29[15 + 7]  # 센서 타입
        if s_type == 13:
            raw_value = (data_chunk_29[24] << 16) + (data_chunk_29[25] << 8) + data_chunk_29[26]  # 전류 센서 값 계산
            s_current = raw_value / 1000.0  # 실제 전류 값 계산
            print(f"Node ID: {s_nodeid}, Voltage: {s_volt}, Type: {s_type}")
            print(f"Current value: {s_current}")  # 전류 센서 값 출력
            print("\n")

            # 현재 시간을 가져옴
            s_measuretime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 파라미터화된 쿼리 사용
            query = """INSERT INTO sensor (s_measuretime, s_nodeid, s_volt, s_type, s_value1, s_value2, s_value3, s_value4) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (s_measuretime, s_nodeid, s_volt, s_type, s_current, 0.0, 0.0, 0))
            conn.commit()

            send_data = {
                "s_measuretime" : s_measuretime,
                "s_nodeid": s_nodeid,
                "s_volt": s_volt,
                "s_type": s_type,
                "s_value1": s_current,
                "s_value2": 0,
                "s_value3": 0,
                "s_value4": 0,
            }

            send_sensor_data(MAIN_SERVER_URL, send_data)

            # 29바이트 처리 후 result 리스트에서 해당 데이터 제거
            data = data[29:]
            tot = len(data)
    return data, tot

def process_vibration_sensor_data(data, tot):
    # 54바이트 데이터를 처리 (진동/온도 센서 데이터)
    if tot >= 54:
        data_chunk_54 = data[:54]  # 54바이트 데이터를 가져옴
        print("Received 54 bytes of data:", data_chunk_54)

        s_nodeid = data_chunk_54[15 + 1]  # 예시로 nodeid를 읽어오기
        s_volt = (data_chunk_54[15 + 3] * 256 + data_chunk_54[15 + 4]) * 0.00322  # 전압 계산
        s_type = data_chunk_54[15 + 7]  # 센서 타입
        if s_type == 8:
            s_rmsx = ((data_chunk_54[15 + 9] << 16) + (data_chunk_54[15 + 10] << 8) + data_chunk_54[15 + 11]) / 100000  # RMS 값 계산
            s_rmsy = ((data_chunk_54[15 + 12] << 16) + (data_chunk_54[15 + 13] << 8) + data_chunk_54[15 + 14]) / 100000  # RMS 값 계산
            s_rmsz = ((data_chunk_54[15 + 15] << 16) + (data_chunk_54[15 + 16] << 8) + data_chunk_54[15 + 17]) / 100000  # RMS 값 계산
            s_temp = (data_chunk_54[15 + 36] << 8) + data_chunk_54[15 + 37]  # 온도 계산

            print(f"Node ID: {s_nodeid}, Voltage: {s_volt}, Type: {s_type}")
            print(f"RMS (X, Y, Z): {s_rmsx}, {s_rmsy}, {s_rmsz}, Temperature: {s_temp}")
            print("\n")

            # 현재 시간을 가져옴
            s_measuretime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 파라미터화된 쿼리 사용
            query = """INSERT INTO sensor (s_measuretime, s_nodeid, s_volt, s_type, s_value1, s_value2, s_value3, s_value4) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (s_measuretime, s_nodeid, s_volt, s_type, s_rmsx, s_rmsy, s_rmsz, s_temp))
            conn.commit()

            send_data = {
                "s_measuretime" : s_measuretime,
                "s_nodeid": s_nodeid,
                "s_volt": s_volt,
                "s_type": s_type,
                "s_value1": s_rmsx,
                "s_value2": s_rmsy,
                "s_value3": s_rmsz,
                "s_value4": s_temp,
            }

            send_sensor_data(MAIN_SERVER_URL, send_data)

            # 54바이트를 처리한 후 result 리스트에서 해당 데이터 제거
            data = data[54:]
            tot = len(data)
    return data, tot

try:
    while True:
        data = receive_data(client_socket)
        now = datetime.datetime.now()

        if data is None:  # 데이터가 없으면 연결이 끊어진 것
            print("Connection lost. Reconnecting...")
            client_socket.close()  # 기존 소켓 닫기
            client_socket = connect_to_server()  # 재연결 시도
            continue  # 재연결 후 다음 반복으로 넘어감

        # 데이터 처리
        datalen = len(data)
        if datalen > 0:
            result.extend(data)
            tot += len(data)

        result, tot = process_sensor_data(result, tot)
        result, tot = process_vibration_sensor_data(result, tot)

except Exception as e:
    print(f"Error: {e}")

finally:
    client_socket.close()
    cursor.close()
    conn.close()
    print("Connection closed.")
