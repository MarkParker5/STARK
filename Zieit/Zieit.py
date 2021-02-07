from Command import Command                     #   import parent class

class Zieit (Command):
    lessonsStartTime = ['07:55','09:25','11:05','12:35','14:05','15:45','17:15']
    lessonsEndTime = ['09:15','10:45','12:25','13:55','15:25','17:05','18:35']

    def start(this, string):                    #   main method
        pass

    @staticmethod
    def getShedule():
        url = 'https://www.zieit.edu.ua/wp-content/uploads/Rozklad/2k.xls'
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
                date = last_day.split('\n')[1]
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
        return week

    @staticmethod
    def getTodaysShedule():
        week = getShedule()
        for d, lessons in week.items():
            date = datetime.strptime(d, "%d.%m.%Y").date()
            today = datetime.now().date() + timedelta(days=1)
            if date == today: return lessons
        return None

    @staticmethod
    def getNextLesson(lessonsTime):
        lessons = getTodaysShedule()
        next = {}
        for i, lesson in lessons.items():
            border = datetime.strptime(lessonsTime[i-1], '%H:%M').time()
            now = datetime.strptime('11:00', '%H:%M').time()#datetime.now().time()
            print(now, start, now < border)
            if now < start: next[i] = lesson
        if next: return next[min(next.keys())]
        else:   return None
