import html
import json
import logging
import re
import time
from telegram import Bot
import os
import requests
from secrets import *

# TODO: Comments
# TODO: Remove sensitive data
# TODO: More dynamic
# TODO: Download password protected files

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# Load json-data with already sent files
def load_data():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data.json')) as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        data = {}
    return data


# Login to MyStudy webpage
def login(session):
    payload = {'user': USERNAME,
               'password': PASSWORD}
    response = session.post('{}/rz/userauthLDAPwhs.php'.format(CAMPUSURL), data=payload)
    sid = re.findall('PHPSESSID=([^;]*);', response.headers['Set-Cookie'])[0]
    session.get('{}/rz/login/content.php?'.format(CAMPUSURL) + sid)
    session.get('{}/rz/login/tostudywise1718.php?sid='.format(CAMPUSURL) + sid)
    session.get('{}/mystudy32/login/senduser_rac.php?sid='.format(CAMPUSURL) + sid)
    path = re.findall("URL=(start_session.php.*)'>$", session.get(
        '{}/mystudy32/login/valid.php?PHPSESSID='.format(CAMPUSURL) + sid).text)[0]


#
def get_courses(session):
    site = session.get('{}/mystudy32/stundenplan/stundenplan.php'.format(CAMPUSURL))
    sessid = re.findall("/stundenplan/stundenplan.php\?PHPSESSID=([^']*)'", site.text)[0]
    course_list = re.findall(
        "stundenplan_felder_text.*?>.<a href=\"javascript:myWindow\(1,([0-9]*),'[^']*'\)\">.([0-9]*)",
        site.text, re.DOTALL)
    course_dict = {x[1]: "https://www.rheinahrcampus.de/mystudy32/seminarkarten/seminar_info.php?vid=" + x[
        0] + "&PHPSESSID=" + sessid for x in course_list}
    return course_dict


def get_file_list(session, course_dict):
    stuff = []
    for key, value in course_dict.items():
        session.get(value)
        material = session.get(
            '{}/mystudy32/seminarkarten/seminar_material.php?karte=material'.format(CAMPUSURL)).text
        course = re.findall('<title>[0-9]* ([^<]*)</title>', material)[0]
        stuff += [[x[0], x[1], course, x[2], key] for x in
                  re.findall('a href="material_download\.php\?datei=([0-9]*)"><b>([^<]*)<.*?"top">([^<]*)</', material,
                             re.DOTALL)]
    return stuff[::-1] if not DEBUG else [stuff[0]]


def download(session, stuff, data):
    send_list = []
    payload = {'submit': 'Datei herunterladen', 'userID': ''}
    for file in stuff:
        if not file[4] in data or not file[0] in data[file[4]]:
            r = session.post(
                '{}/mystudy32/seminarkarten/material_download.php?datei={}'.format(CAMPUSURL, file[0]),
                payload, stream=True)
            if r.status_code == 200:
                send_list.append([html.unescape(file[2]), file[1], html.unescape(file[3]), file[0], file[4]])
                if not os.path.isdir(os.path.join(os.path.dirname(__file__), './downloads/')):
                    os.mkdir(os.path.join(os.path.dirname(__file__), './downloads/'))
                if not os.path.isdir(os.path.join(os.path.dirname(__file__), './downloads/{}'.format(file[2]))):
                    os.mkdir(os.path.join(os.path.dirname(__file__), './downloads/{}'.format(file[2])))
                with open(os.path.join(os.path.dirname(__file__), './downloads/{}/{}'.format(file[2], file[1])),
                          'wb') as f:
                    for chunk in r:
                        f.write(chunk)
    return send_list


def send_data(send_list, data):
    bot = Bot(BOTTOKEN)
    for file in send_list:
        try:
            tag = "".join([re.findall('[a-zA-Z0-9]', x)[0] for x in file[0].split(" ")])
            caption = '{} #{}\n{}'.format(file[0], tag, file[2]) if not file[2] == '' else '{} #{}'.format(file[0], tag)
            bot.sendDocument(chat_id=CHAT_ID if not DEBUG else TEST_ID,
                             document=open(
                                 os.path.join(os.path.dirname(__file__), './downloads/{}/{}'.format(file[0], file[1])),
                                 'rb'), caption=caption, timeout=60)
            data[file[4]] = {'name': file[0]} if not file[4] in data else data[file[4]]
            data[file[4]][file[3]] = {'file': file[1], 'description': file[2]}
        except Exception as e:
            logging.exception(e)
        time.sleep(5)
    return data


def save_data(data):
    with open(os.path.join(os.path.dirname(__file__), './data.json'), 'w') as outfile:
        json.dump(data, outfile, indent=4)


def main():
    data = load_data()
    with requests.Session() as session:
        login(session)
        course_dict = get_courses(session)
        stuff = get_file_list(session, course_dict)
        send_list = download(session, stuff, data)
        data = send_data(send_list, data)
    save_data(data)


if __name__ == '__main__':
    main()
