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
import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Blog(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC Limit 5")
        self.render("blog.html", title=title, blog=blog, error = error, blogs = blogs)

    def get(self):
        self.render_front()


class NewPost(Handler):
    def render_new(self, title="", blog="", error=""):
        self.render("newpost.html", title=title, blog=blog, error = error)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")
        if title and blog:
            a = Blog(title = title, content = blog)
            a.put()
            string_id = a.key().id()
            self.redirect("/blog/" + str(string_id))
        else:
            error = "we need both a title and some content!"
            self.render_new(title = title, blog = blog, error = error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        id_num = int(id)
        post = Blog.get_by_id(id_num)
        post_title = "<h2>" + post.title + "</h2>"
        post_content = "<p>" + post.content + "</p>"
        self.response.write(post_title + post_content)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
