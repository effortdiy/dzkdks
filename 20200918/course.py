# coding:utf8


class Course():
    def __init__(self,http):
        self.http = http
        pass

    def GetCourseList(self):
        from bs4 import BeautifulSoup

        url = "https://student.uestcedu.com/console/apply/student/student_learn.jsp"
        resReturn = []
        
        res = self.http.get(url)
        soup = BeautifulSoup(res.text,features='lxml')

        # 用户的账号密码也在这里
        userInfo = {}
        inputs = soup.select_one('form').select('input')        
        for input in inputs:
            name = input.attrs['name']
            value = input.attrs['value']
            userInfo[name] = value

        table = soup.select_one('table[id=tblDataList]')
        trs = table.select('tr')
        for tr in trs:
            key = tr.contents[2].text.strip()
            value = tr.contents[9].contents[0].attrs.get('learning_course_id')
            if value and value!='0':
                resReturn.append({'key':key,'value':value})
        return userInfo,resReturn

    def GetCourseDetail(self,course_id):
        from bs4 import BeautifulSoup

        url = 'http://learning.uestcedu.com/learning3/course/ajax_learn_content.jsp?course_id={}&parent_id=1&content_type=&flag=2&b_edit=0&r=0%2e9508102444684912&59834'.format(course_id)
        res = self.http.get(url)
        soup = BeautifulSoup(res.text,features="lxml")
        a = soup.select('a')
        resReturn = []
        for item in a:
            if item.parent.parent.find('div').attrs['class'] == ['scorm','completed']:
                continue
            href = item.attrs['href']
            resReturn.append(self.__maths(r'javascript:showLearnContent\((.+?),',href))        
        return resReturn

    def CheckCourseDetailFinished(self,course_id):
        url = 'http://learning.uestcedu.com/learning3/scorm/scoplayer/after_commit.jsp?item_id=%s' % course_id
        res = self.http.get(url)
        return '"cmi.core.lesson_status","completed"' in res.text

    def SubmitCourseDetail(self,lmsServer,params):
        url = "http://learning.uestcedu.com/learning3/{}?op=commit_data&script=&afterscript=window%2elocation%2ehref%3d%40%40%40http%3a%2f%2flearning%2euestcedu%2ecom%2flearning3%2fscorm%2fscoplayer%2fafter%5fcommit%2ejsp%3fitem%5fid%3d106568%26url%3dhttp%253a%252f%252fispace%252euestcedu%252ecom%252fispace2%255fsync%252fscormplayer%252fcommit%252ehtm%253f0%252e2650634293858696%40%40%40%3b&07411".format(lmsServer)
        # url = "http://learning.uestcedu.com/learning3/servlet/com.lemon.web.ActionServlet?handler=com%2elemon%2escorm2%2eScormWebServlet&op=commit_data&script=&_no_html=0&afterscript=window%2elocation%2ehref%3d%40%40%40http%3a%2f%2flearning%2euestcedu%2ecom%2flearning3%2fscorm%2fscoplayer%2fafter%5fcommit%2ejsp%3fitem%5fid%3d104768%26url%3dhttp%253a%252f%252fispace%252euestcedu%252ecom%252fispace2%255fsync%252fscormplayer%252fcommit%252ehtm%253f0%252e5371122291517825%40%40%40%3b&27432"    
        res = self.http.post(url,params)    
        pass

    def loadSco(self,course_id,content_id,lmsDic):
        from bs4 import BeautifulSoup
        import time

        url = "http://learning.uestcedu.com/learning3/scorm/scoplayer/load_sco.jsp?r=0.11965429171195896&course_id={}&content_id={}&urlto=http%3a%2f%2flearning%2euestcedu%2ecom%2flearning3%2fcourse%2flearn%5fcontent%5finfo%2ejsp%3fcontent%5fid%3d113757%26index%3d42%26item%5fid%3d104780%26type%3dsco%2670287&returl=course%5flearning%2ejsp%3fcourse%5fid%3d2629%26course%5fname%3d&prev_item_id=104779&87642".format(course_id,content_id)
        # url = "http://learning.uestcedu.com/learning3/scorm/scoplayer/load_sco.jsp?r=0.4372567652851451&course_id=2669&content_id=115717&urlto=http%3a%2f%2flearning%2euestcedu%2ecom%2flearning3%2fcourse%2flearn%5fcontent%5finfo%2ejsp%3fcontent%5fid%3d115717%26index%3d7%26item%5fid%3d106561%26type%3dsco%2645107&returl=course%5flearning%2ejsp%3fcourse%5fid%3d2669%26course%5fname%3d&prev_item_id=106560&00114"
        res = self.http.get(url)
        if "登录已失效，请" in res.text:
            return False,None

        soup = BeautifulSoup(res.text,features="lxml")
        form = soup.find('form')
        inputs = form.select('input')
        resReturn = {}
        for item in inputs:
            name = item.attrs['name']
            value = item.attrs.get('value')
            # 如果有value
            if not value:
                value = self.__maths('%s.value="(.+?)";'%name,res.text)
                if not value:
                    _name = self.__maths('%s.value=(.+?);'% name,res.text)
                    value = self.__maths('%s="(.+?)";'%_name,res.text)
            resReturn[name]=value
        resReturn['txtItemId'] = self.__maths("scoHandle.ItemId=\"(.+?)\"",res.text)
        resReturn['txtLMSWeb'] = resReturn['txtLMSServer'] = 'http://learning.uestcedu.com/learning3'
        urlParams = self.__maths('@@SERVER_IP/@@WEB_APP_ID/(.+?)"',res.text)
        sScormIp =  self.__maths('sScormIp = "(.+?)"',res.text)
        upload = self.__maths('sScormUploadApp = "(.+?)"',res.text)
        resReturn['txtScormIp'] = sScormIp
        resReturn['txtURL'] = 'http://%s/%s/%s' %(sScormIp,upload,urlParams)
        resReturn['token'] =  self.__maths("form1.token.value=\"(.+?)\"",res.text)
        lmsValue = self.__maths('apiHandle.LMSSetValue\((.+?)\);',res.text,True)
        self.__getMyDic(lmsDic,lmsValue)    
        
        # 反算时间
        needTotal = int(lmsDic.get('cmi.interactions.0.time',60))
        currTotal = int(lmsDic.get('cmi.core.total_time',0))

        if not resReturn.get('txtItemId'):
            raise Exception("课程有异常，请重新选择其他课程！")

        print(resReturn['txtItemId'].center(40,'*'))
        print(u'已看:%s' % currTotal)
        print(u'共需:%s' % needTotal)
        if needTotal>currTotal:
            # 服务器采用的是两次请求间隔来算的时间,所以改大也没意义
            time.sleep(15)        
            lmsDic['cmi.core.session_time'] = '15'#str(needTotal-currTotal+1)
            lmsDic['cmi.core.total_time'] = str(currTotal+15)

        resReturn['txtCommit'] = '&'.join([key+'='+value for key,value in lmsDic.items()])
        flag = self.__maths('flag=(.+?)"',res.text)
        return resReturn,flag

    def index_sco(self,params,flag,lmsDic):
        url = "http://ispace.uestcedu.com/ispace2_sync/scormplayer/index_sco.jsp?flag=%s" % flag
        res = self.http.post(url,params)
        resReturn = {}
        lmsValue = self.__maths('apiHandle.LMSSetValue\((.+?)\);',res.text,True) 
        self.__getMyDic(lmsDic,lmsValue)
        lmsDic['cmi.core.lesson_status'] = 'completed'  
        resReturn['txtCommit'] = '&'.join([key+'='+value for key,value in lmsDic.items()])
        resReturn['txtUserId'] = self.__maths('userId="(.+?)"',res.text)
        resReturn['txtSCOType'] = self.__maths('scoHandle.type="(.+?)"',res.text)
        resReturn['txtCoursewareId'] = self.__maths('organHandle.coursewareId="(.+?)"',res.text)
        resReturn['txtItemId'] = self.__maths('scoHandle.ItemId="(.+?)"',res.text)
        lmsServer = self.__maths('apiHandle.LMSServer="(.+?)"',res.text)
        return lmsServer,resReturn

    def __getMyDic(self,dic,array):
        for item in array:
            key,value = item.replace('"','').split(',')
            dic[key] = value

    def __maths(self,search,source,isMore = False):
        import re
        if not isMore:
            m = re.search(search,source)
            if m:
                return re.search(search,source).group(1)
            else:
                return None
        else:
            return re.findall(search,source)