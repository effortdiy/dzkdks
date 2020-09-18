# coding:utf8


class LoginCls():
    def __init__(self, http):
        self.http = http

    def login(self):
        # 获取二维码
        url = "https://student.uestcedu.com/rs/login/qrcode/create"
        res = self.http.get(url)
        # 扫码登录
        js_json = res.json()
        if js_json.get('success'):
            data = js_json.get('data')
            if data:
                qrCode = data.get('qrCode')
                uuid = data.get('uuid')
                self.__showImage(qrCode)
                return self.__checkLogin(uuid)
        return False

    def __showImage(self, qrCode):
        import base64

        b64_data = qrCode.split(';base64,')[1]
        data = base64.b64decode(b64_data)
        with open('./qr.png', 'wb') as f:
            f.write(data)

        from PIL import Image
        im = Image.open('./qr.png')
        im.show()
        print("请通过微信扫码登录！")

    def __checkLogin(self, uuid):
        import time
        url = "https://student.uestcedu.com/rs/login/qrcode/query?uuid={}".format(
            uuid)

        while True:
            time.sleep(2)
            res = self.http.get(url)
            js_json = res.json()
            if js_json.get('success'):
                data = js_json.get('data')
                if data and data == 'new':
                    continue
                elif data and data == 'expired':
                    print("二维码过期，请关闭后重新打开！")
                    break
                elif data and data == 'scanned':
                    print("扫码成功，请在移动端确认登录")
                    continue
                elif data and data == 'finish':
                    print("登录成功".center(40, '='))
                    res = self.http.get(
                        'https://student.uestcedu.com/console/user_info.jsp?0.7357649383724503')
                    js_json = res.json()
                    user_id = js_json.get('user_id')
                    login_name = js_json.get('login_name')
                    user_name = js_json.get('user_name')
                    print("user_id:%s" % user_id)
                    print("login_name:%s" % login_name)
                    print("user_name:%s" % user_name)
                    print("登录完毕".center(40, '='))
                    return True
        return False

    def loginCourse(self, user_info, course_id):

        # 跳转登录获取cookie
        data = {'txtLoginName': user_info.get('txtLoginName'),
                'txtPassword': user_info.get('txtPassword'),
                'txtUserType': 'student',
                'txtCourseId': course_id,
                'txtClassId': '',
                'txtClassName': '',
                'txtSiteId': 20}
        url = 'http://learning.uestcedu.com/learning3/uestc_login.jsp?0.4207359735055143'
        res = self.http.post(url, data=data)

        # 1
        url = 'http://learning.uestcedu.com/learning3/theme_cc/_ui_switch.jsp?0.9311432166115505'
        res = self.http.get(url)

        # 2
        url = 'http://learning.uestcedu.com/learning3/_language.jsp'
        res = self.http.get(url)

        # 3
        url = 'http://learning.uestcedu.com/learning3/servlet/com.lemon.web.LanguageServlet?base_name=global_ui&0.5820032088127391'
        res = self.http.get(url)

        # 4
        url = 'http://learning.uestcedu.com/learning3/servlet/com.lemon.web.ActionServlet?handler=com%2euestc%2euser%2eUserLoginAction&op=login&type=to_learning&op=execscript&urlto=&script=parent.afterAction()&_no_html=1&0.4457956593229837'
        res = self.http.get(url)

        # post密码过去，获取登录成功
        url = 'http://learning.uestcedu.com/learning3/servlet/com.lemon.web.ActionServlet?handler=com%2euestc%2euser%2eUserLoginAction&op=login&type=to_learning&op=execscript&urlto=&script=parent.afterAction()&_no_html=1&0.35688546309448843'
        data = {'txtLoginName':  user_info.get('txtLoginName'),
                'txtPassword':  user_info.get('txtPassword'),
                'txtCourseId': course_id,
                'ran': '0.8806067547585541'}
        res = self.http.post(url, data=data)

        # 开始学习课程
        url = 'http://learning.uestcedu.com/learning3/course/enter_in_course.jsp'
        data = {'txtLoginName': user_info.get('txtLoginName'),
            'txtPassword': '',
            'txtUserType': 'student',
            'txtCourseId': course_id,
            'txtClassId': '',
            'txtClassName': '',
            'txtSiteId': 20}
        res = self.http.post(url, data=data)

        pass


if __name__ == "__main__":
    import requests
    http = requests.session()

    l = LoginCls(http)
    l.login()
