Steps to deploy Flask's minitwit on Google App Enginee 
---


[Flask](https://github.com/mitsuhiko/flask) is a light-weight web framework for Python, which is well documented and clearly written. Its Github depository provides a few examples, which includes [minitwit](https://github.com/mitsuhiko/flask/tree/master/examples/minitwit). The `minittwit` website enjoys a few basic features of social network such as following, login/logout. 

[Google App Engine](https://appengine.google.com/) or GAE is a major public clouder service besides Amazon EC2. 

- Pro: 
  - It allows up to 25 free apps (great for exercise)
  - Use of database is free
  - Automatical memoryCached for high IO
- Con:
  - Database is no-SQL, which is hard to port
  - More expensive for production than EC2
  
Most importantly, GAE is friendly to Python users, possibly because Guido van Rossum worked there and personally created Python datastore interface. As for me, it is a good choice for a Flask app. 
  
####Step1: download GAE SDK and GAE Flask skeleton 

GAE SDK tests the staging app and eventuall pushes the app to the cloud. 
Flask skeleton can be dowloaded from [Google Developer Console](https://console.developers.google.com/start/appengine). 


####Step2: schema design 
The 






This repo is the example [minitwit](https://github.com/mitsuhiko/flask/tree/master/examples/minitwit) from Flask running on Google App Engine. The site URL is http://minitwit-123.appspot.com

1. Used Google Datastore instead of SQLite
2. Modified schemes and added indexes


