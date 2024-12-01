import pandas as pd
import numpy as np
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import font_manager, rc
import pymysql
import requests
from datetime import datetime, timedelta

import tensorflow as tf
# import tensorflow.keras as keras
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import SimpleRNN, LSTM, GRU, Dropout, Dense
from sklearn.preprocessing import MinMaxScaler

# FILE_PATH= 'C:/Users/bizforce/Desktop/241122_jusung_ncd_remake'
FILE_PATH= 'C:/bizforce_dev/ML'
MAIN_SERVER_URL = "http://jusung1.iptime.org:5000/sensor/sensor_ncd/event"


def send_sensor_data(url, s_nodeid, s_type, event_log):
    send_data = {
        "s_nodeid": s_nodeid,
        "s_type": s_type,
        "event_log": event_log
        }
    try:
        response = requests.get(url, params=send_data, timeout=5)
        print(response.text)
    except Exception as e:
        print(e)


class MyApp(QWidget) :  # 클래스 정의
    def __init__(self) :
        super().__init__()  # 부모클래스 생성자 호출(가장 위쪽 코딩)

        initial_time_str = "2020-11-25 14:00:00"
        initial_time = datetime.strptime(initial_time_str, "%Y-%m-%d %H:%M:%S")

        self.RIMIT_X = 10 # mape값이 rimit보다 클 때 이벤트 발생으로 판단
        self.EVENT_INTERVAL_TIME_X = 10 # 이벤트 발생 휴면 시간(분)
        self.event_time_x = initial_time # 최근 이벤트 발생 시간

        self.RIMIT_Y = 10
        self.EVENT_INTERVAL_TIME_Y = 10
        self.event_time_y = initial_time

        self.RIMIT_Z = 10
        self.EVENT_INTERVAL_TIME_Z = 10
        self.event_time_z = initial_time

        self.RIMIT_C = 10
        self.EVENT_INTERVAL_TIME_C = 10
        self.event_time_c = initial_time

        self.initUI()
        
    def initUI(self) :  # 윈도우 환경 구성
        self.font_name1 = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf", size=20)
        
        
        #self.conn = pymysql.connect(host='127.0.0.1' , user='root', password='bizforce', db='bizdemo', charset='utf8')
        #self.cursor = self.conn.cursor()
        
        
        # self.btnOpen = QPushButton('불러오기')
        # self.btnSave = QPushButton('저장하기')
        # self.tblVibOrg = QTableWidget(1000, 4)
        # col_head = ['Date', 'RmsX','RmsY','RmsZ']
        # self.tblVibOrg.setHorizontalHeaderLabels(col_head)
        # self.tblVibOrg.setStyleSheet('font-size : 12pt;'
        #                              'color : blue;')
        
        self.txtLog = QTextEdit()
        self.txtLog.setAcceptRichText(True)  # 텍스트에 디자인 적용 가능
        self.txtLog.setReadOnly(True)
        self.txtLog.setStyleSheet('font-size : 14pt;'
                                  'color : blue;')
        self.txtLog.append('-------------------------')
        self.txtLog.append('YYYY-MM-DD HH:mm:ss')
        self.txtLog.append('\"Current Error\"')
        self.txtLog.append('-------------------------')
        
        self.fig = plt.Figure(figsize=(6,4))  # 그래프 영역 변수 생성
        self.canvas = FigureCanvas(self.fig)  # 그래프 그리기 영역
        self.fig2 = plt.Figure(figsize=(6,4))  # 그래프 영역 변수 생성
        self.canvas2 = FigureCanvas(self.fig2)  # 그래프 그리기 영역
        
        self.figX = plt.Figure(figsize=(6,3))
        self.figY = plt.Figure(figsize=(6,3))
        self.figZ = plt.Figure(figsize=(6,3))
        self.figC = plt.Figure(figsize=(6,3))
        self.canvasX = FigureCanvas(self.figX)  # 그래프 그리기 영역
        self.canvasY = FigureCanvas(self.figY)  # 그래프 그리기 영역
        self.canvasZ = FigureCanvas(self.figZ)  # 그래프 그리기 영역
        self.canvasC = FigureCanvas(self.figC)  # 그래프 그리기 영역
        

        layout = QHBoxLayout() # 상자 배치관리자(최상위)
        layoutMonitor = QVBoxLayout()
        layoutML = QVBoxLayout()
        
        # 왼쪽 레이아웃
        layoutMenu = QHBoxLayout()
        layoutTbl = QHBoxLayout()  # 왼쪽에 테이블, 오른쪽에 텍스트상자(로그)
        layoutGraph = QVBoxLayout()
        
        # layoutMenu.addWidget(self.btnOpen)
        # layoutMenu.addWidget(self.btnSave)
        
        # layoutTbl.addWidget(self.tblVibOrg)
        layoutGraph.addWidget(self.txtLog)
        layoutGraph.addWidget(self.canvas)
        layoutGraph.addWidget(self.canvas2)

        layoutGraph.setStretch(0, 1)  # txtLog 차지 비율
        layoutGraph.setStretch(1, 1)  # canvas 차지 비율
        layoutGraph.setStretch(2, 1)  # canvas2 차지 비율
        
        # layoutMonitor.addLayout(layoutMenu)
        # layoutMonitor.addLayout(layoutTbl)
        layoutMonitor.addLayout(layoutGraph)
        
        # 오른쪽 레이아웃
        layoutRmsX = QVBoxLayout()
        layoutRmsY = QVBoxLayout()
        layoutRmsZ = QVBoxLayout()
        layoutRmsC = QVBoxLayout()
        
        layoutRmsX.addWidget(self.canvasX)
        layoutRmsY.addWidget(self.canvasY)
        layoutRmsZ.addWidget(self.canvasZ)
        layoutRmsC.addWidget(self.canvasC)
        
        layoutML.addLayout(layoutRmsX)
        layoutML.addLayout(layoutRmsY)
        layoutML.addLayout(layoutRmsZ)
        layoutML.addLayout(layoutRmsC)
        
        layout.addLayout(layoutMonitor)
        layout.addLayout(layoutML)
        
        self.setLayout(layout)
        self.setWindowTitle('VibMonitor')  # 윈도우 제목
        self.setGeometry(0, 0, 1200, 780)  # 좌상단좌표, 너비, 높이
        self.show()  # 윈도우 보이기
        
        self.dataProcess()
        self.dataProcess2()
        self.tblDisplay()
        self.graph()
        self.graph2()
        self.graphX()
        self.graphY()
        self.graphZ()
        self.graphC()
        
        self.timer = QTimer(self) # 타이머 객체 생성
        self.timer.start(15000)  # 10000ms, 1분으로 수정되어야 함
        self.timer.timeout.connect(self.timerHandler) # 이벤트핸들러 등록
        
    def getDataSetX(self, item, start, to, size) : # 원시데이터, 데이터 시작, 데이터 끝, 입력데이터 개수
        arr = []  # 공백 리스트 생성
        for i in range(start, to - (size-1)) :
            arr.append(item[i:i+size , 0])
        nparr = np.array(arr)  # 넘파이 배열로 변환
        nparr = np.reshape(nparr, (nparr.shape[0], nparr.shape[1], 1)) # 차원 확장
        return (nparr)  
    
    def getDataSetY(self, item, start, to, size) :
        arr = []
        for i in range(start + size, to + 1) :
            arr.append(item[i, 0])
        nparr = np.array(arr) # 넘파이 배열로 변환(차원변경 없음)
        return (nparr)
        
    def dataProcess(self) :
        
        self.conn = pymysql.connect(host='127.0.0.1' , user='root', password='bizforce', db='ncd', charset='utf8')
        self.cursor = self.conn.cursor()
        # 데이터베이스 테이블을 읽어 전역 리스트에 저장
        query = 'select s_measuretime, s_value1, s_value2, s_value3 from sensor where s_nodeid = 101 order by s_measuretime desc limit 600'
        self.cursor.execute(query)  # 쿼리 실행
        
        result = self.cursor.fetchall()  # 테이블 전체 저장
        # print(result[0])
        rowCount = self.cursor.rowcount  # 행 개수 추출
        self.cursor.close()
        self.conn.close()
        self.df = [[0] * 4 for i in range(rowCount)] # 2차원 리스트(1행에 7개의 열이 0으로 초기화)
        
        count = 0
        for item in result : # item은 1개의 행
            for j in range(4) :
                self.df[count][j] = item[j]
            count += 1
            
            
        # log_df1 = 'rmsx value : %f' % (self.df[0][1]) # rmsx 원본(가장최근)    
        # log_df2 = 'rmsy value : %f' % (self.df[0][2]) # rmsy 원본(가장최근)    
        # log_df3 = 'rmsz value : %f' % (self.df[0][3]) # rmsz 원본(가장최근)    
        # # self.txtLog.append(log_df1)
        # # self.txtLog.append(log_df2)
        # # self.txtLog.append(log_df3)
        # print(log_df1)
        # print(log_df2)
        # print(log_df3)
        
        # rmsx 데이터셋을 저장하여 model 과 비교(120 타임)
        df1 = [k[1] for k in self.df[0:120]]  # 0,1,2,3 열 중에서 1열 리스트
        final_df1 = np.array(df1)  # 넘파이배열로 변환
        final_df1 = final_df1.reshape(-1, 1)  # 차원 증가
        scaler_df1 = MinMaxScaler(feature_range=(0,1)) # 정규화 객체 생성
        scaled_df1 = scaler_df1.fit_transform(final_df1)  # 정규화
        x_test_df1 = self.getDataSetX(scaled_df1, 0, scaled_df1.shape[0] - 1, 10)
        y_test_df1 = self.getDataSetY(scaled_df1, 0, scaled_df1.shape[0] - 1, 10)
        
        self.lstm_model_rmsx = tf.keras.models.load_model(f'{FILE_PATH}/lstm_jusungx.h5')  # lstm model 로드
        
        self.pred_s_rmsx = self.lstm_model_rmsx.predict(x_test_df1)
        # 예측과 원본 비교
        self.pred_s_rmsx = scaler_df1.inverse_transform(self.pred_s_rmsx) # 정규화 역변환
        self.test_df1 = final_df1[0: , :]
        mape_rmsx = np.mean(np.abs(self.test_df1[10:] - self.pred_s_rmsx) / self.test_df1[10:]) * 100  # 1개 발생됨
        mape_rmsx_str = 'rmsx mape : %f' % (mape_rmsx)
        # self.txtLog.append(mape_rmsx_str)
        print(mape_rmsx_str)
        if not np.isinf(mape_rmsx) and mape_rmsx > self.RIMIT_X:
            current_time = datetime.now()
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            time_difference = current_time - self.event_time_x
            if time_difference >= timedelta(minutes=self.EVENT_INTERVAL_TIME_X):
                send_sensor_data(MAIN_SERVER_URL, 101, 8, "rms_x_error")

                self.txtLog.append(f'{current_time_str}')
                self.txtLog.append('\"rms_x_error\"')
                self.txtLog.append('-------------------------')

                self.event_time_x = current_time

        #----------------------------------------------------
        
        
        # rmsy 데이터셋을 저장하여 model 과 비교(120 타임)
        df2 = [k[2] for k in self.df[0:120]]  # 0,1,2,3 열 중에서 1열 리스트
        final_df2 = np.array(df2)  # 넘파이배열로 변환
        final_df2 = final_df2.reshape(-1, 1)  # 차원 증가
        scaler_df2 = MinMaxScaler(feature_range=(0,1)) # 정규화 객체 생성
        scaled_df2 = scaler_df2.fit_transform(final_df2)  # 정규화
        x_test_df2 = self.getDataSetX(scaled_df2, 0, scaled_df2.shape[0] - 1, 10)
        y_test_df2 = self.getDataSetY(scaled_df2, 0, scaled_df2.shape[0] - 1, 10)
        
        self.lstm_model_rmsy = tf.keras.models.load_model(f'{FILE_PATH}/lstm_jusungy.h5')  # lstm model 로드
        self.pred_s_rmsy = self.lstm_model_rmsy.predict(x_test_df2)
        # 예측과 원본 비교
        self.pred_s_rmsy = scaler_df2.inverse_transform(self.pred_s_rmsy) # 정규화 역변환
        self.test_df2 = final_df2[0: , :]
        mape_rmsy = np.mean(np.abs(self.test_df2[10:] - self.pred_s_rmsy) / self.test_df2[10:]) * 100  # 1개 발생됨
        mape_rmsy_str = 'rmsy mape : %f' % (mape_rmsy)
        # self.txtLog.append(mape_rmsy_str)
        print(mape_rmsy_str)
        if not np.isinf(mape_rmsy) and mape_rmsy > self.RIMIT_Y:
            current_time = datetime.now()
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            time_difference = current_time - self.event_time_y
            if time_difference >= timedelta(minutes=self.EVENT_INTERVAL_TIME_Y):
                send_sensor_data(MAIN_SERVER_URL, 101, 8, "rms_y_error")

                self.txtLog.append(f'{current_time_str}')
                self.txtLog.append('\"rms_y_error\"')
                self.txtLog.append('-------------------------')

                self.event_time_y = current_time
        #----------------------------------------------------
        
        # rmsz 데이터셋을 저장하여 model 과 비교(120 타임)
        df3 = [k[3] for k in self.df[0:120]]  # 0,1,2,3 열 중에서 1열 리스트
        final_df3 = np.array(df3)  # 넘파이배열로 변환
        final_df3 = final_df3.reshape(-1, 1)  # 차원 증가
        scaler_df3 = MinMaxScaler(feature_range=(0,1)) # 정규화 객체 생성
        scaled_df3 = scaler_df3.fit_transform(final_df3)  # 정규화
        x_test_df3 = self.getDataSetX(scaled_df3, 0, scaled_df3.shape[0] - 1, 10)
        y_test_df3 = self.getDataSetY(scaled_df3, 0, scaled_df3.shape[0] - 1, 10)
        
        self.lstm_model_rmsz = tf.keras.models.load_model(f'{FILE_PATH}/lstm_jusungz.h5')  # lstm model 로드
        self.pred_s_rmsz = self.lstm_model_rmsy.predict(x_test_df3)
        # 예측과 원본 비교
        self.pred_s_rmsz = scaler_df3.inverse_transform(self.pred_s_rmsz) # 정규화 역변환
        self.test_df3 = final_df3[0: , :]
        mape_rmsz = np.mean(np.abs(self.test_df3[10:] - self.pred_s_rmsz) / self.test_df3[10:]) * 100  # 1개 발생됨
        mape_rmsz_str = 'rmsz mape : %f' % (mape_rmsz)
        # self.txtLog.append(mape_rmsz_str)
        print(mape_rmsz_str)
        if not np.isinf(mape_rmsz) and mape_rmsz > self.RIMIT_Z:
            current_time = datetime.now()
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            time_difference = current_time - self.event_time_z
            if time_difference >= timedelta(minutes=self.EVENT_INTERVAL_TIME_Z):
                send_sensor_data(MAIN_SERVER_URL, 101, 8, "rms_z_error")

                self.txtLog.append(f'{current_time_str}')
                self.txtLog.append('\"rms_z_error\"')
                self.txtLog.append('-------------------------')

                self.event_time_z = current_time
        #----------------------------------------------------
        
    def dataProcess2(self) :
        self.conn = pymysql.connect(host='127.0.0.1' , user='root', password='bizforce', db='ncd', charset='utf8')
        self.cursor = self.conn.cursor()
        # 데이터베이스 테이블을 읽어 전역 리스트에 저장
        query = 'select s_measuretime, s_value1 from sensor where s_nodeid = 201 order by s_measuretime desc limit 1000'
        self.cursor.execute(query)  # 쿼리 실행
        
        result = self.cursor.fetchall()  # 테이블 전체 저장
        # print(result[0])
        rowCount = self.cursor.rowcount  # 행 개수 추출
        self.cursor.close()
        self.conn.close()
        self.df2 = [[0] * 2 for i in range(rowCount)] # 2차원 리스트(1행에 7개의 열이 0으로 초기화)
        
        count = 0
        for item in result : # item은 1개의 행
            for j in range(2) :
                self.df2[count][j] = item[j]
            count += 1
            
            
        # log_df1 = 'current value : %f' % (self.df2[0][1]) # current 원본(가장최근)    
        # # self.txtLog.append(log_df1)
        # print(log_df1)
        
        # current 데이터셋을 저장하여 model 과 비교(120 타임)
        df1 = [k[1] for k in self.df2[0:120]]  # 0,1,2,3 열 중에서 1열 리스트
        final_df1 = np.array(df1)  # 넘파이배열로 변환
        final_df1 = final_df1.reshape(-1, 1)  # 차원 증가
        scaler_df1 = MinMaxScaler(feature_range=(0,1)) # 정규화 객체 생성
        scaled_df1 = scaler_df1.fit_transform(final_df1)  # 정규화
        x_test_df1 = self.getDataSetX(scaled_df1, 0, scaled_df1.shape[0] - 1, 10)
        y_test_df1 = self.getDataSetY(scaled_df1, 0, scaled_df1.shape[0] - 1, 10)
        
        self.lstm_model_current = tf.keras.models.load_model(f'{FILE_PATH}/lstm_current.h5')  # lstm model 로드
        
        self.pred_s_current = self.lstm_model_current.predict(x_test_df1)
        # 예측과 원본 비교
        self.pred_s_current = scaler_df1.inverse_transform(self.pred_s_current) # 정규화 역변환
        self.test_df4 = final_df1[0: , :]
        mape_current = np.mean(np.abs(self.test_df4[10:] - self.pred_s_current) / self.test_df4[10:]) * 100  # 1개 발생됨
        mape_current_str = 'current mape : %f' % (mape_current)
        # self.txtLog.append(mape_current_str)
        print(mape_current_str)
        if not np.isinf(mape_current) and mape_current > self.RIMIT_C:
            current_time = datetime.now()
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            time_difference = current_time - self.event_time_c
            if time_difference >= timedelta(minutes=self.EVENT_INTERVAL_TIME_C):
                send_sensor_data(MAIN_SERVER_URL, 101, 8, "current_error")

                self.txtLog.append(f'{current_time_str}')
                self.txtLog.append('\"current_error\"')
                self.txtLog.append('-------------------------')

                self.event_time_c = current_time
        #----------------------------------------------------
        
        

    def tblDisplay(self) :
        pass
        # for i in range(1000) :
        #     for j in range(4) :
        #        self.tblVibOrg.setItem(i, j, QTableWidgetItem(str(self.df[i][j])))  # 테이블에 출력
               
    def graph(self) :
        self.fig.clear()  # 그래프 영역 초기화
        
        ax1 = self.fig.add_subplot(111)  # 그래프 영역이 1개일 경우
        ax1.clear() # 그래프 영역 초기화(subplot 각각 필요)
        
        df1 = [k[1] for k in self.df]
        df2 = [k[2] for k in self.df]
        df3 = [k[3] for k in self.df]
        #df1.reverse()
        #df2.reverse()
        #df3.reverse()


        ax1.plot(df1, label='rmsx')
        ax1.plot(df2, label='rmsy')
        ax1.plot(df3, label='rmsz')

        ax1.legend()
        
        self.canvas.draw()  # 그래프 다시 그리기
        
    def graph2(self) :
        self.fig2.clear()  # 그래프 영역 초기화
        
        ax1 = self.fig2.add_subplot(111)  # 그래프 영역이 1개일 경우
        ax1.clear() # 그래프 영역 초기화(subplot 각각 필요)
        
        df1 = [k[1] for k in self.df2]
        #df1.reverse()


        ax1.plot(df1, label='current')

        ax1.legend()
        
        self.canvas.draw()  # 그래프 다시 그리기

    def graphX(self) :
        
        self.figX.clear()  # 그래프 영역 초기화
        
        ax1 = self.figX.add_subplot(111)  # 그래프 영역이 1개일 경우
        ax1.clear() # 그래프 영역 초기화(subplot 각각 필요)
        df1 = [k[1] for k in self.df] # 2차원 리스트에서 rmsx 추출
        #npdf1 = np.array(df1)  # 넘파이 배열로 변환
        #ax1.plot(npdf1[880:], label='rmsx')
        
        ax1.plot(self.test_df1[10: , 0], label='rmsx') # 120개
        ax1.plot(self.pred_s_rmsx, label='pred')
        ax1.legend()
        ax1.set_title('RMS X', fontproperties=self.font_name1)

        # 자동으로 여백 최적화
        self.figX.tight_layout()
        
        self.canvasX.draw()  # 그래프 다시 그리기
        
    def graphY(self) :
        self.figY.clear()  # 그래프 영역 초기화
        
        ax1 = self.figY.add_subplot(111)  # 그래프 영역이 1개일 경우
        ax1.clear() # 그래프 영역 초기화(subplot 각각 필요)
        df2 = [k[2] for k in self.df] # 2차원 리스트에서 rmsx 추출
        #npdf2 = np.array(df2)  # 넘파이 배열로 변환
        #ax1.plot(npdf2[880:], label='rmsy')
        ax1.plot(self.test_df2[10: , 0], label='rmsy') # 120개
        ax1.plot(self.pred_s_rmsy, label='pred')
        ax1.legend()
        ax1.set_title('RMS Y', fontproperties=self.font_name1)

        self.figY.tight_layout()
        
        self.canvasY.draw()  # 그래프 다시 그리기            
            
            
    def graphZ(self) :
        self.figZ.clear()  # 그래프 영역 초기화
        
        ax1 = self.figZ.add_subplot(111)  # 그래프 영역이 1개일 경우
        ax1.clear() # 그래프 영역 초기화(subplot 각각 필요)
        df3 = [k[3] for k in self.df] # 2차원 리스트에서 rmsx 추출
        #npdf3 = np.array(df3)  # 넘파이 배열로 변환
        #ax1.plot(npdf3[880:], label='rmsz')
        ax1.plot(self.test_df3[10: , 0], label='rmsz') # 120개
        ax1.plot(self.pred_s_rmsz, label='pred')
        ax1.legend()
        ax1.set_title('RMS Z', fontproperties=self.font_name1)

        self.figZ.tight_layout()
        
        self.canvasZ.draw()  # 그래프 다시 그리기  

    def graphC(self) :
        self.figC.clear()  # 그래프 영역 초기화
        
        ax1 = self.figC.add_subplot(111)  # 그래프 영역이 1개일 경우
        ax1.clear() # 그래프 영역 초기화(subplot 각각 필요)
        df3 = [k[1] for k in self.df2] # 2차원 리스트에서 rmsx 추출
        #npdf3 = np.array(df3)  # 넘파이 배열로 변환
        #ax1.plot(npdf3[880:], label='current')
        ax1.plot(self.test_df4[10: , 0], label='current') # 120개
        ax1.plot(self.pred_s_current, label='pred')
        ax1.legend()
        ax1.set_title('CURRENT', fontproperties=self.font_name1)

        self.figC.tight_layout()
        
        self.canvasC.draw()  # 그래프 다시 그리기    

    def timerHandler(self) :
        self.dataProcess()
        self.dataProcess2()
        self.tblDisplay()
        self.graph()
        self.graphX()
        self.graphY()
        self.graphZ()
        self.graphC()
            
        
if __name__ == '__main__' :  # 진입점 판단(운영체제에서 프로그램 호출)
    app = QApplication(sys.argv)
    ex = MyApp() # 클래스 객체 생성
    sys.exit(app.exec_())  # 프로그램 실행상태 유지(윈도우 실행)