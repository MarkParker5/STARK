import datetime, time
import requests
from bs4 import BeautifulSoup as BS
import math
from ArchieCore import Command, Response

@Command.new([
    'который * час в $text',
    'скольк* * (врем|час)* * в $text',
    'время в $text',
    'который * час',
    'скольк* * (врем|час)*'])
def ctime(params):
    if city := params.get('text'):
        city     = city.title()
        responce = requests.get(f'https://www.google.ru/search?&q=время+в+{city}&lr=lang_ru&lang=ru')
        page     = BS(responce.content, 'html.parser')
        now      = page.select('div.BNeawe>div>div.BNeawe')[0].get_text().split(':') or ''
        now      = datetime.time(int(now[0]), int(now[1]))
    else:
        now      = datetime.datetime.now()

    hours   = now.hour%12 or 12
    minutes = now.minute
    get_str = ['десять', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']

    if hours%20 == 1:
        str_hour = 'час'
    elif 5 > hours%20 > 1:
        str_hour =  'часа'
    else:
        str_hour = 'часов'

    if minutes%10 == 1 and 20<minutes or minutes == 1:
        str_minute = 'минута'
    elif 0 < minutes%10 < 5 and math.floor(minutes/10) != 1:
        str_minute = 'минуты'
    else:
        str_minute = 'минут'

    def get_str_num(num, bool):
        result = []
        for i in [100, 10, 1]:
            j = num//i%10
            str_num = get_str[j]

            if i == 1 and bool:
                if j==1:
                    str_num = 'одна'
                elif j==2:
                    str_num = 'две'

            if str_num=='десять':
                continue
            elif i==10 and j == 1:
                j = int(num%10)
                str_num = get_str[j]
                if j==0:
                    str_num = ''
                elif j==2:
                    str_num = 'две'
                elif j==4:
                    str_num = 'четыр'
                elif j==5:
                    str_num = 'пят'
                str_num += 'надцать'
                if j==0:
                    str_num = 'десять'
                result.append(str_num)
                break

            elif i==10:
                if j==4:
                    str_num = 'сорок'
                elif j<5:
                    str_num += 'дцать'
                elif j==9:
                    str_num = 'девяноста'
                else:
                    str_num += 'десят'
            result.append(str_num)
        return ' '.join(result)

    if city: voice = f'В {city} сейчас {get_str_num(hours, 0)} {str_hour}'
    else:    voice = f'Сейчас {get_str_num(hours, 0)} {str_hour}'
    if(minutes): voice += f', {get_str_num(minutes, 1)} {str_minute}'

    hours   = now.hour if now.hour > 9 else '0'+str(now.hour)
    minutes = minutes  if minutes  > 9 else '0'+str(minutes) if minutes else '00'

    if city: text = f'Текущее время в {city}: {hours}:{minutes}'
    else:    text = f'Текущее время: {hours}:{minutes}'

    return Response(text = text, voice = voice)
