Steps to deploy Flask's minitwit on Google App Enginee 
---

[Flask](https://github.com/mitsuhiko/flask) is a light-weight web framework for Python, which is well documented and clearly written. Its Github depository provides a few examples, which includes [minitwit](https://github.com/mitsuhiko/flask/tree/master/examples/minitwit). The `minittwit` website enjoys a few basic features of social network such as following, login/logout. The demo site on GAE is [http://minitwit-123.appspot.com](http://minitwit-123.appspot.com). The Github depo is [https://github.com/dapangmao/minitwit](https://github.com/dapangmao/minitwit).

[Google App Engine](https://appengine.google.com/) or GAE is a major public clouder service besides Amazon EC2. Among the four languages(Java/Python/Go/PHP) it supports, GAE is friendly to Python users, possibly because Guido van Rossum worked there and personally created Python datastore interface. As for me, it is a good choice for a Flask app. 
  
####Step1: download GAE SDK and GAE Flask skeleton 

[GAE's Python SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python) tests the staging app and eventuall pushes the app to the cloud. 

A Flask skeleton can be dowloaded from [Google Developer Console](https://console.developers.google.com/start/appengine). It contains three files:
  - app.yaml: specify the entrance of run-time
  - appengine_config.py: add the external libraries such as Flask to system path 
  - main.py: the root Python program

####Step2: schema design 
The dabase used for the original minitwit is SQLite. [The schema](https://github.com/mitsuhiko/flask/blob/master/examples/minitwit/schema.sql) consists of three tables: `user`, `follower` and `message`, which makes a normalized database together. GAE has two Datastore APIs: [DB](https://cloud.google.com/appengine/docs/python/datastore/) and [NDB](https://cloud.google.com/appengine/docs/python/ndb/). Since neither of them supports joining (in this case one-to-many joining for user to follower), I move the `follwer` table as an nested text propery into the `user` table, which eliminatse the need for joining. 

As the result, the `main.py` has two data models: `User` and `Message`. They will create and maintain two `kind`s (or we call them as tables) with the same names in Datastore. 
```python
class User(ndb.Model):
  username = ndb.StringProperty(required=True)
  email = ndb.StringProperty(required=True)
  pw_hash = ndb.StringProperty(required=True)
  following = ndb.IntegerProperty(repeated=True)
  start_date = ndb.DateTimeProperty(auto_now_add=True)
  
class Message(ndb.Model):
  author = ndb.IntegerProperty(required=True)
  text = ndb.TextProperty(required=True)
  pub_date = ndb.DateTimeProperty(auto_now_add=True)
  email = ndb.StringProperty(required=True)
  username = ndb.StringProperty(required=True)
```

####Step3: replace SQL statements
The next step is to replace SQL operations in each of the routing functions with NDB's methods. NDB's two fundamental methods are `get()` that retrieves data from Datastore as a list, and `put()` that pushes list to Datastore as a row. In short, data is created and manipulated as individual object. 

For example, if a follower needs to add to a user, I first retrieve the user by its ID that returns a list like `[username, email, pw_hash, following, start_date]`, where following itself is a list. Then I insert the new follower into the following element and save it back again. 
```python
u = User.get_by_id(cid)
if u.following is None:
  u.following = [whom_id]
  u.put()
else:
  u.following.append(whom_id)
  u.put()
```
People with experience in ORM such as [SQLAlchemy](http://www.sqlalchemy.org/) will be comfortable to implement the changes. 

####Setp4: testing and deployment
Without the schema file, now the minitwit is a real single file web app. It's time to use GAE SDK to test it locally, or eventually push it to the cloud. On [GAE](https://appengine.google.com/), We can check any error or warning through the `Logs` tab to find bugs, or view the raw data through the `Datastore Viewer` tab. 

In conclusion, GAE has a few advantages and disadvantages to work with Flask as a web app.
- Pro: 
  - It allows up to 25 free apps (great for exercise)
  - Use of database is free
  - Automatical memoryCached for high IO
- Con:
  - Database is No-SQL, which is hard to port
  - More expensive for production than EC2


