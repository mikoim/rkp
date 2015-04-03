import re
import unicodedata
import mysql.connector

from bs4 import BeautifulSoup


regex = re.compile('<td.+?>(.+?)</td>', flags=re.DOTALL)
cnx = mysql.connector.connect(database='rkp', user='rkp', password='UBFVVPNAGQKqAfNr')


class Course:
    def __init__(self, list_data):
        self.year = list_data[0]  # 年度
        self.dummy = list_data[1]  # 課程
        self.code = list_data[2]  # 科目コード
        self.season = list_data[3]  # 開講期間
        self.name = list_data[4]  # 開講科目名
        self.class_no = list_data[5]  # クラス
        self.professors = list_data[6]  # 担当者
        self.students = int(list_data[7])  # 登録者数
        self.score = Score(list_data[7:14])  # 成績評価, 評点平均値
        self.dummy = list_data[15]  # 備考


class Score:
    def __init__(self, count_students, list_score):
        if len(list_score) != 7:
            raise Exception('unexpected data')

        self.__data = list(map(float, list_score))

    def get_a(self):
        return self.__data[0]

    def get_b(self):
        return self.__data[1]

    def get_c(self):
        return self.__data[2]

    def get_d(self):
        return self.__data[3]

    def get_f(self):
        return self.__data[4]

    def get_average(self):
        return self.__data[5]

    def __str__(self):
        for f in self.__data:
            print(f)


def normalize(t):
    t = t.replace('\n', '')

    while "  " in t:
        t = t.replace('  ', ' ')

    t = unicodedata.normalize('NFKC', t)

    if t == '<br/>':
        t = None

    return t


def main():
    soup = BeautifulSoup(open('sample.html'), "html5lib")

    raw = soup.find_all('tbody')[6].find_all('tr')

    for x in raw[2:]:
        test = Course([normalize(regex.match(str(y)).group(1)) for y in x.find_all('td')])
        print(test.score)
        break


if __name__ == "__main__":
    main()