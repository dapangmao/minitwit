Steps to deploy Flask minitwit on Google App Enginee 
---


Flask is a light-weight web framework for Python, which is well documented and clearly written. Its Github depository provides a few examples, which includes [minitwit](https://github.com/mitsuhiko/flask/tree/master/examples/minitwit). The `minittwit` website enjoys a few basic features of social network such as following, login/logout. 

[Google App Engine](https://appengine.google.com/) is a major public clouder service besides Amazon EC2. 

- Pro: 
  - It allows 25 free apps
  - The database is free

####Step1

This repo is the example [minitwit](https://github.com/mitsuhiko/flask/tree/master/examples/minitwit) from Flask running on Google App Engine. The site URL is http://minitwit-123.appspot.com

1. Used Google Datastore instead of SQLite
2. Modified schemes and added indexes


