import datetime

from google.appengine.ext import db
from google.appengine.api import memcache

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

    enabled = db.BooleanProperty(default=True)

    @property
    def thumb_width(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[0]

    @property
    def thumb_height(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[1]

    def as_dict(self):
        return {
            "key": str(self.key()),
            "id": self.key().id(),
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
        return template


class Vote(db.Model):
    score = db.IntegerProperty(default=0)


class Meme(db.Model):
    top_text = db.StringProperty()
    bottom_text = db.StringProperty()

    template = db.ReferenceProperty(Template, collection_name="memes", required=True)

    author = db.StringProperty(required=True)

    width = db.IntegerProperty(required=True)
    height = db.IntegerProperty(required=True)
    image = db.BlobProperty(required=True)

    added = db.DateTimeProperty(required=True, auto_now_add=True)

    enabled = db.BooleanProperty(default=True)

    votes_up = db.IntegerProperty(default=0)
    votes_down = db.IntegerProperty(default=0)

    votes_avg = db.IntegerProperty(default=0)

    num_comments = db.IntegerProperty(default=0)

    @property
    def thumb_width(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[0]

    @property
    def thumb_height(self):
        return get_size(self.width, self.height, THUMB_WIDTH, THUMB_HEIGHT)[1]

    def get_vote_for_author(self, author):
        meme_id = self.key().id()
        key_name = "vote-%s-%s" % (meme_id, author)

        score = memcache.get(key_name)
        if score is not None:
            return score

        vote = Vote.get_by_key_name(key_name)
        if vote is None:
            memcache.set(key_name, 0)
            return 0

        memcache.set(key_name, vote.score)
        return vote.score


    def as_dict(self, author=None):
        ret = {
            "key": str(self.key()),
            "id": self.key().id(),

            "thumb_width": self.thumb_width,
            "thumb_height": self.thumb_height,
            "num_comments": self.num_comments,

            "votes_up": self.votes_up,
            "votes_down": self.votes_down,
        }

        if author:
            ret["score"] = self.get_vote_for_author(author)

        return ret


class MemeComment(db.Model):

    author = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)

    meme = db.ReferenceProperty(Meme, collection_name="comments", required=True)

    added = db.DateTimeProperty(required=True, auto_now_add=True)

    enabled = db.BooleanProperty(default=True)

    def as_dict(self):
        return {
            "author": self.author,
            "comment": self.comment,
            "added": str(self.added),
        }
