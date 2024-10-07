from .. import CURSOR, CONN

class Attendee:
    # This class represents an Attendee and manages DB interactions for the attendees table.
    all = {}

    # Initialize an Attendee object with name, email, and an optional id.
    # If the object is new, id is None and is automatically generated when saving to the DB.
    def __init__(self, name, email, id=None):
        self.id = id
        self.name = name
        self.email = email
        self.favorite_artists = []  # List to store favorite artists
    
    # String representation of the Attendee object.
    def __repr__(self):
        return f"<Attendee {self.id}: {self.name}, {self.email}>"

    # Property methods for name and email, with validation.
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        if isinstance(name, str) and len(name.strip()) > 0:
            self._name = name
        else: 
            raise ValueError("Name must be a string longer than 0 characters.")
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        if "@" in email and "." in email:
            self._email = email
        else:
            raise ValueError("Please enter a valid email.")

    # Create the `attendees` and `attendee_events` tables in the database (if they don't exist).
    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS attendees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS attendee_events (
                attendee_id INTEGER,
                event_id INTEGER,
                FOREIGN KEY (attendee_id) REFERENCES attendees(id) ON DELETE CASCADE,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                PRIMARY KEY (attendee_id, event_id)
            )
        ''')
        CONN.commit()

    @classmethod
    def drop_table(cls):
        # Drop the attendees table from the database, useful during testing to reset the DB.
        CURSOR.execute('DROP TABLE IF EXISTS attendees')
        CONN.commit()

    def save(self):
        # Save the attendee object to the DB. If the attendee is new, it will be inserted into the table.
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO attendees(name, email)
                VALUES (?, ?)
            ''', (self.name, self.email))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE attendees
                SET name = ?, email = ?
                WHERE id = ?
            ''', (self.name, self.email, self.id))
            CONN.commit()
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, email):
        # Factory method to create a new attendee object and save it to the DB.
        attendee = cls(name, email)
        attendee.save()
        return attendee

    def delete(self):
        # Delete the attendee object from the DB and from the in-memory dictionary.
        if self.id is not None:
            CURSOR.execute('DELETE FROM attendees WHERE id= ?', (self.id,))
            CONN.commit()
            del type(self).all[self.id]
            self.id = None
        else:
            raise ValueError("Attendee does not exist in the database")

    @classmethod
    def get_all(cls):
        # Fetch all attendee records from the DB and return them as a list of attendee objects.
        rows = CURSOR.execute("SELECT * FROM attendees").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, attendee_id):
        # Find an attendee by their unique ID. If found, return the attendee object; otherwise, return None.
        row = CURSOR.execute("SELECT * FROM attendees WHERE id = ?", (attendee_id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def find_by_event_id(cls, event_id):
        # This method will retrieve attendees by event_id from the attendee_events association table.
        rows = CURSOR.execute('''
            SELECT attendees.* FROM attendees
            JOIN attendee_events ON attendees.id = attendee_events.attendee_id
            WHERE attendee_events.event_id = ?
        ''', (event_id,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def instance_from_db(cls, row):
        # Return an attendee object initialized from a DB row.
        attendee_id = row[0]
        if attendee_id in cls.all:
            return cls.all[attendee_id]
        attendee = cls(id=row[0], name=row[1], email=row[2])
        cls.all[attendee.id] = attendee
        return attendee

    def add_to_event(self, event_id):
        # Check if the attendee is already associated with the event.
        existing_record = CURSOR.execute('''
            SELECT * FROM attendee_events 
            WHERE attendee_id = ? AND event_id = ?
        ''', (self.id, event_id)).fetchone()
        if existing_record:
            print(f"Warning: Attendee {self.name} is already added to event ID {event_id}.")
            return
        # If not already associated, insert into the attendee_events table.
        CURSOR.execute('''
            INSERT INTO attendee_events (attendee_id, event_id)
            VALUES (?, ?)
        ''', (self.id, event_id))
        CONN.commit()

    @classmethod
    def get_events_for_attendee(cls, attendee_id):
        # Fetch the events an attendee is associated with.
        rows = CURSOR.execute('''
            SELECT events.* FROM events
            JOIN attendee_events ON events.id = attendee_events.event_id
            WHERE attendee_events.attendee_id = ?
        ''', (attendee_id,)).fetchall()
        from .event import Event
        return [Event.instance_from_db(row) for row in rows]

    def add_favorite_artist(self, artist):
        # Add an artist to the attendee's favorite list (stored in memory, not DB).
        if artist not in self.favorite_artists:
            self.favorite_artists.append(artist)

    def get_favorite_artists(self):
        # Return the favorite artists of the attendee.
        return self.favorite_artists

    def remove_from_event(self, event_id):
        # Check if the attendee is associated with the event.
        existing_record = CURSOR.execute('''
            SELECT * FROM attendee_events 
            WHERE attendee_id = ? AND event_id = ?
        ''', (self.id, event_id)).fetchone()
        if not existing_record:
            raise ValueError(f"Attendee {self.name} is not associated with this event.")
        # If associated, remove the attendee from the event.
        CURSOR.execute('''
            DELETE FROM attendee_events 
            WHERE attendee_id = ? AND event_id = ?
        ''', (self.id, event_id))
        CONN.commit()