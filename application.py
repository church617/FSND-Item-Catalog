from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Items
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/category')
def showCategories():
	categories = session.query(Category).order_by(asc(Category.cat_id))
	return render_template('category.html', categories=categories)


@app.route('/Category/new/', methods=['GET', 'POST'])
def newCategory():
	if request.method == 'POST':
		newCategory= Category(name= request.form['name'], 
			user_token=login_session['user_token'])
		session.add(newCategory)
		flash('New Category %s succesfully created' % newCategory.name)
		return redirect(url_for('category.html'))
	else:
		return render_template('newCategory.html')


@app.route('/Category/delete/', methods=['GET', 'POST'])
def deleteCategory():
	return render_template('deleteCategory.html')

@app.route('/item')
def showItems():
	items = session.query(Items).order_by(asc(Items.item_id))
	return render_template('item.html', items = items)


@app.route('/newItem')
def newItem():
	return render_template('createItem.html')


@app.route('/editItem')
def editItem():
	return render_template('editItem.html')


@app.route('/deleteItem')
def deleteItem():
	return render_template('deleteItem.html')


@app.route('/login')
def login():
	return render_template('login.html')



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)