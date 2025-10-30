from core import app

from threading import Timer

def delApp():
    app.restart()

time = Timer(3, delApp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
