import re
import unicodedata

import urllib.parse

import math

import mysql.connector
from bs4 import BeautifulSoup
import httplib2


class Course:
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
            self.season = 1
        elif list_data[3] == '秋':
            self.season = 2
        elif list_data[3] == '春秋':
            self.season = 3
        else:
            raise Exception('unknown season: {:s}'.format(list_data[3]))

        # 開講科目名
        soup = BeautifulSoup(list_data[4], "html5lib")
        link = soup.find('a')
        if link:
            self.syllabus = link['href']
            self.name = link.string
        else:
            self.syllabus = None
            self.name = list_data[4]

        # クラス
        self.class_no = list_data[5]

        # 担当者
        self.professors = re.split('<br>|<br/>', list_data[6])

        # 登録者数
        self.students = int(list_data[7])

        # 成績評価, 評点平均値
        if None in list_data[7:14]:
            self.score = [None] * 8
        else:
            self.score = list(map(float, list_data[7:14]))

        # 備考
        self.dummy = list_data[15]

    def dump(self):
        print(self.year, self.code, self.season, self.name, self.class_no)
        print(self.professors)
        print(self.students, self.score)
        print(self.syllabus)
        print('----------')


class Crawler:
    def __init__(self):
        self.regex = re.compile('<td.+?>(.+?)</td>', flags=re.DOTALL)
        self.cnx = mysql.connector.connect(database='rkp', user='rkp', password='UBFVVPNAGQKqAfNr')
        self.http = httplib2.Http(cache='.cache')

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

        soup = BeautifulSoup(content.decode('Shift_JIS'), "html5lib")

        with open('debug.html', mode='w+', encoding='Shift_JIS') as tmp:
            tmp.write(content.decode('Shift_JIS'))

        raw = soup.find('table', width="95%").find('tbody').find_all('tr')
        raw_max_page = soup.find(attrs={"name": "KekkaMax"}).get('value')

        if raw_max_page:
            max_page = math.ceil(int(raw_max_page) / 50)
        else:
            max_page = None

        for x in raw[2:]:
            try:
                test = Course([self.normalize(self.regex.match(str(y)).group(1)) for y in x.find_all('td')])
                print(','.join([test.code, test.name]))
            except SyntaxError:
                print(x)

        return max_page

    def fetch(self, faculty, year):
        page = 1
        max_page = 2

        while True:
            if max_page < page:
                break

            print(page, faculty, year)

            ret = self.__fetch(faculty, year, page)
            if ret:
                max_page = ret

            page += 1

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

    c.fetch('010', '2004')


if __name__ == "__main__":
    main()