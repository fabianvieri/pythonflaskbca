import os
from datetime import datetime
from flask import Blueprint
from flask import jsonify, request, render_template
from flasgger import swag_from

from extensions import db
from models.room import Room
from models.booking import Booking

bp = Blueprint("booking", __name__)

basedir = os.path.abspath(os.path.dirname(__file__))
swagger_dir = os.path.join(basedir, "..", "swagger_docs")


# convert str to date
def convert_date(date):
    return datetime.strptime(date, "%Y-%m-%d")


# save booking data to db
def save_booking(room_id, customer_name, check_in_date, check_out_date, total_price):
    new_booking = Booking(
        room_id=room_id,
        customer_name=customer_name,
        check_in_date=convert_date(check_in_date),
        check_out_date=convert_date(check_out_date),
        total_price=total_price,
    )
    db.session.add(new_booking)
    db.session.commit()


# convert booking model to list
def get_all_booking_array():
    booking_list = []
    bookings = Booking.query.all()
    for book in bookings:
        book_data = {
            "booking_id": book.booking_id,
            "room_id": book.room_id,
            "customer_name": book.customer_name,
            "check_in_date": book.check_in_date,
            "check_out_date": book.check_out_date,
            "total_price": book.total_price,
        }
        booking_list.append(book_data)
    return booking_list


# check room booking availibility
def check_room(room_id):
    room = db.session.get(Room, room_id)
    if not room or not room.availibility:
        return False
    return room


# check date difference
def check_date(in_date, out_date):
    diff = convert_date(out_date) - convert_date(in_date)
    return diff.days


# create booking
@bp.route("/booking", methods=["POST"])
@swag_from(os.path.join(swagger_dir, "create_booking.yaml"))
def create_booking():
    try:
        data = request.json
        room_id = data["room_id"]
        customer_name = data["customer_name"]
        check_in_date = data["check_in_date"]
        check_out_date = data["check_out_date"]

        # check room availibility
        room = check_room(room_id)
        if not room:
            return jsonify({"message": "Room is not available"}), 404

        # check dates
        diff_days = check_date(check_in_date, check_out_date)
        if diff_days < 0:
            return jsonify({"message": "Invalid check in/out date"}), 400

        # get total price
        total_price = (
            room.price_per_night if diff_days == 0 else room.price_per_night * diff_days
        )

        # set room to unavailable
        room.availibility = 0

        # save to db
        save_booking(room_id, customer_name, check_in_date, check_out_date, total_price)
        return jsonify({"message": "Booking was successfully created"}), 201
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# get all booking
@bp.route("/all-booking", methods=["GET"])
@swag_from(os.path.join(swagger_dir, "get_all_booking.yaml"))
def booking_list():
    try:
        booking_list = get_all_booking_array()
        return jsonify(booking_list), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# get booking
@bp.route("/booking/<int:booking_id>", methods=["GET"])
@swag_from(os.path.join(swagger_dir, "get_booking.yaml"))
def get_booking(booking_id):
    try:
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return jsonify({"message": "Booking is not found"}), 404

        booking_data = {
            "booking_id": booking.booking_id,
            "room_id": booking.room_id,
            "customer_name": booking.customer_name,
            "check_in_date": booking.check_in_date,
            "check_out_date": booking.check_out_date,
            "total_price": booking.total_price,
        }

        return jsonify(booking_data), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# update booking
@bp.route("/booking/<int:booking_id>", methods=["PUT"])
@swag_from(os.path.join(swagger_dir, "update_booking.yaml"))
def update_booking(booking_id):
    try:
        # check booking
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return jsonify({"message": "Booking is not found"}), 404

        # get data
        data = request.json
        new_room_id = data["room_id"]
        customer_name = data["customer_name"]
        check_in_date = data["check_in_date"]
        check_out_date = data["check_out_date"]

        # check dates
        diff_days = check_date(check_in_date, check_out_date)
        if diff_days < 0:
            return jsonify({"message": "Invalid check in/out date"}), 400

        old_room_id = booking.room_id
        old_room_booking = db.session.get(Room, old_room_id)
        new_room_booking = db.session.get(Room, new_room_id)

        # set room booking availibility
        if str(old_room_id) != new_room_id:
            # check new room
            if not new_room_booking:
                return jsonify({"message": "Room is not available"}), 404

            # check room availibility
            if not new_room_booking.availibility:
                return jsonify({"message": "Room is not available"}), 404

            old_room_booking.availibility = 1
            new_room_booking.availibility = 0

        # get total price
        price_per_night = new_room_booking.price_per_night
        total_price = price_per_night if diff_days == 0 else price_per_night * diff_days

        # update booking
        booking.room_id = new_room_id
        booking.customer_name = customer_name
        booking.check_in_date = convert_date(check_in_date)
        booking.check_out_date = convert_date(check_out_date)
        booking.total_price = total_price

        db.session.commit()
        return jsonify({"message": "Booking was successfully updated"}), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# delete booking
@bp.route("/booking/<int:booking_id>", methods=["DELETE"])
@swag_from(os.path.join(swagger_dir, "delete_booking.yaml"))
def delete_booking(booking_id):
    try:
        booking = db.session.get(Booking, booking_id)
        # check booking
        if not booking:
            return jsonify({"message": "Booking is not found"}), 404

        # set room to available
        room_booking = db.session.get(Room, booking.room_id)
        if room_booking:
            room_booking.availibility = 1

        db.session.delete(booking)
        db.session.commit()
        return jsonify({"message": "Booking was successfully deleted"}), 200
    except Exception as e:
        return (
            jsonify({"message": f"There is unknown error: {str(e)}"}),
            500,
        )


# get all bookings ui
@bp.route("/booking-list", methods=["GET"])
def booking_list_ui():
    try:
        booking_list = get_all_booking_array()
        return render_template("bookinglist.html", bookings=booking_list)
    except Exception as e:
        return render_template("error.html", pesan=f"There is unknown error {str(e)}")


# create booking ui
@bp.route("/create-booking", methods=["GET", "POST"])
def create_booking_ui():
    try:
        rooms = Room.query.all()
        if request.method == "POST":
            room_id = request.form.get("room_id")
            customer_name = request.form.get("customer_name")
            check_in_date = request.form.get("check_in_date")
            check_out_date = request.form.get("check_out_date")

            # check input fields
            if (
                not room_id
                or not customer_name
                or not check_in_date
                or not check_out_date
            ):
                return render_template(
                    "createbooking.html", error="Please fill all fields", rooms=rooms
                )

            # check room availibility
            room = check_room(room_id)
            if not room:
                return render_template(
                    "createbooking.html", error="Room is not available", rooms=rooms
                )

            # check dates
            diff_days = check_date(check_in_date, check_out_date)
            if diff_days < 0:
                return render_template(
                    "createbooking.html", error="Invalid check in/out date", rooms=rooms
                )

            # get total price
            total_price = (
                room.price_per_night
                if diff_days == 0
                else room.price_per_night * diff_days
            )

            # set room to unavailable
            room.availibility = 0

            # save to db
            save_booking(
                room_id, customer_name, check_in_date, check_out_date, total_price
            )
            return render_template(
                "success.html", pesan="Booking was successfully created"
            )

        return render_template("createbooking.html", rooms=rooms)
    except Exception as e:
        return render_template("error.html", pesan=f"There is unknown error {str(e)}")
