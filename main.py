import re
import json
import time
import requests
# from urllib.parse import quote, unquote
from PIL import Image
from io import BytesIO

from selenium import webdriver
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import os
import sys

USE_DRIVER = "Edge"

WEBDRIVER_EXECUTABLE_NAME = {
    "Chrome": "chromedriver.exe",
    "Edge": "msedgedriver.exe",
    "Firefox": "geckodriver.exe"
}


if USE_DRIVER == "Chrome":
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
elif USE_DRIVER == "Edge":
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.edge.service import Service
elif USE_DRIVER == "Firefox":
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
else:
    print("Not Supported !")
    exit(-1)


LOL_AREAS_ID = {
    1: "电信 艾欧尼亚",
    2: "网通 比尔吉沃特",
    3: "电信 祖安",
    4: "电信 诺克萨斯",
    6: "网通 德玛西亚",
    5: "电信 班德尔城",
    7: "电信 皮尔特沃夫",
    8: "电信 战争学院",
    9: "网通 弗雷尔卓德",
    10: "电信 巨神峰",
    11: "电信 雷瑟守备",
    12: "网通 无畏先锋",
    13: "电信 裁决之地",
    14: "电信 黑色玫瑰",
    15: "电信 暗影岛",
    17: "电信 钢铁烈阳",
    16: "网通 恕瑞玛",
    18: "电信 水晶之痕",
    21: "教育网专区",
    22: "电信 影流",
    23: "电信 守望之海",
    20: "网通 扭曲丛林",
    24: "电信 征服之海",
    25: "电信 卡拉曼达",
    27: "电信 皮城警备",
    26: "网通 巨龙之巢",
    30: "全网 男爵领域",
    19: "电信 均衡教派"
}

SUMMONER_NAME_PATTERN = re.compile('(?<=(summonerName=)).*?(?=&)')


def get_driver_path():
    if os.path.isfile(os.path.join(os.path.dirname(sys.argv[0]), WEBDRIVER_EXECUTABLE_NAME[USE_DRIVER])):
        return os.path.join(os.path.dirname(sys.argv[0]), WEBDRIVER_EXECUTABLE_NAME[USE_DRIVER])
    # 若使用pyInstaller打包
    try:
        if os.path.isfile(os.path.join(sys._MEIPASS, WEBDRIVER_EXECUTABLE_NAME[USE_DRIVER])):
            return os.path.join(sys._MEIPASS, WEBDRIVER_EXECUTABLE_NAME[USE_DRIVER])
    except AttributeError:
        return None
    return None


class LoginQQDaoju:
    login_url = "https://daoju.qq.com/lol/"

    def __init__(self):
        # 定义设置
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        options.add_argument('--disable-gpu')
        options.add_argument('--incognito')
        # 定义浏览器
        driver_path = get_driver_path()
        if driver_path is None:
            service = Service()
        else:
            service = Service(driver_path)
        self.browser = webdriver.Edge(service=service, options=options)
        # 定义显示等待
        self.wait = WebDriverWait(self.browser, 60)

    def open(self):
        self.browser.get(self.login_url)
        self.browser.set_window_size(1000, 1000)
        # 点击登录
        self.wait.until(
            ec.presence_of_element_located((By.ID, "btn_topbar_unlogin_login"))
        ).click()

    def get_qrcode(self):
        self.browser.switch_to.frame("loginIframe")
        get_screenshot_as_png = self.wait.until(
            ec.presence_of_element_located((By.ID, "qrlogin_img"))
        ).screenshot_as_png
        stream = BytesIO(get_screenshot_as_png)
        i = Image.open(stream)
        print("Image loaded.")
        print("请尽快扫码登录.")
        i.show()

    def get_cookies(self):
        self.wait.until(
            ec.visibility_of_element_located((By.ID, "blk_index_main_logined"))
        )
        return self.browser.get_cookies()

    def close(self):
        self.browser.quit()


if __name__ == '__main__':
    instance = LoginQQDaoju()
    instance.open()
    instance.get_qrcode()
    cookies = instance.get_cookies()
    instance.close()
    s = requests.session()
    s.headers = {
        # "referer": "https://daoju.qq.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
        "origin": "https://lol.qq.com",
        "referer": "https://lol.qq.com/",
        "accept-encoding": "gzip",
    }
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])

    for area_id in LOL_AREAS_ID:
        url = "https://apps.game.qq.com/daoju/igw/main?_service=buy.plug.svr.sysc_ext&paytype=8&iActionId=22565" \
              "&propid=338943&buyNum=1&_app_id=1006&_plug_id=72007&_biz_code=lol&areaid={0}&roleid={1}&source=4_0" \
              "&reportUserUin={1}"\
            .format(area_id, s.cookies.get("uin")[2:])
        res = s.get(url)
        res_text = res.text
        json_obj = json.loads(res.text)

        try:
            msg = json.loads(json_obj['msg'])[0]["sMsg"]
        except Exception:
            msg = json_obj['msg']
        print("{0}  {1}".format(LOL_AREAS_ID[area_id], msg))
        time.sleep(1.5)
    print("执行完成。")
    input()
    raise Exception()
