#####!/usr/bin/env python3
#-*- coding: utf-8 -*-

#导入tm1637模块，并检查模块是否引入成功：
#请保证tm1637.py已复制到当前目录下
import tm1637
import time as tm
import threading


class TM1637Ctrl:
    def __init__(self, clk=20, dio=21):
        self.CLK = clk
        self.DIO = dio
        #BCM pin coding,I2C SDA SCL
        # CLK=20  #15 #CLK
        # DIO=21  #14 #DIO
        #实例化TM1637
        self.led = tm1637.TM1637(clk=self.CLK, dio=self.DIO)
        self.led.show('    ')
        self.cur_cmd = ' '
        self.pre_cmd = ' '
        self.cmd_count = 0
        self.timer_show = None

    def set_cur_cmd(self, value):
        self.cur_cmd = value

    def set_pre_cmd(self, value):
        self.pre_cmd = value

    def set_cmd_count(self, value):
        self.cmd_count = value

    def get_show_value(self):
        value1 = "{}{}".format(self.cur_cmd,self.pre_cmd)
        value2 = "%02d" % self.cmd_count
        return value1+value2

    def start(self):
        self.timer_show = threading.Timer(0.1, self.timer_handle_show_func)  # 首次启动
        self.timer_show.start()
        self.led.show('    ')

    def stop(self):
        self.led.show('    ')
        self.timer_show.cancel()

    def timer_handle_show_func(self):
        # print('hello timer')  # 打印输出
        self.timer_show = threading.Timer(0.2, self.timer_handle_show_func)  # 60秒调用一次函数
        self.timer_show.start()  # 启用定时器
        value = self.get_show_value()
        self.led.show(value)


if __name__ == "__main__":
    tmc = TM1637Ctrl(20,21)
    tmc.start()