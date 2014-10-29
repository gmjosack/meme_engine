import webapp2

from . import handlers

application = webapp2.WSGIApplication([
    ('/', handlers.MemesView),

    ('/template', handlers.TemplatesView),
    ('/template/(?P<template_id>[\d]+)/?', handlers.TemplateView),

    ('/meme', handlers.MemesView),
    ('/meme/(?P<meme_id>[\d]+)/?', handlers.MemeView),

    ('/add_template', handlers.AddTemplate),
    ('/create_meme', handlers.CreateMeme),

    ('/image', handlers.Image),

    ('/rpc/list_templates', handlers.ListTemplates),
    ('/rpc/upload_meme', handlers.UploadMeme),

], debug=True)
