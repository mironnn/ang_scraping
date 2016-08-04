# -*- coding: utf-8 -*-
import argparse
from multiprocessing import Pool
import bs4
import requests
from app import db
from models import Vacancy, Location

root_url = 'http://www.stepstone.se'


def get_vacancy_page_urls(index_url, max1=None):
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return [a.attrs.get('href') for a in soup.select('a[href^=http://www.stepstone.se/ledigt-jobb]')][0:max1][1::2]


def get_vacancy_data(vacancy_page_url, soup):
    vacancy_data = {}
    # response = requests.get(vacancy_page_url)
    try:
        vacancy_data['title'] = soup.select('a[href^='+vacancy_page_url+']')[1].attrs['title']
    except:
        vacancy_data['title'] = 'Error'
    try:
        vacancy_data['company'] = soup.select('a[href^='+vacancy_page_url+']')[1].parent.parent.span.a.get_text()
    except:
        vacancy_data['company'] = 'Error'
    try:
        vacancy_data['location'] = [soup.select('a[href^='+vacancy_page_url+']')[1].parent.parent.contents[7]
                                        .contents[2].get_text()]
    except:
        vacancy_data['location'] = 'Error'
    vacancy_data['url'] = vacancy_page_url
    return vacancy_data


def get_vacancies_data(vacancy_page_urls, index_url):
    vacancies_data = []
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    for vacancy_page_url in vacancy_page_urls:
        vacancies_data.append(get_vacancy_data(vacancy_page_url, soup))
    return vacancies_data


def parse_args():
    parser = argparse.ArgumentParser(description='Show Stepstone openings.')
    parser.add_argument('--sort', metavar='FIELD', choices=['title', 'date'],
                        default='date',
                        help='sort by the specified field. Options are title and date.')
    parser.add_argument('--max', metavar='MAX', type=int, help='show the top MAX entries only.')
    parser.add_argument('--csv', action='store_true', default=False,
                        help='output the data in CSV format.')
    parser.add_argument('--workers', type=int, default=8,
                        help='number of workers to use, 8 by default.')
    return parser.parse_args()


def get_index_urls():
    index_urls = []
    i = 0
    while True:
        i += 1
        index_url = root_url + '/lediga-jobb-i-hela-sverige/data-it/sida' + str(i) + '/'
        response = requests.get(index_url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        index_urls.append(index_url)
        # $('section#pagination').children().length
        if len(soup.select('section#pagination')[0].contents) >= 7:
            if len(soup.select('a.btn.btn-caret.right')) != 1:
                return index_urls
        else:
            return index_urls


def show_stepstone_vacancies(options):
    index_urls = get_index_urls()
    for index_url in index_urls:
        vacancy_page_url = get_vacancy_page_urls(index_url)
        vacancies_data = get_vacancies_data(vacancy_page_url, index_url)
        for vacancy_data in vacancies_data:
            # print vacancy_data

            title = vacancy_data['title']
            company = vacancy_data['company']
            url = vacancy_data['url']
            locations = vacancy_data['location']

            vacancy = Vacancy(title=title, company=company, url=url, description='Empty')
            for loc in locations:
                if loc in [locat.place for locat in Location.query.all()]:
                    location = Location.query.filter_by(place=loc).first()
                else:
                    location = Location(place=loc)
                vacancy.locations.append(location)
            db.session.add(vacancy)
            db.session.commit()


if __name__ == '__main__':
    show_stepstone_vacancies(parse_args())
