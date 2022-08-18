from ast import While
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import requests,bs4
from rich import print,logging,pretty,inspect
from rich.console import Console
import logging
from rich.logging import RichHandler
from fastapi import FastAPI, Body
from starlette.websockets import WebSocket
import format_result_race
import format_result_nar_race
import getRaceInfo
console = Console()
pretty.install()
"""
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("rich")
"""

app = FastAPI()

# websocketで接続中のクライアントを識別するためのIDを格納
clients = {}



@app.get("/")
def read():
    return {"Result": "ok"}

@app.get("/nar_result_info/{race_id}")
def result_info(race_id:str):
    url = f"https://nar.netkeiba.com/race/result.html?race_id={race_id}"
    return format_result_nar_race.get_race_result(url)

@app.get("/result_info/{race_id}")
def result_info(race_id:str):
    url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}"
    return format_result_race.get_race_result(url)

@app.get("/race_list/{date}")
def result_info(date:str):
    try:
        date = f"{date[:4]}/{date[4:6]}/{date[6:]}"
        race_list = getRaceInfo.getRaceInfo(date)
    except:
        return "error"
    return race_list

@app.get("/nar_race_list/{date}")
def result_info(date:str):
    try:
        date = f"{date[:4]}/{date[4:6]}/{date[6:]}"
        race_list = getRaceInfo.getRaceInfoNar(date)
    except:
        return "error"
    return race_list

@app.websocket("/ws/result")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    
    try:
        text = await ws.receive_text()
        console.log(text)
        for client in clients.values():
            await client.send_text(text)
    except Exception as e:
        console.log("LOG_DEBUG", '{}:{}'.format(type(e),e))
        ws.close()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    # クライアントを識別するためのIDを取得
    key = ws.headers.get('sec-websocket-key')
    clients[key] = ws
    
    try:
        while True:
            data = await ws.receive_text()
    except:
        #await ws.close()
        # 接続が切れた場合、当該クライアントを削除する
        del clients[key]

'''
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path="C:/Users/takeyoshi_murakami/chromedriver.exe", options=options)

result_raceID_list = []
done_raceID_list = []
while True:
    try:
        driver.get('https://www.netkeiba.com/')
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
    except:
        print("ERROR: driver.get()")
        driver = webdriver.Chrome(executable_path="C:/Users/takeyoshi_murakami/chromedriver.exe", options=options)
        sleep(10)
        continue
    for data in soup.find_all(class_ = "ResultFlash01 flash_item"):
        try:
            #aタグの中にあるhref属性を取得
            href = data.find('a').get('href')
            #地方競馬の場合は処理を中断する
            """
            if "nar" in href:
                continue
            """
            #hrefのrace_idを取得
            race_id = href.split("race_id=")[-1]
            result_raceID_list.append(race_id)
        except:
            pass
    #result_raceID_listの重複を取り除く
    result_raceID_list = list(set(result_raceID_list))
    for race_id in result_raceID_list:
        #通知済みrace_idか判断し、通知済みの場合何もしない
        if race_id in done_raceID_list:
            result_raceID_list.remove(race_id)
            continue
        try:
            result_url = f"https://nar.netkeiba.com/race/result.html?race_id={race_id}&rf=race_submenu"
            driver.get(result_url)
            html = driver.page_source
            result_soup = bs4.BeautifulSoup(html, 'html.parser')
            #レース結果が確定してから表示されるまで時間がかかるため、確定情報がない場合はスキップする
            #Race_Infomation_Boxがある場合は表示されない
            RaceInfoBox = result_soup.find_all(class_ = "Race_Infomation_Box")
            if len(RaceInfoBox) != 0:
                continue
            result = RaceInfoBox = result_soup.find_all(class_ = "ResultTableWrap")
            console.log(result)
            result_raceID_list.remove(race_id)
            done_raceID_list.append(race_id)
        except:
            continue
    print(result_raceID_list)
    sleep(60)
'''