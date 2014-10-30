import webapp2

from . import handlers

application = webapp2.WSGIApplication([
    ('/', handlers.MemesView),

    ('/template', handlers.TemplatesView),
    ('/template/(?P<template_id>[\d]+)/?', handlers.TemplateView),

    ('/meme', handlers.MemesView),
    ('/meme/(?P<meme_id>[\d]+)/?', handlers.MemeView),
    ('/meme/(?P<meme_id>[\d]+)/delete/?', handlers.DeleteMeme),
    ('/meme/(?P<meme_id>[\d]+)/add_comment/?', handlers.AddMemeComment),

    ('/add_template', handlers.AddTemplate),
    ('/create_meme', handlers.CreateMeme),

    ('/image', handlers.Image),

    ('/rpc/list_templates', handlers.ListTemplates),
    ('/rpc/upload_meme', handlers.UploadMeme),
    ('/rpc/list_meme_comments/(?P<meme_id>[\d]+)/?', handlers.ListMemeComments),

    ('/admin/__update_schema', handlers.UpdateSchema),
    ('/admin/__fix_comment_counts', handlers.FixCommentCounts),

], debug=True)
