from core.module import ApplicationModule

class MelodiDocs(ApplicationModule):
    def load(self):
        super().load()

module = MelodiDocs(
    name="melodi docs", router_name="melodi_docs"
)