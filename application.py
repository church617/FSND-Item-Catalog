from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Items
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
    category = session.query(Category).filter_by(id=cat_id).one()
    items = session.query(Items).filter_by(cat_id=cat_id).all()
    return jsonify(items=items.serialize)


@app.route('/category/<int:cat_id>/items/<int:item_id>/JSON')
def itemListJSON():
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


@app.route('/category/JSON')
def categoryJSON():
    category = session.query(Category).all()
    return jsonify(category=[r.serialize for r in category])


@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('publicCategory.html', categories=categories)
    else:
        return render_template('category.html', categories=categories)


@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


@app.route('/category/<int:cat_id>/edit', methods=['GET', 'POST'])
def editCategory(cat_id):
    categoryEdit = session.query(Category).filter_by(cat_id=cat_id).one()
    if request.method == 'POST':
        if request.form['name']:
            categoryEdit.name = request.form['name']
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=categoryEdit)


@app.route('/category/<int:cat_id>/delete', methods=['GET', 'POST'])
def deleteCategory(cat_id):
    categoryToDelete = session.query(Category).filter_by(cat_id=cat_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',
                            category=categoryToDelete)


@app.route('/category/<int:cat_id>/')
@app.route('/category/<int:cat_id>/items')
def showItems(cat_id):
    category = session.query(Category).filter_by(cat_id=cat_id).one()
    items = session.query(Items).filter_by(cat_id=cat_id).all()
    return render_template('item.html', items=items, category=category)


@app.route('/category/<int:cat_id>/items/<int:item_id>/edit',
            methods=['GET', 'POST'])
def editItem(cat_id, item_id):
    editedItem = session.query(Items).filter_by(item_id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', cat_id=cat_id))
    else:
        return render_template('editItem.html', cat_id=cat_id, item_id=item_id)


@app.route('/category/<int:cat_id>/items/new', methods=['GET', 'POST'])
def newItem(cat_id):
    if request.method == 'POST':
        newItem = Items(name=request.form['name'],
                        description=request.form['description'], cat_id=cat_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', cat_id=cat_id))
    else:
        return render_template('createItem.html', cat_id=cat_id)


@app.route('/category/<int:cat_id>/items/<int:item_id>/delete',
            methods=['GET', 'POST'])
def deleteItem(cat_id, item_id):
    itemToDelete = session.query(Items).filter_by(item_id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', cat_id=cat_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


@app.route('/login')
def login():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# GConnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.' ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserToken(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.token


def getUserInfo(user_token):
    user = session.query(User).filter_by(token=user_token).one()
    return user


def getUserToken(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.token
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
