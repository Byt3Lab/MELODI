from core import Module
import asyncio

class MelodiDoc(Module):
    def load(self):
        def home():
            return self.router.render_template("index.html")
        
        # self.app.home_page_manager.register_home_page("melodi_doc", home)

        @self.router.add_route("/docs", methods=["GET"])
        async def index():
            async def a():
                await asyncio.sleep(5)
                print(1)

            async def b():
                print(2)

            tasks = [a(), b()]
            ts=[]

            for t in tasks:
                ts.append(asyncio.create_task(t))
            
            for t in ts:
                await t
            # await asyncio.gather(a(),b())

            return self.router.render_template("index.html")
            
        super().load()

module = MelodiDoc(
    name="melodi doc" , router_name="melodi_doc", version="0.1"
)