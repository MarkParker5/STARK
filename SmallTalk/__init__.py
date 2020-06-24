#   Initialisation SmallTalk
#   Creating objects (add commands)
#   setStart(method) is required
#   setConfirm(method) is optional
#
#   How to add new command:
#   1.  def method()                 #  return string
#   1.2 def confirm_method()         #  optional, not required
#   2.  kw = {
#           (int)weight  : ['word1', 'word2', 'word3'],
#           (int)weight1 : ['word3', 'word4'],
#           (int)weight2 : ['word5', 'word6', 'word7', 'word8', 'word9'],
#       }
#   3.  new_command = SmallTalk(Name, kw)
#   4.  new_command.setStart(method)
#   5.  new_command.setConfirm(confirm_method)    # optional, not required



from .SmallTalk import *
import datetime, time
import math
################################################################################
def method():
    return 'Я не понимаю'

keywords = {}
void = SmallTalk('Undefined', keywords)
void.setStart(method)
################################################################################
def method():
    now     = datetime.datetime.now()
    hours   = now.hour%12 if now.hour else 12
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
    answer = f'Сейчас {get_str_num(hours, 0)} {str_hour}'
    if(minutes): answer += f', {get_str_num(minutes, 1)} {str_minute}'
    return answer

keywords = {
    10:     ['который час', 'сколько времени'],
    5:      ['текущее', 'сейчас', 'время'],
    1:      ['сколько']
}
ctime = SmallTalk('Current Time', keywords)
ctime.setStart(method)
################################################################################
