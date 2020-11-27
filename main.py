"""
Author: zgq-drawbirder
Project: AutoSendQQMsg
Data: 2020/11/24
File: main
info:
    --：自动发送天气和温馨提示语句到指定qq号
"""
import requests
import Config
import re
import time
from threading import Timer


# 打开日志文件
logfile = open("./log.log", "a", encoding="utf8")

# 获取配置文件的所有发送者信息
AllToWhos = Config.AllToWhos


def tolog(printmsg):
    """
    日志实时输出
    :param printmsg: 输出的信息
    :return:
    """
    print(printmsg)
    logfile.writelines(printmsg + "\n")
    logfile.flush()


def SendQQMsg(qq, msg, status=0):
    """
    发送指定消息到指定qq 上
    :param status: 标记是否为第一次调用 以方便二次回调
    :param qq: QQ号
    :param msg: 发送的消息
    :return: 返回是否发送成功 0 1
    """
    try:
        response = requests.get(Config.SendUrl.format(Config.Token, qq, msg))
        result = response.json()
        if status == 0 and result["code"] != 200:
            SendQQMsg(qq, msg, status=1)
    except Exception as e:
        tolog(str(e))


def getWeatherNight2(ToWhos):
    """
    晚上获取明天的天气信息 接口3
        需要转换成msg的格式
    :param ToWhos: 发送人
    """
    response = requests.get(Config.WeatherUrl3, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 "
    })
    results = re.compile("<ul>(.*?)</ul>", re.S).findall(response.text)[0]
    results = re.compile("<li .*?>(.*?)</li>", re.S).findall(results)
    weatherInfo = {}
    for result in results:
        if "明天天气" in result:
            weatherInfo["type"] = re.compile("<i>(.{1,3})</i>").findall(result)[0]
            weatherInfo["high"] = re.compile('<span class="tem-show">(\w{1,2})~(\w{1,2})°</span>').findall(result)[0]
            weatherInfo["fx"] = re.compile('<span class="wind-name">(.*?)</span>').findall(result)[0]
    for who in ToWhos:
        Msg = """
        ---明天天气---
        天气：{}
        最高温度：{}
        最低温度：{}
        风力：{}

        {}
        """.format(weatherInfo["type"],
                   weatherInfo["high"][0],
                   weatherInfo["high"][1],
                   weatherInfo["fx"],
                   "{}，记着明天带伞哦！".format(who["name"]) if "雨" in weatherInfo["type"] else "")
        SendQQMsg(who["qq"], Msg)


def getWeatherNight(ToWhos, city=Config.DEFAULT_CITY):
    """
    晚上获取明天的天气信息 接口2
        需要转换成msg的格式
    :param ToWhos: 发送人
    :param city: 接口的城市拼音
    """
    response = requests.get(Config.WeatherUrl2.format(Config.WeatherCityCode[city]))
    weatherInfo = response.json()["data"]["forecast"][1]
    for who in ToWhos:
        Msg = """
        ---明天天气---
        天气：{}
        最高温度：{}
        最低温度：{}
        风力：{}
        温馨提示：{}

        {}
    """.format(weatherInfo["type"],
               weatherInfo["high"],
               weatherInfo["low"],
               weatherInfo["fx"] + weatherInfo["fl"],
               weatherInfo["notice"], "{}，记着明天带伞哦！".format(who["name"]) if "雨" in weatherInfo["type"] else "")
        SendQQMsg(who["qq"], Msg)


def TheTimeWeather(ToWhos, city=Config.DEFAULT_CITY):
    """
        接口1
        指定特定的时间发送
    :param ToWhos: 发送给谁个
    :param city: 接口的城市拼音
    :return: 当前时间后面五个小时的天气信息字符串
    """
    try:
        responsehtml = requests.get(Config.WeatherUrl1[0], headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 "
        })
        indexhtml = responsehtml.text
        atag = re.compile('<a href="//www.weaoo.com/{}.*?.html" title=".*?天气一周查询">.*?天气</a>'.format(city)).findall(indexhtml)[0]
        infourl = re.compile('<a href="(.*?)" title=".*?天气一周查询">.*?天气</a>').findall(atag)[0]
        inforeponse = requests.get("http:" + infourl, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 "
        })
        inforeponse.encoding = "utf-8"
        infohtml = inforeponse.text
        timeweathers = re.compile('<h2 class="lborder">合肥24小时天气预报</h2>(.*?)</ul>', re.S).findall(infohtml)[0].replace("\n", "")
        timewts = re.compile('<li><span>(..)点</span><span><i class="wi .*?"></i></span><span>(.{1,3})</span><span>(.*?)</span><span title="(.*?)" class="aqi-bg-1">(.*?)</span></li>').findall(timeweathers)
        fiveHoursWeatherMsg = []
        Tips = ""
        # 获取当前时间 小时
        nowHour = time.localtime(time.time()).tm_hour
        for hour in range(nowHour, nowHour + 5):
            if hour >= 24:
                hour = hour - 23
            for timewt in timewts:
                if int(timewt[0]) == hour:
                    fiveHoursWeatherMsg.append("{0[0]}点，{0[1]}，{0[2]}，{0[3]}".format(timewt[:-1]))
                    if Tips == "" and "雨" in timewt[1]:
                        Tips = "{}点有雨，记得带伞".format(timewt[0])
        for who in ToWhos:
            Msg = """
        ---接下来五个小时天气---
        {0[0]}
        {0[1]}
        {0[2]}
        {0[3]}
        {0[4]}

        {1},{2}
            """.format(fiveHoursWeatherMsg, who["name"], Tips)
            SendQQMsg(who["qq"], Msg)
    except Exception as e:
        tolog(str(e))
        SendQQMsg("358694798", str(e))


