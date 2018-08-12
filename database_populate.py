from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


session.query(Category).delete()
session.query(Items).delete()



Category1 = Category(name = "Soccer")
session.add(Category1)
session.commit()


Item1 = Items(name = "Football",
				description = "A Football.",
				cat_id = 1)
session.add(Item1)
session.commit()


Item2 = Items(name = "Soccer Ball",
				description = "A Soccer Ball",
				cat_id = 1)
session.add(Item2)
session.commit()


print "Database populated"