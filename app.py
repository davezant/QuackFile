# main.py
import uvicorn
from flask import Flask, render_template
from routes import main_routes
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)
app.debug = True
asgi_app = WsgiToAsgi(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

app.register_blueprint(main_routes)

@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", error=400,  msg="Bad Request.")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error=404, msg="Page not found.")


if __name__ == "__main__":
    
    
    if app.debug:
        from livereload import Server

        server = Server(app)

        server.watcher.ignore("*.pyc")
        
        server.watch("routes/*.py")
        server.watch("templates/*.html")
        server.watch("static/**/*.*")
        server.watch("app.py")
        
        server.serve(host="127.0.0.1", port=5000)
    else:
        
        uvicorn.run(
            "app:asgi_app",
            host="0.0.0.0",
            port=80,
            workers=4
        )