def sendStart():
    msg = """
    ---天气消息推送订阅成功---
    说明：
        每天7，13，15点，定时推送五小时的天气
        晚上10定时推送明天的天气
    {}，记得定时查看哦！
    """
    for who in AllToWhos:
        SendQQMsg(who["qq"], msg.format(who["name"]))


def sendTheTime():
    """
    发送指定时间的消息推送
        可以执行一次错误回调
    :return:
    """
    try:
        TheTimeWeather(AllToWhos)
    except Exception as e:
        tolog(str(e))
        TheTimeWeather(AllToWhos)


def sendNight():
    """
    发送晚上的消息推送
        第一个接口如果调用次数到达上限（失败），启用第二个接口获取信息
    :return:
    """
    try:
        getWeatherNight(AllToWhos)
    except Exception as e:
        tolog(str(e))
        getWeatherNight2(AllToWhos)


def createTheTimeProcess(date):
    """
    创建一个线程指定时间发生消息（特定时间发送）
    :param date: 指定的时间  小时
    :return:
    """
    now = time.localtime(time.time())
    # 获取时间差
    StepTime = int(time.mktime(time.strptime('{}-{}-{} {}:00:00'.format(now.tm_year, now.tm_mon, now.tm_mday, date),
                                             '%Y-%m-%d %H:%M:%S'))) - int(time.time())
    process = Timer(StepTime, sendTheTime)
    process.start()
    tolog("[{}]：设置了一个{}({})秒后的日程。".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), StepTime, date))


def createNightTimeProcess(date=22):
    """
    创建一个线程指定时间发生消息（晚上发送 默认22点）
    :param date: 指定的时间  小时
    :return:
    """
    now = time.localtime(time.time())
    # 获取时间差
    StepTime = int(time.mktime(time.strptime('{}-{}-{} {}:00:00'.format(now.tm_year, now.tm_mon, now.tm_mday, date),
                                             '%Y-%m-%d %H:%M:%S'))) - int(time.time())
    t4 = Timer(StepTime, sendNight)
    t4.start()
    tolog("[{}]：设置了一个{}({})秒后的日程。".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), StepTime, date))


def mains():
    # 消息启动通知
    sendStart()
    tolog("程序开始......")
    # 先根据当前程序的启动时间判断 然后启动接下来时间的消息推送
    now = time.localtime(time.time())
    nowH = now.tm_hour
    if 1 < nowH < 22:
        tolog("即将设置今天接下来的定时任务。")
        if nowH < 7:
            createTheTimeProcess(7)
            createTheTimeProcess(13)
            createTheTimeProcess(17)
            createNightTimeProcess()
        elif nowH < 13:
            createTheTimeProcess(13)
            createTheTimeProcess(17)
            createNightTimeProcess()
        elif nowH < 17:
            createTheTimeProcess(17)
            createNightTimeProcess()
        else:
            # createNightTimeProcess(18)
            createNightTimeProcess()
    while True:
        nowH = time.localtime(time.time()).tm_hour
        nowM = time.localtime(time.time()).tm_min
        # 判断时间是否为新一天的开始 如果是 开启今天的消息推送
        if nowH == 0 and nowM == 1:
            tolog("开始今天的定时任务！")
            createTheTimeProcess(7)
            createTheTimeProcess(13)
            createTheTimeProcess(17)
            createNightTimeProcess()
        # 每四十秒执行一次以防止每分钟只可以执行一次
        time.sleep(40)


if __name__ == '__main__':
    mains()
