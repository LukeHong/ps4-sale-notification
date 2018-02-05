import re
import json
import datetime

from selenium import webdriver
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

def notification(title, link):
    with open('data/notify_list.json', 'r') as file:
        notify_list = json.load(file)
    if len(notify_list) == 0:
        return False
    
    content = "{}\n{}".format(title, link)
    line_bot_api.multicast(notify_list, TextSendMessage(text=content))
    return True

line_bot_api = LineBotApi('ACCESS TOKEN')

driver = webdriver.PhantomJS()
driver.get('https://www.ptt.cc/bbs/Gamesale/index.html')
#driver.get('https://www.ptt.cc/bbs/Gamesale/index3599.html')
soup = BeautifulSoup(driver.page_source, "html.parser")

re_gs_title = re.compile(r'\[PS4\s*\]\s*售.*pro.*', re.I)
re_gs_id = re.compile(r'.*\/Gamesale\/M\.(\S+)\.html')

match = []
for article in soup.select('.r-list-container .r-ent .title a'):
    title = article.string
    if re_gs_title.match(title) != None:
        link = 'https://www.ptt.cc' + article.get('href')
        article_id = re_gs_id.match(link).group(1)
        match.append({'title':title, 'link':link, 'id':article_id})

if len(match) > 0:
    with open('data/history/gamesale.json', 'r+') as file:
        history = json.load(file)

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')       
        new_flag = False
        for article in match:
            if article['id'] in history:
                continue
            new_flag = True
            history.append(article['id'])
            notification(article['title'], article['link'])
            print("{}: New Article: {} {}".format(now, article['title'], article['link']))

        if new_flag == True:
            file.seek(0)
            file.truncate()
            file.write(json.dumps(history))
        else:
            print("{}: Nothing".format(now))
