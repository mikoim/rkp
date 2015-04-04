import re
import unicodedata

import mysql.connector
from bs4 import BeautifulSoup


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


class Crawler:
    def __init__(self):
        self.regex = re.compile('<td.+?>(.+?)</td>', flags=re.DOTALL)
        self.cnx = mysql.connector.connect(database='rkp', user='rkp', password='UBFVVPNAGQKqAfNr')

    def do(self):
        soup = BeautifulSoup(open('sample.html'), "html5lib")

        raw = soup.find('table', width="95%").find('tbody').find_all('tr')

        for x in raw[2:]:
            test = Course([self.normalize(self.regex.match(str(y)).group(1)) for y in x.find_all('td')])
            test.dump()

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
    c.do()


if __name__ == "__main__":
    main()