import os

from sqlalchemy import create_engine, Column, Integer, Float, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

lecture_relationship = Table(
    'lecturer_relationship', Base.metadata,
    Column('subject_id', Integer, ForeignKey('subject.id')),
    Column('lecturer_id', Integer, ForeignKey('lecturer.id'))
)


class Faculty(Base):
    __tablename__ = 'faculty'

    id = Column(Integer, primary_key=True)
    # 学部
    name = Column(String(250), unique=True, nullable=False)
    search_term4 = Column(String(3), unique=True, nullable=False)

    def __repr__(self):
        return "Faculty(id={!r}, name={!r}, search_term4={!r})".format(self.id, self.name, self.search_term4)

    def __str__(self):
        return self.name


class Season(Base):
    __tablename__ = 'season'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)

    def __repr__(self):
        return 'Season(id={!r}, name={!r})'.format(self.id, self.name)

    def __str__(self):
        return self.name


class Lecturer(Base):
    __tablename__ = 'lecturer'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(250), unique=True, nullable=False)

    def __repr__(self):
        return 'Lecturer(id={!r}, fullname={!r})'.format(self.id, self.fullname)

    def __str__(self):
        return self.fullname


class Subject(Base):
    __tablename__ = 'subject'

    id = Column(Integer, primary_key=True)
    # 開講年度
    school_year = Column(Integer)
    # 学部
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    faculty = relationship('Faculty')
    # 科目コード
    code = Column(String(250))
    # 開講期間
    season_id = Column(Integer, ForeignKey('season.id'))
    season = relationship('Season')
    # 開講科目名
    name = Column(String(250))
    # シラバス
    syllabus_link = Column(String(250))
    # クラス
    class_no = Column(String(250))
    # 担当者
    lecturers = relationship('Lecturer', lecture_relationship)
    # 登録者数
    number_participants = Column(Integer)
    # 成績評価
    grade_a = Column(Float)
    grade_b = Column(Float)
    grade_c = Column(Float)
    grade_d = Column(Float)
    grade_f = Column(Float)
    grade_other = Column(Float)
    # 評点平均値
    average_grade = Column(Float)
    # RKP Index
    rkp_index = Column(Float, index=True)

    def __repr__(self):
        return 'Subject(id={!r}, school_year={!r}, faculty_id={!r}, faculty={!r}, code={!r}, season_id={!r}, season={!r}, name={!r}, syllabus_link={!r}, class_no={!r}, lecturers={!r}, number_participants={!r}, grade_a={!r}, grade_b={!r}, grade_c={!r}, grade_d={!r}, grade_f={!r}, grade_other={!r}, average_grade={!r}, rkp_index={!r})'.format(self.id, self.school_year, self.faculty_id, self.faculty, self.code, self.season_id, self.season, self.name, self.syllabus_link, self.class_no, self.lecturers, self.number_participants, self.grade_a, self.grade_b, self.grade_c, self.grade_d, self.grade_f, self.grade_other, self.average_grade, self.rkp_index)

    def __str__(self):
        return self.name


class DB:
    def __init__(self, url=None):
        if url is None:
            url = os.environ['RKP_DB_URL']

        self.engine = create_engine(url)

    def session(self):
        return sessionmaker(bind=self.engine)()

    def init_db(self):
        Base.metadata.create_all(self.engine)
        session = self.session()

        seasons = ['春', '秋', '春秋']
        for x in seasons:
            session.add(Season(name=x))

        faculties = [('010', '神学部'), ('020', '文学部'), ('030', '法学部'), ('040', '経済学部'), ('050', '商学部'), ('070', '政策学部'), ('080', '文化情報学部'), ('090', '社会学部'), ('0E0', '生命医科学部'), ('0F0', 'スポーツ健康科学部'),
                     ('060', '理工学部'), ('0H0', '心理学部'), ('0J0', 'グローバル・コミュニケーション学部'), ('0K0', '国際教育インスティテュート'), ('0M0', 'グローバル地域文化学部'), ('200', '語学科目'), ('300', '保健体育科目'), ('400', '留学生科目'),
                     ('100', '全学共通教養教育科目')]
        for x in faculties:
            session.add(Faculty(search_term4=x[0], name=x[1]))

        session.commit()


if __name__ == '__main__':
    pass
