from google.appengine.ext import db

class Blog(db.Model):
      """ A datamodel to represent a blog post. Inherits from db.Model class """

      title=db.StringProperty(required=True)
      text = db.TextProperty(required=True)
      owner = db.TextProperty(required=False)
      likes = db.StringListProperty()
      comments = db.StringListProperty()
      user_comments = db.StringListProperty()
      created = db.DateTimeProperty(auto_now_add = True)
