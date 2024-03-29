"""
    @author: lenjin
    @date:2019/06/22
    @common: load foot match data from www.okooo.com
             save into mongdb
"""
import pymongo
import datetime
import time
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

WEEKCN =("周一","周二","周三","周四","周五","周六","周日")

def repstrstr(instr):
    return instr.rstrip('↑').rstrip('↓')


def save_to_mongo(data):
    """
    save to MongoDB
    keep one day data
    """
    if len(data) == 0 :
        print('save_to_mongo no data input')
        return
    try:
        if len(data) == 1:
            mycol.insert_one(data)
        else:
            mycol.insert_many(data)
        print('save to mongodb success')
    except Exception as e:
        print('fail to save to mongodb ' + e)

if __name__ == '__main__':

    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['lotteryMatches']
    mycol = mydb["ratio24"]
    mycol.delete_many({})

    url = 'http://www.okooo.com'
    lotterymatches = list()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    # browser.set_page_load_timeout(18960)
    try:
        browser.get(url + '/jingcai/')
        # print(browser.window_handles)
        # print(browser.title)
        doc = pq(browser.page_source)
        # 返回一个生成器, 使用for循环就可以打印出来。循环的每一个节点还是PyQuery类型可以继续CSS选择器选择
        selectstr = '.touzhu_1[data-ordercn^={}]'.format(WEEKCN[datetime.datetime.now().weekday()])
        items = doc(selectstr).items()
        for item in items:
            if item.attr('id') == 'match_0' or item.attr('data-end') =='1':
                continue
            lotterymatch = {
                'matchid': item.attr('id'),
                'data_ordercn': item.attr('data-ordercn'),
                'zhutitle': item.find('.zhu .zhum.fff.hui_colo').attr('title'),
                'futitle': item.find('.fu  .zhum.fff.hui_colo').attr('title')
            }
            matchhref = url + item.find('div.fengxin1.textnowrap > a:nth-child(1)').attr('href')
            if 'javascript' in matchhref:
                matchhref = matchhref.replace('javascript:warnMsg(\'', '').replace('\');', '').strip()
                lotterymatch['zhutitle'], lotterymatch['futitle'] = lotterymatch['futitle'],lotterymatch['zhutitle']
            lotterymatch['matchhref'] = matchhref
            browser.get(matchhref)
            print(browser.title)
            wait2 = WebDriverWait(browser, 300)
            link24 = wait2.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[id=tr24]  a>span')))
            link24.click()

            browser.switch_to.window(browser.window_handles[-1])
            print(browser.title)
            wait = WebDriverWait(browser, 600)
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'table')))
            
             #way to waste time to get the whole data
            doc24str = browser.page_source
            n = 1
            while n < 1988316 :
                time.sleep(1)
                doc24strnew = browser.page_source
                if  doc24strnew == doc24str :
                    break
                doc24str = doc24strnew
                n+=n
            
            doc24 = pq(browser.page_source)
            items24 = doc24(' table > tbody >tr').items()
            next(items24)
            next(items24)
            ratio24time,ratio24zhu,ratio24fu,ratio24ping = list(),list(),list(),list()
            for item in items24:
                date24 = item.find('td:nth-child(1)').text().replace('(初)', '')
                ratio24time.append(datetime.datetime.strptime(date24, '%Y/%m/%d %H:%M'))
                ratio24zhu.append(
                    float(repstrstr(item.find('td:nth-child(3)').text())))
                ratio24ping.append(
                    float(repstrstr(item.find('td:nth-child(4)').text())))
                ratio24fu.append(float(repstrstr(item.find('td:nth-child(5)').text())))
            lotterymatch['ratio24time'] = ratio24time[::-1]
            lotterymatch['ratio24zhu'] = ratio24zhu[::-1]
            lotterymatch['ratio24ping'] = ratio24ping[::-1]
            lotterymatch['ratio24fu'] = ratio24fu[::-1]
            lotterymatches.append(lotterymatch)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])

    except Exception as err:
        print("Error:"+str(err))
        print('Browser:'+browser.page_source)
    else:
        save_to_mongo(lotterymatches)
    finally:
        browser.quit()
        myclient.close()

