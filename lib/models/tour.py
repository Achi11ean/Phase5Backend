from .. import CURSOR, CONN
from .event import Event  # Importing Event model

class Tour:
    all = {}

    def __init__(self, name, description, start_date, end_date, id=None):
        self.id = id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return f"<Tour {self.id}: {self.name}, Description: {self.description}, Start: {self.start_date}, End: {self.end_date}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS tours (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                start_date TEXT,
                end_date TEXT
            )
        ''')

        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS tour_events (
                tour_id INTEGER,
                event_id INTEGER,
                FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                PRIMARY KEY (tour_id, event_id)
            )
        ''')
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute('DROP TABLE IF EXISTS tours')
        CURSOR.execute('DROP TABLE IF EXISTS tour_events')  # Drop the association table too
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO tours (name, description, start_date, end_date)
                VALUES (?, ?, ?, ?)
            ''', (self.name, self.description, self.start_date, self.end_date))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE tours
                SET name = ?, description = ?, start_date = ?, end_date = ?
                WHERE id = ?
            ''', (self.name, self.description, self.start_date, self.end_date, self.id))
            CONN.commit()

    @classmethod
    def create(cls, name, description, start_date, end_date):
        tour = cls(name, description, start_date, end_date)
        tour.save()
        return tour

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute('SELECT * FROM tours').fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, tour_id):
        row = CURSOR.execute('SELECT * FROM tours WHERE id = ?', (tour_id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def instance_from_db(cls, row):
        tour_id = row[0]
        if tour_id in cls.all:
            return cls.all[tour_id]
        tour = cls(id=row[0], name=row[1], description=row[2], start_date=row[3], end_date=row[4])
        cls.all[tour.id] = tour
        return tour

    def add_event(self, event_id):
        """Assign an event to this tour"""
        existing_record = CURSOR.execute('''
            SELECT * FROM tour_events WHERE tour_id = ? AND event_id = ?
        ''', (self.id, event_id)).fetchone()

        if existing_record:
            raise ValueError(f"Event {event_id} is already assigned to this tour.")
        
        CURSOR.execute('''
            INSERT INTO tour_events (tour_id, event_id) 
            VALUES (?, ?)
        ''', (self.id, event_id))
        CONN.commit()

    def get_events(self):
        """Retrieve all events assigned to this tour"""
        rows = CURSOR.execute('''
            SELECT events.* FROM events
            JOIN tour_events ON events.id = tour_events.event_id
            WHERE tour_events.tour_id = ?
        ''', (self.id,)).fetchall()
        
        return [Event.instance_from_db(row) for row in rows]

    def delete(self):
        if self.id is not None:
            # Delete all associations with events first
            CURSOR.execute('DELETE FROM tour_events WHERE tour_id = ?', (self.id,))
            # Now delete the tour itself
            CURSOR.execute('DELETE FROM tours WHERE id = ?', (self.id,))
            CONN.commit()
            if self.id in type(self).all:
                del type(self).all[self.id]
            self.id = None
        else:
            raise ValueError("Tour does not exist in the database")

    def remove_event(self, event_id):
        """Remove an event from this tour"""
        existing_record = CURSOR.execute('''
            SELECT * FROM tour_events WHERE tour_id = ? AND event_id = ?
        ''', (self.id, event_id)).fetchone()

        if not existing_record:
            raise ValueError(f"Event {event_id} is not assigned to this tour.")
    
        CURSOR.execute('''
            DELETE FROM tour_events WHERE tour_id = ? AND event_id = ?
        ''', (self.id, event_id))
        CONN.commit()