import re
import unicodedata
import urllib.parse

import math

import mysql.connector
from bs4 import BeautifulSoup
import httplib2


class Course:
    @staticmethod
    def __safe_float(data):
        if data:
            return float(data)
        return data

    def __init__(self, list_data):
        if len(list_data) != 16:
            raise SyntaxError('column number is not 16')

        # 年度
        self.year = int(list_data[0])

        # 課程
        self.dummy = list_data[1]

        # 科目コード
        self.code = list_data[2]

        # 開講期間
        if list_data[3] == '春':
            self.season_id = 1
        elif list_data[3] == '秋':
            self.season_id = 2
        elif list_data[3] == '春秋':
            self.season_id = 3
        else:
            raise Exception('unknown season: {:s}'.format(list_data[3]))

        # 開講科目名
        soup = BeautifulSoup(list_data[4], "html5lib")
        link = soup.find('a')
        if link:
            self.syllabus = link['href']
            self.name = str(link.string)
        else:
            self.syllabus = None
            self.name = list_data[4]

        # クラス
        self.class_no = list_data[5]

        # 担当者
        self.professors = set(re.split('<br>|<br/>', list_data[6]))

        # 登録者数, 成績評価, 評点平均値
        self.score = list(map(self.__safe_float, list_data[7:15]))

        # 備考
        self.dummy = list_data[15]

    def dump(self):
        print(self.year, self.code, self.season_id, self.name, self.class_no)
        print(self.professors)
        print(self.score)
        print(self.syllabus)
        print('----------')


class Crawler:
    def __init__(self):
        self.regex = re.compile('<td.+?>(.+?)</td>', flags=re.DOTALL)
        self.cnx = mysql.connector.connect(database='rkp', user='rkp', password='UBFVVPNAGQKqAfNr')
        self.http = httplib2.Http(cache='.cache')

        self.cursor = self.cnx.cursor(buffered=True)
        self.cursor.execute('SELECT * FROM faculty;')
        self.faculty = list(self.cursor)

    def __fetch(self, faculty, year, page):
        if faculty == '060':
            parm1 = '0G0'
        else:
            parm1 = 'ZZZ'

        response, content = self.http.request(
            'http://duet.doshisha.ac.jp/info/GPA', method='POST',
            headers={
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 4.0; MSN 2.5; Windows 95)',
                'Referer': 'http://duet.doshisha.ac.jp/info/GPA',
                'Content-type': 'application/x-www-form-urlencoded'
            },
            body=urllib.parse.urlencode({
                'furiwakeid': 'GP1001',  # Fix 未使用
                'gakubuKenkyuka1': faculty,  # Var 学部: 010, 020, ...
                'hOffSet': (page - 1) * 50,  # Var オフセット: 0, 50, 100, ...
                'hQueryNo': '1',  # Fix 未使用
                'languageCode': 'ja',  # Fix 言語
                'pageNo': page,  # Var ページ番号: 1, 2, 3, ...
                'rowCount': '50',  # Fix 項目数
                'search_term0': '',  # Fix 検索ワード
                'search_term2': year,  # Var 開講年度: 2004, 2005, ..., 2014
                'search_term4': faculty,  # Var 学部: 010, 020, ...
                'search_term4_2': parm1,  # Var 理工学部 0G0, 他 ZZZ
                'search_term6': '12',  # Fix 課程
                'search_term8': '',  # Fix 未使用
                'toEmpty0': '1',  # Fix 検索ワードが空白の場合は1
                'toEmpty4': '0'  # Fix 学部が選択されている場合は0
            })
        )

        html = content.decode('Shift_JIS')
        soup = BeautifulSoup(html, "html5lib")

        if '入力された検索条件に該当する情報はありません。' in html:
            return -1

        raw = soup.find('table', width="95%").find('tbody').find_all('tr')
        raw_max_page = soup.find(attrs={"name": "KekkaMax"}).get('value')

        if raw_max_page:
            max_page = math.ceil(int(raw_max_page) / 50)
        else:
            max_page = None

        for x in raw[2:]:
            try:
                course = Course([self.normalize(self.regex.match(str(y)).group(1)) for y in x.find_all('td')])
                self.__insert(course, faculty)
            except SyntaxError:
                with open('debug.html', mode='w+', encoding='Shift_JIS') as tmp:
                    tmp.write(html)

        self.cnx.commit()

        return max_page

    def fetch(self, faculty, year):
        page = 1
        max_page = 2

        while True:
            if max_page < page:
                break

            print('\t' + ','.join([faculty, str(year), str(page)]))

            ret = self.__fetch(faculty, year, page)
            if ret:
                max_page = ret

            page += 1

    def __insert(self, course, faculty):
        sql_insert_course = 'INSERT INTO course VALUES (NULL, %s, %s, %s, %s, %s, %s, %s);'
        sql_insert_score = 'INSERT INTO score VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        sql_insert_professor = 'INSERT INTO professor VALUES (NULL, %s);'
        sql_insert_professor_relationship = 'INSERT INTO professor_relationship VALUES (%s, %s);'
        sql_select_professor = 'SELECT * FROM professor WHERE name = %s;'

        faculty_id = [y for y in self.faculty if faculty == y[1]][0][0]

        self.cursor.execute(sql_insert_course, (
            faculty_id, course.year, course.code, course.season_id, course.name, course.class_no, course.syllabus
        ))

        course_id = self.cursor.lastrowid

        self.cursor.execute(sql_insert_score, (
            course_id, course.score[0], course.score[1], course.score[2], course.score[3], course.score[4],
            course.score[5], course.score[6], course.score[7], 0
        ))

        professors_id = []

        for professor in course.professors:
            self.cursor.execute(sql_select_professor, (professor,))
            result = list(self.cursor)

            if len(result) == 0:
                self.cursor.execute(sql_insert_professor, (professor,))
                professors_id.append(self.cursor.lastrowid)
            else:
                professors_id.append(result[0][0])

        for professor_id in professors_id:
            self.cursor.execute(sql_insert_professor_relationship, (course_id, professor_id))

    def start(self):
        for faculty_id, code, name in self.faculty:
            print(faculty_id, code, name)

            for year in range(2004, 2015):
                self.fetch(code, year)

    @staticmethod
    def normalize(t):
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