"""
    author：lenjin
    version:1.0.0
    common：DrawMe by python
    date:2019/06/18-2019/06/19

"""

from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import time
import pymongo
import matplotlib.pyplot as plt
import  matplotlib
import sys

myfont = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simfang.ttf')
myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['lotteryMatches']
mycol = mydb["ratio24"]

lotteryMatches = []
lotterysize = 0
lotteryindex = lotterysize

url = 'http://www.okooo.com'
handerr = ''


def repAstr(instr):
    return instr.replace('↑',' ').replace('↓',' ').strip()

def save_to_mongo(data):
    """
    save to MongoDB
    keep one day data
    """
    mycol.delete_many({})
    try:
        if mycol.insert_many(data):
            print('save to MongoDB success')
    except Exception as e:
        print('fail to save to MongoDB '+e)


def load24Data():
    # browser = webdriver.Chrome()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    try:
        browser.get(url + '/jingcai/')
        # print(browser.window_handles)
        doc = pq(browser.page_source)
        # 返回一个生成器, 使用for循环就可以打印出来。循环的每一个节点还是PyQuery类型可以继续CSS选择器选择
        items = doc('#content > div:nth-child(6) > div.touzhu .touzhu_1').items()
        for item in items:
            lotterymatch = {
                'matchid': item.attr('id'),
                'data_ordercn': item.attr('data-ordercn'),
                'zhutitle': item.find('.zhu .zhum.fff.hui_colo').attr('title'),
                'futitle': item.find('.fu  .zhum.fff.hui_colo').attr('title'),
                'matchhref': url + item.find('div.fengxin1.textnowrap > a:nth-child(1)').attr('href')
            }
            # print(lotterymatch)
            browser.get(lotterymatch['matchhref'])
            wait2 = WebDriverWait(browser, 10)
            link24 = wait2.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[id=tr24]  a>span')))
            link24.click()

            browser.switch_to.window(browser.window_handles[-1])
            time.sleep(5)
            doc24 = pq(browser.page_source)
            items24 = doc24('body > div.wrap > table > tbody  .sjbg01').items()
            ratio24time = []
            ratio24zhu = []
            ratio24fu = []
            ratio24ping = []
            for item in items24:
                handerr = item.find('td:nth-child(3)').text()
                date24 = item.find('td:nth-child(1)').text().replace('(初)', '')
                ratio24time.append(datetime.datetime.strptime(date24, '%Y/%m/%d %H:%M'))
                ratio24zhu.append(
                    float(repAstr(item.find('td:nth-child(3)').text())))
                ratio24ping.append(
                    float(repAstr(item.find('td:nth-child(4)').text())))
                ratio24fu.append(float(repAstr(item.find('td:nth-child(5)').text())))
            lotterymatch['ratio24time'] = ratio24time.copy()
            lotterymatch['ratio24time'].reverse()
            lotterymatch['ratio24zhu'] = ratio24zhu.copy()
            lotterymatch['ratio24zhu'].reverse()
            lotterymatch['ratio24ping'] = ratio24ping.copy()
            lotterymatch['ratio24ping'].reverse()
            lotterymatch['ratio24fu'] = ratio24fu.copy()
            lotterymatch['ratio24fu'].reverse()
            # print(lotterymatch['matchid']+' '+lotterymatch['zhutitle']+' VS '+lotterymatch['futitle'])
            lotteryMatches.append(lotterymatch)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
          
    except ValueError as e:
        # the error can not find so just add to find the question
        print(e + ' ' + handerr)
    finally:
        browser.quit()
        # pass

def onclick(event):
    global lotteryindex
    #ugly to fit 3 == forward 2 == backward
    #toolbar so hard to find the way get the event ???
    if event.button != 3 and event.button != 2:
        return False
    if event.button == 3:
        lotteryindex = lotteryindex+1
        if lotteryindex == lotterysize :
            lotteryindex = 0
    if event.button == 2:
        lotteryindex = lotteryindex -1
        if lotteryindex < 0:
            lotteryindex = lotterysize -1
    event.canvas.figure.clear()
    # event.canvas.figure.gca().plot()
    drawOneLottery(lotteryindex)
    #use canvas draw to update the picture
    event.canvas.draw()
    #return value really need???
    return True

def drawOneLottery(index):
    if 0 <= index and index < lotterysize :
        plt.ylabel('百分比',fontproperties=myfont )
        plt.title(lotteryMatches[index]['zhutitle'] + ' VS ' + lotteryMatches[index]['futitle'], fontproperties=myfont)
        data24 = lotteryMatches[index]['ratio24time']
        temp = lotteryMatches[index]['ratio24zhu'][0]
        data24zhu = [(x - temp) / temp * 100 for x in lotteryMatches[index]['ratio24zhu']]
        temp = lotteryMatches[index]['ratio24ping'][0]
        data24ping = [(x - temp) / temp * 100 for x in lotteryMatches[index]['ratio24ping']]
        temp = lotteryMatches[index]['ratio24fu'][0]
        data24fu = [(x - temp) / temp * 100 for x in lotteryMatches[index]['ratio24fu']]
        plt.plot(data24, data24zhu, 'blue', label=lotteryMatches[index]['zhutitle'])
        plt.plot(data24, data24ping, 'black', label='Ping')
        plt.plot(data24, data24fu, 'orange', label=lotteryMatches[index]['futitle'])
        plt.legend(loc='upper left', prop=myfont, framealpha=0.5)
        plt.grid(True, axis='y', linestyle='dashdot', linewidth=0.3)


if __name__ == '__main__':
    if len(sys.argv) > 1 :
        load24Data()
        save_to_mongo(lotteryMatches)
    else:
        for item in mycol.find():
            lotteryMatches.append(item)
    lotterysize = len(lotteryMatches)
    fig = plt.figure('football match',figsize=(11,4))
    fig.canvas.mpl_connect('button_press_event', onclick)
    drawOneLottery(0)
    #plt.show() create canvas and cause too many memory cause
    # error "maximum recursion depth exceeded in comparison"
    plt.show()


