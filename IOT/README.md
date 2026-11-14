# IoT 온습도 발행기

`send_rabbitmq_humi_temp_2_1.py`는 DHT22(GPIO 4) 측정값을 RabbitMQ로 한 번 전송합니다.
실제 실행에는 호환되는 Raspberry Pi 하드웨어, `Adafruit_DHT`, `pika`가 필요합니다.

## 접속 설정

모든 설정은 프로세스 환경변수로 받습니다. `.env` 파일을 자동으로 읽지는 않습니다.

- `RABBITMQ_HOST`: 기본 `localhost`. 센서 장치와 브로커가 다르면 브로커 주소 지정.
- `RABBITMQ_PORT`: 기본 `5672`. 1–65535 정수.
- `RABBITMQ_VHOST`: 기본 `egov`.
- `RABBITMQ_USER`: 발행용 계정. 미설정 시 `RABBITMQ_DEFAULT_USER`, 그마저 없으면 `guest`.
- `RABBITMQ_PASSWORD`: 필수. 미설정 시 Compose와 같은 `RABBITMQ_DEFAULT_PASS` 사용.
- `RABBITMQ_EXCHANGE`: 기본 `sensor`.
- `RABBITMQ_ROUTING_KEY`: 기본 `q_temp_humi`.

`RABBITMQ_USER`/`RABBITMQ_PASSWORD`가 Compose 이름보다 우선합니다.
비밀번호가 없거나 포트가 잘못되면 센서 읽기와 연결 전에 오류를 냅니다.
기존 고정 IP와 `guest` 비밀번호는 더 이상 기본값으로 사용하지 않습니다.

Bash 설정 예시(예제 비밀번호를 실제 비밀번호로 바꾸고 파일을 커밋하지 마세요):

```bash
export RABBITMQ_HOST='broker.example.invalid'  # 실제 브로커 주소로 변경
export RABBITMQ_VHOST='egov'
export RABBITMQ_USER='sensor-publisher'
read -rs -p 'RabbitMQ password: ' RABBITMQ_PASSWORD; echo
export RABBITMQ_PASSWORD
python3 IOT/send_rabbitmq_humi_temp_2_1.py
unset RABBITMQ_PASSWORD
```

## 브로커 준비

1. `DOCKER/rabbitmq/.env.example`을 참고해 브로커 계정을 설정합니다.
2. 관리 콘솔 등으로 `egov` vhost를 만들고 발행용 계정에 필요한 권한을 부여합니다.
   기본 `guest` 계정은 원격 센서 연결용으로 사용하지 말고 별도 계정을 만드세요.
3. 소비자 설정과 일치하는 `sensor` 교환기, 큐, `q_temp_humi` routing key 바인딩을 준비합니다.
   이 스크립트는 교환기·큐·vhost를 자동 생성하지 않습니다.
4. 센서가 다른 장치라면 브로커의 주소와 방화벽 접근 범위를 확인합니다.
   이 예제 연결은 TLS를 설정하지 않으므로 신뢰할 수 없는 네트워크에 그대로 노출하지 마세요.

## 회귀 테스트

```bash
python3 -m unittest discover -s IOT/tests -v
```

센서와 AMQP 라이브러리를 테스트 더블로 대체하므로 하드웨어·브로커·실제 비밀번호가 필요 없습니다.
접속 인자와 메시지 전달을 검증하며 실제 하드웨어/브로커 통합 테스트를 대신하지 않습니다.
