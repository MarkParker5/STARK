class Media():
    @staticmethod
    def findPage(name):
        query = name + ' site:kinogo.by'
        responce = requests.get(f'https://www.google.ru/search?&q={query}&lr=lang_ru&lang=ru')
        page = BS(responce.content, 'html.parser')
        link = page.select_one('.ZINbbc.xpd.O9g5cc.uUPGi>.kCrYT>a')
        title = page.select_one('.ZINbbc.xpd.O9g5cc.uUPGi .BNeawe.vvjwJb.AP7Wnd').text.split(' смотреть')[0].strip()
        return (link['href'][7:].split('&')[0], title) if link else None

    @staticmethod
    def getFilm(url):
        id = url[18:].split('-')[0].split(',')[-1]
        url = f'https://kinogo.la/engine/ajax/cdn_download.php?news_id={id}'
        responce = requests.get(url)

        page = BS(responce.content, 'html.parser')
        elems = page.children
        for elem in elems:
            if elem == '\n': continue
            spans = elem.find_all('span')
            audio = spans[1].text
            if 'Оригинальная дорожка' in audio or 'Полное дублирование' in audio or 'LostFilm' in audio:
                return elem.ul.li.a['href']
        return None

    @staticmethod
    def getSerial(url):
        id = url[18:].split('-')[0].split(',')[-1]
        url = f'https://kinogo.la/engine/ajax/cdn_download.php?news_id={id}'
        responce = requests.get(url)
        page = BS(responce.content, 'html.parser')
        elems = page.children
        n = len(page.select('.cdn_download_season')) or 1
        seasons = [None]*n
        current_season = n-1
        for elem in elems:
            if elem == '\n': continue
            if elem['class'][0] == 'cdn_download_season':
                current_season = int(elem.text.split(' ')[0])-1
                seasons[current_season] = {}
                continue
            spans = elem.find_all('span')
            if not spans: break
            audio = spans[2].text
            if audio in ['Оригинальная дорожка', 'Полное дублирование', 'LostFilm']:
                num = int(spans[0].text.split(' ')[0])-1
                seasons[current_season][num] = {'href': elem.ul.li.a['href'], 'title': f'{current_season+1} сезон {num+1} серия'}

        new_seasons = []
        for dict_s in seasons:
            season = [None]*(max(dict_s.keys())+1)
            for i, value in dict_s.items():
                season[i] = value
            season = list(filter(None, season))
            new_seasons.append(season)

        return new_seasons

    @staticmethod
    def startFilm(url, title):
        os.system(f'lxterminal --command="vlc {url} -f --meta-title=\\"{title}\\" "')

    @staticmethod
    def startSerial(seasons, name):
        for season in seasons:
            for series in season:
                print(series)
                href = series['href']
                title = name + ' ' + series['title']
                os.system(f'lxterminal --command="vlc --playlist-enqueue {href} --meta-title=\\"{title}\\" "')
