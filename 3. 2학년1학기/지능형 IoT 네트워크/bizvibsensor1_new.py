import socket
from _thread import *
import time
import pymysql
import datetime
import numpy as np
import pandas as pd

# 추가 : 상관계수 DB에 넣는 스레드
def corr_execute(conn, cursor, devid):
    
    df_load_query ="SELECT s_rmsx, s_rmsy, s_rmsz, vector, seta FROM tblvibsensor1data WHERE devid = '" + devid + "';"

    query_result = pd.read_sql(df_load_query, conn)

    # DB 데이터 df에 넣고 상관분석
    corr = query_result.corr()
    print(corr)

    # data = [[(cell, row_idx),(cell, row_idx),(cell, row_idx),(cell, row_idx),(cell, row_idx)] << 리스트 하나에 1개의 필드값
    #           ,[...], [...]]
    data = []
    columns = ['s_rmsx','s_rmsy', 's_rmsz', 'vector', 'seta']

    for row in range(5):
        row_data = []
        for idx, column in enumerate(columns):
            if row == idx:
                cell = int(corr[column].values[row])
            else:
                cell = float(round(corr[column].values[row], 6))
            cell_data = (cell, idx)
            row_data.append(cell_data)
        data.append(row_data)

    print(data)

    query = "UPDATE tblcorrdata SET s_rmsx = %s WHERE row_idx = %s AND devid = '" + devid + "';"
    cursor.executemany(query,data[0])
    conn.commit()

    query = "UPDATE tblcorrdata SET s_rmsy = %s WHERE row_idx = %s AND devid = '" + devid + "';"
    cursor.executemany(query,data[1])
    conn.commit()

    query = "UPDATE tblcorrdata SET s_rmsz = %s WHERE row_idx = %s AND devid = '" + devid + "';"
    cursor.executemany(query,data[2])
    conn.commit()

    query = "UPDATE tblcorrdata SET vector = %s WHERE row_idx = %s AND devid = '" + devid + "';"
    cursor.executemany(query,data[3])
    conn.commit()

    query = "UPDATE tblcorrdata SET seta = %s WHERE row_idx = %s AND devid = '" + devid + "';"
    cursor.executemany(query,data[4])
    conn.commit()

    print('상관분석 결과 DB 저장')

