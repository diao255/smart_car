#!/usr/bin python
# -*- coding: utf-8 -*-

# 输入通道与角度。即可选通并使该通道的舵机转动到相应的角度
from __future__ import division                             #导入 __future__ 文件的 division 功能函数(模块、变量名....)   #新的板库函数  //=
import time
# Import the PCA9685 module.
import Adafruit_PCA9685                                     #导入Adafruit_PCA9685模块

# Uncomment to enable debug output.
# import logging
# logging.basicConfig(level=logging.DEBUG)                   # 调试打印日志输出

# Initialise the PCA9685 using the default address (0x40).
pca9685 = Adafruit_PCA9685.PCA9685()                            # 把Adafruit_PCA9685.PCA9685()引用地址赋给PWM标签

# Set frequency to 50hz, good for servos.
pca9685.set_pwm_freq(50)
# Alternatively specify a different address and/or bus:#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
# 2^12精度  角度转换成数值  #angle输入的角度值(0--180)  #pulsewidth高电平占空时间(0.5ms--2.5ms)   #/1000将us转换为ms  #20ms时基脉冲(50HZ)
# MG90S:800-2800=0-180 MG996R:500-2800=0-180 # data=int(4096*(angle/180*2500+500)/20000+0.5)


class Rudder:
    def __init__(self, channel, min_pulse=500, max_pulse=2800, min_angle=0, max_angle=180, angle_range=180,step_angle = 5,step_time = 0.05):
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.angle_range = angle_range
        # 计算角度到脉宽比率
        self.angle_ratio = (max_pulse-min_pulse)/angle_range
        self.step_angle = step_angle
        self.step_time = step_time #50ms移动3度
        self.angle = min_angle
        pca9685.set_pwm(self.channel, 0, 0)

    def adjust_input_angle(self,angle):
        if angle > self.max_angle:
            angle = self.max_angle
        elif angle < self.min_angle:
            angle = self.min_angle
        return angle

    def set_servo_angle(self, angle):                    # 输入角度转换成12^精度的数值
        angle = self.adjust_input_angle(angle)
        data=int(4096*(angle*self.angle_ratio+self.min_pulse)/20000+0.5)              # 进行四舍五入运算 
        pca9685.set_pwm(self.channel, 0, data)
        self.angle = angle

    def set_servo_angle_slow(self, angle):                    # 输入角度转换成12^精度的数值
        angle = self.adjust_input_angle(angle)
        while angle > self.angle:
            self.set_servo_angle(self.angle+self.step_angle)
            time.sleep(self.step_time)
        #
        while angle < self.angle:
            self.set_servo_angle(self.angle-self.step_angle)
            time.sleep(self.step_time)
        #
        self.set_servo_angle(self.angle)

    def set_step_params(self,step_angle=3,step_time=0.05):
        self.step_angle = step_angle
        self.step_time = step_time

    def set_angle_params(self,min_angle=0,max_angle=180,angle_range=180):
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.angle_range = angle_range

    def release(self):
        pca9685.set_pwm(self.channel, 0, 0)

    def get_cur_angle(self):
        return self.angle

class CameraPan:
    def __init__(self):
        self.rudder1 = Rudder(14, 800, 2800,20,90)
        self.rudder2 = Rudder(15, 800, 2800,5,140)
        print("CameraPan initialize OK.")

class ClawSix:
    def __init__(self):
        self.rudder1 = Rudder(2, 500, 2800,40,160)
        self.rudder2 = Rudder(3, 500, 2800,50,160)
        self.rudder3 = Rudder(4, 500, 2800,35,130)
        self.rudder4 = Rudder(5, 500, 2800,40,90)
        self.rudder5 = Rudder(6, 500, 2800)
        self.rudder6 = Rudder(7, 500, 2800)
        print("ClawSix initialize OK.")


