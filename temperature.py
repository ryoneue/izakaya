import machine
import utime

class Temperature:
    def __init__(self):
        # 温度センサが接続されている、
        # 4つ目の ADC(アナログデジタルコンバータ) を取得します
        self.sensor_temp = machine.ADC(4)

        # ADCの最大電圧3.3Vを16bit(65535)で割って、
        # 16bitの 1 目盛りのあたりの電圧(変換係数)を計算します( 約 0.00005V)
        self.conversion_factor = 3.3 / (65535)
        
    def check_temperature(self):
        # センサから取得した値(0~65535) を電圧に変換します。
        reading = self.sensor_temp.read_u16() * self.conversion_factor
        temperature = 27 - (reading - 0.706)/0.001721 # 読取り値を温度に変換
        return temperature

if __name__ == '__main__':
    temp = Temperature()
    sensor = temp.check_temperature()
    print(sensor)

