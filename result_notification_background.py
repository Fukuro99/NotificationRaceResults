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
import time 
import websocket

import format_result_race
import format_result_nar_race

console = Console()
pretty.install()
#chomedriverのパスを指定
executable_path="./chromedriver.exe"
#レース結果通知先のwebsocketサーバーのアドレスを指定
ws_result_endpoint = "ws://localhost:8000/ws/result"

def on_message(wsapp, message):
    print(message)

def main():
    result_raceID_list = []
    done_raceID_list = []
    result_raceID_dict = {}
    options = Options()
    options.add_argument('--headless')
    try:
        driver = webdriver.Chrome(executable_path=executable_path, options=options)
        while True:
            #data = await ws.receive_text()
            driver.get('https://race.netkeiba.com/top/')
            html = driver.page_source
            soup = bs4.BeautifulSoup(html, 'html.parser')
            result_state = soup.select_one('.Race_State').text
            print(result_state)
            for data in soup.find_all(class_ = "ResultFlash01"):
                try:
                    is_nar = False
                    #pan class="Race_State"の値が"確定"の場合のみ処理を行う
                    if not  "確定" in data.text:
                        continue
                    #aタグの中にあるhref属性を取得
                    href = data.find('a').get('href')
                    #地方競馬の場合は別のリンクを開く
                    if "nar" in href:
                        is_nar = True
                    #hrefのrace_idを取得
                    race_id = href.split("race_id=")[-1]
                    result_raceID_list.append(race_id)
                    result_raceID_dict[race_id] = is_nar
                except:
                    pass
            #result_raceID_listの重複を取り除く
            result_raceID_list = list(set(result_raceID_list))
            console.log(result_raceID_list)
            for race_id in result_raceID_list:
                #通知済みrace_idか判断し、通知済みの場合何もしない
                if race_id in done_raceID_list:
                    continue
                try:
                    if result_raceID_dict[race_id]:
                        result_url = f"https://nar.netkeiba.com/race/result.html?race_id={race_id}&rf=race_submenu"
                    else:
                        result_url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}&rf=race_submenu"
                    driver.get(result_url)
                    html = driver.page_source
                    result_soup = bs4.BeautifulSoup(html, 'html.parser')
                    #レース結果が確定してから表示されるまで時間がかかるため、確定情報がない場合はスキップする
                    #Race_Infomation_Boxがある場合は表示されない
                    RaceInfoBox = result_soup.find_all(class_ = "Race_Infomation_Box")
                    if len(RaceInfoBox) != 0:
                        continue
                    result = result_soup.find_all(class_ = "ResultTableWrap")
                    console.log(result)
                    #結果から確定情報を整形してWSで送信する
                    if result_raceID_dict[race_id]:
                        result_url = f"https://nar.netkeiba.com/race/result.html?race_id={race_id}"
                        race_result = format_result_nar_race.format_result_race(result_url)
                    else:
                        result_url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}"
                        race_result = format_result_race.format_result_race(result_url)
                    console.log(result_url)
                    console.log(race_result)
                    
                    ws = websocket.WebSocket()
                    ws.connect(ws_result_endpoint)
                    ws.send(race_result)
                    ws.close()
                    result_raceID_list.remove(race_id)
                    done_raceID_list.append(race_id)
                    break

                except:
                    continue
            time.sleep(1)
    except Exception as e:
        driver = webdriver.Chrome(executable_path=executable_path, options=options)
        console.log("LOG_DEBUG", '{}:{}'.format(type(e),e))
        time.sleep(1)

if __name__ == "__main__":
    main()