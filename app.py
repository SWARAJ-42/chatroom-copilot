from flask import Flask, render_template, request, session, redirect, url_for, jsonify,  after_this_request
from flask_socketio import join_room, leave_room, send, SocketIO
from helper_functions import generate_unique_code, generate_answer
from flan_model import generate_summary

app = Flask(__name__)
app.config["SECRET_KEY"] = "foobarbas"
socketio = SocketIO(app)

rooms = {}

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)
        if join != False and not code:
            return render_template("home.html", error="Please enter the room code.", code=code, name=name)
        
        room = code 
        if create != False:
            room = generate_unique_code(4, rooms=rooms)
            rooms[room] = {"members": 0, "messages":[]}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))
    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@app.route('/summary', methods=['GET'])
def summarize():
    room = session.get("room")
    name = session.get("name")
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    dialogue = """"""
    for msg in rooms[room]["messages"]:
        dialogue += f"{msg['name']}: {msg['message']}"
    summary = generate_summary(dialogue)
    return jsonify({"summary":summary})

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    rooms[room]["messages"].append({"name":name, "message":"has entered the room"})
    send({"name":name, "message":"has entered the room"}, to=room)
    rooms[room]['members'] += 1
    print(f"{name} joined room {room}")

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    if "@Co-pilot" in data["data"]:
        data["data"] = data["data"].strip("@Co-pilot").strip(" ")
        response = str(generate_answer(data["data"]))
        content = {
            "name": "Co-pilot",
            "message": f"""<pre style="max-width: 350px;">{session.get('name')}: {data["data"]}
Response:
    {response}
</pre>
            """
        }
        if " --private " in data["data"]:
            data["data"] = data["data"].strip("--private").strip(" ")
            send(content)
        else:
            send(content, to=room)
            content = {
                "name": session.get("name"),
                "message": f"{session.get('name')} asked Co-pilot: {data['data']}"
            }
            rooms[room]["messages"].append(content)
    else:
        content = {
            "name": session.get("name"),
            "message": data["data"]
        }
        send(content, to=room)
        rooms[room]["messages"].append(content)

    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name":name, "message":"has left the room"}, to=room)
    print(f"{name} joined room {room}")


if __name__ == "__main__":
    socketio.run(app, debug=True)
