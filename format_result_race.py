import requests,bs4
from rich import print,logging,pretty,inspect
from rich.console import Console

console = Console()
pretty.install()

def race_info(url:str)->list[str]:
    html = requests.get(url)
    soup = bs4.BeautifulSoup(html.content, 'html.parser')
    race_num = soup.find_all(class_ = "RaceNum")[0].text.replace("\n","")
    race_name = soup.find_all(class_ = "RaceName")[0].text.replace("\n","")
    race_place = soup.find_all(class_ = "RaceKaisaiWrap")[0].find_all(class_ = "Active")[0].text.replace("\n","")
    race_starttime = soup.find_all(class_ = "RaceData01")[0].text.replace("\n","").split("発走")[0]
    race_length = soup.find_all(class_ = "RaceData01")[0].text.replace("\n","").split("/")[1]
    race_weater = soup.find_all(class_ = "RaceData01")[0].text.replace("\n","").split("天候:")[1].split("/")[0]
    race_baba = soup.find_all(class_ = "RaceData01")[0].text.replace("\n","").split("馬場:")[1].split("/")[0]
    return [race_place,race_num,race_name,race_starttime,race_length,race_weater,race_baba]

def format_result_race(url:str)->str:
    html = requests.get(url)
    soup = bs4.BeautifulSoup(html.content, 'html.parser')
    result = soup.find_all(class_ = "FullWrap")
    #レース情報の取得
    info = race_info(url)
    #単勝の結果取得
    tansho = result[0].find_all(class_ = "Tansho")[0]
    tansho_result = tansho.find_all(class_ = "Result")[0].text.split("\n")
    tansho_result = [i for i in tansho_result if i != ""]
    tansho_payout = tansho.find_all(class_ = "Payout")[0].text.split("円")
    tansho_payout = [i.replace(",","") for i in tansho_payout if i != ""]
    #複勝の結果取得
    fukusho = result[0].find_all(class_ = "Fukusho")[0]
    fukusho_result = fukusho.find_all(class_ = "Result")[0].text.split("\n")
    fukusho_result = [i for i in fukusho_result if i != ""]
    fukusho_payout = fukusho.find_all(class_ = "Payout")[0].text.split("円")
    fukusho_payout = [i.replace(",","") for i in fukusho_payout if i != ""]
    #枠連の結果取得
    wakuren = result[0].find_all(class_ = "Wakuren")
    if len(wakuren) == 0:
        wakuren_result = [","]
        wakuren_payout = [","]
    else:
        wakuren_result = wakuren[0].find_all(class_ = "Result")[0].text.split("\n")
        wakuren_result = [i for i in wakuren_result if i != ""]
        wakuren_payout = wakuren[0].find_all(class_ = "Payout")[0].text.split("円")
        wakuren_payout = [i.replace(",","") for i in wakuren_payout if i != ""]
    #馬連の結果取得
    umaren = result[0].find_all(class_ = "Umaren")[0]
    umaren_result = umaren.find_all(class_ = "Result")[0].text.split("\n")
    umaren_result = [i for i in umaren_result if i != ""]
    umaren_payout = umaren.find_all(class_ = "Payout")[0].text.split("円")
    umaren_payout = [i.replace(",","") for i in umaren_payout if i != ""]
    #ワイドの結果取得
    wide = result[0].find_all(class_ = "Wide")[0]
    wide_result = wide.find_all(class_ = "Result")[0].text.split("\n")
    wide_result = [i for i in wide_result if i != ""]
    wide_payout = wide.find_all(class_ = "Payout")[0].text.split("円")
    wide_payout = [i.replace(",","") for i in wide_payout if i != ""]
    #馬単の結果取得
    umatan = result[0].find_all(class_ = "Umatan")[0]
    umatan_result = umatan.find_all(class_ = "Result")[0].text.split("\n")
    umatan_result = [i for i in umatan_result if i != ""]
    umatan_payout = umatan.find_all(class_ = "Payout")[0].text.split("円")
    umatan_payout = [i.replace(",","") for i in umatan_payout if i != ""]
    #三連複の結果取得
    sanrenfuku = result[0].find_all(class_ = "Fuku3")[0]
    sanrenfuku_result = sanrenfuku.find_all(class_ = "Result")[0].text.split("\n")
    sanrenfuku_result = [i for i in sanrenfuku_result if i != ""]
    sanrenfuku_payout = sanrenfuku.find_all(class_ = "Payout")[0].text.split("円")
    sanrenfuku_payout = [i.replace(",","") for i in sanrenfuku_payout if i != ""]
    #三連単の結果取得
    sanrentan = result[0].find_all(class_ = "Tan3")[0]
    sanrentan_result = sanrentan.find_all(class_ = "Result")[0].text.split("\n")
    sanrentan_result = [i for i in sanrentan_result if i != ""]
    sanrentan_payout = sanrentan.find_all(class_ = "Payout")[0].text.split("円")
    sanrentan_payout = [i.replace(",","") for i in sanrentan_payout if i != ""]
    format_payout_text = f"払い戻し:単勝:{tansho_result},{tansho_payout},複勝:{fukusho_result},{fukusho_payout},枠連:{wakuren_result},{wakuren_payout},馬連:{umaren_result},{umaren_payout},ワイド:{wide_result},{wide_payout},馬単:{umatan_result},{umatan_payout},三連複:{sanrenfuku_result},{sanrenfuku_payout},三連単:{sanrentan_result},{sanrentan_payout}"
    format_payout_text = format_payout_text.replace("'", "")
    format_info_text = f"レース場:{info[0]},レース:{info[1]},レース名:{info[2]},出走:{info[3]},距離:{info[4]},天気:{info[5]},馬場:{info[6]}"
    format_text = f"{format_info_text},{format_payout_text}"
    #console.log(format_text)
    return format_text

def get_race_result(url):
    try:
        return format_result_race(url)
    except Exception as e:
        console.log("LOG_DEBUG", '{}:{}'.format(type(e),e))
        return "error"

if __name__ == "__main__":
    format_result_race("https://race.netkeiba.com/race/result.html?race_id=202204020311")