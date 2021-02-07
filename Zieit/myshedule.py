from .Zieit import *
import urllib.request
import xlrd
import xlwt
from xlutils.copy import copy
################################################################################
def nextLesson(params):
    lesson = Zieit.getNextLesson(Zieit.lessonsStartTime)
    voice = f'{lesson['type']} по предмету {lesson['subject']} в аудитории {lesson['auditory']}'
    text = f'{lesson['subject']}\n{lesson['teacher']}\n{lesson['auditory']}\n{lesson['type']}'
    return {
        'type': 'simple',
        'text': text,
        'voice': voice,
    }

keywords = {}
patterns = ['* следующ* (предмет|урок|пара)']
nextLesson = Zieit('Next Lesson', keywords, patterns)
nextLesson.setStart(method)
