# Item Catalog Application


The Item catalog is an application that shows a listed items on a web application by connecting to a created database and give the user the ability to modify this data according to a certain criteria.



# Featuers:

  - Provide Gmail login
  - API Endpoint displayed in HTML
  - Provide detailed info for each item
  - The user can add new item
  - The user can modify the info of an item if he is the creator of it
  - The user can delete an item if he is the creator of it
  - Third party authentication service






## Requried Softwares


* Linux based OS or a virtual machine if you have windows OS
* [GitBash](https://git-scm.com/downloads) for windows users
* Installed [Python](https://www.python.org/downloads/) enviroment

## Required Libraries
* [Flask](http://flask.pocoo.org/docs/0.12/installation/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [JSON](https://docs.python.org/2/library/json.html)
* [Requests](http://docs.python-requests.org/en/master/)
* [Random](https://docs.python.org/2/library/random.html)
* [httplib2](https://pypi.python.org/pypi/httplib2/0.7.2)
* [oauth2client.client ](http://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html)


## Files Included
* templates folder : the place wehere the HTML templates are stored to be rendered
* database_setup.py : initializing the database paramaters
* add_data.py : create the database file with a new data called catalogemenu.db
* client_secrets.JSON : has OAuth 2.0 client info
* project.py : has the main program to run the application
## Installation
* Open your Git and write the following to create the database file

1 
```sh
python add_data.py
```

2
```sh
python project.py
```





