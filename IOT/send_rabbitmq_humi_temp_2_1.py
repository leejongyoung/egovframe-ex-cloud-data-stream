#!/usr/bin/python3 

import os

import Adafruit_DHT      # 라이브러리 불러오기
import pika # AMQP 라이브러리

class Publisher:
    def __init__(self):
        self.__url = os.environ.get('RABBITMQ_HOST', 'localhost')
        try:
            self.__port = int(os.environ.get('RABBITMQ_PORT', '5672'))
        except ValueError:
            raise ValueError('RABBITMQ_PORT must be an integer between 1 and 65535') from None
        if not 1 <= self.__port <= 65535:
            raise ValueError('RABBITMQ_PORT must be an integer between 1 and 65535')
        self.__vhost = os.environ.get('RABBITMQ_VHOST', 'egov')
        username = os.environ.get('RABBITMQ_USER') or os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
        password = os.environ.get('RABBITMQ_PASSWORD') or os.environ.get('RABBITMQ_DEFAULT_PASS')
        if not password:
            raise ValueError('Set RABBITMQ_PASSWORD or RABBITMQ_DEFAULT_PASS before publishing')
        self.__cred = pika.PlainCredentials(username, password)
        self.__exchange = os.environ.get('RABBITMQ_EXCHANGE', 'sensor')
        self.__queue = os.environ.get('RABBITMQ_ROUTING_KEY', 'q_temp_humi')
        return

    def main(self):
    
        sensor = Adafruit_DHT.DHT22     #  sensor 객체 생성 
        pin = 4                        # Data핀의 GPIO핀 넘버

        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)   # 센서 객체에서 센서 값(ㅇ노도, 습도) 읽기
        result = ''
  
        if humidity is not None and temperature is not None:   #습도 및 온도 값이 모두 제대로 읽혔다면 
            result = '{{ "temp":{0:0.1f} , "humidity":{1:0.1f} }}'.format(temperature, humidity)
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))  # 온도, 습도 순으로 표시
        else:                                                  # 에러가 생겼다면 
            result = '{"temp":-100.0 , "humidity": -1.0}'
            print('Failed to get reading. Try again!')        #  에러 표시

        print(result)  # 온도, 습도 순으로 표시
    
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.basic_publish(
            exchange = self.__exchange,
            routing_key = self.__queue,
            body = result
        )
        conn.close()
        return

if __name__ == '__main__':
    publisher = Publisher()
    publisher.main()




