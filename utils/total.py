import json as js
import requests as r

def get_total():
    information= r.get("https://status.hitokoto.cn/",timeout=60).json()
    total=information['status']['hitokoto']['total']
    return total

get_total()