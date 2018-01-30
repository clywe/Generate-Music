from bs4 import BeautifulSoup
import re
import requests
import cgi
import os
import shutil
import argparse


def download_gtp(ids):
    # ссылка для скачивания связана с id
    # вот /n/tabs/download/<номер id>.html
    # просто переходим по ссылке и сохраняем в папку
    for song_id in ids:
        url = "http://www.gtp-tabs.ru/n/tabs/download/" + song_id + ".html"
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise ValueError('Failed to download')
        params = cgi.parse_header(
            response.headers.get('Content-Disposition', ''))[-1]
        if 'filename' not in params:
            raise ValueError('Could not find a filename')

        filename = re.sub('([\(\[]).*?([\)\]])', '', os.path.basename(params['filename']))
        filename = re.sub(' ','', filename)
        directory = "out/" + band + "/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        abs_path = os.path.join(directory, filename)
        with open(abs_path, 'wb') as target:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, target)


def choose_better_rating(songs):
    # выбираем для каждой песни лучший рейтинг,
    # то есть оставляем только один гтп для каждой песни
    song_titles = []
    song_ratings = []
    song_ids = []
    for song in songs:
        song_title = (song["Song"].translate(
                    str.maketrans(" ", " ", "'?.!/;&’:1234567890"))).lower()
        if song_title not in song_titles:
            song_titles.append(song_title)
            song_ratings.append(song["Rating"])
            song_ids.append(song["Id"])
        else:
            if song["Rating"] > song_ratings[-1]:
                song_ratings[-1] = song["Rating"]
                song_ids[-1] = song["Id"]
    download_gtp(song_ids)
    pass


def main():
    URL = "http://www.gtp-tabs.ru/n/search/go.html?SearchForm%5BsearchIn%5D+" \
             "=artist&SearchForm%5BsearchString%5D=" + band.replace(' ','+')
    search_query = requests.get(URL)
    search_result = BeautifulSoup(search_query.content, 'html.parser')
    html_band = str(search_result.find('table',
                   {"class" : "content-table alt"})).lower()
    link_to_band = (html_band[html_band.find("href="):
                   html_band.find(band)])[6:-2]
    URL_to_band = "http://www.gtp-tabs.ru" + link_to_band
    search_all_songs = requests.get(URL_to_band)
    html_songs_info =  BeautifulSoup(search_all_songs.content, 'html.parser')
    html_songs = html_songs_info.find_all('div', {"class", "col-2"})[1:-1]
    html_ratings = (html_songs_info.find_all('div', {"class", "col-4"}))[:-1]
    ratings = [str(rating)[str(rating).rfind('e">')+3:
             str(rating).rfind('e">')+4] for rating in html_ratings]
    ids = [str(rating)[str(rating).find("data-item")+11:
               str(rating).find("data-model")-2] for rating in html_ratings]
    songs = [str(song)[str(song).rfind('">')+2:str(song).rfind("</a")]
            for song in html_songs]
    songs2=[]
    for song in songs:
        bracket = song.find("(")
        if bracket > 0:
            song=song[:bracket-1]
        song = song.replace("_'", "'")
        song = song.replace("&amp;", "&")
        song = song.replace("_", "/")
        songs2.append(song)
    data = []
    for i in range(0, len(songs2)):
        songs_and_ratings = {}
        songs_and_ratings["Song"] = songs2[i]
        songs_and_ratings["Id"] = ids[i]
        songs_and_ratings["Rating"] = int(ratings[i]) if ratings[i] != 'i' else 0
        data.append(songs_and_ratings)
    choose_better_rating(data)


band = ''
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='You need enter a band name')
    parser.add_argument('band', action="store")
    band = parser.parse_args()
    band = str(band)[str(band).find("'")+1:-2]
    print ("Cкачиваем табулатуры группы " + band)
    main()
