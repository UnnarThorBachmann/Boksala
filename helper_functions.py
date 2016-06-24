"""
Author: Unnar Thor Bachmann.
"""

"""
Next functions are functions to enable hashing of passwords for security.
They were all written in class.
"""
import re
import hashlib
import hmac
import random
import string

SECRET='imosecret'

def hash_str(s):
    return hmac.new(SECRET,s).hexdigest()
def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
       return val
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw,salt=None):    
    if not salt:
       salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
    a = h.split('|')
    salt = a[1]
    val = a[0]
    print val
    print make_pw_hash(name,pw,salt)
    if val == make_pw_hash(name,pw,salt).split('|')[0]:
       return True
    else:
        return False
""" End of hashing functions. """

""" These are functions to enable usage of regular expressions to validate user input."""
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
EMAIL_RE = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0]{2,4})$)")

def valid_username(username):
        return USER_RE.match(username)
def valid_email(email):
    return EMAIL_RE.match(email)
""" En of regular expression functions. """
