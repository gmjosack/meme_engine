import webapp2

from . import handlers

application = webapp2.WSGIApplication([
    ('/', handlers.Index),

    ('/template', handlers.TemplatesView),
    ('/template/(?P<template_id>[\d]+)/?', handlers.TemplateView),

    ('/add_template', handlers.AddTemplate),
    ('/create_meme', handlers.CreateMeme),

    ('/image', handlers.Image),

    ('/rpc/list_templates', handlers.ListTemplates),

], debug=True)
