from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", active="home")

@app.route("/gameplay")
def services():
    return render_template("gameplay.html", active="services")

@app.route("/history")
def contact():
    return render_template("history.html", active="contact")

@app.route("/about")
def about():
    return render_template("about.html", active="about")

@app.route("/tips")
def tips():
    return render_template("tips.html", active="tips")

if __name__ == "__main__":
    app.run(debug=True)

    #this is a comment