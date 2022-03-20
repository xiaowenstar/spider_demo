import os
import re
import time
import uuid

import execjs
import requests
from PIL import Image


class Login(object):
    def __init__(self, mobile):
        self.mobile = mobile
        self.http = requests.session()
        self.js = execjs.compile(open(f"{os.getcwd()}/encrypt.js", "r").read())
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'referer': 'https://passport.58.com/login/?path=https%3A//hz.58.com/searchjob/%3Fspm%3D116138685575.zhaopin_baidu%26utm_source%3D12345&PGTID=0d302409-0004-f026-99d0-d5d7983ad769&ClickID=5',
        }

    def encrypt(self, mobile):
        # 加密mobile
        result = self.js.call("main", mobile)
        return result

    def get_code(self, vcodekey):
        # 获取图片验证码
        url = "https://passport.58.com/sec/58/validcode/get?vcodekey={}&time={}".format(vcodekey, str(int(time.time()*1000)))
        response = self.http.get(url, headers=self.headers)
        with open("code.jpg", "wb") as f:
            f.write(response.content)
        img = Image.open("code.jpg")
        img.show()
        os.remove("code.jpg")
        validcode = input("请输入图片验证码:")
        return validcode

    def getPath(self):
        # 获取网页中的path参数
        res = self.http.get("https://passport.58.com/login?source=58-homepage-pc&path=https://yj.58.com/?utm_source=market&spm=u-2d2yxv86y3v43nkddh1.BDPCPZ_BT").text
        pattern = re.compile(r'PATH = "(.*?)"', re.S)
        path = re.findall(pattern, res)[0]
        print("path:", path)
        return path

    def getToken(self, path):
        # 获取初始化token参数
        params = {
            "source": "58-homepage-pc",
            "path": path,
            "psdk-d": "jsdk",
            "psdk-v": "1.1.2",
            "xxzl_staticvalue": "11be4f83b0e71d49b9e3b93d1f50cad6_1647673332118_99265f44afbe433d8543c1c3500bb546_3702641554",
            "xxzl_namespace": "zhaq_pc",
            "callback": "",
        }
        url = "https://passport.58.com/58/mobile/init"
        token = self.http.get(url, params=params, headers=self.headers).json()["data"]["token"]
        print("token:", token)
        return token

    def getCode(self, params):
        # 获取短信验证码 返回tokencode参数
        url = f"https://passport.58.com/58/mobile/getcode"
        res = self.http.get(url, params=params).json()
        msg = res["msg"]
        print(msg)
        if msg == "请输入正确的手机号码":
            os._exit(9)
        if "图片验证码" in msg:
            if msg == "图片验证码错误":
                vcodekey = params["vcodekey"]
            if msg == "请输入图片验证码":
                vcodekey = res["data"]["vcodekey"]
            validcode = self.get_code(vcodekey)
            params["vcodekey"] = vcodekey
            params["validcode"] = validcode
            return self.getCode(params)
        if msg == "动态码已发送":
            tokencode = res["data"]["tokencode"]
            print("tokencode:", tokencode)
            return tokencode

    def login(self, params, mobilecode, tokencode):
        # 登陆
        params["mobilecode"] = mobilecode
        params["tokencode"] = tokencode
        params["finger2"] = "zh-CN|30|1.25|8|1920_1080|1920_1055|-480|1|1|1|undefined|1|unknown|MacIntel|unknown|5|false|false|false|false|false|0_false_false|d41d8cd98f00b204e9800998ecf8427e|b7aaa8eba8616771a7861e79060fe491"
        params["fingerprint"] = "-vkd7sT77XOGEo0B0p3M1_HQw3iyG2Sh"
        url = f"https://passport.58.com/58/mobile/pc/login"
        res = self.http.get(url, params=params)
        print(res.json())
        print(res.headers)

    def run(self):
        path = self.getPath()
        token = self.getToken(path)
        date = {
            "path": path,
            "mobile": self.encrypt(self.mobile),
            "codetype": "0",
            "token": token,
            "voicetype": "0",
            "source": "58-homepage-pc",
            "psid": uuid.uuid4(),
            "psdk-d": "jsdk",
            "psdk-v": "1.1.2",
            "xxzl_staticvalue": "11be4f83b0e71d49b9e3b93d1f50cad6_1647673332118_99265f44afbe433d8543c1c3500bb546_3702641554",
            "xxzl_dynamicvalue": "0",
            "xxzl_namespace": "zhaq_pc",
            "callback": ""
        }
        tokencode = self.getCode(date)
        mobilecode = input("请输入短信验证码:")
        self.login(date, mobilecode, tokencode)


if __name__ == "__main__":
    login = Login("")  # 手机号登陆
    login.run()
