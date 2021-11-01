from ArchieCore import Command, Response
from .Zieit import Zieit

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

@Command.new(['следующ* (предмет|урок|пара)'])
def nextLesson(params):
    return formatLesson(Zieit.getNextLesson(Zieit.lessonsStartTime))

@Command.new(['(текущ*|сейчас) (предмет|урок|пара)'])
def currentLesson(params):
    return formatLesson(Zieit.getNextLesson(Zieit.lessonsEndTime))

@Command.new(['сегодня (предметы|уроки|пары|расписание)', '* (предметы|уроки|пары|расписание) * сегодня'])
def todaysShedule(params):
    if lessons := Zieit.getTodaysShedule():
        return formatDay(lessons)
    else:
        text = voice = 'Сегодня пар нет'
        return Response(text = text, voice = voice)

@Command.new(['завтра (предметы|уроки|пары|расписание)', '* (предметы|уроки|пары|расписание) * завтра'])
def tomorrowsShedule(params):
    if lessons := Zieit.getTomorrowsShedule():
        return formatDay(lessons)
    else:
        text = voice = 'Завтра пар нет'
        return Response(text = text, voice = voice)
