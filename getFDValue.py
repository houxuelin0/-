import numpy as np
import requests
import json
import common
import urllib.parse
from urllib.parse import urlencode
#将文件上传到云音服务器，获取文件路径
def getYYAbFilePath(wavfilepath):
    upFileURL = common.dealFileUrl + r'jiepai/hardware/device/type/das/soundDetector/upload-quan'
    files = {'file': open(wavfilepath, 'rb')}
    r = requests.request('POST', upFileURL, files=files)  # 1.上传文件，返回一个路径r.text
    common.YYSeverFilename = r.text
    return r.text

#调用接口计算声音文件
def getwavRedata(freq1,freq2,Nnum,serverfile):
    ''' if common.YYSeverFilename is None:
        rtext = getYYAbFilePath(common.now_wavfilename)
    else:
        rtext = common.YYSeverFilename'''
    #参数
    params = {
        'freq1':int(freq1)*640000/48000,
        'freq2':int(freq2)*640000/48000,
        'N':Nnum,
    }

    query_string = urlencode(params,)  # 将参数编码为URL查询字符串
    full_url = common.soundUrl + "?" + query_string  # 拼接URL和查询字符串
    lasturl = urllib.parse.quote(serverfile)
    response = requests.request('GET', full_url+'&file='+lasturl)
    data = json.loads(response.text)  # 解码字符串
    return data

#删除服务器上的文件
def delSeerverFile(serverfilename):
    parmas = {
        'fileName':(serverfilename).split('/')[-1]
    }
    rd = requests.request('GET', common.DelUrl,params=parmas)#删除只需传文件名
    return rd.text

#返回数值
def calculateData(dataList):
    freq1 = dataList[0]
    freq2 = dataList[1]
    n = int(dataList[2])
    #开始频率
    freq1list = np.array(dataList[3:3 + n])
    #结束频率
    freq2list = np.array(dataList[3 + n:len(dataList)])
    #求出q的值 freq1*q**(n-1)=freq2
    q = (freq2/freq1)**(1/n-1)
    x_trtuevalue=[]
    x=[]
    for i_db in range(n):
        x_num = (freq1*q**i_db/(640000/48000))*1000
        x.append(i_db)
        x_trtuevalue.append(x_num)
    common.xtrue = x_trtuevalue
    common.xfrem = x
    common.prelist = freq1list
    common.dblist = freq2list
    return x_trtuevalue,x,freq1list,freq2list

