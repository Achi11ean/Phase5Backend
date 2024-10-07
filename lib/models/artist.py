from .. import CURSOR, CONN
from .song import Song  # Import the Song model
from .event import Event
from .attendee import Attendee

class Artist:
    all = {}

    def __init__(self, name, hometown, love_for_music, future_goals, social_media, email, id=None):
        self.id = id  # Initialize the artist's id (will be assigned when saved to the database)
        self.name = name
        self.hometown = hometown
        self.love_for_music = love_for_music
        self.future_goals = future_goals
        self.social_media = social_media
        self.email = email
        self.events = []  # A list to store events associated with the artist

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        # Validate the email format
        if isinstance(email, str) and len(email.strip()) > 0:
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError("Email must contain '@' and a '.' after '@'.")
            self._email = email
        else:
            raise ValueError("Email must be a non-empty string.")

    def __repr__(self):
        return (f"<Artist {self.id}: {self.name}, Hometown: {self.hometown}, "
                f"Love for Music: {self.love_for_music}, Future Goals: {self.future_goals}, "
                f"Social Media: {self.social_media}, Email: {self.email}>")  # Include email in representation

    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY,
                name TEXT,
                hometown TEXT,
                love_for_music TEXT,
                future_goals TEXT,
                social_media TEXT,
                email TEXT  -- Add the email column
            )
        ''')
        # Create a junction table for the many-to-many relationship between artists and events
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS artist_events (
                artist_id INTEGER,
                event_id INTEGER,
                FOREIGN KEY (artist_id) REFERENCES artists(id),
                FOREIGN KEY (event_id) REFERENCES events(id),
                PRIMARY KEY (artist_id, event_id)
            )
        ''')
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute('DROP TABLE IF EXISTS artist_events')
        CURSOR.execute('DROP TABLE IF EXISTS artists')
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO artists (name, hometown, love_for_music, future_goals, social_media, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.name, self.hometown, self.love_for_music, self.future_goals, self.social_media, self.email))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE artists
                SET name = ?, hometown = ?, love_for_music = ?, future_goals = ?, social_media = ?, email = ?
                WHERE id = ?
            ''', (self.name, self.hometown, self.love_for_music, self.future_goals, self.social_media, self.email, self.id))
            CONN.commit()

    def delete(self):
        if self.id is not None:
            CURSOR.execute('DELETE FROM artists WHERE id = ?', (self.id,))
            CURSOR.execute('DELETE FROM artist_events WHERE artist_id = ?', (self.id,))  # Remove artist-event links
            CONN.commit()
            if self.id in type(self).all:
                del type(self).all[self.id]
            self.id = None
        else:
            raise ValueError("Artist does not exist in the database")

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute('SELECT * FROM artists').fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, artist_id):
        row = CURSOR.execute('SELECT * FROM artists WHERE id = ?', (artist_id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def instance_from_db(cls, row):
        artist_id = row[0]
        if artist_id in cls.all:
            return cls.all[artist_id]
        artist = cls(id=row[0], name=row[1], hometown=row[2], love_for_music=row[3], 
                     future_goals=row[4], social_media=row[5], email=row[6])  # Include email here
        cls.all[artist.id] = artist
        return artist

    # Add the relationship to Songs
    def get_songs(self):
        rows = CURSOR.execute('SELECT * FROM songs WHERE artist_id = ?', (self.id,)).fetchall()
        return [Song.instance_from_db(row) for row in rows]

    def add_song(self, title, genre, release_date):
        # Create a new song linked to this artist
        song = Song.create(title, genre, release_date, artist_id=self.id)
        return song

    def remove_song(self, song_id):
        # Remove a song linked to this artist by song ID
        song = Song.find_by_id(song_id)
        if song and song.artist_id == self.id:
            song.delete()
        else:
            raise ValueError("Song not found or does not belong to this artist")

    @classmethod
    def create(cls, name, hometown, love_for_music, future_goals, social_media, email):
        # Create a new artist instance without an id initially
        artist = cls(name, hometown, love_for_music, future_goals, social_media, email)
        artist.save()  # Save the artist to assign an id
        return artist

    # Event management for Artist

    def add_event(self, event):
        # Add the event to the artist's list of events and link it in the DB
        self.events.append(event)
        CURSOR.execute('''
            INSERT INTO artist_events (artist_id, event_id)
            VALUES (?, ?)
        ''', (self.id, event.id))
        CONN.commit()

    def get_events(self):
        # Fetch events associated with this artist from the DB
        rows = CURSOR.execute('''
            SELECT e.* FROM events e
            JOIN artist_events ae ON e.id = ae.event_id
            WHERE ae.artist_id = ?
        ''', (self.id,)).fetchall()
        return [Event.instance_from_db(row) for row in rows]

    def get_favorite_by_attendees(self):
        # Return attendees who have this artist in their `favorite_artists` list
        attendees_favoriting_this_artist = []
        for attendee in Attendee.get_all():
            if self in attendee.favorite_artists:
                attendees_favoriting_this_artist.append(attendee)
        return attendees_favoriting_this_artist