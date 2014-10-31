import json
import re

from google.appengine.ext import db
from google.appengine.api import images

from .util import MemeEngineRequestHandler, get_image, trim_data_url
from .models import Template, Meme, MemeComment


def normalize_name(name):
    if name is None:
        return
    name = name.lower()
    name = re.sub(r"\W+", "_", name)
    return name.strip("_")


class ListTemplates(MemeEngineRequestHandler):
    def get(self):
        templates = Template.all()

        name = self.request.get("name")
        if name:
            name = normalize_name(name)
            templates.filter("name >=", name).filter('name <', name + u'\ufffd')

        self.render_json({
            "templates": [template.as_dict() for template in templates]
        })


class ListMemeComments(MemeEngineRequestHandler):
    def get(self, meme_id):
        meme = Meme.get_by_id(int(meme_id))

        self.render_json({
            "comments": [comment.as_dict() for comment in meme.comments.order("added")]
        })


class AddMemeComment(MemeEngineRequestHandler):

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


class UploadMeme(MemeEngineRequestHandler):
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


class TemplatesView(MemeEngineRequestHandler):
    def get(self):

        offset = int(self.request.get("offset", 0))
        limit = int(self.request.get("limit", 20))
        if limit > 20:
            limit = 20

        templates = Template.all().filter("enabled = ", True).order("-added").fetch(limit, offset)

        self.render("templates.html", templates=templates, args=self.request.GET, offset=offset, limit=limit)


class TemplateView(MemeEngineRequestHandler):
    def get(self, template_id):
        template = Template.get_by_id(int(template_id))

        if not template.enabled:
            return self.error(404)

        self.render("template.html", template=template)


class MemesView(MemeEngineRequestHandler):
    def get(self):

        offset = int(self.request.get("offset", 0))
        limit = int(self.request.get("limit", 20))
        if limit > 20:
            limit = 20

        memes = Meme.all().filter("enabled = ", True).order("-added").fetch(limit, offset)

        self.render("memes.html", memes=memes, args=self.request.GET, offset=offset, limit=limit)


class MemeView(MemeEngineRequestHandler):
    def get(self, meme_id):
        meme = Meme.get_by_id(int(meme_id))

        if not meme.enabled:
            return self.error(404)

        self.render("meme.html", meme=meme, author=self.email)


class DeleteMeme(MemeEngineRequestHandler):
    def get(self, meme_id):
        meme = Meme.get_by_id(int(meme_id))

        if not meme.enabled:
            return self.error(404)

        if meme.author != self.email:
            return self.error(403)

        self.render("delete-meme.html", meme=meme, author=self.email)

    def post(self, meme_id):
        print meme_id
        meme = Meme.get_by_id(int(meme_id))

        if not meme.enabled:
            return self.error(404)

        if meme.author != self.email:
            return self.error(403)

        meme.enabled = False
        meme.put()

        self.redirect("/")


class CreateMeme(MemeEngineRequestHandler):
    def get(self):
        self.render("create_meme.html")


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


class AddTemplate(MemeEngineRequestHandler):

    def get(self):
        self.render("add_template.html")


    def post(self):

        name = self.request.get("name")
        name = normalize_name(name)
        if not name:
            return self.render("add_template.html", error="Name is a required field")

        try:
            template_image = get_image(self.request.get("template_file"))
        except images.Error as err:
            return self.render("add_template.html", error=err)

        try:
            template = Template.upload(name, self.email, template_image)
        except ValueError as err:
            return self.render("add_template.html", error=err)

        self.redirect("/template/%s" % template.key().id())


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

