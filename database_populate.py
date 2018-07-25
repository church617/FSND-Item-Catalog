from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


session.query(User).delete()
session.query(Category).delete()
session.query(Items).delete()


User1 = User(name = "John Wayne",
				email = "JWayne@gmail.com")
session.add(User1)
session.commit()


Category1 = Category(name = "Soccer",
						user_token=1)
session.add(Category1)
session.commit()


Item1 = Items(name = "Football",
				description = "A Football.",
				cat_id = 1,
				user_token = 1)
session.add(Item1)
session.commit()


Item2 = Items(name = "Soccer Ball",
				description = "A Soccer Ball",
				cat_id = 1,
				user_token=1)
session.add(Item2)
session.commit()


print "Database populated"
