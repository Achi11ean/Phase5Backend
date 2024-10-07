from lib.models.event import Event
from lib.models.attendee import Attendee
from lib.models.venue import Venue
from lib.models.tour import Tour
from lib.models.artist import Artist  # Import the Artist model
from lib.models.song import Song
from lib import commit_and_close
from lib import CURSOR, CONN

def enable_foreign_keys():
    CURSOR.execute("PRAGMA foreign_keys = ON;")
    CONN.commit()

def setup_database():
    # Ensure all necessary tables are created
    Attendee.create_table()
    Event.create_table()
    Venue.create_table()
    Tour.create_table()
    Artist.create_table()  # Ensure Artist table is created
    Song.create_table()  # Add Song table here


if __name__ == "__main__":
    setup_database()
    print("Database setup has been completed!")
    commit_and_close()