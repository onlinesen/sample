# coding=utf8
# 如果有中文，在第一行必须声明utf8编码，否则会在python2.7报编码错误。
import uiautomator2


class SampleTest(object):

    def __init__(self):
        pass

    def day_1(self):
        plan_auto_work = {"培训": "Pass", "安装git": "Pass"}
        plan_test_work = {"测试160": "50%"}
