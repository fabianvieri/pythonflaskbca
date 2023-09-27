from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    Float,
    Date,
    ForeignKey,
    MetaData,
    Table,
)

from decouple import config

MYSQL_URL = config("MYSQL_URL")

DATABASE_URI = f"mysql://{MYSQL_URL}"
engine = create_engine(DATABASE_URI, echo=True)
metadata = MetaData()

room = Table(
    "room",
    metadata,
    Column("room_id", Integer, primary_key=True),
    Column("type", String),
    Column("price_per_night", Float),
    Column("availibility", Boolean),
)

booking = Table(
    "booking",
    metadata,
    Column("booking_id", Integer, primary_key=True),
    Column("room_id", Integer, ForeignKey("room.room_id")),
    Column("customer_name", String),
    Column("check_in_date", Date),
    Column("check_out_date", Date),
    Column("total_price", Float),
)

metadata.create_all(engine)

print("Database hotelbca.db dan table booking dan room telah berhasil dibuat!")
