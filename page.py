from tiny_line import tiny_line
# import threading


import socket
# from machine import Pin
import time

#from pio_timer import pio_timer

# from machine import RTC
import json
import sys
import os

# from flask import Flask, render_template


if "MicroPython" in sys.version:
    import urequests as requests
    from wifi import Wifi
    from ntp_date import ntp_date
    date = ntp_date().now
    from temperature import Temperature
    temp = Temperature()
else:
    import requests as requests
    from datetime import datetime
    date = datetime.now
    import threading
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import argparse


class izakaya:
    def __init__(self):
        # PCでのCI/CDの時のみデバッグモードをTrue
        if not "MicroPython" in sys.version:
            parser = argparse.ArgumentParser()
            parser.add_argument('--debug', type=bool, default=False)
            args = parser.parse_args()
            self.debug = args.debug
        else:
            self.debug = False

        self.head = """HTTP/1.1 200 OK Content-Type: text/html

"""

    def load_json(self,json_file="info.json"):
        # 設定用jsonファイルの読み込み
        with open(json_file) as f:
            self.info = json.load(f)



    def set_wifi_info(self):
        #Wi-FiのSSIDとパスワードを読み込み
        ssid = self.info["ssid"]
        password = self.info["password"]
        access_token = self.info["access_token"]


        if "MicroPython" in sys.version:
            net = Wifi(ssid, password)
            status = net.status
            print("status: ",status)
        else:
            net = False
            status = False
        self.net = net
        self.status = status
        self.access_token = access_token
        
        # return net, status, access_token, ssid, password

    def setting(self):
        if "MicroPython" in sys.version:
            # date = ntp_date()
            if (not self.access_token==False or not self.access_token=="False"):
                self.setting_line()            
        # else:
            # date = datetime.now()
        # self.date = date





    def load_html(self):
        # html読み込み
        if self.debug:
            file = "./izakaya.html"
        else:
            file = "./izakaya.html"

        html = ""
        with open(file, encoding='utf-8') as f:
            for line in f:
                html = html + line

        self.html = html


    def open_socket(self):
        # Open socket
        port = int(self.info["port_number"])
        # picowの時のみWIFIの設定
        if "MicroPython" in sys.version:
            self.set_wifi_info()
            print("status:", type(self.status[0]))
            # picowのときはport:80じゃないとダメっぽい？
            port = 80
            addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

        else:

            addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
            print(addr)
            self.status = "False"
            self.access_token = "False"

        self.addr = addr

        self.s = socket.socket()
        self.s.bind(addr)
        self.s.listen(2)
        
        

    def setting_line(self):
        # 通知用Line設定
        
        tl = tiny_line(self.access_token, debug=True)
        print('listening on', self.addr)
        tl.notify("http://"+self.status[0])

    def detect_count(self):
        """
        設備の生産数を検出する処理を記述
        M1 = get_data()
        M2 = get_data()
        M3 = get_data()
        """
        
        self.M1 = 10000
        self.M2 = 20000
        self.M3 = 30000

#         with open("data_sample.txt", "r") as f:
#             tmp = f.readlines()
#         self.M1, self.M2, self.M3 = [i.replace("\n", "") for i in tmp]



    def main_loop(self):
        # 以下ループ処理
        # 変数M1,M2,M3を更新したWebページを作成する（もっと頻度を落としてもいいかも）
        
        # HTTPレスポンスのフォーマット
        RESPONSE = """HTTP/1.1 200 OK
        Content-Length: %d
        Content-Type: %s

        """
        response_headers = "HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: %s\r\n\r\n"
        
        while True:
            try:
                if "MicroPython" in sys.version:
                    self.temperature = temp.check_temperature()
                else:
                    self.temperature = ""
                now = date()
                self.detect_count()
                # cl, addr = s.accept()
                cl, addr = self.s.accept()
                print('client connected from', addr)
                request = cl.recv(1024).decode('utf-8')
                print("request:")
                print(request)
                
                # %以下の変数がhtml内部に代入される
#                 print(now, self.temperature, self.M1, self.M2, self.M3)
#                 response = self.html
        #         if not "MicroPython" in sys.version:
#                 response = self.head + response
#                 cl.sendall(response.encode('utf-8'))

                # HTTPリクエストがGETであり、リクエストされたファイルがHTMLファイルである場合
                if request.startswith(b"GET / ") or request.startswith(b"GET /index.html "):
#                     response = HTML_CONTENT.encode("utf-8")
                    html_e = self.html.encode()
                    response = response_headers % (len(html_e), "text/html")
#                     print(self.html)
                    cl.send(response)
                    cl.send(html_e)
#                     cl.send(response_headers)

                # リクエストされたファイルが画像ファイルである場合
                elif request.startswith(b"GET /menu_image1.jpg "):

                    with open("menu_image1.jpg", "rb") as f:
#                         image_data = f.read()
#                     print(image_data)    
#                     response_headers = RESPONSE % (len(image_data), "image/jpeg", image_data)
#                         print(os.stat(f)[6])
                        response = response_headers % (os.stat("menu_image1.jpg")[6], "image/jpeg")
                        cl.send(response.encode())                    
                        # チャンクサイズ
                        CHUNK_SIZE = 1024

                        # 画像ファイルの送信
                        while True:
                            chunk = f.read(CHUNK_SIZE)
                            if chunk:
                                print(chunk)
                                cl.send(chunk)
                            else:
                                break
    #                     cl.send(RESPONSE % (len(image_data), "image/jpeg", image_data))
                elif request.startswith(b"GET /order"):
                    print("注文ボタンがクリックされました！")
        # ここにボタンがクリックされたときの処理を追加する
                # cl.send(response)
# #                 # 1秒ごとにページを作成しなおす
                time.sleep(1)
                cl.close()

                
            except OSError as e:
                cl.close()
                print('connection closed')



func = izakaya()

# func.set_wifi_info(json_file="info.json")
func.load_json(json_file="info.json")
func.load_html()
func.open_socket()
func.setting()
# func.setting_line()
# 
func.detect_count()
func.main_loop()







    
