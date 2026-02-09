from flask import Flask, render_template, send_from_directory, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route("/")
def index():
    if session.pop('secret_clicked', True):
        return render_template("Sercet.html")
    else:
        return render_template("index.html", active="home")

@app.route("/secret")
def secret():
    session['secret_clicked'] = True
    return redirect(url_for('index'))


@app.route("/gameplay")
def services():
    return render_template("gameplay.html", active="services")

@app.route("/history")
def contact():
    return render_template("history.html", active="contact")

@app.route("/about")
def about():
    return render_template("about.html", active="about")

@app.route('/Content/<path:filename>')
def content_files(filename):
    return send_from_directory('Content', filename)

@app.route("/tips")
def tips():
    return render_template("tips.html", active="tips")

if __name__ == "__main__":
    app.run(debug=True)

    #this is a comment