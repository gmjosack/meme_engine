from hashlib import md5

import base64
import jinja2
import json
import os
import re
import webapp2

from google.appengine.api import users
from google.appengine.api import images


DATAURL_RE = re.compile("data:image/(png|jpeg);base64,(.*)$")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), "templates")
    ),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


def trim_data_url(data_url):
    image = DATAURL_RE.match(data_url).group(2)
    return base64.b64decode(image)


class MemeEngineRequestHandler(webapp2.RequestHandler):

    def get_current_user(self):
        return users.get_current_user()

    @property
    def email(self):
        return users.get_current_user().email()

    def render(self, template_name, **kwargs):
        _template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.write(_template.render(kwargs))

    def render_json(self, data):
        self.response.write(json.dumps({
            "data": data,
        }))


def get_size(width, height, max_width, max_height):
    ratio = min(
        float(max_width) / width,
        float(max_height) / height,
        1.0  # Don't allow an image to grow.
    )
    return int(width * ratio), int(height * ratio)


def resize(image_data, max_width, max_height):

    image = images.Image(image_data=image_data)
    # Access properties immediately to force exception to be raised
    # if not an image.

    width, height = get_size(image.width, image.height, max_width, max_height)
    image.resize(width=width, height=height)

    return image.execute_transforms(), width, height


def get_image(image_data):
    image, width, height = resize(image_data, 600, 600)
    return {
        "image": image,
        "image_hash": md5(image).hexdigest(),
        "width": width,
        "height": height,
    }


