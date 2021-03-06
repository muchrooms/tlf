#-*-encoding=utf-8-*-
from lxml import etree
from spider import async_http
from spider import log_with_time
from spider import jsonp_json
from spider import format_price
import pdb
import re
import json
import time
import random
import simple_http
import traceback

#http://list.jd.com/list.html?cat=670,671,672
#http://list.jd.com/670-677-678.html

base = "http://list.jd.com/list.html?cat="

def fix_url(url):
    if "tuan" in url:
        log_with_time("skip url: %s" % url)
        return
    x = re.findall("/([0-9\-]+)\.", url)
    if not x:
        return
    return base + ",".join(x[0].split("-"))


all_cats = None

def cats_parser(url, res, rule):
    content = res['text']
    global all_cats
    if url == "http://www.jd.com/allSort.aspx":
        t = etree.HTML(content)
        cats = t.xpath(rule[0])
        ret = []
        for i in cats:
            href = i.attrib["href"]
            if "/1713" in href:
                continue
            url = fix_url(i.attrib["href"].encode("utf-8"))
            if url:
                ret.append(url)
        all_cats = set(ret)
    else:
        cats = set(re.findall("([0-9]+-[0-9]+-[0-9]+)\|", content))
        urls = []
        for cat in cats:
            if cat.startswith("1713"):
                continue
            urls.append(base + cat.replace("-", ","))
        return list(all_cats.union(set(urls)))


normal_base = "http://list.jd.com/list.html?cat={0}&stock=0&page={1}&JL=6_0_0"


def pager(task, rule):
    try:
        tree = etree.HTML(task["text"])
    except:
        traceback.print_exc()
        return
    count = tree.xpath(rule["normal"])
    if not count:
        log_with_time("pager, no count: %s" % task["url"])
        return
    count = int(count[0])
    if count > 450:
        log_with_time("need split page: %s" % task["url"])
    url = task["url"]
    cats =  re.findall("=([0-9,]+)", url)
    price_range = re.findall("(ev=.*%40)", url)
    if price_range:
        base = "%s&%s" % (normal_base, price_range[0])
    else:
        base = normal_base
    ret = []
    if not cats:
        log_with_time("no cats in url: %s" % url);
        return
    if task.get("limit"):
        count = min((task.get("limit"), count))
    for i in range(1, count+1):
        ret.append(base.format(async_http.quote(cats[0]), i))
    return ret


def test_list(items):
    pdb.set_trace()


dp_base = "http://item.jd.com/%s.html"


def list_parser(task, rule):
    tree = etree.HTML(task["text"].decode("utf-8", "ignore"))
    nodes = tree.xpath(rule["node"])
    prices = []
    dps = []
    now = int(time.time())
    dps_log = {}
    styles = []
    comments = {} 
    for node in nodes:
        sku = node.attrib.get("data-sku") 
        title = node.xpath(rule["title"])
        comment = node.xpath(rule["comment"])
        if not sku:
            log_with_time("sku rule error: %s" % task["url"])
            continue
        if not title:
            log_with_time("no title: %s %s" % (task["url"], sku))
            title = [""]
        if sku and comment:
            comments[sku] = comment[0]
        groups = node.xpath(rule["group"])
        if sku and len(groups) > 1:
            styles.append(sku)
        if sku:
            dps.append((dp_base % sku, title[0]))
        if groups:
            for item in groups:
                sku = item.attrib["data-sku"]
                dps_log[sku] = now
                prices.append(sku)
        else:
            dps_log[sku] = now
            prices.append(sku) 
    return {
            "dps_log": dps_log,
            "promo": prices,
            "dp": dps,
            "price": prices,
            "styles": styles,
            "comment": comments
            }


def styles_parser(task, rule):
    text = re.findall(rule, task["text"])
    if not text:
        log_with_time("colorSize rule error: %s" % task["url"])
        return
    prices = []
    dps_log = {}
    styles= json.loads(text[0].decode("gbk"))
    now = int(time.time())
    for style in styles:
        sku = str(style["SkuId"])
        dps_log[sku] = now
        prices.append(sku)
    return {
            "dps_log": dps_log,
            "price": prices,
            }



def price_parser(task, rule):
    try:
        items = jsonp_json(task["text"])
    except ValueError as e:
        log_with_time("price_parser: jsonp_json: %s" % task["text"])
        return
    d = {}
    for item in items:
        d[item["id"].split("_")[1]] =  item["p"]
    return [d]



def stock_parser(task, rule):
    try:
        stock = jsonp_json(task["text"].decode("gbk"))
    except ValueError as e:
        log_with_time("stock_parser: jsonp_json: %s" % task["text"])
        return
    stocks = {}
    for key,value in stock.items():
        s = value["StockStateName"]
        if u"现货" in s or u"有货" in s:
            stocks[key] = 1
        else:
            stocks[key] = 0
    ret = []
    prices = task["price"]
    for key,price in prices.items():
        if key not in stocks:
            log_with_time("key not in stocks: %s" % task["url"])
            continue
        ret.append((key, price, stocks[key]))
    result = format_price(ret) 
    return result



def get_pids(items):
    pids = {}
    for entry in items: 
        pid = GET_PID.findall(entry[2])
        if not pid:
            continue
        pid = pid[0]
        pids[pid] = entry  
    return pids.keys() 


GET_PID = re.compile("/([0-9]+)\.") 

price_url = "http://p.3.cn/prices/mgets?type=1&skuIds=%s&area=1_72_2799&callback=JQuery%s&_=%s" 

stock_url = "http://st.3.cn/gsis.html?type=getstocks&skuids=%s&provinceid=1&cityid=72&areaid=2799&callback=jsonp%s&_=%s"


def rt_test(items):
    pdb.set_trace()


def rt_parser(items): 
    pids = get_pids(items)
    if not pids:
        log_with_time("got nothing: %s" % entries)
        return
    purl = price_url % (",".join(["J_" + i for i in pids]), 
            random.randint(1000000, 10000000), int(time.time() * 1000)) 
    surl = stock_url % (async_http.quote(",".join([i for i in pids])), 
            random.randint(1000000, 10000000), int(time.time() * 1000)) 

    price_res = simple_http.get(purl) 
    stock_res = simple_http.get(surl)
    if price_res["status"] != 200 or stock_res["status"] != 200:
        log_with_time("not200: %s" % price["res"])
        return
    try:
        price_json = jsonp_json(price_res["text"]) 
        stock_json = jsonp_json(stock_res["text"].decode("gbk"))
    except: 
        traceback.print_exc()
        return
    prices = {} 
    for i in price_json: 
        prices[i["id"].split("_")[1]] = i["p"]
    stocks = {} 
    for k,v in stock_json.items(): 
        s = v["StockStateName"]
        if u"有货" in s or u"现货" in s:
            stocks[k] = 1
        else:
            stocks[k] = 0 
    ret = []
    for pid in prices:
        ret.append((str(pid), str(prices[pid]), stocks[pid])) 
    return format_price(ret)
