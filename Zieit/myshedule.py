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
        voice    = f'{type} по предмету {subject} в аудитории {auditory}'
        text     = f'{subject}\n{teacher}\n{auditory}\n{type}'
    return {
        'type': 'simple',
        'text': text,
        'voice': voice,
    }

keywords = {}
patterns = ['* следующ* (предмет|урок|пара)']
nextLesson = Zieit('Next Lesson', keywords, patterns)
nextLesson.setStart(nextLessonMethod)
