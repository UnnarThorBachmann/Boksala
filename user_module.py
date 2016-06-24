"""
Author: Unnar Thor Bachmann.
"""

from google.appengine.ext import db

class User(db.Model):
      """
      class User: A datamodel to represent a user. Inherits from db.Model class
      """

      username=db.StringProperty(required=True)
      password = db.TextProperty(required=True)
      email = db.TextProperty(required=False)
