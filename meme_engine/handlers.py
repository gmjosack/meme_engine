from .util import MemeEngineRequestHandler

class Index(MemeEngineRequestHandler):
    def get(self):
        self.render("index.html", user=self.get_current_user())
