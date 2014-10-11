import webapp2

from . import handlers

application = webapp2.WSGIApplication([
    ('/', handlers.Index),
], debug=True)
