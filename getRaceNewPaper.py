import time
import requests,bs4
from rich import print,logging,pretty,inspect
from rich.console import Console
import re
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By

console = Console()

#chomedriverのパスを指定
executable_path="./chromedriver.exe"

def getRaceHorseInfo(race_id:str) -> str:
    #中央レース情報を取得する
    url = f"https://race.netkeiba.com/race/newspaper.html?race_id={race_id}&rf=shutuba_submenu"
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=executable_path, options=options)
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    HorseList = soup.find_all(class_ = "HorseList")
    for horse in HorseList:
        horse_waku = horse.attrs["data-index"]
        horse_umaban = horse.find(class_ = "Waku Waku_Horse orderfix").text
        console.log(horse_waku,horse_umaban)
    
    
    return None

getRaceHorseInfo("202205030211")