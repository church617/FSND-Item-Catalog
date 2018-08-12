from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///item_catalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/category/<int:cat_id>/items/JSON')
def categoryListJSON(cat_id):
    category=session.query(Category).filter_by(id=cat_id).one()
    items=session.query(Items).filter_by(cat_ic=cat_id).all()
    return jsonify(items=items.serialize)


@app.route('/category/<int:cat_id>/items/<int:item_id>/JSON')
def itemListJSON():
    item=session.query(Items).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


@app.route('/category/JSON')
def categoryJSON():
    category=session.query(Category).all()
    return jsonify(category=[r.serialize for r in category])


@app.route('/')
@app.route('/category/')
def showCategories():
    categories=session.query(Category).all()
    return render_template('category.html', categories=categories)


@app.route('/category/new', methods=['GET','POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


@app.route('/category/<int:cat_id>/edit', methods=['GET','POST'])
def editCategory(cat_id):
    categoryEdit=session.query(Category).filter_by(cat_id=cat_id).one()
    if request.method=='POST':
        if request.form['name']:
            categoryEdit.name=request.form['name']
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=categoryEdit)


@app.route('/category/<int:cat_id>/delete', methods=['GET', 'POST'])
def deleteCategory(cat_id):
    categoryToDelete=session.query(Category).filter_by(cat_id=cat_id).one()
    if request.method=='POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)


@app.route('/category/<int:cat_id>/')
@app.route('/category/<int:cat_id>/items')
def showItems(cat_id):
    category = session.query(Category).filter_by(cat_id=cat_id).one()
    items = session.query(Items).filter_by(cat_id=cat_id).all()
    return render_template('item.html', items=items, category=category)


@app.route('/category/<int:cat_id>/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(cat_id, item_id):
	editedItem=session.query(Items).filter_by(item_id=item_id).one()
	if request.method=='POST':
		if request.form['name']:
			editedItem.name=request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		session.add(editedItem)
		session.commit()
		return redirect(url_for('showItems', cat_id=cat_id))
	else:
		return render_template('editItem.html', cat_id=cat_id, item_id=item_id)


@app.route('/category/<int:cat_id>/items/new', methods=['GET', 'POST'])
def newItem(cat_id):
	if request.method=='POST':
		newItem = Items(name=request.form['name'], description=request.form['description'], 
			cat_id=cat_id)
		session.add(newItem)
		session.commit()
		return redirect(url_for('showItems', cat_id=cat_id))
	else:
		return render_template('createItem.html', cat_id=cat_id)


@app.route('/category/<int:cat_id>/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(cat_id,item_id):
	itemToDelete=session.query(Items).filter_by(item_id=item_id).one()
	if request.method=='POST':
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('showItems', cat_id=cat_id))
	else:
		return render_template('deleteItem.html', item=itemToDelete)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
