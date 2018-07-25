from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


update = session.query(User).filter_by(name='John Wayne').one()
print update.name
print update.email
print update.token
print "\n"


