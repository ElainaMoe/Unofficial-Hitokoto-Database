import requests as r
import json as js
import csv
import os
import datetime
from array import array
import time
import logging
from utils.total import get_total as total
import sys
import telepot

new=False
token=str(sys.argv[1])
chat_id=str(sys.argv[2])
bot=telepot.Bot(token)

def send(message):
    bot.sendMessage(chat_id,message, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)
# logging.basicConfig(level=logging.INFO,#控制台打印的日志级别
#                     filename=('./logs/{}.log'.format(time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) )),
#                     filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
#                     #a是追加模式，默认如果不写的话，就是追加模式
#                     format=
#                     '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
#                     #日志格式
#                     )
# 程序运行时间开始
start_Pro=datetime.datetime.now()
start_timestamp=time.time()
def create_csv(path):
    with open(path,"w+",newline="",encoding="utf8") as file:    # 打开文件，也相当于一个回车，避免覆盖文档
        csv_file = csv.writer(file)
        head = heads # 创建csv表头
        csv_file.writerow(head)
def append_csv(path):
    with open(path,"a+",newline='',encoding="utf8") as file:
        csv_file = csv.writer(file)
        data = [inputs]
        csv_file.writerows(data)
def get_requests():
    try:
        res = r.get('https://international.v1.hitokoto.cn/',timeout=60) # 得到服务器回应，此时回应的内容为json文件（res.text）和状态码
        return res
    except Exception as e:
        print('获取失败，原因：{}，即将重试'.format(e))
        return True
path = 'hitokoto.csv'
heads = ["id","sort","hitokoto","from", "from_who", "creator", 'creator_uid', 'reviewer', 'uuid', 'created_at']
num = total()
temp=array('i',[0])   # 初始化temp变量，用于放置已抓取的ID
if (os.path.exists(path)!=True):    # 判断文件是否存在，不存在则创建
    create_csv(path)
    i=0
else:
    print('断点续抓模式已开启！')
    file=open(path,'r',encoding='utf8')
    ids_in_file=csv.reader(file)
    for id_in_file in ids_in_file:
        try:
            temp.append(int(id_in_file[0])) # 将文件中已有的id加入temp数组
        except ValueError:
            id_in_file[0] = 0   # 读取已有文件时"id"无法被识别为int型所以要去掉
        i=0
        i=i+len(temp)
