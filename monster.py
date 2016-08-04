# -*- coding: utf-8 -*-
import argparse
# from multiprocessing import Pool
import bs4
import requests
from app import Vacancy, Location, db

root_url = 'http://jobb.monster.se'


def get_vacancy_page_urls(index_url, max1=None):
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return [a.attrs.get('href') for a in soup.select('a[href^=http://annonsoversikt.monster.se:80/]')][0:max1]


def get_vacancy_data(vacancy_page_url, soup):
    vacancy_data = {}
    # response = requests.get(vacancy_page_url)
    try:
        vacancy_data['title'] = [a.get_text() for a in soup.select('a[href^='+vacancy_page_url+']')][0]
    except:
        vacancy_data['title'] = 'Error'
    try:
        vacancy_data['company'] = [a.parent.parent.contents[3].a.attrs['title'] for a in
                                   soup.select('a[href^='+vacancy_page_url+']')][0]
    except:
        vacancy_data['company'] = 'Error'
    try:
        vacancy_data['location'] = [a.parent.parent.parent.parent.contents[5].a.attrs['title'] for a in
                                    soup.select('a[href^='+vacancy_page_url+']')][0].split(',')
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
    parser = argparse.ArgumentParser(description='Show Monster openings.')
    parser.add_argument('--sort', metavar='FIELD', choices=['title', 'date'],
                        default='date',
                        help='sort by the specified field. Options are title and date.')
    parser.add_argument('--max', metavar='MAX', type=int, help='show the top MAX entries only.')
    parser.add_argument('--csv', action='store_true', default=False,
                        help='output the data in CSV format.')
    parser.add_argument('--workers', type=int, default=8,
                        help='number of workers to use, 8 by default.')
    return parser.parse_args()


# def get_monster_vacancies(options):
#     pool = Pool(options.workers)
#     vacancy_page_urls = get_vacancy_page_urls(options.max)
#     results = sorted(pool.map(get_vacancy_data, vacancy_page_urls, soup), key=lambda vacancy: vacancy[options.sort],
#                      reverse=True)
#     return results


def get_index_urls():
    index_urls = []
    i = 0
    while True:
        i += 1
        index_url = root_url + '/browse/Data-IT_4?pg=' + str(i)
        response = requests.get(index_url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        index_urls.append(index_url)
        if soup.select('div.navigationBar'):
            if soup.select('span.boxWrap.selected.last'):
                return index_urls
        else:
            return index_urls


def show_monster_vacancies(options):
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
            # if title in [vac.title for vac in Vacancy.query.all()]:
            #     if company in [vac.company for vac in Vacancy.query.filter_by(title=title).all()]:
            #         pass
            #     else:
            #         vacancy = Vacancy(title=vacancy_data['title'], company=vacancy_data['company'],
            #                           url=vacancy_data['url'], description='Empty')
            #         locations = vacancy_data['location']
            #         for loc in locations:
            #             if loc in [locat.place for locat in Location.query.all()]:
            #                 location = Location.query.filter_by(place=loc).first()
            #             else:
            #                 location = Location(place=loc)
            #             vacancy.locations.append(location)
            #         db.session.add(vacancy)
            #         db.session.commit()
            # else:
            #     vacancy = Vacancy(title=vacancy_data['title'], company=vacancy_data['company'],
            #                       url=vacancy_data['url'], description='Empty')
            #     locations = vacancy_data['location']
            #     for loc in locations:
            #         if loc in [locat.place for locat in Location.query.all()]:
            #             location = Location.query.filter_by(place=loc).first()
            #         else:
            #             location = Location(place=loc)
            #         vacancy.locations.append(location)
            #     db.session.add(vacancy)
            #     db.session.commit()

            vacancy = Vacancy(title=title, company=company, url=url, description='Empty')
            for loc in locations:
                if loc in [locat.place for locat in Location.query.all()]:
                    location = Location.query.filter_by(place=loc).first()
                else:
                    location = Location(place=loc)
                vacancy.locations.append(location)
            db.session.add(vacancy)
            db.session.commit()

    # results = get_monster_vacancies(options)
    #
    # print len(results)
    # max1 = options.max
    # if max1 is None or max1 > len(results):
    #     max1 = len(results)
    # if options.csv:
    #     print(u'"title","date"')
    # else:
    #     print(u'Date  Title ')
    # for i in range(max1):
    #     if options.csv:
    #         print(u'{0},{1}'.format(
    #             results[i]['title'], results[i]['date']))
    #     else:
    #         print(u'{0} {1}'.format(
    #             results[i]['date'], results[i]['title']))


if __name__ == '__main__':
    show_monster_vacancies(parse_args())
