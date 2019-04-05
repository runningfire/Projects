from sqlalchemy import *
from sqlalchemy.orm import mapper , clear_mappers

engine = create_engine('sqlite:///:memory:', echo=True)
metadata = MetaData()
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String),
    Column('password', String)
)

metadata.create_all(engine)
class User(object):
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)

mapper(User, users_table)

clear_mappers()
print(mapper(User, users_table))
user = User("Вася", "Василий", "qweasdzxc")
print (user)
print (user.id)
