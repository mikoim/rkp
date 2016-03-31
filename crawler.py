import math
import os.path
import re
import unicodedata
import urllib.parse

import httplib2
from bs4 import BeautifulSoup

from db import *


class Crawler:
    def __init__(self):
        self.regex = re.compile('<td.+?>(.+?)</td>', flags=re.DOTALL)
        self.http = httplib2.Http()
        self.db = DB()
        self.session = self.db.session()

        self.lecturers_cache = {}
        self.seasons_cache = {}

    def __http(self, body) -> str:
        cache_path = '.cache/{:d}-{:s}-{:d}.html'.format(body['search_term2'], body['search_term4'], body['pageNo'])

        if os.path.isfile(cache_path):
            with open(cache_path, mode='r', encoding='Shift_JIS') as file:
                return file.read()

        response, content = self.http.request(
            'http://duet.doshisha.ac.jp/info/GPA', method='POST',
            headers={
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 4.0; MSN 2.5; Windows 95)',
                'Referer': 'http://duet.doshisha.ac.jp/info/GPA',
                'Content-type': 'application/x-www-form-urlencoded'
            },
            body=urllib.parse.urlencode(body)
        )

        html = content.decode('Shift_JIS')

        with open(cache_path, mode='w', encoding='Shift_JIS') as file:
            file.write(html)

        return html

    def __fetch(self, faculty, year, page):
        term4 = faculty.search_term4
        if term4 == '060':
            term4_2 = '0G0'
        else:
            term4_2 = 'ZZZ'

        body = {
            'furiwakeid': 'GP1001',  # Fix 未使用
            'gakubuKenkyuka1': term4,  # Var 学部: 010, 020, ...
            'hOffSet': (page - 1) * 50,  # Var オフセット: 0, 50, 100, ...
            'hQueryNo': '1',  # Fix 未使用
            'languageCode': 'ja',  # Fix 言語
            'pageNo': page,  # Var ページ番号: 1, 2, 3, ...
            'rowCount': '50',  # Fix 項目数
            'search_term0': '',  # Fix 検索ワード
            'search_term2': year,  # Var 開講年度: 2004, 2005, ..., 2015
            'search_term4': term4,  # Var 学部: 010, 020, ...
            'search_term4_2': term4_2,  # Var 理工学部 0G0, 他 ZZZ
            'search_term6': '12',  # Fix 課程
            'search_term8': '',  # Fix 未使用
            'toEmpty0': '1',  # Fix 検索ワードが空白の場合は1
            'toEmpty4': '0'  # Fix 学部が選択されている場合は0
        }

        html = self.__http(body)
        soup = BeautifulSoup(html, "html5lib")

        if '入力された検索条件に該当する情報はありません。' in html:
            return -1

        raw = soup.find('table', width="95%").find('tbody').find_all('tr')
        raw_max_page = soup.find(attrs={"name": "KekkaMax"}).get('value')

        if raw_max_page:
            max_page = math.ceil(int(raw_max_page) / 50)
        else:
            max_page = None

        try:
            subjects = list(map(lambda x: self.__raw_to_subject(faculty, [self.__normalize(self.regex.match(str(y)).group(1)) for y in x.find_all('td')]), raw[2:]))
            return max_page, subjects
        except Exception as e:
            with open('debug.html', mode='w+', encoding='Shift_JIS') as tmp:
                tmp.write(html)
            raise e

    def fetch(self, faculty, year):
        page = 1
        max_page = 2

        while True:
            if max_page < page:
                break

            print('\t' + ','.join([faculty.name, str(year), str(page)]))

            ret, subjects = self.__fetch(faculty, year, page)
            if ret:
                max_page = ret

            self.session.add_all(subjects)
            self.session.commit()

            page += 1

    def __insert(self, course, faculty):
        pass

    def __raw_to_subject(self, faculty, raw):
        if len(raw) != 16:
            raise AssertionError('raw length is must be 16! {:d} != 16'.format(len(raw)))

        # 年度
        year = int(raw[0])

        # 科目コード
        code = raw[2]

        # 開講期間
        season = raw[3]

        # 開講科目名
        soup = BeautifulSoup(raw[4], "html5lib")
        link = soup.find('a')
        if link:
            syllabus = link['href']
            name = str(link.string)
        else:
            syllabus = None
            name = raw[4]

        # クラス
        class_no = raw[5]

        # 担当者
        lecturers = list(map(self.__raw_to_lecturer, set(re.split('<br>|<br/>', raw[6]))))

        # 登録者数, 成績評価, 評点平均値
        data = list(map(self.__safe_float, raw[7:15]))

        return Subject(
            school_year=year, faculty=faculty, code=code, season=self.__raw_to_season(season), name=name, syllabus_link=syllabus, class_no=class_no, lecturers=lecturers,
            number_participants=data[0], grade_a=data[1], grade_b=data[2], grade_c=data[3], grade_d=data[4], grade_f=data[5], grade_other=data[6], average_grade=data[7],
            rkp_index=0
        )

    def __raw_to_season(self, name):
        """
        Ret Season object based on name.

        :type name: str
        :param name: season name
        :rtype: Season
        :return: Season object
        """

        if name in self.seasons_cache:
            return self.seasons_cache[name]

        query = self.session.query(Season).filter_by(name=name)
        count = query.count()

        if count > 1:
            raise LookupError('matched multiple rows! count:{:d} name:{:s}'.format(count, name))

        elif count == 1:
            season = query.one()
            self.seasons_cache[name] = season
            return season

        else:
            self.session.add(Season(name=name))
            return self.__raw_to_season(name)

    def __raw_to_lecturer(self, fullname):
        """
        Ret Lecturer object based on normalized fullname.

        :type fullname: str
        :param fullname: lecturer's name
        :rtype: Lecturer
        :return: Lecturer object
        """

        if fullname in self.lecturers_cache:
            return self.lecturers_cache[fullname]

        query = self.session.query(Lecturer).filter_by(fullname=fullname)
        count = query.count()

        if count > 1:
            raise LookupError('matched multiple rows! count:{:d} fullname:{:s}'.format(count, fullname))

        elif count == 1:
            lecturer = query.one()
            self.lecturers_cache[fullname] = lecturer
            return lecturer

        else:
            self.session.add(Lecturer(fullname=fullname))
            return self.__raw_to_lecturer(fullname)

    def start(self):
        faculties = self.session.query(Faculty).all()

        for f in faculties:
            print(f.name, f.search_term4)

            for year in range(2004, 2016):
                self.fetch(f, year)

    @staticmethod
    def __safe_float(s):
        if s:
            return float(s)

        return s

    @staticmethod
    def __normalize(t):
        t = t.replace('\n', '')

        while "  " in t:
            t = t.replace('  ', ' ')

        t = unicodedata.normalize('NFKC', t)

        if t == '<br/>':
            t = None

        return t


def main():
    c = Crawler()
    c.start()


if __name__ == "__main__":
    main()
