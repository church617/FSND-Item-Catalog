from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


update = session.query(User).order_by(User.name)
for name in update:
	print(name)

