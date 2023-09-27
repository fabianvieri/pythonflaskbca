import os
from flask import Blueprint
from flask import jsonify, request, render_template
from flasgger import swag_from

from extensions import db
from models.room import Room

bp = Blueprint("room", __name__)

basedir = os.path.abspath(os.path.dirname(__file__))
swagger_dir = os.path.join(basedir, "..", "swagger_docs")


# save room to db
def save_room(type, price_per_night, availibility):
    new_room = Room(
        type=type,
        price_per_night=price_per_night,
        availibility=availibility,
    )
    db.session.add(new_room)
    db.session.commit()


# convert room model to list
def get_all_room_array():
    room_list = []
    rooms = Room.query.all()
    for room in rooms:
        room_data = {
            "room_id": room.room_id,
            "type": room.type,
            "price_per_night": room.price_per_night,
            "availibility": room.availibility,
        }
        room_list.append(room_data)
    return room_list


# create room
@bp.route("/room", methods=["POST"])
@swag_from(os.path.join(swagger_dir, "create_room.yaml"))
def create_room():
    try:
        # get data
        data = request.json
        type = data["type"]
        price_per_night = data["price_per_night"]
        availibility = data["availibility"]

        # save to db
        save_room(type, price_per_night, availibility)
        return jsonify({"message": "Room was successfully created"}), 201
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# get all rooms
@bp.route("/all-room", methods=["GET"])
@swag_from(os.path.join(swagger_dir, "get_all_room.yaml"))
def room_list():
    try:
        room_list = get_all_room_array()
        return jsonify(room_list), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# get room
@bp.route("/room/<int:room_id>", methods=["GET"])
@swag_from(os.path.join(swagger_dir, "get_room.yaml"))
def get_room(room_id):
    try:
        room = db.session.get(Room, room_id)
        # check room
        if not room:
            return jsonify({"message": "Room is not found"}), 404

        # convert to dict
        room_data = {
            "room_id": room.room_id,
            "type": room.type,
            "price_per_night": room.price_per_night,
            "availibility": room.availibility,
        }

        return jsonify(room_data), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# update room
@bp.route("/room/<int:room_id>", methods=["PUT"])
@swag_from(os.path.join(swagger_dir, "update_room.yaml"))
def update_room(room_id):
    try:
        room = db.session.get(Room, room_id)
        # check room
        if not room:
            return jsonify({"message": "Room is not found"}), 404

        data = request.json
        type = data["type"]
        price_per_night = data["price_per_night"]
        availibility = data["availibility"]

        availibility = 1 if availibility == "1" else 0

        room.type = type
        room.price_per_night = price_per_night
        room.availibility = availibility
        db.session.commit()
        return jsonify({"message": "Room was successfully updated"}), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# delete room
@bp.route("/room/<int:room_id>", methods=["DELETE"])
@swag_from(os.path.join(swagger_dir, "delete_room.yaml"))
def delete_room(room_id):
    try:
        room = db.session.get(Room, room_id)
        # check room
        if not room:
            return jsonify({"message": "Room is not found"}), 404

        db.session.delete(room)
        db.session.commit()
        return jsonify({"message": "Room was successfully deleted"}), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# get all rooms UI
@bp.route("/room-list", methods=["GET"])
def room_list_ui():
    try:
        room_list = get_all_room_array()
        return render_template("roomlist.html", rooms=room_list)
    except Exception as e:
        return render_template("error.html", pesan=f"There is unknown error {str(e)}")


# create room UI
@bp.route("/create-room", methods=["GET", "POST"])
def create_room_ui():
    try:
        if request.method == "POST":
            type = request.form.get("type")
            price_per_night = request.form.get("price_per_night")
            availibility = True

            # check input fields
            if not type or not price_per_night or not availibility:
                return render_template(
                    "createroom.html", error="Please fill all fields"
                )

            # save to db
            save_room(type, price_per_night, availibility)
            return render_template(
                "success.html", pesan="Room was successfully created"
            )

        return render_template("createroom.html")
    except Exception as e:
        return render_template("error.html", pesan=f"There is unknown error {str(e)}")
