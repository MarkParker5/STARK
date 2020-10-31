from .SmallTalk import *
import time
################################################################################
#                           Only for tests
@SmallTalk.background(answer = 'Запуск фонового процесса', voice = 'Запускаю фоновый процесс')
def method(params, finish_event):
    time.sleep(10)
    finish_event.set()
    return {
        'text': 'Фоновый процесс завершен',
        'voice': 'Фоновый процесс завершен',
    }


keywords = {
    10:     ['тестирование', 'проверка', 'потоков', 'фоновых', 'процессов'],
}
patterns = ['* [тест|провер]* * [фонов*] * (процесс|поток)* *']
test = SmallTalk('Test threads', keywords, patterns)
test.setStart(method)
