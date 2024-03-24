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
import uos



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

def file_exists(file_path):
    try:
        # ファイルの情報を取得し、存在を確認する
        uos.stat(file_path)
        return True
    except OSError:
        # ファイルが存在しない場合はFalseを返す
        return False

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

        self.init_total(path="./total.txt")
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
    def add_menu(self, name,num):
        html = """
                            <h3>%s</h3>
                            <button class="btn order-btn" onclick="confirmOrder(order_number=%d)">注文する</button>
                        </div>        
                        """
        if file_exists("./menu_image"+str(num)+".jpg"):
            html = """<div>
                        <img src="menu_image%d.jpg" alt="%d">""" % (num, num)  + html
        else:
            html = """<div>
                        """ + html
        add_html = html % (name, num)
        return add_html


    def load_html(self):
        # html読み込み
        if self.debug:
            file = "./izakaya.html"
        else:
            file = "./izakaya.html"

        html = ""
        with open(file, encoding='utf-8') as f:
                
            for line in f:
                if '<div class="menu-item">' in line:

                    for i in range(len(self.menu_table)):
                        name = self.menu_table[i]["name"]
                        line += self.add_menu(name,i)
                        
                a = 1
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
        
        self.tl = tiny_line(self.access_token, debug=True)
        print('listening on', self.addr)
        self.tl.notify("http://"+self.status[0])

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

    def load_table(self,table_path):
        with open(table_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(data)
        print(len(data))
        self.menu_table = data

    def add_total(self, name, value, path="./total.txt"):
        s = "\n" + name + " :" + str(value)
        with open('./total.txt', mode='a') as f:
            f.write(s)

    def init_total(self,path="./total.txt"):
        s = "ryosuke pub recipt"
        with open('./total.txt', mode='w') as f:
            f.write(s)
            pass
        
    def calc_total(self, path="./total.txt"):
        with open("./total.txt", "r") as f:
            data = f.readlines()
        
        print(data)
        all = 0
        for num,i in enumerate(data):
            if num == 0:
                continue
            all += float(i.split(":")[1])
        print(all)
        return all
        
    def make_recipt(self):
        # 商品名と値段を読み込む
        products = []
        with open('./total.txt', 'r', encoding='utf-8') as file:
            for line in file:
                print(line)
                if 'ryosuke' in line:
                    continue
                name, price = line.strip().split(' :')
                print(name, price)
                products.append({'name': name, 'price': float(price)})

        # HTMLを生成する
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Receipt</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }
                .receipt {
                    border: 1px solid #ccc;
                    padding: 20px;
                    max-width: 400px;
                    margin: 0 auto;
                }
                .item {
                    margin-bottom: 10px;
                }
                .item span {
                    float: left;
                }
                .price {
                    float: right;
                }
                .total {
                    font-weight: bold;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="receipt">
                <h2>Ryosuke's Holidays Pub </h2>
                <h3>Recipt</h3>
                <div class="items">
        """

        for product in products:
            html += f"""
                    <div class="item">
                        <span>{product['name']}:</span>
                        <span class="price">GBP{product['price']:,.2f}</span>
                        
                    </div><br>
            """

        html += """
                    <div class="item">
                        <span>Service Charge:</span>
                        <span class="price">GBP%.2f</span>
                    </div><br>  
                    <div class="item">
                        <span>Total:</span>
                        <span class="price">GBP%.2f</span>
                    </div><br>
                    <h3>Thank YOU!!! <3</h3>
                    <img src="mochi.jpg" alt="0">
                </div>
            </div>
        </body>
        </html>
        """
        return html
            
    def main_loop(self):
        # 以下ループ処理
        # 変数M1,M2,M3を更新したWebページを作成する（もっと頻度を落としてもいいかも）
        
        # HTTPレスポンスのフォーマット
        RESPONSE = """HTTP/1.1 200 OK
        Content-Length: %d
        Content-Type: %s

        """
        response_headers = "HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: %s\r\n\r\n"
        menu_number_old = ""
        result = False
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
                    menu_number_old = ""
                    if result:
                        time.sleep(5)
                        self.init_total()
                        self.load_html()
#                     cl.send(response_headers)

                # リクエストされたファイルが画像ファイルである場合
                elif request.startswith(b"GET /menu_image"):
                    menu_number = request.split("GET")[1].split("HTTP/1.1")[0].split("image")[1][:-5]
                    print(menu_number)
                    print("./menu_image"+str(menu_number)+".jpg")
                    print(file_exists("./menu_image"+str(menu_number)+".jpg"))
                    with open("./menu_image"+str(menu_number)+".jpg", "rb") as f:
#                         image_data = f.read()
#                     print(image_data)    
#                     response_headers = RESPONSE % (len(image_data), "image/jpeg", image_data)
#                         print(os.stat(f)[6])
                        response = response_headers % (os.stat("./menu_image"+str(menu_number)+".jpg")[6], "image/jpeg")
                        print(response)
                        cl.send(response.encode())                    
                        # チャンクサイズ
                        CHUNK_SIZE = 1024

                        # 画像ファイルの送信
                        while True:
                            time.sleep(0.01)
                            chunk = f.read(CHUNK_SIZE)
                            if chunk:
#                                 print(chunk)
                                cl.send(chunk)
                            else:
                                break
    #                     cl.send(RESPONSE % (len(image_data), "image/jpeg", image_data))
                elif request.startswith(b"GET /mochi.jpg "):
                    with open("mochi2.jpg", "rb") as f:
                        response = response_headers % (os.stat("mochi2.jpg")[6], "image/jpeg")
                        cl.send(response.encode())                    
                        # チャンクサイズ
                        CHUNK_SIZE = 1024

                        # 画像ファイルの送信
                        while True:
                            time.sleep(0.01)
                            chunk = f.read(CHUNK_SIZE)
                            if chunk:
                                cl.send(chunk)
                            else:
                                break
                elif request.startswith(b"GET /purin.jpg "):
                    with open("purin.jpg", "rb") as f:
                        response = response_headers % (os.stat("purin.jpg")[6], "image/jpeg")
                        cl.send(response.encode())                    
                        # チャンクサイズ
                        CHUNK_SIZE = 1024
                        # 画像ファイルの送信
                        while True:
                            time.sleep(0.01)
                            chunk = f.read(CHUNK_SIZE)
                            if chunk:
                                cl.send(chunk)
                            else:
                                break                             
                elif request.startswith(b"GET /order"):
                    print("注文ボタンがクリックされました！")
                    
                    print(request.split("GET")[1].split("HTTP/1.1")[0])
                                      
                    menu_number = request.split("GET")[1].split("HTTP/1.1")[0].split("_")[1]
                    print(menu_number)
                    if menu_number == menu_number_old:
                        continue

                    if int(menu_number) == -1:
                        self.tl.notify("チェック")
                        print("check total amount")
                        total = self.calc_total()
                        self.html = self.make_recipt() % (total*0.3, total*1.3)
                        result = True
#                         html_e = recipt_html.encode()
#                         response = response_headers % (len(html_e), "text/html")
#                         cl.send(response)
#                         cl.send(html_e)
                    else:
                        self.tl.notify("注文； " + self.menu_table[int(menu_number)]["name"])
                        print(self.menu_table[int(menu_number)])
                        table = self.menu_table[int(menu_number)]
                        self.add_total(name=table["name"], value=table["value"])
                        time.sleep(1)                        
                        menu_number_old = menu_number
                    
                # cl.send(response)
# #                 # 1秒ごとにページを作成しなおす
                time.sleep(0.1)
                cl.close()

                
            except OSError as e:
                cl.close()
                print('connection closed')



func = izakaya()

# func.set_wifi_info(json_file="info.json")
func.load_json(json_file="info.json")
func.load_table("./menu_table.json")
func.load_html()
func.open_socket()
func.setting()
# func.setting_line()
# 
func.detect_count()
func.main_loop()







    
