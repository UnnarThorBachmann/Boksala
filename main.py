#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
The code was written by Unnar Thor Bachmann except for helper functions written in class for
jinja2, hashing and regular expressions.
"""

import os
import jinja2
import webapp2

import user_module
import blog_module
import helper_functions

from google.appengine.ext import db

""" This code was covered in class and and does enable us to
    use jinja2 in a constructive way as well as autoescape.
"""
template_dir= os.path.join(os.path.dirname(__file__),'template')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

#Global variable to enable editing.
EDIT_ID = 0
   
class BaseHandler(webapp2.RequestHandler):
      """
      class BaseHandler: class which contains functions which the other handlers had in common.
          My attempt to refactor the code. The functions were written in class.
          Each handler has bot the post method and get method. A get method is ran upon redirects
          and post when something is posted on forms.
      """   
      def write(self, *a,**kw):
          self.response.write(*a,**kw)
      def render_str(self,template, **params):
          t = jinja_env.get_template(template)
          return t.render(params)
      def render(self,template, **kw):
          """
          method render: Renders a proper page. Used by a handler.
          """
          self.write(self.render_str(template, **kw))
      def escape_html(self,s):
          return cgi.escape(s,quote=True)
        
      def names(self,like_list):
          """
          method names: Method for making a string out of list of names.
          Returns string of names who have liked this post.
          """
          like_str = ""
          like_cnt = len(like_list)
          if like_cnt == 1:
             like_str = like_list[0]
          elif like_cnt == 2:
               like_str = like_list[0] + " and " + like_list[1]
          elif like_cnt > 2:
               like_str = like_list[0] 
               for i in range(1,like_cnt-1):
                   like_str += ', '
                   like_str += like_list[i]
                   like_str += ' and '
                   like_str += like_list[like_cnt-1]
                   like_str += '.'
          else:
              like_str = ""
          return like_str
        
class LoginHandler(BaseHandler):
      """
      class LoginHandler:  The handler used to handle the login requests.
      """          

      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          self.render("login.html", username = "",
                      login="",
                      logout="hidden",
                      newpost="hidden",
                      blogs="hidden",
                      signup="",
                      password = "",
                      error_login = "")
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          passed_tests = True
  
          username = self.request.get("username")
          password  = self.request.get("password")
          
          p1 = helper_functions.valid_username(username)
          p2 = helper_functions.valid_username(password)

          #If sentence to detect error in login.
          error_login = ''
          if (p1 is None or p2 is None):
             error_login = 'Invalid login'
             passed_tests = False
             self.render("login.html",
                          login="",
                          logout="hidden",
                          newpost="hidden",
                          blogs="hidden",
                          signup="",
                          username = username,
                          password = password,
                          error_login = 'Invalid Login')
             return
          #Detecting if user exists.  
          users = db.GqlQuery("SELECT* FROM User WHERE username= :user",user=str(username))
          user=users.get()
          if user is None:
             passed_tests = False
             error_login="Invalid Login."
          else:
              if  not helper_functions.valid_pw(username,password, user.password):
                  passed_tests = False
                  error_login="Invalid Login."
          if passed_tests:
             self.response.headers.add_header('Set-Cookie', 'name=' + str(user.username) + '|' + str(user.password) + '; Path=/') 
             self.redirect('/blogs')
          else:
              self.render("login.html",
                          login="",
                          logout="hidden",
                          newpost="hidden",
                          blogs="hidden",
                          signup="",
                          username = username,
                          password = password,
                          error_login = error_login)
              
class LogoutHandler(BaseHandler):
      """
      class LogoutHandler: The handler used when user logs out.
      """          
      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          #If user logs out then the cookie is made empty.
          self.response.headers.add_header('Set-Cookie', 'name=; Path=/') 

          self.redirect("/login")
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          pass
        
class DeleteHandler(BaseHandler):
      """
      class DeleteHandler: Class which reports the success of delete.
      """
      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          # showin the success page upon deleting.
          self.render("delete.html",
                      login="hidden",
                      logout="",
                      signup="hidden",)
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          pass
        
class PostHandler(BaseHandler):
      """
      PostHandler: The handler used when user attempts to create a new post.
      """        

      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          if self.request.cookies.get('name') is None or self.request.cookies.get('name')=="":
             self.redirect("/login")
          else:
              self.render("newpost.html",
                      login = "hidden",
                      logout= "",
                      signup="hidden",
                      newpost="",
                      blogs="",
                      title="",
                      text="",
                      cancel="hidden",
                      post="post",
                      action="newpost",
                      greeting="Feel free to blog, " + self.request.cookies.get('name').split("|")[0]+"!")
          
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          # Detecting if user is the one that is logged in otherwise redirect to login.
          if self.request.cookies.get('name') is None or self.request.cookies.get('name')=="":
             self.redirect("/login")
          else:
              #Only allow post when user has written title and blog text.
              title = self.request.get("title")
              text = self.request.get("text")
              if title and text:
                 b = blog_module.Blog(title=title, text=text, owner=self.request.cookies.get('name').split("|")[0])
                 b.put()
                 self.redirect('/blog'+'?q=' + str(b.key().id()) )
              else:
                  error = "we need both a title and some blog!"
                  self.render("newpost.html",
                      login = "hidden",
                      logout= "",
                      signup="hidden",
                      newpost="",
                      blogs="",
                      title=title,
                      text=text,
                      error=error,
                      username=self.request.cookies.get('name').split("|")[0])
                  
class EditHandler(BaseHandler):
      """
      EditHandler: The handler used when user attempts to edit his blog.
      """        

      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          if self.request.cookies.get('name') is None or self.request.cookies.get('name')=="":
             self.redirect("/login")
          else:
              id_str = self.request.url.split("?q=")[1]
              blog = blog_module.Blog.get_by_id(int(id_str))
              global EDIT_ID
              EDIT_ID = int(id_str)
              self.render("newpost.html",
                      login = "hidden",
                      logout= "",
                      signup="hidden",
                      newpost="",
                      blogs="",
                      title=blog.title,
                      text=blog.text,
                      cancel="",
                      post="edit",
                      action="edit",
                      greeting="Edit, " + self.request.cookies.get('name').split("|")[0]+"!")
          
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          if self.request.cookies.get('name') is None or self.request.cookies.get('name')=="":
             self.redirect("/login")
          else:    
              if 'edit' in self.request.arguments():
                 title = self.request.get("title")
                 text = self.request.get("text")
                 
                 if title and text:
                    global EDIT_ID
                    blog = blog_module.Blog.get_by_id(EDIT_ID)
                    blog.title = title
                    blog.text=text
                    blog.put()
                    self.redirect("/blog/" + str(EDIT_ID))
                 else:
                     error = "we need both a title and some blog!"
                     title = self.request.get("title")
                     text = self.request.get("text")
                 
                     self.render("newpost.html",
                                 login = "hidden",
                                 logout= "",
                                 signup="hidden",
                                 newpost="",
                                 blogs="",
                                 title=title,
                                 text=text,
                                 cancel="",
                                 post="edit",
                                 action="edit",
                                 error=error,
                                 greeting="Edit, " + self.request.cookies.get('name').split("|")[0]+"!")
              else:
                  self.redirect("/blog/" + str(EDIT_ID))
        
                  

class BlogsHandler(BaseHandler):
      """
      BaseHandler: The handler used when user attempts to view all the blogs in the system.
      """        

      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          if self.request.cookies.get('name') is None or self.request.cookies.get('name')=="":
             self.redirect("/login")
          else:
              blogs = db.GqlQuery("SELECT* FROM Blog ORDER BY created DESC")
              self.render("blogs.html",
                         login = "hidden",
                         logout= "",
                         signup="hidden",
                         newpost="",
                         blogs = blogs)
              
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          pass
        
class BlogHandler(BaseHandler):
      """
      class BlogHandler: The handler used when user attempts to view a single blog post. 
          He may attempt to like the post, edit it or delete it. 
      """        

      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          if self.request.cookies.get('name') is None or self.request.cookies.get('name')=="":
             self.redirect("/login")
          else:
              if self.request.url.find("?q=") != -1:
                 id_str = self.request.url.split("?q=")[1]
              else:
                  id_str = self.request.url.split("/blog/")[1]

              blog = blog_module.Blog.get_by_id(int(id_str))
              users_comments = zip(blog.comments,blog.user_comments)
              like_list = blog.likes
              like_str = self.names(like_list)
              like_cnt = len(like_list)
              if self.request.cookies.get('name').split("|")[0] == blog.owner:
                 edit = ""
                 delete = ""
              else:
                  edit="hidden"
                  delete="hidden"
                  
              self.render("blog.html",
                      login = "hidden",
                      logout= "",
                      signup="hidden",
                      newpost="",
                      edit=edit,
                      delete=delete,
                      id_str = id_str,
                      users_comments= users_comments,
                      like_cnt = like_cnt,
                      like_str = like_str,
                      blog = blog)
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          if self.request.cookies.get('name') is None or self.request.cookies.get('name')=="":
             self.redirect("/login")
          else:
              text = self.request.get("text")
              
              if self.request.url.find("?q=") != -1:
                  id_str = self.request.url.split("?q=")[1]
              else:
                  id_str = self.request.url.split("/blog/")[1]
              blog = blog_module.Blog.get_by_id(int(id_str))
              like_list = blog.likes
              if self.request.cookies.get('name').split("|")[0] == blog.owner:
                 edit = ""
                 delete = ""
              else:
                  edit="hidden"
                  delete="hidden"
                  
              
              if self.request.arguments()[0] == 'liked':             
                 user = self.request.cookies.get('name').split("|")[0]
                 if user != blog.owner:
                    blog.likes.append(user)
                    blog.likes = list(set(blog.likes))
                    blog.put()
                 like_list = blog.likes
                 like_str = self.names(like_list)
                 like_cnt = len(like_list)
                 users_comments = zip(blog.comments,blog.user_comments)
                 self.render("blog.html",
                          login = "hidden",
                          logout= "",
                          signup="hidden",
                          newpost="",
                          id_str = id_str,
                          users_comments= users_comments,
                          like_cnt = like_cnt,
                          like_str = like_str,
                          blog = blog,
                          edit=edit,
                          delete=delete)
              elif self.request.arguments()[0] == 'edited':
                   if blog_module.Blog.get_by_id(int(id_str)).owner == self.request.cookies.get('name').split("|")[0]:
                      self.redirect("/edit"+"?q="+id_str)
                   else: self.redirect("/logout")
              elif self.request.arguments()[0] == 'deleted':
                   if blog_module.Blog.get_by_id(int(id_str)).owner != self.request.cookies.get('name').split("|")[0]:
                      self.redirect("/logout")
                   else:
                       if  self.request.cookies.get('name').split("|")[0] == blog.owner:
                           blog.delete() 
                           self.redirect("/deleted")
                       else:
                           self.redirect("/blogs")
              else:
                  like_list = blog.likes
                  like_str = self.names(like_list)
                  like_cnt = len(like_list)
                  if text == "" or text is None:
                     users_comments = zip(blog.comments,blog.user_comments)
                     
                     self.render("blog.html",
                          login = "hidden",
                          logout= "",
                          signup="hidden",
                          newpost="",
                          id_str = id_str,
                          like_cnt = like_cnt,
                          like_str = like_str,
                          users_comments= users_comments,
                          blog = blog,
                          edit=edit,
                          delete=delete,
                          error="Empty comments not allowed.")
                  else: 
                      blog.comments.append(text)
                      blog.user_comments.append(self.request.cookies.get('name').split("|")[0])
                      blog.put()
                      users_comments = zip(blog.comments,blog.user_comments)
                      self.render("blog.html",
                          login = "hidden",
                          logout= "",
                          signup="hidden",
                          newpost="",
                          id_str = id_str,
                          like_cnt = like_cnt,
                          like_str = like_str,
                          users_comments= users_comments,
                          blog = blog,
                          edit=edit,
                          delete=delete)
                  
class SignupHandler(BaseHandler):
      """
      class SignupHandler:
      The handler used when user attempts to sing up.
      """        

      def get(self):
          """
          method get: Renders a page upon redirect.
          """
          self.render("signup.html",
                    login = "",
                    logout= "hidden",
                    signup="",
                    newpost="hidden",
                    blogs="hidden",
                    username = "",
                    password = "",
                    verify = "",
                    email = "",
                    error_username = "",
                    error_password = "",
                    error_verify = "",
                    error_email = "")
       
    
      def post(self):
          """
          method post: Renders a page or redirect depending on the nature of the post.
          """
          username = self.request.get("username")
          password  = self.request.get("password")
          verify  = self.request.get("verify")
          email  = self.request.get("email")
       
          valid_usr = helper_functions.valid_username(username)
          valid_pw = helper_functions.valid_username(password)
          valid_em = helper_functions.valid_email(email)
       
          error_username = ''
          error_password =''
          error_verify = ''
          error_email=''
          passed_tests = True
       
          if (valid_usr is None):
             error_username = 'This is not a valid username.'
             passed_tests = False
          if (valid_pw is None):
             error_password= "That wasn't a valid password"
             passed_tests = False
          else:
              if password != verify:
                 error_verify = "Your passwords didn't match."
                 passed_tests = False
         
          if (valid_em is None and email != ''):
             error_email = "This is not a valid email."
             passed_tests = False

          if passed_tests:
             users = db.GqlQuery("SELECT* FROM User WHERE username=:user",user=username)
             for user in users:
                 if user.username == username:
                    passed_tests = False
                    error_username="User already exists."
                    break
             if self.request.cookies.get('name'):
                if self.request.cookies.get('name').split("|")[0] == username:
                   passed_tests = False
                   error_username="User already exists."
          
          if passed_tests:
             salt = helper_functions.make_salt()
             u = user_module.User(username=username, password=helper_functions.make_pw_hash(username,password,salt),email = email)
             u.put()
             self.response.headers.add_header('Set-Cookie', 'name=' + str(username) + '|' + str(helper_functions.make_pw_hash(username,password,salt)) + '; Path=/') 
             self.redirect("/blogs")
          else:
              self.render("signup.html",
                          login="",
                          logout="hidden",
                          signup="",
                          newpost="hidden",
                          blogs="hidden",
                          username = username,
                          password = password,
                          verify = verify,
                          email = email,
                          error_username = error_username,
                          error_password = error_password,
                          error_verify = error_verify,
                          error_email = error_email)

                  
class MainHandler(BaseHandler):
      """
      class MainHandler:
      The handler which handles the base url and redirects to to the login page.
      """        
      def get(self):
          self.redirect("/login")
          
       
#Registering the handlers.   
app = webapp2.WSGIApplication([
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
     ('/logout', LogoutHandler),
    ('/blogs', BlogsHandler),
    ('/newpost', PostHandler),
    ('/blog|/blog/\d+',BlogHandler),
    ('/deleted',DeleteHandler),
    ('/edit',EditHandler),
    ('/', MainHandler)
], debug=True)
