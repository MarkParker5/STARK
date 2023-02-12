from datetime import datetime, timedelta
import urllib.request
import ssl
import xlrd
import xlwt
from xlutils.copy import copy

ssl._create_default_https_context = ssl._create_unverified_context

class Zieit:
    lessonsStartTime = ['08:00', '09:30', '11:10', '12:40', '14:10', '15:50', '17:20']
    lessonsEndTime   = ['09:20', '10:50', '12:30', '14:00', '15:30', '17:10', '18:40']
    weekdays = ["Неділя", "Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"]

    @classmethod
    def getShedule(self):
        url = 'https://www.zieit.edu.ua/wp-content/uploads/Rozklad/3k.xls'
        name = url.split('/')[-1]
        urllib.request.urlretrieve(url, name)

        rbook = xlrd.open_workbook(name, formatting_info=True)
        rsheet = rbook.sheet_by_index(0)
        wbook = copy(rbook)
        wsheet = wbook.get_sheet(0)
        for crange in rsheet.merged_cells:
            rlo, rhi, clo, chi = crange
            base = rsheet.cell_value(rlo, clo)
            for row in range(rlo, rhi):
                for col in range(clo, chi):
                    wsheet.write(row, col, base)

        wbook.save(name)
        book = xlrd.open_workbook(name, formatting_info=True)
        table = book.sheet_by_index(0)

        week = {}
        day = {}
        lesson = {}
        last_day = table.row_values(7)[0]
        for rownum in range(7, table.nrows):
            row = table.row_values(rownum)
            if row[0] != last_day:
                date = last_day.split('\n')[bool(last_day.split('\n')[1])]
                week[date] = day
                day = {}
                last_day = row[0]
            if row[14]:
                if rownum%4 == 1:
                    lesson['teacher'] = row[14]
                elif rownum%4 == 2:
                    lesson['auditory'] = row[14]
                    day[int(row[2])] = lesson
                    lesson = {}
                elif rownum%4 == 3:
                    lesson['subject'] = row[14]
                elif rownum%4 == 0:
                    lesson['type'] = row[14]
                    lesson['index'] = int(row[2])
                    lesson['time']  = str(row[3])
        return week

    @classmethod
    def getTodaysShedule(self):
        today = datetime.now().date()
        return self.getSheduleForDate(today)

    @classmethod
    def getTomorrowsShedule(self):
        tomorrow = datetime.now().date() + timedelta(days = 1)
        return self.getSheduleForDate(tomorrow)

    @classmethod
    def getSheduleForDate(self, target_date):
        week = self.getShedule()
        for d, lessons in week.items():
            try:
                date = datetime.strptime(d, "%d.%m.%Y").date()
                if date == target_date: return lessons
            except:
                if self.weekdays.index(d) == target_date.isoweekday():
                    return lessons
        return None

    @classmethod
    def getNextLesson(self, lessonsTime):
        lessons = self.getTodaysShedule()
        if lessons == None: return None
        next = {}
        for i, lesson in lessons.items():
            border = datetime.strptime(lessonsTime[i-1], '%H:%M').time()
            now = datetime.now().time()
            if now < border: next[i] = lesson
        if next: return next[min(next.keys())]
        else:   return None

    @classmethod
    def fullNames(self, string):
        string = string.lower()
        names = {
            'алгоритми та структури даних': 'Алгоритмы и структуры данных',
            'філософія': 'Философия',
            'архітектура комп\'ютерів': 'Архитектура компьютеров',
            'web-програмування': 'WEB-программирование',
            'бази даних': 'Базы данных',
            'укр мова': 'украинский язык',
            'дискретна': 'дискретная',
            'безпека життєдіяльності та основи охорони праці':'обж',
            'історія україни': 'история',
            'основи програмування':'основы программирования',
            'осн. програм.':'основы программирования',
            'вища':'высшая',
            'пр.заняття':'практика',
            'іноземна мова':'английский',
            'фізична культура':'физкультура',
            'модульний': 'модульный',
            'укр ': '',
            'доц.':'',
            'викл.':'',
            'ст.в.':'',
            '(шк)':'',
            'і':'и',
            'ауд.': '',
            '  ': ' ',
        }
        for short, full in names.items():
            string = string.replace(short, full)
        return string