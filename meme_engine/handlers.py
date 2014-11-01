import json
import re

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from .util import MemeEngineRequestHandler, get_image, trim_data_url
from .models import Template, Meme, MemeComment, Vote


def normalize_name(name):
    if name is None:
        return
    name = name.lower()
    name = re.sub(r"\W+", "_", name)
    return name.strip("_")


class NgAppView(MemeEngineRequestHandler):
    def get(self):
        self.render("index.html")


class Image(MemeEngineRequestHandler):
    def get(self):

        self.response.headers["Content-Type"] = "image/png"
        self.response.headers["Cache-Control"] = "max-age=31556926"
        # These never change. Data taken from Last-Modified example in
        # rfc2616 and is otherwise arbitrary.
        self.response.headers["Last-Modified"] = "Tue, 15 Nov 1994 12:45:26 GMT"
        self.response.headers["Expires"] = "Mon, 23 Jan 2023 00:00:00 GMT"

        if "If-Modified-Since" in self.request.headers:
            return self.response.set_status(304)

        try:
            image = db.get(self.request.get("key"))
        except db.BadKeyError:
            return self.error(404)

        if image is None:
            return self.error(404)

        self.response.out.write(image.image)


# API Handlers


class TemplatesHandler(MemeEngineRequestHandler):
    def get(self):
        offset = int(self.request.get("offset", 0))
        limit = int(self.request.get("limit", 20))
        if limit > 20:
            limit = 20

        # Override limit and fetch all. This is used right now
        # for creating memes.
        get_all = bool(self.request.get("all", False))

        templates = Template.all()

        name = self.request.get("name")
        if name:
            name = normalize_name(name)
            templates = templates.filter("name >=", name).filter('name <', name + u'\ufffd')

        templates = templates.filter("enabled =", True)

        if get_all:
            templates = templates.order("name")
        else:
            templates = templates.order("-added").fetch(limit, offset)


        self.render_json({
            "templates": [template.as_dict() for template in templates],
            "offset": offset,
            "limit": limit,
        })

    def post(self):

        name = self.request.get("name")
        name = normalize_name(name)
        if not name:
            self.error(400)
            return self.render_json({
                "error": "Name is a required field",
            })

        try:
            template_image = get_image(self.request.get("template_file"))
        except images.Error as err:
            self.error(400)
            return self.render_json({
                "error": err,
            })

        try:
            template = Template.upload(name, self.email, template_image)
        except ValueError as err:
            self.error(400)
            return self.render_json({
                "error": ", ".join(err),
            })

        self.redirect("/template/%s" % template.key().id())


class TemplateHandler(MemeEngineRequestHandler):
    def get(self, template_id):
        template = Template.get_by_id(int(template_id))

        if template is None or not template.enabled:
            return self.error(404)

        self.render_json({
            "template": template.as_dict(),
        })


class MemesHandler(MemeEngineRequestHandler):
    def get(self):

        offset = int(self.request.get("offset", 0))
        limit = int(self.request.get("limit", 20))
        if limit > 20:
            limit = 20

        memes = Meme.all().filter("enabled = ", True).order("-added").fetch(limit, offset)

        self.render_json({
            "memes": [meme.as_dict(self.email) for meme in memes],
            "offset": offset,
            "limit": limit,
        })

    def post(self):


        request = json.loads(self.request.body)

        image_data = trim_data_url(request["image"])
        image = images.Image(image_data=image_data)

        template = db.get(request["template"]["key"])

        meme = Meme(
            top_text=request["texts"]["topText"],
            bottom_text=request["texts"]["bottomText"],
            template=template,
            author=self.email,
            width=image.width,
            height=image.height,
            image=image_data
        )
        meme.put()

        self.render_json({
            "id": meme.key().id(),
        })


class MemeHandler(MemeEngineRequestHandler):
    def get(self, meme_id):
        meme = Meme.get_by_id(int(meme_id))

        if meme is None or not meme.enabled:
            return self.error(404)

        self.render_json({
            "meme": meme.as_dict(),
            "show_delete": self.email == meme.author,
        })


class MemeCommentsHandler(MemeEngineRequestHandler):
    def get(self, meme_id):
        meme = Meme.get_by_id(int(meme_id))

        self.render_json({
            "comments": [comment.as_dict() for comment in meme.comments.order("added")]
        })

    def post(self, meme_id):

        meme = Meme.get_by_id(int(meme_id))

        comment = self.request.get("comment")
        if not comment:
            self.redirect("/meme/%s" % meme.key().id())


        comment = MemeComment(comment=comment, author=self.email, meme=meme)
        comment.put()
        meme.num_comments = meme.num_comments + 1
        meme.put()

        self.redirect("/meme/%s" % meme.key().id())


class MemeVoteHandler(MemeEngineRequestHandler):

    score_transition = {
        -1: {
            -1: (0, 0),
             0: (0, -1),
             1: (1, -1),
        },
        0: {
            -1: (0, 1),
             0: (0, 0),
             1: (1, 0),
        },
        1: {
            -1: (-1, 1),
             0: (-1, 0),
             1: (0, 0),
        },
    }

    def post(self, meme_id):
        request = json.loads(self.request.body)
        score = int(request.get("score"))

        meme_id = int(meme_id)

        if score not in (-1, 0, 1):
            return self.error(400)

        meme = Meme.get_by_id(meme_id)
        if meme is None:
            return self.error(404)

        key_name = "vote-%s-%s" % (meme_id, self.email)

        vote = Vote.get_or_insert(key_name)
        votes_up, votes_down = self.score_transition[vote.score][score]

        if any([votes_up, votes_down]):
            if votes_up:
                meme.votes_up += votes_up

            if votes_down:
                meme.votes_down += votes_down

            meme.put()

        vote.score = score
        vote.put()
        memcache.set(key_name, score)

        self.render_json({
            "votes_up": meme.votes_up,
            "votes_down": meme.votes_down,
        })


class MemeDeleteHandler(MemeEngineRequestHandler):
    def post(self, meme_id):
        meme = Meme.get_by_id(int(meme_id))

        if not meme or not meme.enabled:
            return self.error(404)

        if meme.author != self.email:
            return self.error(403)

        meme.enabled = False
        meme.put()

        self.redirect("/")


# Admin Handlers


class UpdateSchema(MemeEngineRequestHandler):
    def get(self):
        memes = Meme.all()
        for meme in memes:
            meme.put()

        templates = Template.all()
        for template in templates:
            template.put()

        meme_comments = MemeComment.all()
        for meme_comment in meme_comments:
            meme_comment.put()


class FixCommentCounts(MemeEngineRequestHandler):
    def get(self):
        memes = Meme.all()
        for meme in memes:
            meme.num_comments = meme.comments.count()
            meme.put()
