from flask import (Flask, jsonify, request, url_for,
                   abort, g, render_template, redirect, flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask.ext.httpauth import HTTPBasicAuth
# importing libraries

app = Flask(__name__)

# read the client ID from client_secrets.JSON file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# application name
APPLICATION_NAME = "Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogemenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# render the login template and create state variable


@app.route('/login')
def showlogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Connet with gmail when sending post request


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

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
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;
    border-radius: 150px;-webkit-border-radius: 150px;
    -moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# disconnect the current user


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
    print login_session['access_token']
    print result['status']
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

# create new user


def createUser(login_session):
    # assign user info
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# get the information of a user by ID


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# get the user id using his email


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# return JSON end point for category


@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])

# return JSON end point for all items in a category


@app.route('/category/<int:category_id>/item/JSON')
def restaurantMenuJSON(category_id):
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])

# return JSON end point for item details


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def menuItemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)
# render the home page of the application


@app.route('/')
@app.route('/catalog/')
def showCataglog():
    categories = session.query(Category).order_by(
        asc(Category.name))  # get the categories from database file
    items = session.query(Item).limit(6)  # get the first 6 items
    # render the home page template
    return render_template('publicCatalog.html',
                           categories=categories, items=items)

# show the items of a certain category


@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/item/')
def showCategory(category_id):
    current_category = session.query(Category).filter_by(
        id=category_id).one()  # get the currenct category
    categories = session.query(Category).all()  # get all categories
    # get the number of items in the currecnt category
    number_items = session.query(Item).filter_by(
        category_id=category_id).count()
    # get the info of the creator user
    creator = getUserInfo(current_category.user_id)
    # get all the items of the current category
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template('Category.html', items=items,
                           current_category=current_category, creator=creator,
                           categories=categories, number_items=number_items)

# show the info of a certain Item


@app.route('/catalog/<int:category_id>/<int:item_id>/')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(
        id=item_id).one()  # get the item from the database
    # render a template to show the items info
    return render_template('item.html', item=item)

# edit the info of a certain item


@app.route('/restaurant/<int:category_id>/menu/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:  # check if the user is logged in
        return redirect('/login')
    editedItem = session.query(Item).filter_by(
        id=item_id).one()  # get the item
    category = session.query(Category).filter_by(
        id=category_id).one()  # get the category of the item
    # check if the current user is the creator for the item or not
    if login_session['user_id'] != editedItem.user_id:
        not_authorized = '''<script>function myFunction(){
            alert('You are not authorized to edit this item');}
            </script><body onload='myFunction()'>'''
        return not_authorized
    if request.method == 'POST':
        if request.form['name']:
            # store a new name in a variable
            editedItem.name = request.form['name']
        if request.form['description']:
            # store a new description in a variable
            editedItem.description = request.form['description']
        if request.form['category']:
            new_category = session.query(Category).filter_by(
                name=request.form['category']).one()  # get a new category
            # store the id of the new category
            editedItem.category_id = new_category.id
        session.add(editedItem)  # add the new info
        session.commit()
        flash('Menu Item Successfully Edited')
        # return to the category of the item
        return redirect(url_for('showCategory', category_id=category.id))
    else:
        # show edit item template
        return render_template('editItem.html',
                               category_id=category_id,
                               editeItem=editedItem)

# create new item


@app.route('/catalog/<int:category_id>/item/new/ ', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:  # check if the user is logged in
        return redirect('/login')
    # get the current category
    current_category = session.query(Category).filter_by(
        id=category_id).one()
    if request.method == 'POST':
        # get the info from the form on the template
        newItem = Item(
            name=request.form['name'], user_id=login_session['user_id'],
            description=request.form['description'],
            category_id=category_id)
        session.add(newItem)
        flash('New Restaurant %s Successfully Created' % newItem.name)
        session.commit()
        # return to the category
        return redirect(url_for('showCategory', category_id=category_id))
    else:

        # show new item template
        return render_template('newItem.html',
                               current_category=current_category)


# delte item
@app.route('/category/<int:Item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(Item_id):
    itemToDelete = session.query(
        Item).filter_by(id=Item_id).one()  # get the item by id
    # check if the user is logged in or not
    if 'username' not in login_session:
        return redirect('/login')
    # check if the current user is the creator of the item or not
    if itemToDelete.user_id != login_session['user_id']:
        not_authorized = '''<script>function myFunction() {alert('You are not
         authorized to delete this item.');}</script>
        <body onload='myFunction()'>'''
        return not_authorized
    if request.method == 'POST':
        session.delete(itemToDelete)  # delete the item
        flash('%s Successfully Deleted' % itemToDelete.name)
        session.commit()
        # return to the category
        return redirect(url_for('showCategory',
                                category_id=itemToDelete.category_id))
    else:
        # render the delete item template
        return render_template('deleteItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
