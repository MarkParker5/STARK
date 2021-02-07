from .Zieit import *
import urllib.request
import xlrd
import xlwt
from xlutils.copy import copy
################################################################################
def nextLesson(params):
    lesson   = Zieit.getNextLesson(Zieit.lessonsStartTime)
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
nextLesson.setStart(method)
