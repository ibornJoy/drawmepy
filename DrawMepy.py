"""
    @author:lenjin
    @date:2019/06/22
    @comment:draw the football match
"""
import matplotlib
import matplotlib.pyplot as plt
import pymongo

lotterymatches = []
lotterysize = 0
lotteryindex = lotterysize
myfont = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simfang.ttf')


def onclick(event):
    global lotteryindex
    # ugly to fit 3 == forward 2 == backward
    # toolbar so hard to find the way get the event ???
    if event.button != 3 and event.button != 2:
        return False
    if event.button == 3:
        lotteryindex = lotteryindex + 1
        if lotteryindex == lotterysize:
            lotteryindex = 0
    if event.button == 2:
        lotteryindex = lotteryindex - 1
        if lotteryindex < 0:
            lotteryindex = lotterysize - 1
    event.canvas.figure.clear()
    # event.canvas.figure.gca().plot()
    drawonelottery(lotteryindex)
    # use canvas draw to update the picture
    event.canvas.draw()
    # return value really need???
    return True


def drawonelottery(index):
    if 0 <= index and index < lotterysize:
        plt.ylabel('百分比', fontproperties=myfont)
        plt.title(lotterymatches[index]['zhutitle'] + ' VS ' + lotterymatches[index]['futitle'], fontproperties=myfont)
        data24 = lotterymatches[index]['ratio24time']
        temp = lotterymatches[index]['ratio24zhu'][0]
        data24zhu = [(x - temp) / temp * 100 for x in lotterymatches[index]['ratio24zhu']]
        temp = lotterymatches[index]['ratio24ping'][0]
        data24ping = [(x - temp) / temp * 100 for x in lotterymatches[index]['ratio24ping']]
        temp = lotterymatches[index]['ratio24fu'][0]
        data24fu = [(x - temp) / temp * 100 for x in lotterymatches[index]['ratio24fu']]
        plt.plot(data24, data24zhu, 'blue', label=lotterymatches[index]['zhutitle'])
        plt.plot(data24, data24ping, 'black', label='Ping')
        plt.plot(data24, data24fu, 'orange', label=lotterymatches[index]['futitle'])
        plt.legend(loc='upper left', prop=myfont, framealpha=0.5)
        #ugly to do it
        bottom,top = plt.ylim()
        maxtemp = max(abs(math.floor(bottom)),math.ceil(top))
        plt.ylim(-maxtemp,maxtemp)
        plt.grid(True, axis='y', linestyle='dashdot', linewidth=0.3)


if __name__ == '__main__':
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['lotteryMatches']
    mycol = mydb["ratio24"]
    for item in mycol.find():
        lotterymatches.append(item)
    lotterysize = len(lotterymatches)
    myclient.close()
    fig = plt.figure('Football Match', figsize=(12, 4))
    fig.canvas.mpl_connect('button_press_event', onclick)
    drawonelottery(0)
    # plt.show() create canvas and cause too many memory cause
    # error "maximum recursion depth exceeded in comparison"
    plt.show()
