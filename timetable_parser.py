import json
import requests
from bs4 import BeautifulSoup
from jsondiff import diff

timetable_url = 'http://www.mstu.edu.ru/study/timetable/'


def get_last_update_date():
    res = requests.post(timetable_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    last_update = soup.find('p', class_='text-right').text

    return last_update


def get_current_timetable():
    with open('current_timetable.json') as json_file:
        current_timetable = json.load(json_file)

    message = str()
    message = message + get_last_update_date() + '\n\n'

    for study_day in current_timetable.items():
        message = message + study_day[0] + '\n'
        lessons = study_day[1]
        for lesson in lessons:
            lesson_list = list(lesson)
            message = message + lesson_list[0] + ') ' + lesson.get(lesson_list[0]) + '\n'
        message = message + '\n'

    return message


def format_date(per):
    return per.split('.')[2] + '-' + per.split('.')[1] + '-' + per.split('.')[0]


def get_timetable_param():
    res = requests.post(timetable_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    facs = soup.find('select', attrs={"name": "facs"}).find('option', string='ИАТ').get('value')
    pers = soup.find('select', attrs={"name": "pers"}).find('option', selected=True).get('value')
    perstart, perend, parity = soup.find('select', attrs={"name": "pers"}).find('option', selected=True).text.replace(' ', '-').split('-')

    timetables = requests.post(timetable_url, data={'mode': '1', 'pers': f'{pers}', 'facs': f'{facs}', 'courses': '4'})

    soup = BeautifulSoup(timetables.text, 'html.parser')
    key = soup.find('a', class_='btn btn-default', text='ИВТб17о-1').get('href').replace('=', '&').split('&')[1]

    return key, format_date(perstart), format_date(perend)


def get_new_timetable():
    key, perstart, perend = get_timetable_param()

    timetable = requests.get(
        f'http://www.mstu.edu.ru/study/timetable/schedule.php?key={key}&perstart={perstart}&perend={perend}&perkind=%F7')

    soup = BeautifulSoup(timetable.text, 'html.parser')
    study_days = soup.findAll('tbody')

    new_timetable = {}
    for study_day in study_days:

        lessons = []
        if study_day.find('th') is not None:
            day_name = study_day.find('th').text

        study_day = study_day.findAll("td")
        if study_day:
            for row in range(0, 28, 4):
                lessons.append({study_day[row].text: study_day[row + 1].text + ' ' + study_day[row + 2].text + ' ' + study_day[row + 3].text})

            new_timetable.update({day_name: lessons})
    return new_timetable


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


