#include "WiFiS3.h"
#include <DFRobotHighTemperatureSensor.h>

// Wi-Fi 변수 정의
char ssid[] = "KT_GiGA_AE01";        // 네트워크 SSID
char pass[] = "cec48hb500";          // 네트워크 비밀번호

int status = WL_IDLE_STATUS;
WiFiClient client;

// 서버 설정
IPAddress server(172, 30, 1, 66);    // 서버 IP 주소
const int serverPort = 15002;        // 서버 포트

// 온도 센서 변수 정의
const float voltageRef = 5.000;      // 기준 전압
int HighTemperaturePin = A0;         // 센서 핀
DFRobotHighTemperature PT100 = DFRobotHighTemperature(voltageRef); // PT100 객체 생성

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // 시리얼 포트 연결 대기
  }

  // Wi-Fi 모듈 확인
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    while (true);
  }

  // Wi-Fi 연결 시도
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(10000);  // 연결 대기
  }

  Serial.println("Connected to WiFi!");
  printWifiStatus();
}

void loop() {
  // 온도 데이터 읽기
  float temperature = PT100.readTemperature(HighTemperaturePin);
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  // 서버로 데이터 전송
  sendTemperatureToServer(temperature);

  delay(10000);  // 10초 간격으로 데이터 전송
}

void sendTemperatureToServer(float temperature) {
  if (client.connect(server, serverPort)) {
    Serial.println("Connected to server");

    // HTTP POST 요청 생성
    client.println("POST /data HTTP/1.1");
    client.println("Host: 172.30.1.66");
    client.println("Content-Type: application/json");
    client.println("Connection: close");
   
    // JSON 데이터 생성
    String jsonData = "{\"temperature\":" + String(temperature) + "}";
    client.print("Content-Length: ");
    client.println(jsonData.length());
    client.println();
    client.println(jsonData);

    // 서버 응답 읽기
    while (client.available()) {
      String response = client.readStringUntil('\n');
      Serial.println(response);
    }

    client.stop();  // 연결 종료
    Serial.println("Data sent successfully");
  } else {
    Serial.println("Connection to server failed");
  }
}

void printWifiStatus() {
  // 연결된 SSID 출력
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // IP 주소 출력
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // 신호 세기 출력
  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI): ");
  Serial.print(rssi);
  Serial.println(" dBm");
}
