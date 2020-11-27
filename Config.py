"""
Author: zgq-drawbirder
Project: AutoSendQQMsg
Data: 2020/11/24
File: Config
info: 
    --: 配置文件
"""
# QQpush 的接口使用Token
Token = "*********************"

# 发送qq的接口
SendUrl = "http://api.qqpusher.yanxianjun.com/send_private_msg?token={}&user_id={}&message={}"

# 获取天气的接口
WeatherUrl1 = ["https://www.weaoo.com/", "https://www.weaoo.com/hefei-181409.html"]
WeatherUrl2 = "http://t.weather.itboy.net/api/weather/city/{}"
WeatherUrl3 = "http://tianqi.2345.com/tomorrow-58321.htm"

# WeatherUrl2 的天气查询接口的城市代码
WeatherCityCode = {
    "hefei": 101220101,
    "suzhou": 101220701
}

# 指定查询天气的地点
DEFAULT_CITY = "hefei"

# 指定发送的人
AllToWhos = [
    {
        "name": "***",
        "qq": "**********"
    },
    {
        "name": "**",
        "qq": "*********"
    }
]

