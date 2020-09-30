#!/usr/bin python
# -*- coding: utf-8 -*-

import time
import json
from PcaRudderCtrl import CarMotor
from tm1637_ctrl import TM1637Ctrl

# smart car control commands
CMD_FRONT      = 1
CMD_BACK       = 2
CMD_LEFT       = 3
CMD_RIGHT      = 4
CMD_TURN_LEFT  = 5
CMD_TURN_RIGHT = 6
CMD_CANCEL     = 7
CMD_START      = 9
CMD_OK         = 0


class SmartCarCtrl:
    def __init__(self):
        self.carMotor = CarMotor(
            pinLeftV1=0, pinLeftH1=1, pinLeftL1=2,
            pinLeftV2=5, pinLeftH2=4, pinLeftL2=3,
            pinRightV1=11, pinRightH1=10, pinRightL1=9,
            pinRightV2=6, pinRightH2=8, pinRightL2=7,
        )
        self.initialize()
        self.tmc = TM1637Ctrl(20,21)
        self.tmc.start()
        #
        self.cmd_list = []
        self.cmd_pre = 0
        self.cmd_check_list = []
        self.valid_cmd = (CMD_FRONT, CMD_BACK, CMD_LEFT, CMD_RIGHT, CMD_TURN_LEFT, CMD_TURN_RIGHT)

    def initialize(self):
        self.carMotor.stop()
        self.carMotor.set_speed(20)
        print("RobotCtrl initialize OK.")

    def finalize(self):
        self.carMotor.stop()
        self.carMotor.set_speed(0)
        self.tmc.stop()
        print("RobotCtrl finalize OK.")

    def cmd_handle(self, cmd):
        if cmd == 10:  # 为方便led显示，将10置为0
            cmd = 0
        # 校验指令合理
        self.cmd_check_list.append(cmd)
        if len(self.cmd_check_list) < 10:
            return
        self.cmd_check_list.pop(0)
        # 取临时指令列表中指令数最多的指令
        cmd = max(self.cmd_check_list, key=self.cmd_check_list.count)
        self.tmc.set_cur_cmd(cmd)
        # 所有指令都要OK指令确认
        if cmd == CMD_OK:
            if self.cmd_pre == CMD_CANCEL:
                self.cmd_list = []
                self.cmd_pre = -1
                self.tmc.set_pre_cmd(' ')
                self.tmc.set_cmd_count(0)
            elif self.cmd_pre == CMD_START:
                self.exec_cmd(self.cmd_list)
                self.cmd_list = []
                self.cmd_pre = -1
                self.tmc.set_pre_cmd(' ')
                self.tmc.set_cmd_count(0)
            elif self.cmd_pre in self.valid_cmd:
                self.cmd_list.append(self.cmd_pre)
                self.tmc.set_pre_cmd(self.cmd_pre)
                self.tmc.set_cmd_count(len(self.cmd_list))
                self.cmd_pre = -1
        else:
            self.cmd_pre = cmd

    def exec_cmd(self, cmd_list):
        # 判断列表
        for cmd in cmd_list:
            if cmd == CMD_FRONT:
                self.carMotor.front()
            elif cmd == CMD_BACK:
                self.carMotor.back()
            elif cmd == CMD_LEFT:
                self.carMotor.left()
            elif cmd == CMD_RIGHT:
                self.carMotor.right()
            elif cmd == CMD_TURN_LEFT:
                self.carMotor.turn_left()
            elif cmd == CMD_TURN_RIGHT:
                self.carMotor.turn_right()
            else:
                self.carMotor.stop()
            time.sleep(1)
        self.carMotor.stop()

    def json_ctrl_func(self, cmd_data):
        if cmd_data is None:
            return
        cmd = cmd_data.get("cmd")
        if cmd is None:
            return
        value = cmd_data.get("value")
        if value is None:
            value = 0
        value = int(value)
        print("RobotCtrl cmd:%s,value=%d" % (cmd, value))
        if cmd == "exit":
            return cmd
        # carMotor Ctrl
        elif cmd == "front":
            self.carMotor.front()
        elif cmd == "back":
            self.carMotor.back()
        elif cmd == "left":
            self.carMotor.left()
        elif cmd == "right":
            self.carMotor.right()
        elif cmd == "turn_left":
            self.carMotor.turn_left()
        elif cmd == "turn_right":
            self.carMotor.turn_right()
        elif cmd == "stop":
            self.carMotor.stop()
        elif cmd == "speed":
            self.carMotor.set_speed(value)
        else:
            return cmd

    def app_test_run(self):
        while True:
            cmd = str(input('pleas input cmd:'))
            value = int(input('pleas input value:'))
            data = {"cmd": cmd, "value": value}
            self.json_ctrl_func(data)


# single modular run
if __name__ == '__main__':
    try:
        carCtrl = SmartCarCtrl()
        carCtrl.initialize()
        carCtrl.app_test_run()
        carCtrl.finalize()
    except KeyboardInterrupt:
        print("SmartCarCtrl app_test_run exit.")
