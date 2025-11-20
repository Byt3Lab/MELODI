from core.module import ApplicationModule
import markdown
import os
from flask import abort, render_template

class MelodiDocs(ApplicationModule):
    def load(self):
        super().load()
        self.router.add_route("/docs/", methods=["GET"])(self.index)
        self.router.add_route("/docs/<path:page>", methods=["GET"])(self.show_page)

    def index(self):
        return self.show_page('index')

    def show_page(self, page):
        # Construct path to markdown file
        base_path = os.path.dirname(os.path.abspath(__file__))
        content_path = os.path.join(base_path, 'content', f'{page}.md')
        
        if not os.path.exists(content_path):
            abort(404)
            
        with open(content_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        html = markdown.markdown(text, extensions=['fenced_code', 'tables'])
        
        # Use self.router.render_template which handles the module prefix
        return self.router.render_template('page.html', content=html)

module = MelodiDocs(
    name="melodi docs", router_name="melodi_docs"
)