import re

from google.appengine.ext import db
from google.appengine.api import images

from .util import MemeEngineRequestHandler, get_image
from .models import Template, Meme


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

        templates.run(limit=15)

        self.render_json({
            "templates": [template.as_dict() for template in templates]
        })


class TemplatesView(MemeEngineRequestHandler):
    def get(self):
        templates = Template.all().run()
        self.render("template.html", templates=templates)


class TemplateView(MemeEngineRequestHandler):
    def get(self, template_id):
        template = Template.get_by_id(int(template_id))
        self.render("template.html", template=template)


class CreateMeme(MemeEngineRequestHandler):
    def get(self):
        self.render("create_meme.html")


class Index(MemeEngineRequestHandler):
    def get(self):
        self.render("index.html", user=self.get_current_user())


class Image(MemeEngineRequestHandler):
    def get(self):

        try:
            image = db.get(self.request.get("key"))
        except db.BadKeyError:
            return self.error(404)

        if image is None:
            return self.error(404)

        self.response.headers["Content-Type"] = "image/png"
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
            Template.upload(name, self.email, template_image)
        except ValueError as err:
            return self.render("add_template.html", error=err)

        self.render("add_template.html")
