from bs4 import BeautifulSoup as BS
from ArchieCore import CommandsManager, Command, Response, ResponseAction
import wikipedia as wiki
import requests
import random
import json
import re

class QAHelper():

    @staticmethod
    def googleDictionary(word):
        responce = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/ru/{word}')
        if responce.status_code == 200:
            responce = json.loads(responce.content)
            text = ''
            r = responce[0]
            definition = r['meanings'][0]['definitions'][0]
            short = r['word'].lower().capitalize() + ' (' + ( r['meanings'][0]['partOfSpeech'].capitalize() if r['meanings'][0]['partOfSpeech'] != 'undefined' else 'Разговорный' ) + ') — ' + definition['definition'].lower().capitalize() + ( '. Синонимы: ' + ', '.join(definition['synonyms']) if definition['synonyms'] else '')
            short = short.replace(word[0].lower()+'.', word.lower())
            short = short.replace(word[0].upper()+'.', word.capitalize())
            short = short.replace('-н.', '-нибудь')
            short = short.replace('потр.', 'потребляется')
            short = short.replace('знач.', 'значении')

            for r in responce:
                text += '\n' + r['word'].lower().capitalize() + ' (' + (r['meanings'][0]['partOfSpeech'].capitalize() if r['meanings'][0]['partOfSpeech'] != 'undefined' else 'Разговорный') + ')\n'
                for definition in r['meanings'][0]['definitions']:
                    text += '\t— ' + definition['definition'].lower().capitalize()
                    if example := definition.get('example'):
                        text += '\n\tНапример: ' + example
                    if synonyms := definition['synonyms']:
                        text += '\n\tСинонимы: ' + ', '.join(synonyms) + '.'
                    if antonyms := definition['antonyms']:
                        text += '\n\tАнтонимы: ' + ', '.join(antonyms) + '.'
                    text += '\n\n'

            return {
                'text': text,
                'short': short,
            }
        return {}

    @staticmethod
    def wikipedia(word):
        wiki.set_lang("ru")
        article = wiki.summary(word, sentences=5)
        try:    return article[:article.find('\n\n')][:600]
        except: return ''

    @staticmethod
    def googleSearch(word):
        responce = requests.get(f'https://www.google.ru/search?&q={word}&lr=lang_ru&lang=ru',
            headers = {'User-Agent': 'Mozilla/5.0'})
        page = BS(responce.content, 'html.parser')
        info = page.select('div.BNeawe>div>div.BNeawe')
        return info[0].get_text() if info else ''

@Command.new()
def qa_start(params):
    query = params['string'].value

    voice = text = ''
    actions = [ResponseAction.commandNotFound]

    if 'вики' in query:
        query = query.replace('википедия', '').replace('вики', '').strip()
        try:    search = QAHelper.googleSearch(query)
        except: search = ''
        try:    wiki   = QAHelper.wikipedia(query) if not 'Википедия' in search else ''
        except: wiki   = ''
        try:    gdict  = QAHelper.googleDictionary(query)
        except: gdict  = []
        voice          = search or (gdict['short'] if gdict else '') or wiki
        text           = (f'Google Search:\n\t{search}' if search else '') + (f'\n\nWikipedia:\n\t{wiki}' if wiki else '') + ('\n\nDictionary:'+gdict['text'] if gdict else '')
        if not text and not voice:
            actions.append(ResponseAction.answerNotFound)
    else:
        try:    search = QAHelper.googleSearch(query)
        except: search = ''
        if not search:
            actions.append(ResponseAction.answerNotFound)
        voice = text = search or random.choice(['Не совсем понимаю, о чём вы.', 'Вот эта последняя фраза мне не ясна.', 'А вот это не совсем понятно.', 'Можете сказать то же самое другими словами?', 'Вот сейчас я совсем вас не понимаю.', 'Попробуйте выразить свою мысль по-другому',])

    return Response(text = text, voice = voice, actions = actions)

CommandsManager().QA = qa_start