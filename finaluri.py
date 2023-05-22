from flask import Flask, render_template, redirect, session, url_for
from flask import flash, request
app = Flask(__name__)
@app.route('/')
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run()
