from flask import Flask, render_template, send_from_directory, session, redirect, url_for, send_file
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route("/")
def index():
    if session.pop('secret_clicked', False):
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


@app.route('/download')
def download_game():
    try:
        # Path to your game.exe in the static folder
        file_path = os.path.join(app.root_path, 'static', 'game.exe')
        return send_file(
            file_path,
            as_attachment=True,
            download_name='minecraft_game.exe'  # Name it will download as
        )
    except FileNotFoundError:
        return "Game file not found!", 404

if __name__ == "__main__":
    app.run(debug=True)

    #this is a comment