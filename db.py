import os

from sqlalchemy import create_engine, Column, Integer, Float, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


class ReprBase:
    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{:s}={!r}'.format(x, y) for x, y in self.__dict__.items() if x[0] != '_'])
        )


Base = declarative_base(cls=ReprBase)

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

    def __str__(self):
        return self.name


class Season(Base):
    __tablename__ = 'season'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)

    def __str__(self):
        return self.name


class Lecturer(Base):
    __tablename__ = 'lecturer'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(250), unique=True, nullable=False)

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

    def __str__(self):
        return self.name

    def dict(self):
        return {
            'school_year': self.school_year,
            'faculty': str(self.faculty),
            'code': self.code,
            'season': str(self.season),
            'name': self.name,
            'syllabus_link': self.syllabus_link,
            'class_no': self.class_no,
            'lecturers': list(map(str, self.lecturers)),
            'number_participants': self.number_participants,
            'grade': {
                'a': self.grade_a,
                'b': self.grade_b,
                'c': self.grade_c,
                'd': self.grade_d,
                'f': self.grade_f,
                'other': self.grade_other
            },
            'average_grade': self.average_grade
        }


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
    a = DB()
    s = a.session()

    t = s.query(Faculty).filter_by(name='理工学部').one()

    print(s.query(Subject).filter_by(faculty=t, school_year=2014, class_no=1).first())