def functhread(client_socket, addr) :
    conn = pymysql.connect(host='127.0.0.1', user='root', password='bizforce', db='bizdemo', charset='utf8')
    cursor = conn.cursor()  # 커서 설정
    
    print(addr[0], addr[1]) # 클라이언트의 접속정보 출력
    result = []
    tot = 0
    cnt = 7199 # 추가
    while True :
        try : # 예외가 발생할 가능성이 있는 코드
            data = client_socket.recv(1024)  # 버퍼 크기는 서버와 동일하게

            datalen = len(data)
            if data[0] == '\x7F' :
                #tot = 0
                #result = []
                
                for i in data :
                    result.append(i)
                tot = datalen
            elif tot < 54 :
                for i in data :
                    result.append(i)
                tot += datalen
            
            if tot == 54 :
                
                print(result)
                s_nodeid = data[15+1]
                s_volt = (data[15+3] * 256 + data[15+4]) * 0.00322
                s_type = data[15+7]
                datatmp = 0
                
                s_rmsx = ((data[15+9] << 16) + (data[15+10] << 8) + data[15+11]) / 100000
                s_rmsy = ((data[15+12] << 16) + (data[15+13] << 8) + data[15+14]) / 100000
                s_rmsz = ((data[15+15] << 16) + (data[15+16] << 8) + data[15+17]) / 100000
                s_temp = (data[15+36] << 8) + data[15+37]
                
                # 추가 : type 구해서 DB에 저장
                v_type = None
                if s_rmsx >= s_rmsy and s_rmsx >= s_rmsz: # x가 제일 클 때
                    if s_rmsy >= s_rmsz: # 다음으로 y가 크면
                        v_type = 1 #type1
                    elif s_rmsy < s_rmsz:
                        v_type = 2 # type2
                elif s_rmsy >= s_rmsz:
                    if s_rmsx >= s_rmsz:
                        v_type = 3 # type3
                    elif s_rmsx < s_rmsz: 
                        v_type = 4 # type4
                elif s_rmsy < s_rmsz:
                    if s_rmsx >= s_rmsy:
                        v_type = 5 # type5
                    elif s_rmsx < s_rmsy:
                        v_type = 6 # type6
                        
                # 추가 : 벡터값, 각도 구해서 DB 저장
                        
                # 벡터
                num = (s_rmsx)**2 + (s_rmsy)**2 + (s_rmsz)**2
                vector = np.sqrt(num)
                
                # 각도합
                dir1_num1 = (s_rmsx)**2 + (s_rmsy)**2
                dir1_num2 = np.sqrt(dir1_num1) / vector
                dir1_num3 = np.arccos(dir1_num2) * 180 / np.pi

                dir2_num1 = (s_rmsy)**2 + (s_rmsz)**2
                dir2_num2 = np.sqrt(dir2_num1) / vector
                dir2_num3 = np.arccos(dir2_num2) * 180 / np.pi

                dir3_num1 = (s_rmsx)**2 + (s_rmsz)**2
                dir3_num2 = np.sqrt(dir3_num1) / vector
                dir3_num3 = np.arccos(dir3_num2) * 180 / np.pi

                seta = dir1_num3 + dir2_num3 + dir3_num3
                
                query = "insert into tblvibsensor1 (s_nodeid, s_volt, s_type, s_rmsx, s_rmsy, s_rmsz, s_temp) values (%d,%d,%d,%f,%f,%f,%d)" % (s_nodeid, s_volt, s_type, s_rmsx, s_rmsy, s_rmsz, s_temp)
                print(query)
                cursor.execute(query)
                conn.commit()
                
                devid = "jhsensor001" # 데이터 받고 있는 기기식별값
                # 추가 : 분석 결과값 DB 저장
                query2 = "insert into tblvibsensor1data (s_nodeid, s_volt, s_type, s_rmsx, s_rmsy, s_rmsz, s_temp,v_type, vector, seta, devid) values (%d,%d,%d,%f,%f,%f,%d,%d,%f,%f,'%s')" % (s_nodeid, s_volt, s_type, s_rmsx, s_rmsy, s_rmsz, s_temp, v_type, vector, seta, devid)
                cursor.execute(query2)
                conn.commit()
                
                '''
                realdata = []
                
                for item in range(13) :
                    tmp = 0
                    for offset in range(4) :
                        tmp += result[5+item*5+(offset+1)]*(10**(3-offset))
                    #tmp = result[5+item*5+1]*1000 + result[5+item*5+2]*100 + result[5+item*5+3]*10 + result[5+item*5+4]*1
                    if result[5+item*5+0] == 1 :
                        tmp = tmp * (-1)
                    realdata.append(tmp)
                #query = "insert into tblsensor (s_temp1, s_temp2, s_temp3, s_temp4, s_temp5, s_temp6, s_co2, s_voc, s_humi, s_tempair, s_pm1, s_pm25, s_pm10) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                query = "insert into tbllacquera (s_temp1, s_temp2, s_temp3, s_temp4, s_temp5, s_temp6, s_co2, s_voc, s_humi, s_tempair, s_pm1, s_pm25, s_pm10) values (%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)" % (realdata[0], realdata[1],realdata[2],realdata[3],realdata[4],realdata[5],realdata[6],realdata[7],realdata[9],realdata[10],realdata[11],realdata[11],realdata[12])
                
                
                #queryvalue = (realdata[0], realdata[1],realdata[2],realdata[3],realdata[4],realdata[5],realdata[6],realdata[7],realdata[8],realdata[9],realdata[10],realdata[11],realdata[12])
                print(query)
                cursor.execute(query)
                conn.commit()
                '''
                tot = 0
                result = []
                # 추가 : 상관분석 thread 실행
                cnt += 1
                if cnt == 7200: # 하루에 한번 상관분석
                    start_new_thread(corr_execute, (conn, cursor, devid))
                    cnt = 0

        except : 
            break
    client_socket.close()  # 소킷 종료
    cursor.close()
    conn.close()
HOST = '172.30.1.48'  # local loopback address, localhost 와 동일
PORT = 12301  # 0 ~ 65535 범위에서 사용가능(0 ~ 1024 는 사용하지 않도록 함)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소킷 객체 생성
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 소킷 옵션 설정
server_socket.bind((HOST, PORT))  # 문자열과 정수
server_socket.listen()  # 클라이언트로부터 수신 준비, 서버 시작



while True :
    print('wait')
    client_socket, addr = server_socket.accept()  # 대기상태, 아래 라인으로 내려가지 않음, 접속할 경우 클라이언트소킷과 IP주소를 반환
    #print('kkk')
    start_new_thread(functhread, (client_socket, addr))  # 스레드 함수 호출
    
server_socket.close()  # 서버 종료
    
    
    
    
    
    
    
    
    
    

