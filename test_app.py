import unittest
from datetime import datetime
from flask_testing import TestCase

from app import app, db
from models.room import Room
from models.booking import Booking


# convert str to date
def convert_date(date):
    return datetime.strptime(date, "%Y-%m-%d")


class MyTest(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hotelbca.db"
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        # assert home page
        response = self.client.get("/")
        self.assert200(response)
        self.assert_template_used("index.html")

    def test_create_room(self):
        # create room
        response = self.client.post(
            "/room",
            json={
                "type": "Type Test",
                "availibility": True,
                "price_per_night": 15000,
            },
        )
        # assert room values
        self.assertStatus(response, 201)
        room = Room.query.first()
        self.assertEqual(room.type, "Type Test")

    def test_delete_room(self):
        # create room
        room = Room(type="Type Test", availibility=True, price_per_night=15000)
        db.session.add(room)
        db.session.commit()
        # assert room values
        response = self.client.delete(f"/room/{room.room_id}")
        self.assert200(response)
        self.assertIsNone(db.session.get(Room, room.room_id))

    def test_get_all_room(self):
        # create rooms
        room1 = Room(type="Type Test 1", availibility=True, price_per_night=15000)
        room2 = Room(type="Type Test 2", availibility=False, price_per_night=12000)
        db.session.add(room1)
        db.session.add(room2)
        db.session.commit()

        # assert room values
        response = self.client.get("/all-room")
        self.assert200(response)
        self.assertIn(b"Type Test 1", response.data)
        self.assertIn(b"Type Test 2", response.data)

    def test_create_booking(self):
        # create room for booking
        room_booking = Room(
            type="Booking Create Room", availibility=True, price_per_night=15000
        )
        db.session.add(room_booking)
        db.session.commit()

        # add booking
        response = self.client.post(
            "/booking",
            json={
                "customer_name": "John Doe",
                "room_id": room_booking.room_id,
                "check_in_date": "2023-09-09",
                "check_out_date": "2023-09-11",
            },
        )

        # get total price
        diff_days = 2
        total_price = diff_days * room_booking.price_per_night

        # assert status
        self.assertStatus(response, 201)
        booking = Booking.query.first()

        # assert booking values
        self.assertEqual(booking.customer_name, "John Doe")
        self.assertEqual(booking.total_price, total_price)

    def test_delete_booking(self):
        # create room for booking
        room_booking = Room(
            type="Booking Create Room", availibility=True, price_per_night=15000
        )
        db.session.add(room_booking)
        db.session.commit()

        # create booking
        booking = Booking(
            customer_name="Mary Jane",
            room_id=room_booking.room_id,
            check_in_date=convert_date("2023-09-09"),
            check_out_date=convert_date("2023-09-11"),
            total_price=45000,
        )
        db.session.add(booking)
        db.session.commit()

        response = self.client.delete(f"/booking/{booking.booking_id}")
        self.assert200(response)
        self.assertIsNone(db.session.get(Booking, booking.booking_id))

    def test_get_all_booking(self):
        # create room for booking
        room_booking = Room(
            type="Booking Create Room", availibility=True, price_per_night=15000
        )
        db.session.add(room_booking)

        # create bookings
        booking1 = Booking(
            customer_name="Mary Jane",
            room_id=room_booking.room_id,
            check_in_date=convert_date("2023-09-09"),
            check_out_date=convert_date("2023-09-11"),
            total_price=45000,
        )

        booking2 = Booking(
            customer_name="John Doe",
            room_id=room_booking.room_id,
            check_in_date=convert_date("2023-09-09"),
            check_out_date=convert_date("2023-09-11"),
            total_price=45000,
        )

        db.session.add(booking1)
        db.session.add(booking2)
        db.session.commit()

        # assert booking values
        response = self.client.get("/all-booking")
        self.assert200(response)
        self.assertIn(b"Mary Jane", response.data)
        self.assertIn(b"John Doe", response.data)


if __name__ == "__main__":
    unittest.main()
