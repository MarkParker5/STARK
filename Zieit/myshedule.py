from .Zieit import *
################################################################################
def nextLessonMethod(params):
    lesson   = Zieit.getNextLesson(Zieit.lessonsStartTime)
    if lesson == None: voice = text = 'Сегодня пар нет'
    else:
        subject  = lesson['subject']
        teacher  = lesson['teacher']
        auditory = lesson['auditory']
        type     = lesson['type']
        voice    = Zieit.fullNames(f'{type} по предмету {subject} в аудитории {auditory}')
        text     = f'{subject}\n{teacher}\n{auditory}\n{type}'
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* следующ* (предмет|урок|пара)']
nextLesson = Zieit('Next Lesson', keywords, patterns)
nextLesson.setStart(nextLessonMethod)

################################################################################

def currentLessonMethod(params):
    lesson   = Zieit.getNextLesson(Zieit.lessonsEndTime)
    if lesson == None: voice = text = 'Сегодня пар нет'
    else:
        subject  = lesson['subject']
        teacher  = lesson['teacher']
        auditory = lesson['auditory']
        type     = lesson['type']
        voice    = Zieit.fullNames(f'{type} по предмету {subject} в аудитории {auditory}')
        text     = f'{subject}\n{teacher}\n{auditory}\n{type}'
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* (текущ*|сейчас) (предмет|урок|пара)']
currentLesson = Zieit('Current Lesson', keywords, patterns)
currentLesson.setStart(currentLessonMethod)

################################################################################

def todaysSheduleMethod(params):
    lessons = Zieit.getTodaysShedule()
    text = voice = ''
    if not lessons: voice = text = 'Сегодня пар нет'
    return Response(text = text, voice = voice)
    for lesson in lessons:
        subject  = lesson['subject']
        teacher  = lesson['teacher']
        auditory = lesson['auditory']
        type     = lesson['type']
        voice    += Zieit.fullNames(f'{type} по предмету {subject} в аудитории {auditory}\n')
        text     += f'{subject} ({auditory})\n'
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* сегодня (предметы|уроки|пары|расписание)']
todaysShedule = Zieit('Todays Shedule', keywords, patterns)
todaysShedule.setStart(todaysSheduleMethod)
