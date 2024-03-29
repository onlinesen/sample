# coding=utf8
# 如果有中文，在第一行必须声明utf8编码，否则会在python2.7报编码错误。
import uiautomator2

# 常量命名全部大写
LOCAL_FILE_NAME = "test.jpg"


# 类名使用UpperCamelCase风格
class CodeSample(object):

    # 全局变量初始化在init中
    def __init__(self):
        self.team_member = ["TOM", "lin.shen", "jixin.hao"]

    # 方法名使用lower_test_case 形式
    def function_test(self):
        # 参数名、成员变量、局部变量都统一小写,下划线连接
        sample_name = "Joe"
        print(sample_name)

    """
    Requirement: V500_Tech_Spec_V3.0/Paddington_AG_3
    CheckPoint: Check Default Android Apps to be included
                1. APK Version: >1.2.3.4
                2. Icons Sytle: Rounded-Corner
    Coder: lin.shen@tinno.com
    Date: 2019/09/10
    """

    def test_get_name(self):
        # 使用try except，确保不会跳出测试
        for i in self.team_member:
            try:
                if i == "lin.shen":
                    print(self.team_member[len(self.team_member) + 1])
                if i == "jixing.hao":
                    print(1 / 0)
            except IndexError as e:
                print(u"出现IndexError:", e)
                continue
            except ZeroDivisionError as e:
                print(u"出现ZeroDivisionError:", e)
                continue
            except Exception as e:
                print(u"有不确定的异常时，要处理的任务")
            finally:
                print(u"必须要完成的任务:" + i)

    # 如果函数未被本class内部调用，请声明为静态方法
    @staticmethod
    def static_function(p):
        return p


class Class(object):
    git = "git clone, git branch, git checkout develop(master), git pull, git commit, git push origin master(develop), git merge, git reset, comflic"
    shell = "ls, grep, found,df, du, locate, mkdir, scp, cp, mv, ln, chmod, chown,su,ssh,apt-get install"
    pycharm = "run, debug, code format, clean, settings,git commit"
    pip = "install, list, requirement"
    code = "principle"
    python_online_class = "https://pythonprinciples.com/lessons/"
    enviroment_manager = "anaconda:python2, python3"
    ui_test_framework = "uiautomator2:https://github.com/openatx/uiautomator2"
    android = "activity, broadcast, service, content"
    adb = "getprop, pull, push, settings, logat"
    web = "html, javascript, bootstrap, flask"


class Traning(object):
    def day_one(self):
        plan_auto_work = {"培训": "Pass", "安装git": "Pass"}
        plan_test_work = {"测试160": "50%"}

    def day_two(self):
        plan_auto_work1 = {"使用git commit,git push,git pull": "Pass"}
        plan_auto_work2 = {"python lessons": "2"}

    def day_three(self):
        plan_auto_work1 = {"安装Anaconda": "Pass"}
        plan_auto_work2 = {"git创建\切换分支": "Pass"}
        plan_auto_work3 = {"Learn QSA": "学习中"}

    def day_four(self):
        plan_auto_work1 = {"安装android studio": "Pass"}
        plan_auto_work2 = {"培训anaconda": "Pass"}
        plan_auto_work3 = {"python lessons": "完成3小课", "整理测试任务中的自动化部分": "50%"}

    def day_five(self):
        plan_auto_work1 = {"android studio": "学习android的一些知识，和andrdoid原生的测试框架Instrumentation"}
        plan_auto_work2 = {"python lessons": "完成4小课", "整理测试任务中的自动化部分": "100%"}

    def day_six(self):
        plan_auto_work1 = {"adb": "整理一些用到的adb 命令"}
        plan_auto_work2 = {"python": "练习写Python程序"}

    def day_seven(self):
        plan_auto_work1 = {"adb": "整理一些用到的adb 命令"}
        plan_auto_work2 = {"整理分类需求": "50%", "python": "写Paddington_MC_3需求用例"}

    def day_eight(self):
        plan_auto_work1 = {"adb": "整理一些用到的adb 命令"}
        plan_auto_work2 = {"整理分类需求":"80%", "python": "编写测试用例"}

    def work(self):
        plan_08 = {"10/8", "pretest工具客户版本信息显示:100%"}
        plan_09 = {"10/9", "pretest工具widget压力测试:80%"}
        plan_10 = {"10/8", "pretest工具calculator压力测试:100%"}


"""下周两个整理工作：
1. adb命令对比下qsa/modules/adb.py,缺少的部分添加作为功能，并做好注释；
2. 整理soft_plugin 插件的所有功能，做成表格(表格包含：
    . 插件名称
    . function功能说明，如  def abc(c)
      adc:检查音量大小
            参数c: 字符型，设备product name（ro.producdt.name)
            返回值：整型，当前音量大小，异常返回None
"""
if __name__ == '__main__':
    code_sample = CodeSample()
    code_sample.test_get_name()
