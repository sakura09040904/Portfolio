from flask import Flask, request, jsonify
import pymysql
from textwrap import dedent
import threading
import queue

app = Flask(__name__)

# MySQL 설정
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "jusung1!"
app.config["MYSQL_DB"] = "jusung"

mysql = pymysql.connect(
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    passwd=app.config["MYSQL_PASSWORD"],
    db=app.config["MYSQL_DB"],
)

# 요청 큐 및 관련 변수
request_queue = queue.Queue()
stop_event = threading.Event()


def process_queue():
    while not stop_event.is_set():
        func, args = request_queue.get()
        if func is None:
            break  # 종료 신호가 들어오면 종료

        with app.app_context():  # 애플리케이션 컨텍스트 설정
            func(*args)
        request_queue.task_done()


# 큐 처리 스레드 시작
threading.Thread(target=process_queue, daemon=True).start()


def enqueue_request(func, *args):
    # 요청 큐에 추가
    request_queue.put((func, args))


@app.route("/sensor/sensor_data", methods=["GET"])
def insert_data():
    required_params = [
        "companyId",
        "deviceCode",
        "measureDatetime",
        "value1",
        "value2",
        "value3",
        "value4",
        "value5",
        "value6",
        "value7",
        "value8",
        "value9",
        "value10",
        "value11",
        "value12",
        "value13",
        "value14",
        "value15",
        "value16",
        "value17",
        "value18",
        "value19",
        "value20",
    ]

    data = {param: request.args.get(param) for param in required_params}

    missing_params = [param for param in required_params if data[param] is None]
    if missing_params:
        return (
            jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}),
            400,
        )

    def process_request():
        try:
            cursor = mysql.cursor()
            query = dedent(
                """
                INSERT INTO sensor 
                (company_id, device_code, measure_datetime, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8, value_9, value_10, value_11, value_12, value_13, value_14, value_15, value_16, value_17, value_18, value_19, value_20) 
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            )
            cursor.execute(query, tuple(data[param] for param in required_params))
            mysql.commit()
            return jsonify({"message": "Data inserted successfully"}), 201

        except pymysql.MySQLError as e:
            mysql.rollback()  # 트랜잭션 롤백
            return jsonify({"error": f"MySQL error: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"General error: {str(e)}"}), 400

    # 요청을 큐에 추가하고 응답 반환
    enqueue_request(process_request)
    return jsonify({"message": "Request is being processed"}), 202

@app.route("/sensor/sensor_ncd", methods=["GET"])
def insert_ncd_data():
    required_params = [
        "s_measuretime",
        "s_nodeid",
        "s_volt",
        "s_type",
        "s_value1",
        "s_value2",
        "s_value3",
        "s_value4",
    ]

    data = {param: request.args.get(param) for param in required_params}

    # 누락된 파라미터 확인
    missing_params = [param for param in required_params if data[param] is None]
    if missing_params:
        return (
            jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}),
            400,
        )

    def process_request():
        try:
            cursor = mysql.cursor()
            query = dedent(
                """
                INSERT INTO sensor_vc
                (s_measuretime, s_nodeid, s_volt, s_type, s_value1, s_value2, s_value3, s_value4)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s)
                """
            )
            cursor.execute(query, tuple(data[param] for param in required_params))
            mysql.commit()
            return jsonify({"message": "Data inserted into sensor_vc successfully"}), 201

        except pymysql.MySQLError as e:
            mysql.rollback()  # 트랜잭션 롤백
            return jsonify({"error": f"MySQL error: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"General error: {str(e)}"}), 400

    # 요청을 큐에 추가하고 응답 반환
    enqueue_request(process_request)
    return jsonify({"message": "Request is being processed"}), 202

@app.route("/sensor/sensor_ncd/event", methods=["GET"])
def insert_ncd_event():
    required_params = [
        "s_nodeid",
        "s_type",
        "event_log",
    ]

    data = {param: request.args.get(param) for param in required_params}

    # 누락된 파라미터 확인
    missing_params = [param for param in required_params if data[param] is None]
    if missing_params:
        return (
            jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}),
            400,
        )

    def process_request():
        try:
            cursor = mysql.cursor()
            query = dedent(
                """
                INSERT INTO sensor_vc_event
                (s_nodeid, s_type, event_log)
                VALUES
                (%s, %s, %s)
                """
            )
            cursor.execute(query, tuple(data[param] for param in required_params))
            mysql.commit()
            return jsonify({"message": "Data inserted into sensor_vc_event successfully"}), 201

        except pymysql.MySQLError as e:
            mysql.rollback()  # 트랜잭션 롤백
            return jsonify({"error": f"MySQL error: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"General error: {str(e)}"}), 400

    # 요청을 큐에 추가하고 응답 반환
    enqueue_request(process_request)
    return jsonify({"message": "Request is being processed"}), 202

# ======================================================================================== 
# ===================================== 딥러닝pc ==========================================
# ========================================================================================

@app.route("/api/project", methods=["POST"])
def insert_project():
    try:
        data = request.json  # JSON 요청 데이터 읽기

        # 필수 필드 확인
        required_fields = ["project_name", "project_directory", "project_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # 메인 서버 DB에 INSERT 쿼리 실행
        cursor = mysql.cursor()
        query = dedent("""
            INSERT INTO project (project_name, project_directory, project_id) 
            VALUES (%s, %s, %s)
        """)
        cursor.execute(
            query, 
            (data["project_name"], data["project_directory"], data["project_id"])
        )
        mysql.commit()

        return jsonify({"message": "Project successfully inserted on main server."}), 201
    except pymysql.MySQLError as e:
        mysql.rollback()
        return jsonify({"error": f"MySQL error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"General error: {str(e)}"}), 500

@app.route("/api/initialimage", methods=["POST"])
def insert_initialimage():
    data = request.json
    required_fields = ["project_id", "initialimage_name", "initialimage_directory", "initialimage_id"]

    # 필수 필드 확인
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        cursor = mysql.cursor()
        query = dedent("""
            INSERT INTO initialimage (project_id, initialimage_name, initialimage_directory, initialimage_id)
            VALUES (%s, %s, %s, %s)
        """)
        cursor.execute(
            query,
            (
                data["project_id"],
                data["initialimage_name"],
                data["initialimage_directory"],
                data["initialimage_id"],
            ),
        )
        mysql.commit()
        return jsonify({"message": "Initial image successfully inserted on main server."}), 201
    except pymysql.MySQLError as e:
        mysql.rollback()
        return jsonify({"error": f"MySQL error: {str(e)}"}), 400


@app.route("/api/spiresult", methods=["POST"])
def insert_spiresult():
    data = request.json
    required_fields = ["initialimage_id", "spiresult_name", "spiresult_directory", "inspection_result"]

    # 필수 필드 확인
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        cursor = mysql.cursor()
        query = dedent("""
            INSERT INTO spiresult (initialimage_id, spiresult_name, spiresult_directory, inspection_result)
            VALUES (%s, %s, %s, %s)
        """)
        cursor.execute(
            query,
            (
                data["initialimage_id"],
                data["spiresult_name"],
                data["spiresult_directory"],
                data["inspection_result"],
            ),
        )
        mysql.commit()
        return jsonify({"message": "SPI result successfully inserted on main server."}), 201
    except pymysql.MySQLError as e:
        mysql.rollback()
        return jsonify({"error": f"MySQL error: {str(e)}"}), 400



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
