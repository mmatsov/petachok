import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import websocket
from uuid import uuid4
import json
import time
from ai_responder import ai
import ast
headers = {

  "cookie": "NBGR=4801C546074842EA7D576A64DFC64BD673E1B8D27390A78E85439B744614F7D80E5F9EE4E6BA3725AD05F9841C1FED8399DED0940EE9EAE34353911B7B1AD67563A8F2D360A518C870AA103BD665361C2B7E32EF57FD109D46761D9EDA1B1C14",
  
}

cookie = 'NBGR=4801C546074842EA7D576A64DFC64BD673E1B8D27390A78E85439B744614F7D80E5F9EE4E6BA3725AD05F9841C1FED8399DED0940EE9EAE34353911B7B1AD67563A8F2D360A518C870AA103BD665361C2B7E32EF57FD109D46761D9EDA1B1C14'

def uplots(headers):     


    url = 'https://petachok.ru/home/mylots'

    html_content = requests.post(url, headers=headers).text

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')
    target_div = soup.select_one('body > div.main-content > div > div > div.mainBlock > div.flexRow_Column.gap-10.ai-start > div > div.hr')

    links = []
    all_tags = target_div.find_all('a', href=True)

    if target_div:
        for a in all_tags:
            link = a['href']      
            links.append(link[15:])
        print(links)


    for i in links:
        payload = {
        "id": i,
        "type": 'account'
        }
        print(requests.post('https://petachok.ru/uplot', headers=headers, data=payload).text)


def getTextSelectora(headers, val):

    url = 'https://petachok.ru/getmoney'
    html_content = requests.get(url, headers=headers).text
    

    soup = BeautifulSoup(html_content, 'html.parser')

    element = soup.select_one(val)

   
    if element:
        text_content = element.get_text(strip=True)
        print(text_content)
    else:
        print("Элемент не найден. Проверьте правильность селектора.")



def getmainbal(headers, mainbal):
    getTextSelectora(headers, mainbal)


def getmessageinfo(text, headers):
    soup = BeautifulSoup(text, 'html.parser')


    message_element = soup.find(string=lambda text: text and "Новое сообщение" in text)

    if message_element:
       
        parent_link = message_element.find_parent('a')
        
        if parent_link and parent_link.has_attr('href'):
            relative_href = parent_link['href']
            
            
            base_url = "https://petachok.ru"  
            full_url = urljoin(base_url, relative_href)
            
            time.sleep(1.5)
            html_content = requests.get(full_url, headers=headers)
            
            soup = BeautifulSoup(html_content.text, 'html.parser')

            # Находим ВСЕ элементы с классом .messmyclass внутри .chat-mesacy
            messages = soup.select("div.chat-mesacy div.messmyclass")

            if messages:
                # Берем самый последний (нижний) элемент из списка
                last_message = messages[-1]
                
                # Выводим его чистый текст
                mes = last_message.text.strip()
            
            
                return mes, full_url
                






def getInfoUser(headers, url):
    text = requests.get(url, headers=headers).text
    
    tousid_match = re.search(r"var tousid\s*=\s*'(\d+)';", text)
    tousname_match = re.search(r"var tousname\s*=\s*'(\w+)';", text)
    myid = re.search(r"var myid\s*=\s*'(\w+)';", text)
    myname_match = re.search(r"var myname\s*=\s*'(\w+)';", text)


   
    tousid = tousid_match.group(1) if tousid_match else None
    tousname = tousname_match.group(1) if myname_match else None
    myid = myid.group(1) if tousid_match else None
    myname = myname_match.group(1) if myname_match else None
  
    
    return tousname, tousid, myname, myid

def send_message(text, url):
    ws_url = "wss://petachok.ru:443/Services/ChatHandler.ashx"
   
    tousname, tousid, myname, myid = getInfoUser(headers, url)

    guid = str(uuid4())
    
    
    ws = websocket.create_connection(ws_url, header=headers, timeout=5)
    
   

    
    ws.send(f"{myname}{{#}}{guid}{{#}}openwebsoketforuser")
    
    ws.send(f"{myname}{{#}}{guid}{{#}}sendmessage{{%}}{myname}{{%}}{tousname}{{%}}{text}{{%}}{myid}{{%}}{tousid}{{%}}")
    
    ws.send(f"{myname}{{#}}{guid}{{#}}closwebsoketforuser")
    
    
    ws.close()



def fai(mes):
    mesai = str(ai(mes))
    text_tuple = ast.literal_eval(mesai)
    clean_text = " ".join(text_tuple).replace('\n', ' ').strip()
    while "  " in clean_text:
        clean_text = clean_text.replace("  ", " ")
    return clean_text


def AIPLUGIN(text):
    mes, full_url = getmessageinfo(text, headers)
                
    clean_text = fai(mes)
    send_message(clean_text, full_url)


mainbal = 'body > div.main-content > div > div > div:nth-child(3) > div > div:nth-child(1) > div > div.size-60_.bold'
hold = 'body > div.main-content > div > div > div:nth-child(3) > div > div:nth-child(2) > div > div.size-60_.bold'



def newmessage(headers):
    while True:
        text = requests.get('https://petachok.ru/home/message', headers=headers).text
        if 'Новое сообщение' in text:
            print('Новое сообщение!')
            AIPLUGIN(text)

# newmessage(headers)

def getLinkSelectora1(headers, url, selector):
    try:
        # Отправляем запрос
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.select_one(selector)
        
        if element:
            # Ищем тег <a> внутри найденного элемента
            link_tag = element.find('a')
            
            if link_tag:
                # Безопасно извлекаем атрибут href
                href = link_tag.get('href')
                
                if href:
                    
                    return href
                else:
                    print(f"⚠️ Тег <a> найден внутри '{selector}', но у него нет атрибута href.")
                    return None
            else:
                print(f"⚠️ Внутри селектора '{selector}' не найден тег <a>.")
                return None
        else:
            print(f"⚠️ Элемент по селектору '{selector}' не найден на странице.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе к сайту: {e}")
        return None