sorts=""
dup=0
all=0   # 总抓取次数
while True:
    end_timestamp=time.time()
    if(int(end_timestamp)-int(start_timestamp)>=19800): # 因Github Action的运行最长时长为六个小时，故在这里做出判断（五个半小时即停下抓取）
        break
    if(i>num):   # 如果不加1那么最后一次将无法运行
        break
    time.sleep(3)
    print("----------------------------------------------------------")
    print("正在获取新的一言……")
    print("Fetching new Hitokoto......")
    
    while True:
        print('正在获取，请稍后……')
        result=get_requests()
        if(result!=True and result.status_code == 200):
            res=result
            break
        else:
            result=get_requests()
    all=all+1
    print(res)
    data=res.json() # 将获取到的结果转为json字符串
    temp_minus=len(temp)-1
    if temp_minus!=0:
        t=1
        print("正在检测是否抓取过结果……")
        for t in range(len(temp)):
            if(int(data["id"])==temp[t]):
                dup=dup+1
                end_Pro=datetime.datetime.now()
                print("发现已经抓取到的结果，正在丢弃……")
                print("已完成数量：{}/{}，已经用时：{} ，总抓取{}次，重复次数{}次，重复率{}".format(len(temp)-1,num,end_Pro-start_Pro,all,dup,dup/all))
                break
            elif(t==len(temp)-1):
                print("未抓取过的结果，正在存入文件……")
                new=True
                if data["type"]== "a": sorts=("Anime")  # 自动把分类码还原为分类
                elif data["type"]== "b": sorts=("Comic")
                elif data["type"]== "c": sorts=("Game")
                elif data["type"]== "d": sorts=("Novel")
                elif data["type"]== "e": sorts=("Myself")
                elif data["type"]== "f": sorts=("Internet")
                elif data["type"]== "g": sorts=("Other")
                elif data['type']== 'h': sorts=("Movie")
                elif data['type']== 'i': sorts=("Poem")
                elif data['type']== 'j': sorts=("Netease")
                elif data['type']== 'k': sorts=("Philosophy")
                elif data['type']== 'l': sorts=('Intelligent')
                else: sorts=('Unknown')
                inputs=[data["id"],sorts,data["hitokoto"],data['from']]
                try:
                    if(data['from_who']==None):
                        inputs.append('null')
                    else:
                        inputs.append(data["from_who"])
                except KeyError:
                    inputs.append("null")
                inputs.append(data['creator'])
                try: 
                    inputs.append(data['creator_uid'])
                except KeyError:
                    inputs.append("null")
                try:
                    inputs.append(int(data['reviewer']))
                except KeyError:
                    inputs.append('0')
                try:
                    inputs.append(data['uuid'])
                except KeyError:
                    inputs.append("null")
                try:
                    timeArray = time.localtime(int(data['created_at']))
                    created_at = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                except ValueError:
                    created_at = ('null')
                except OSError:
                    timeArray = time.localtime(int(data['created_at'])/1000)
                    created_at = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                inputs.append(created_at)
                print(res.text)
                append_csv(path)
                temp.append(data["id"])
                end_Pro=datetime.datetime.now()
                print("已完成数量：{}/{}，已经用时：{} ，总抓取{}次，重复次数{}次，重复率{}".format(len(temp)-1,num,end_Pro-start_Pro,all,dup,dup/all))
                print('Timestamp: {}/19800'.format(end_timestamp-start_timestamp))
                i=i+1
                break
    else:
        if data["type"]== "a": sorts=("Anime")  # 自动把分类码还原为分类
        elif data["type"]== "b": sorts=("Comic")
        elif data["type"]== "c": sorts=("Game")
        elif data["type"]== "d": sorts=("Novel")
        elif data["type"]== "e": sorts=("Myself")
        elif data["type"]== "f": sorts=("Internet")
        elif data["type"]== "g": sorts=("Other")
        elif data['type']== 'h': sorts=("Movie")
        elif data['type']== 'i': sorts=("Poem")
        elif data['type']== 'j': sorts=("Netease")
        elif data['type']== 'k': sorts=("Philosophy")
        elif data['type']== 'l': sorts=('Intelligent')
        else: sorts=('Unknown')
        inputs=[data["id"],sorts,data["hitokoto"],data['from']]
        try:
            if(data['from_who']==None):
                inputs.append('null')
            else:
                inputs.append(data["from_who"])
        except KeyError:
            inputs.append('null')
        inputs.append(data['creator'])
        try: 
            inputs.append(data['creator_uid'])
        except KeyError:
            inputs.append("null")
        try:
            inputs.append(int(data['reviewer']))
        except KeyError:
            inputs.append('0')
        try:
            inputs.append(data['uuid'])
        except KeyError:
            inputs.append("null")
        try:
            timeArray = time.localtime(int(data['created_at']))
            created_at = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        except ValueError:
            created_at = ('null')
        except OSError:
            timeArray = time.localtime(int(data['created_at'])/1000)
            created_at = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        inputs.append(created_at)
        print(res.text)
        append_csv(path)
        temp.append(data["id"])
        end_Pro=datetime.datetime.now()
        print("已完成数量：{}/{}，已经用时：{} ，总抓取{}次，重复次数{}次，重复率{}".format(len(temp)-1,num,end_Pro-start_Pro,all,dup,dup/all))
        print('Timestamp: {}/19800'.format(end_timestamp-start_timestamp))
        i=i+1
end_Pro=datetime.datetime.now()
print('----------------------------------------------------------')
try:
    print('已抓取完成！抓取数量{}，用时{}，总抓取{}次，重复{}次，重复率{}'.format(len(temp)-1,end_Pro-start_Pro,all,dup,dup/all))
    print('Timestamp: {}/19800'.format(end_timestamp-start_timestamp))
except ZeroDivisionError:
    print('已抓取完成！抓取数量{}，用时{}，总抓取{}次，重复{}次，重复率0'.format(len(temp)-1,end_Pro-start_Pro,all,dup))
    print('Timestamp: {}/19800'.format(end_timestamp-start_timestamp))
if new:
    try:
        msg='[Unofficial-Hitokoto-Spider]已抓取完成！抓取数量{}/{}，用时{}，总抓取{}次，重复{}次，重复率{}'.format(len(temp)-1,num,end_Pro-start_Pro,all,dup,dup/all)
        usedtime='[Unofficial-Hitokoto-Spider]Timestamp: {}/19800'.format(end_timestamp-start_timestamp)
    except ZeroDivisionError:
        msg='[Unofficial-Hitokoto-Spider]已抓取完成！抓取数量{}/{}，用时{}，总抓取{}次，重复{}次，重复率0'.format(len(temp)-1,num,end_Pro-start_Pro,all,dup)
        usedtime='[Unofficial-Hitokoto-Spider]Timestamp: {}/19800'.format(end_timestamp-start_timestamp)
    send(msg)
    send(usedtime)
else:
    msg='[Unofficial-Hitokoto-Spider]未抓取到任何新内容！现有数量{}/{}'.format(len(temp)-1,num)
    send(msg)
