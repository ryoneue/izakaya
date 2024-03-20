import ntptime
from machine import RTC
from wifi import Wifi
import utime

class ntp_date:
    def __init__(self):
        try:
            ntptime.settime()
        except:
            print("Network Disconection.")

    def now(self):
        tm = utime.localtime(utime.time()) # UTC now
        jst = str(tm[0])+'/'+str(tm[1])+'/'+str(tm[2])+' '+str((tm[3]+9)%24)+':'+str(tm[4])+':'+str(tm[5])
        self.date = jst
        self.tm = tm        
        jst = str(self.tm[0])+'/'+str(self.tm[1])+'/'+str(self.tm[2])+' '+str((self.tm[3]+9)%24)+':'+str(self.tm[4])+':'+str(self.tm[5])
        return jst

if __name__ == '__main__':
    #自宅Wi-FiのSSIDとパスワードを入力
    ssid = 'Buffalo-G-F5A0'
    password = 'mck4wuvu7eypn'

    access_token    = 'pwpqSJa9p5taVWtZJcmveowcSIeHD5nyghYqUPfSXF4'

    net = Wifi(ssid, password)
    # wlan = network.WLAN(network.STA_IF)
    # wlan.active(True)
    # wlan.connect(ssid, password)

    date = ntp_date()
    
#     tm = utime.localtime(utime.time()) # UTC now
#     jst = str(tm[0])+'/'+str(tm[1])+'/'+str(tm[2])+' '+str((tm[3]+9)%24)+':'+str(tm[4])+':'+str(tm[5])
    # NTPサーバーとの同期を行う

    # 
    # # RTC（リアルタイムクロック）の設定
    # rtc = RTC()
    # print(ntptime.time())
    # rtc.datetime(ntptime.time())
    print(date.now())

