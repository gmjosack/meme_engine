import jinja2
import os
import webapp2

from google.appengine.api import users


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), "templates")
    ),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class MemeEngineRequestHandler(webapp2.RequestHandler):

    def get_current_user(self):
        return users.get_current_user()

    def render(self, template, **kwargs):
        template = JINJA_ENVIRONMENT.get_template(template)
        self.response.write(template.render(kwargs))
