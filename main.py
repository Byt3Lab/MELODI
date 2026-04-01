#!/usr/bin/env python3
from core import Application as Melodi

app = Melodi()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    app = app.get_server()