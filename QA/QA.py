from bs4 import BeautifulSoup as BS
from Command import Command
import wikipedia as wiki
import requests
import random
import json
import re

class QA(Command):
    def confirm(this, string): return True

    def googleDictionary(this, word):
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

    def wikipedia(this, word):
        wiki.set_lang("ru")
        article = wiki.summary(word, sentences=5)
        try:    return article[:article.find('\n\n')][:600]
        except: return ''

    def googleSearch(this, word):
        responce = requests.get(f'https://www.google.ru/search?&q={word}&lr=lang_ru&lang=ru')
        page = BS(responce.content, 'html.parser')
        info = page.select('div.BNeawe>div>div.BNeawe')
        return info[0].get_text() if info else ''

    def start(this, params):
        query = params['string']
        if 'вики' in query:
            query = query.replace('википедия', '').replace('вики', '').strip()
            try:    search = this.googleSearch(query)
            except: search = ''
            try:    wiki   = this.wikipedia(query) if not 'Википедия' in search else ''
            except: wiki   = ''
            try:    gdict  = this.googleDictionary(query)
            except: gdict  = []
            voice          = search or (gdict['short'] if gdict else '') or wiki
            text           = (f'Google Search:\n\t{search}' if search else '') + (f'\n\nWikipedia:\n\t{wiki}' if wiki else '') + ('\n\nDictionary:'+gdict['text'] if gdict else '')
        else:
            try:    search = this.googleSearch(query)
            except: search = ''
            voice = text = search or random.choice(['Не совсем понимаю, о чём вы.', 'Вот эта последняя фраза мне не ясна.', 'А вот это не совсем понятно.', 'Можете сказать то же самое другими словами?', 'Вот сейчас я совсем вас не понимаю.', 'Попробуйте выразить свою мысль по-другому',])
        return {
            'type': 'simple',
            'text':  text,
            'voice': voice,
        }

Command.QA = QA('QA', {}, [])
