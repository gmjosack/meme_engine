
from google.appengine.ext import db

from .util import get_size


THUMB_WIDTH = 400
THUMB_HEIGHT = 400


class Template(db.Model):
    name = db.StringProperty(required=True)

    author = db.StringProperty(required=True)

    width = db.IntegerProperty(required=True)
    height = db.IntegerProperty(required=True)
    image = db.BlobProperty(required=True)
    # Prevent the same image from being uploaded multiple times
    image_hash = db.StringProperty(required=True)

    added = db.DateTimeProperty(required=True, auto_now_add=True)

    @property
    def thumb_width(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[0]

    @property
    def thumb_height(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[1]

    def as_dict(self):
        return {
            "key": str(self.key()),
            "name": self.name,
            "author": self.author,
            "width": self.width,
            "height": self.height,
            "added": str(self.added),
            "thumb_width": self.thumb_width,
            "thumb_height": self.thumb_height,
        }

    @staticmethod
    def upload(name, author, template_image):

        template = Template.all().filter("name =", name).get()
        if template:
            raise ValueError("Name is not unique.")

        template = Template.all().filter(
            "image_hash =", template_image["image_hash"]
        ).get()
        if template:
            raise ValueError("Imagine is not unique.")

        template = Template(
            name=name,
            author=author,
            **template_image
        )
        template.put()


class Meme(db.Model):
    top_text = db.StringProperty()
    bottom_text = db.StringProperty()

    author = db.StringProperty(required=True)

    width = db.IntegerProperty(required=True)
    height = db.IntegerProperty(required=True)
    image = db.BlobProperty(required=True)

    added = db.DateTimeProperty(required=True, auto_now_add=True)

    @property
    def thumb_width(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[0]

    @property
    def thumb_height(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[1]