class CarMotor:
    HIGH = 4095
    LOW = 0

    def __init__(self,pinLeftV1,pinLeftH1,pinLeftL1,pinLeftV2,pinLeftH2,pinLeftL2,
                 pinRightH1,pinRightL1,pinRightV1,pinRightH2,pinRightL2,pinRightV2):
        self.pinLeftV1 = pinLeftV1
        self.pinLeftH1 = pinLeftH1
        self.pinLeftL1 = pinLeftL1
        self.pinLeftV2 = pinLeftV2
        self.pinLeftH2 = pinLeftH2
        self.pinLeftL2 = pinLeftL2
        self.pinRightH1 = pinRightH1
        self.pinRightL1 = pinRightL1
        self.pinRightV1 = pinRightV1
        self.pinRightH2 = pinRightH2
        self.pinRightL2 = pinRightL2
        self.pinRightV2 = pinRightV2
        self.speed = 0
        self.state = "stop"
        # 设置初始值
        self.set_speed(0)
        self.stop()
        print("CarMotor initialize OK.")


    def front(self):
        self.state="front"
        pca9685.set_pwm(self.pinLeftH1, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftL1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftH2, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftL2, 0, self.LOW)

        pca9685.set_pwm(self.pinRightH1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL1, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightH2, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL2, 0, self.HIGH)
        time.sleep(0.1)

    def back(self):
        self.state="back"
        pca9685.set_pwm(self.pinLeftH1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL1, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftH2, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL2, 0, self.HIGH)

        pca9685.set_pwm(self.pinRightH1, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightL1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightH2, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightL2, 0, self.LOW)
        time.sleep(0.1)

    def left(self):
        self.state="left"
        pca9685.set_pwm(self.pinLeftH1, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftL1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftH2, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL2, 0, self.HIGH)

        pca9685.set_pwm(self.pinRightH1, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightL1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightH2, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL2, 0, self.HIGH)
        time.sleep(0.1)

    def right(self):
        self.state = "right"
        pca9685.set_pwm(self.pinLeftH1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL1, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftH2, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftL2, 0, self.LOW)

        pca9685.set_pwm(self.pinRightH1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL1, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightH2, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightL2, 0, self.LOW)
        time.sleep(0.1)

    def turn_left(self):
        self.state="turn_left"
        pca9685.set_pwm(self.pinLeftH1, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftL1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftH2, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftL2, 0, self.LOW)

        pca9685.set_pwm(self.pinRightH1, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightL1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightH2, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightL2, 0, self.LOW)
        time.sleep(0.1)

    def turn_right(self):
        self.state="turn_right"
        pca9685.set_pwm(self.pinLeftH1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL1, 0, self.HIGH)
        pca9685.set_pwm(self.pinLeftH2, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL2, 0, self.HIGH)

        pca9685.set_pwm(self.pinRightH1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL1, 0, self.HIGH)
        pca9685.set_pwm(self.pinRightH2, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL2, 0, self.HIGH)
        time.sleep(0.1)

    def stop(self):
        self.state="stop"
        pca9685.set_pwm(self.pinLeftH1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightH1, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL1, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftH2, 0, self.LOW)
        pca9685.set_pwm(self.pinLeftL2, 0, self.LOW)
        pca9685.set_pwm(self.pinRightH2, 0, self.LOW)
        pca9685.set_pwm(self.pinRightL2, 0, self.LOW)

    # speed = 0-100
    def set_speed(self, speed):
        if speed > 100:
            speed = 100
        elif speed < 0:
            speed = 0
        self.speed = int(speed/100*4096)
        pca9685.set_pwm(self.pinLeftV1, 0, self.speed)
        pca9685.set_pwm(self.pinRightV1, 0, self.speed)
        pca9685.set_pwm(self.pinLeftV2, 0, self.speed)
        pca9685.set_pwm(self.pinRightV2, 0, self.speed)

    def get_speed(self):
        return self.speed

    def test_wheel(self, num):
        if num == 1:
            pca9685.set_pwm(self.pinLeftH1, 0, self.HIGH)
            pca9685.set_pwm(self.pinLeftL1, 0, self.LOW)

