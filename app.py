from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
socketio = SocketIO(app)

current_texts = {}
connected_users = {}


def generate_random_id(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<area_id>")
def area(area_id):
    return render_template("area.html", area_id=area_id)


@app.route("/create_area", methods=["POST"])
def create_area():
    area_id = request.form.get("area_id")
    if not area_id:
        area_id = generate_random_id()
    return redirect(url_for("area", area_id=area_id))


@socketio.on("text_update")
def handle_text_update(data):
    area_id = data["area_id"]
    current_texts[area_id] = data["text"]
    socketio.emit(
        "update_text", {"area_id": area_id, "text": current_texts[area_id]}, to=None
    )


@socketio.on("connect")
def handle_connect():
    area_id = request.args.get("area_id")
    if area_id not in connected_users:
        connected_users[area_id] = 0
    connected_users[area_id] += 1
    if area_id in current_texts:
        emit("update_text", {"area_id": area_id, "text": current_texts[area_id]})


@socketio.on("disconnect")
def handle_disconnect():
    area_id = request.args.get("area_id")
    if area_id in connected_users:
        connected_users[area_id] -= 1
        if connected_users[area_id] <= 0:
            if area_id in current_texts:
                del current_texts[area_id]
            del connected_users[area_id]


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8004, allow_unsafe_werkzeug=True)
