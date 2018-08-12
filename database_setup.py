import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
	__tablename__ = 'user'

	name = Column(String(250), nullable = False)
	email = Column(String(250), nullable = False, unique = True)
	user_token = Column(Integer, primary_key = True, autoincrement = True)


class Category(Base):
	__tablename__ = 'category'

	name = Column(String(250), nullable = False)
	cat_id = Column(Integer, primary_key = True)

	@property
	def serialize(self):
		return {
			'name'			: self.name,
			'id'			: self.cat_id
			}


class Items(Base):
	__tablename__ = 'items'

	item_id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	description = Column(String(400))
	category = relationship(Category, backref=backref('items', cascade='all, delete'))
	cat_id = Column(Integer, ForeignKey('category.cat_id'))

	@property
	def serialize(self):
		return {
			'name'			: self.name,
			'id'			: self.item_id,
			'description'	: self.description,
			'category'		: self.category.name
			}


engine = create_engine('sqlite:///item_catalog.db')

Base.metadata.create_all(engine)