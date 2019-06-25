"""
    @author: lenjin
    @date:2019/06/22
    @common: load foot match data from www.okooo.com
             save into mongdb
"""
import pymongo
import datetime
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

def repstrstr(instr):
    return instr.replace('↑', ' ').replace('↓', ' ').strip()


def save_to_mongo(data):
    """
    save to MongoDB
    keep one day data
    """
    if len(data) == 0 :
        print('save_to_mongo no data input')
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
        items = doc('#content > div:nth-child(6) > div.touzhu .touzhu_1').items()
        for item in items:
            matchid = item.attr('id')
            if matchid == 'match_0':
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

            doc24 = pq(browser.page_source)
            items24 = doc24('body > div.wrap > table > tbody  .sjbg01').items()
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
        save_to_mongo(lotterymatches)
    except Exception as err:
        print("Error:"+str(err))
    finally:
        browser.quit()
        myclient.close()

