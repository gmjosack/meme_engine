import webapp2

from . import handlers

application = webapp2.WSGIApplication([
    ("/", handlers.NgAppView),
    ("/image", handlers.Image),

    ("/api/template", handlers.TemplatesHandler),
    ("/api/template/(?P<template_id>[\d]+)", handlers.TemplateHandler),

    ("/api/meme", handlers.MemesHandler),
    ("/api/meme/(?P<meme_id>[\d]+)", handlers.MemeHandler),
    ("/api/meme/(?P<meme_id>[\d]+)/comments", handlers.MemeCommentsHandler),
    ("/api/meme/(?P<meme_id>[\d]+)/vote", handlers.MemeVoteHandler),
    ("/api/meme/(?P<meme_id>[\d]+)/delete", handlers.MemeDeleteHandler),

    ("/admin/__update_schema", handlers.UpdateSchema),
    ("/admin/__fix_comment_counts", handlers.FixCommentCounts),

    ("/.*", handlers.NgAppView),

], debug=True)
