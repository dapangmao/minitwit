Steps to deploy Flask's minitwit on Google App Enginee 
---


[Flask](https://github.com/mitsuhiko/flask) is a light-weight web framework for Python, which is well documented and clearly written. Its Github depository provides a few examples, which includes [minitwit](https://github.com/mitsuhiko/flask/tree/master/examples/minitwit). The `minittwit` website enjoys a few basic features of social network such as following, login/logout. The demo site on GAE is [http://minitwit-123.appspot.com](http://minitwit-123.appspot.com). The Github depo is [https://github.com/dapangmao/minitwit](https://github.com/dapangmao/minitwit).

[Google App Engine](https://appengine.google.com/) or GAE is a major public clouder service besides Amazon EC2. 

- Pro: 
  - It allows up to 25 free apps (great for exercise)
  - Use of database is free
  - Automatical memoryCached for high IO
- Con:
  - Database is No-SQL, which is hard to port
  - More expensive for production than EC2
  
Most importantly, GAE is friendly to Python users, possibly because Guido van Rossum worked there and personally created Python datastore interface. As for me, it is a good choice for a Flask app. 
  
####Step1: download GAE SDK and GAE Flask skeleton 

[GAE's Python SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python) tests the staging app and eventuall pushes the app to the cloud. 

A Flask skeleton can be dowloaded from [Google Developer Console](https://console.developers.google.com/start/appengine). It contains three files:
  - app.yaml: specify the entrance of run-time
  - appengine_config.py: add the external libraries such as Flask to system path 
  - main.py: the root Python program

####Step2: schema design 
The dabase used for the original minitwit is SQLite. [The schema](https://github.com/mitsuhiko/flask/blob/master/examples/minitwit/schema.sql) consists of three tables: `user`, `follower` and `message`, which makes a normalized database together. GAE has two Datastore APIs: [DB](https://cloud.google.com/appengine/docs/python/datastore/) and [NDB](https://cloud.google.com/appengine/docs/python/ndb/). Since neither of them supports joining (one-to-many joining for user to follower in this app), I move the `follwer` table as an nested text propery into the `user` table, which eliminatse the need for joining. 

Now the schema looks like --
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






This repo is the example [minitwit](https://github.com/mitsuhiko/flask/tree/master/examples/minitwit) from Flask running on Google App Engine. The site URL is http://minitwit-123.appspot.com

1. Used Google Datastore instead of SQLite
2. Modified schemes and added indexes


