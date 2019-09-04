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

    def test_get_name(self):
        # 使用try except，确保不会跳出测试
        for i in self.team_member:
            try:
                if i == "lin.shen":
                    print(self.team_member[len(self.team_member) + 1])
                if i == "jixing.hao":
                    print(1 / 0)
            except IndexError as e:
                print("get member error:", e)
                continue
            except ZeroDivisionError as e:
                print("ZeroDivisionError:", e)
                continue
            finally:
                print(u"必须要完成的任务:" + i)


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
        plan_auto_work2 = {"python lessons": "4"}


if __name__ == '__main__':
    code_sample = CodeSample()
    code_sample.test_get_name()
