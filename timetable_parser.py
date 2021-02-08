import json
import requests
from bs4 import BeautifulSoup
from jsondiff import diff
from loguru import logger

timetable_url = 'http://www.mstu.edu.ru/study/timetable/'


def get_last_update_date():
    res = requests.post(timetable_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    last_update = soup.find('p', class_='text-right')

    return last_update


def get_current_timetable():
    with open('current_timetable.json') as json_file:
        current_timetable = json.load(json_file)

    message = str()
    last_update_date = get_last_update_date()

    if last_update_date:
        message = message + last_update_date.text + '\n\n'
    else:
        message = message + 'Расписание обновляется' + '\n\n'
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


def get_timetable_param(timetable_week=False):
    res = requests.post(timetable_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    facs = soup.find('select', attrs={"name": "facs"}).find('option', string='ИАТ').get('value')
    pers = soup.find('select', attrs={"name": "pers"}).find('option', selected=True).get('value')

    if timetable_week:
        pers = str(int(pers) + 1)
        perstart, perend, parity = soup.find('select', attrs={"name": "pers"}).find('option',value=pers).text.replace(' ', '-').split('-')
    else:
        perstart, perend, parity = soup.find('select', attrs={"name": "pers"}).find('option',selected=True).text.replace(' ', '-').split('-')

    try:
        timetables = requests.post(timetable_url,
                                   data={'mode': '1', 'pers': f'{pers}', 'facs': f'{facs}', 'courses': '4'})

        soup = BeautifulSoup(timetables.text, 'html.parser')
        key = soup.find('a', class_='btn btn-default', text='ИВТб17о-1').get('href').replace('=', '&').split('&')[1]
    except AttributeError:
        return False

    return key, format_date(perstart), format_date(perend)


def get_new_timetable(timetable_week):
    if timetable_week:
        param = get_timetable_param('next')
    else:
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
                lessons.append({study_day[row].text: study_day[row + 1].text + ' ' + study_day[row + 2].text + ' ' +
                                                     study_day[row + 3].text})

            new_timetable.update({day_name: lessons})
    return new_timetable


def get_next_week_timetable():
    with open('nw_timetable.json') as json_file:
        nw_timetable = json.load(json_file)

    message = str()
    last_update_date = get_last_update_date()

    if last_update_date:
        message = message + last_update_date.text + '\n\n'
    else:
        message = message + 'Расписание обновляется' + '\n\n'
        logger.warning("Timetable is being updated ")

    for study_day in nw_timetable.items():
        message = message + study_day[0] + '\n'
        lessons = study_day[1]
        for lesson in lessons:
            lesson_list = list(lesson)
            message = message + lesson_list[0] + ') ' + lesson.get(lesson_list[0]) + '\n'
        message = message + '\n'

    return message


def check_update():
    new_timetable = get_new_timetable(False)

    with open('current_timetable.json') as json_file:
        current_timetable = json.load(json_file)

    with open('nw_timetable.json') as json_file:
        nw_timetable = json.load(json_file)

    if not diff(nw_timetable, new_timetable):
        with open('current_timetable.json', 'w') as outfile:
            json.dump(nw_timetable, outfile, ensure_ascii=False)
        with open('nw_timetable.json', 'w') as outfile:
            json.dump(get_new_timetable(timetable_week='next'), outfile, ensure_ascii=False)
            print('переход на новое расписание')
        return False

    changes = diff(current_timetable, new_timetable)
    changes_message = str('')

    if changes:
        with open('current_timetable.json', 'w') as outfile:
            json.dump(new_timetable, outfile, ensure_ascii=False)

        days = changes.items()

        for day in days:
            date = day[0]
            changes_message = changes_message + date
            lessons = list(day[1].items())

            for lesson in lessons:
                for key, value in lesson[1].items():
                    if value == "  ":
                        value = "Пары нет!"
                    changes_message = changes_message + '\n' + key + ') ' + value
            changes_message = changes_message + '\n'
    return changes_message
