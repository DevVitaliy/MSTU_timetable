import requests
import datetime
from bs4 import BeautifulSoup


timetable_url = 'http://www.mstu.edu.ru/study/timetable/'


def get_perend():
    with open('date', 'rt') as fout:
        date = fout.read()
    # with open('pers', 'rt') as fout:
        pers = 137

    year, month, day = date.split(' ')
    start_date = datetime.date(int(year), int(month), int(day))
    end_date = start_date + datetime.timedelta(days=6)

    current_date = datetime.date.today()
    if current_date > end_date:
        start_date = start_date + datetime.timedelta(days=7)
        end_date = end_date + datetime.timedelta(days=7)

        with open('date', 'wt') as fout:
            fout.write(str(start_date.year) + ' ' + str(start_date.month) + ' ' + str(start_date.day))
        with open('pers', 'wt') as fout:
            fout.write(str(int(pers) + 1))

    return start_date, end_date


def get_request_key():
    with open('pers', 'rt') as fout:
        pers = fout.read()
    res = requests.post('http://www.mstu.edu.ru/study/timetable/',
                        data={'mode':'1', 'pers':f'{pers}', 'facs':'3', 'courses':'4'})
    return res.text


def get_timetable_url():
    s_date, e_date = get_perend()
    soup = BeautifulSoup(get_request_key(), 'html.parser')
    heading = soup.findAll('a', class_="btn btn-default")
    print(heading)
    dict_2 = {head.text: head.get('href').split('=')[1].split('&')[0] for head in heading}
    print(dict_2)
    print(dict_2["ИВТб17о-1"])
    return f'http://www.mstu.edu.ru/study/timetable/schedule.php?key={dict_2["ИВТб17о-1"]}&perstart={s_date}&perend={e_date}&perkind=%F7'


def get_timetable_update_date():
    """Function to get the date of the last timetable update"""
    res = requests.get(timetable_url)
    update_date = BeautifulSoup(res.text, 'html.parser').find('p', class_='text-right')
    return update_date.text


def get_timetable_html_code():
    """Function to get the entire html page with the timetable"""
    timetable_code = requests.get(get_timetable_url())
    return timetable_code.text


def get_heading(soup):
    """Function for getting the heading of the timetable"""
    heading = soup.find('h1')
    return heading.text


def get_timetable_content(soup):
    """"""
    titles = soup.findAll('tbody')
    return titles


def parse_timetable(titles):
    result = str()

    print(titles)

    for title in titles:
        list_2 = []
        working_day = title.findAll('tr')

        day = title.find('th', colspan="4")
        if day:
            result = result + day.text + '\n'

        for row in working_day:
            lessons = row.findAll('td')
            list_1 = []
            for les in lessons:
                list_1.append(les.text)
            list_2.append(list_1)
        for day1 in list_2:
            if day1:
                num, name, teacher, loc = day1
                if name:
                    result = result + f'{num}) {name} ({loc}) ' + '\n'
                else:
                    result = result + f'{num}) - ' + '\n'
        result = result + '\n'
    return result


def create_timetable_message():
    soup = BeautifulSoup(get_timetable_html_code(), 'html.parser')
    update_date = get_timetable_update_date()
    heading = get_heading(soup)
    working_days = get_timetable_content(soup)
    timetable = parse_timetable(working_days)
    current_timetable = heading + '\n\n' + timetable + update_date
    return heading + '\n\n' + timetable + update_date