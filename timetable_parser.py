import json
import requests
from bs4 import BeautifulSoup
from jsondiff import diff
from loguru import logger

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
    last_update_date = get_last_update_date()

    if last_update_date:
        message = message + last_update_date + '\n\n'
    else:
        logger.warning("Timetable is being updated ")

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

    try:
        # facs = None
        facs = soup.find('select', attrs={"name": "facs"}).find('option', string='ИАТ').get('value')
        pers = soup.find('select', attrs={"name": "pers"}).find('option', selected=True).get('value')
        perstart, perend, parity = soup.find('select', attrs={"name": "pers"}).find('option', selected=True).text.replace(' ', '-').split('-')
        timetables = requests.post(timetable_url, data={'mode': '1', 'pers': f'{pers}', 'facs': f'{facs}', 'courses': '4'})

        soup = BeautifulSoup(timetables.text, 'html.parser')
        key = soup.find('a', class_='btn btn-default', text='ИВТб17о-1').get('href').replace('=', '&').split('&')[1]
    except AttributeError:
        return False

    return key, format_date(perstart), format_date(perend)


def get_new_timetable():
    param = get_timetable_param()
    if param:
        key, perstart, perend = param
    else:
        logger.warning("Timetable is being updated ")
        with open('current_timetable.json') as json_file:
            current_timetable = json.load(json_file)
        return current_timetable

    timetable = requests.get(
        f'http://www.mstu.edu.ru/study/timetable/schedule.php?key={key}&perstart={perstart}&perend={perend}&perkind=%F7')

    soup = BeautifulSoup(timetable.text, 'html.parser')
    study_days = soup.findAll('tbody')

    new_timetable = {}
    for study_day in study_days:
        day_name = str()
        lessons = []
        if study_day.find('th') is not None:
            day_name = study_day.find('th').text

        study_day = study_day.findAll("td")
        if study_day:
            for row in range(0, 28, 4):
                lessons.append({study_day[row].text: study_day[row + 1].text + ' ' + study_day[row + 2].text + ' ' + study_day[row + 3].text})

            new_timetable.update({day_name: lessons})
    return new_timetable


def check_update():
    new_timetable = get_new_timetable()

    with open('current_timetable.json') as json_file:
        current_timetable = json.load(json_file)

    changes = diff(current_timetable, new_timetable)
    changes_message = str()
    if changes:
        with open('current_timetable.json', 'w') as outfile:
            json.dump(new_timetable, outfile, ensure_ascii=False)

        days = changes.items()

        for day in days:
            date = day[0]
            lessons = list(day[1].items())
            for key, value in lessons[0][1].items():
                if value == "  ":
                    value = "Пары нет!"
                changes_message = date + '\n' + key + ')' + value
    return changes_message

