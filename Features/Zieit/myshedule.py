from .Zieit import *

def formatLesson(lesson):
    if lesson == None: voice = text = 'Сегодня пар нет'
    else:
        index    = lesson['index']
        time     = lesson['time'].replace('.', ':')
        subject  = lesson['subject']
        teacher  = lesson['teacher']
        auditory = lesson['auditory']
        type     = lesson['type']
        voice    = Zieit.fullNames(f'{type} по предмету {subject} в аудитории {auditory} в {time}')
        text     = Zieit.fullNames(f'{index}. [{time}] {subject}\n{teacher}\n{auditory}\n{type}')
    return Response(text = text, voice = voice)

def formatDay(lessons):
    text = voice = ''
    if not lessons:
        return None
    for i, lesson in lessons.items():
        index    = lesson['index']
        time     = lesson['time'].replace('.', ':')
        subject  = lesson['subject']
        teacher  = lesson['teacher']
        auditory = lesson['auditory']
        type     = lesson['type']
        voice    += Zieit.fullNames(f'.№{index}, {type} по предмету {subject} в аудитории {auditory}.\n').capitalize()
        text     += Zieit.fullNames(f'\n{index}. [{time}] {subject}\n....{type} ({auditory})\n....') + teacher
    return Response(text = text, voice = voice)

################################################################################

def nextLessonFunc(params):
    return formatLesson(Zieit.getNextLesson(Zieit.lessonsStartTime))

patterns = ['* следующ* (предмет|урок|пара)']
nextLesson = Zieit('Next Lesson', patterns)
nextLesson.setStart(nextLessonFunc)

################################################################################

def currentLessonFunc(params):
    return formatLesson(Zieit.getNextLesson(Zieit.lessonsEndTime))

patterns = ['* (текущ*|сейчас) (предмет|урок|пара)']
currentLesson = Zieit('Current Lesson', patterns)
currentLesson.setStart(currentLessonFunc)

################################################################################

def todaysSheduleFunc(params):
    if lessons := Zieit.getTodaysShedule():
        return formatDay(lessons)
    else:
        text = voice = 'Сегодня пар нет'
        return Response(text = text, voice = voice)

patterns = ['* сегодня (предметы|уроки|пары|расписание)', '* (предметы|уроки|пары|расписание) * сегодня *']
todaysShedule = Zieit('Todays Shedule', patterns)
todaysShedule.setStart(todaysSheduleFunc)

################################################################################

def tomorrowsSheduleFunc(params):
    if lessons := Zieit.getTomorrowsShedule():
        return formatDay(lessons)
    else:
        text = voice = 'Завтра пар нет'
        return Response(text = text, voice = voice)

patterns = ['* завтра (предметы|уроки|пары|расписание)', '* (предметы|уроки|пары|расписание) * завтра *']
tomorrowsShedule = Zieit('Todays Shedule', patterns)
tomorrowsShedule.setStart(tomorrowsSheduleFunc)
