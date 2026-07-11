from flask import Flask, render_template
from livereload import Server

app = Flask(__name__)
app.debug = True
@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    server = Server(app)
    server.serve(host="0.0.0.0", port=80)
