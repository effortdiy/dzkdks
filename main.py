import requests
from bs4 import BeautifulSoup
import re
import time

http = requests.session()
print("按要求输入，回车确认!")
cookies=input("输入你的cookie:")# 这里是你的cookies字符串,通过浏览器获得
headers={
    'Referer':'http://learning.uestcedu.com/learning3/scorm/scoplayer/code.htm?r=0.40906900730333606&course_id=2629&content_id=113741&urlto=index%5fsco%2ejsp%3fcontent%5fid%3d113741&returl=course%5flearning%2ejsp%3fcourse%5fid%3d2629%26course%5fname%3d',
    'Cookie':cookies
}

course_id = input("输入你的course_id:")
# 这个地址是你的学习课程的地址      
course_url = "http://learning.uestcedu.com/learning3/course/ajax_learn_content.jsp?course_id={}&parent_id=1&content_type=&flag=2&b_edit=0&r=0%2e9508102444684912&59834".format(course_id)

def maths(search,source,isMore = False):
    if not isMore:
        m = re.search(search,source)
        if m:
            return re.search(search,source).group(1)
        else:
            return None
    else:
        return re.findall(search,source)

def getMyDic(dic,array):
    for item in array:
        key,value = item.replace('"','').split(',')
        dic[key] = value

def getCourse():
    res = http.get(course_url,headers=headers)
    soup = BeautifulSoup(res.text)
    a = soup.select('a')
    resReturn = []
    for item in a:
        if item.parent.parent.find('div').attrs['class'] == ['scorm','completed']:
            continue
        href = item.attrs['href']
        resReturn.append(maths(r'javascript:showLearnContent\((.+?),',href))        
    return resReturn

def loadSco(course_id,content_id,lmsDic):
    url = "http://learning.uestcedu.com/learning3/scorm/scoplayer/load_sco.jsp?r=0.11965429171195896&course_id={}&content_id={}&urlto=http%3a%2f%2flearning%2euestcedu%2ecom%2flearning3%2fcourse%2flearn%5fcontent%5finfo%2ejsp%3fcontent%5fid%3d113757%26index%3d42%26item%5fid%3d104780%26type%3dsco%2670287&returl=course%5flearning%2ejsp%3fcourse%5fid%3d2629%26course%5fname%3d&prev_item_id=104779&87642".format(course_id,content_id)
    res = http.get(url,headers=headers)
    soup = BeautifulSoup(res.text)
    form = soup.find('form')
    inputs = form.select('input')
    resReturn = {}
    for item in inputs:
        name = item.attrs['name']
        value = item.attrs.get('value')
        # 如果有value
        if not value:
            value = maths('%s.value="(.+?)";'%name,res.text)
            if not value:
                _name = maths('%s.value=(.+?);'% name,res.text)
                value = maths('%s="(.+?)";'%_name,res.text)
        resReturn[name]=value
    resReturn['txtLMSWeb'] = resReturn['txtLMSServer'] = 'http://learning.uestcedu.com/learning3'
    urlParams = maths('@@SERVER_IP/@@WEB_APP_ID/(.+?)"',res.text)
    sScormIp =  maths('sScormIp = "(.+?)"',res.text)
    upload = maths('sScormUploadApp = "(.+?)"',res.text)    
    resReturn['txtScormIp'] = sScormIp
    resReturn['txtURL'] = 'http://%s/%s/%s' %(sScormIp,upload,urlParams)
    
    lmsValue = maths('apiHandle.LMSSetValue\((.+?)\);',res.text,True)
    getMyDic(lmsDic,lmsValue)    
    
    # 反算时间
    needTotal = int(lmsDic['cmi.interactions.0.time'])
    currTotal = int(lmsDic.get('cmi.core.total_time',0))
    print(u'已看:%s' % currTotal)
    print(u'共需:%s' % needTotal)
    if needTotal>currTotal:
        # 服务器采用的是两次请求间隔来算的时间,所以改大也没意义
        time.sleep(15)        
        lmsDic['cmi.core.session_time'] = '15'#str(needTotal-currTotal+1)
        lmsDic['cmi.core.total_time'] = str(currTotal+15)

    resReturn['txtCommit'] = '&'.join([key+'='+value for key,value in lmsDic.items()])
    flag = maths('flag=(.+?)"',res.text)
    return resReturn,flag

def index_sco(params,flag,lmsDic):
    url = "http://ispace.uestcedu.com/ispace2_sync/scormplayer/index_sco.jsp?flag=%s" % flag
    res = http.post(url,params)
    resReturn = {}
    lmsValue = maths('apiHandle.LMSSetValue\((.+?)\);',res.text,True) 
    getMyDic(lmsDic,lmsValue)
    lmsDic['cmi.core.lesson_status'] = 'completed'  
    resReturn['txtCommit'] = '&'.join([key+'='+value for key,value in lmsDic.items()])
    resReturn['txtUserId'] = maths('userId="(.+?)"',res.text)
    resReturn['txtSCOType'] = maths('scoHandle.type="(.+?)"',res.text)
    resReturn['txtCoursewareId'] = maths('organHandle.coursewareId="(.+?)"',res.text)
    resReturn['txtItemId'] = maths('scoHandle.ItemId="(.+?)"',res.text)
    return resReturn

# 最后结果
def finish(params):
    url = "http://learning.uestcedu.com/learning3/servlet/com.lemon.web.ActionServlet?handler=com%2elemon%2escorm2%2eScormWebServlet&op=commit_data&script=&_no_html=0&afterscript=window%2elocation%2ehref%3d%40%40%40http%3a%2f%2flearning%2euestcedu%2ecom%2flearning3%2fscorm%2fscoplayer%2fafter%5fcommit%2ejsp%3fitem%5fid%3d104768%26url%3dhttp%253a%252f%252fispace%252euestcedu%252ecom%252fispace2%255fsync%252fscormplayer%252fcommit%252ehtm%253f0%252e5371122291517825%40%40%40%3b&27432"    
    http.post(url,params)    

# 判断课程是否完成
def checkFinished(item_id):
    url = 'http://learning.uestcedu.com/learning3/scorm/scoplayer/after_commit.jsp?item_id=%s' % item_id
    res = http.get(url,headers=headers)
    return '"cmi.core.lesson_status","incomplete"' not in res.text

txtItemId = None
content_ids = getCourse()
for content_id in content_ids:
    is_succ = False
    while not is_succ:
        lmsDic = {}
        scoParmas,flag = loadSco(course_id,content_id,lmsDic)
        txtItemId = scoParmas['txtItemId']
        params = index_sco(scoParmas,flag,lmsDic)
        finish(params)
        is_succ = checkFinished(txtItemId)
print('finshed')