# main.py
import uvicorn
from flask import Flask
from routes import main_routes
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)
app.debug = False
asgi_app = WsgiToAsgi(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

app.register_blueprint(main_routes)

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
