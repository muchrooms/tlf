#-*-encoding=utf-8-*-
from spider import split_list_iter
import random
import time
import pdb
from spider import async_http


def pager_filter(x):
    return {
            "url": x
            } 


def list_filter(x):
    return {
            "url": x
            } 


price_url = "http://p.3.cn/prices/mgets?type=1&skuIds=%s&area=1_72_2799&callback=JQuery%s&_=%s" 
stock_url = "http://st.3.cn/gsis.html?type=getstocks&skuids=%s&provinceid=1&cityid=72&areaid=2799&callback=jsonp%s&_=%s"
#两个组过滤

def price_filter(items): 
    ret = []
    for group in split_list_iter(items, 60):
        url = price_url % (",".join("J_"+ i for i in group), 
                random.randint(1000000, 10000000),
                int(time.time() * 1000)) 
        ret.append({ "url": url})
    return ret 


def stock_filter(items): 
    keys = async_http.quote(",".join(items.keys()))
    url = stock_url % (keys, random.randint(1000000, 10000000),
                int(time.time() * 1000)) 
    return {
            "url": url,
            "price": items
            }

