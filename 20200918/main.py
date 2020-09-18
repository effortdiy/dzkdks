import requests
from bs4 import BeautifulSoup
from login import LoginCls
from course import Course
import re
import time
import os
import sys

http = requests.session()
http.headers['Referer'] = 'http://learning.uestcedu.com/learning3/scorm/scoplayer/code.htm?r=0.40906900730333606&course_id=2629&content_id=113741&urlto=index%5fsco%2ejsp%3fcontent%5fid%3d113741&returl=course%5flearning%2ejsp%3fcourse%5fid%3d2629%26course%5fname%3d'
http.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59'

# 登录
lCls = LoginCls(http)
if not lCls.login():
    print("登录失败，请重新再试！")
    input(".....")
    sys.exit(0)

# 获取课程列表
course = Course(http)
userInfo,courseList = course.GetCourseList()
while True:
    print("请选择需要学习的课程".center(40,"="))
    for i in range(len(courseList)):
        print('%s %s %s' % (i,courseList[i]['key'],courseList[i]['value']))
    print('999 退出学习')
    print("".center(40,"="))
    course_id = int(input("输入最前面的序号进行学习，如：13，回车确认..."))
    if course_id == 999:
        sys.exit(0)

    # 获取课程明细
    course_id = courseList[course_id].get('value')
    course_details = course.GetCourseDetail(course_id)

    # 跳转到学习网站
    lCls.loginCourse(userInfo,course_id)

    # 根据课程明细开始循环读取
    txtItemId = None
    for i in range(len(course_details)):
        print('%s / %s' % (str(i),str(len(course_details))))
        content_id = course_details[i]
        is_succ = False
        try:
            while not is_succ:
                lmsDic = {}
                scoParmas,flag = course.loadSco(course_id,content_id,lmsDic)
                if isinstance(scoParmas,bool):
                    print("有时候，有一定概率会登录失效，继续运行！")
                    continue
                # index_sco 有问题啊啊啊啊啊
                lmsServer,params = course.index_sco(scoParmas,flag,lmsDic)
                
                # 提交结果道服务器
                course.SubmitCourseDetail(lmsServer,params)
                txtItemId = scoParmas.get('txtItemId')
                if not txtItemId:
                    break
                is_succ = course.CheckCourseDetailFinished(txtItemId)
        except Exception as e:
            print(e)
    print('课程学习完成')

