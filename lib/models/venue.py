from .. import CURSOR, CONN

class Venue: 
    all = {}

    def __init__(self, name, organizer, earnings, id=None):
        self.id = id
        self.name = name
        self.organizer = organizer
        self.earnings = earnings
        
    def __repr__(self):
        return f"<Venue {self.id}: {self.name}, Organizer: {self.organizer}, Earnings: {self.earnings}>"
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        if isinstance(name, str) and len(name.strip()) > 0:
            self._name = name
        else:
            raise ValueError("Must be a string longer than 0 characters")
    @property
    def organizer(self):
        return self._organizer
    @organizer.setter
    def organizer(self, organizer):
        if isinstance(organizer, str) and len(organizer.strip()) > 0:
            self._organizer = organizer
        else: 
            raise ValueError("Must be a string longer than 0 characters")
    @property
    def earnings(self):
        return self._earnings
    @earnings.setter
    def earnings(self, earnings):
        if isinstance(earnings, str) and len(earnings.strip()) > 0:
            self._earnings = earnings
        else:
            raise ValueError("Earnings must be a non-empty string.")
    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS venues (
                id INTEGER PRIMARY KEY,
                name TEXT,
                organizer TEXT,
                earnings TEXT
            )
        ''')
        CONN.commit()
    
    @classmethod
    def drop_table(cls):
        CURSOR.execute('DROP TABLE IF EXISTS venues')
        CONN.commit()

    def save(self):
        if self.id == None:
            CURSOR.execute('''
                INSERT INTO venues (name, organizer, earnings)
                VALUES (?, ?, ?)
            ''', (self.name, self.organizer, self.earnings))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE venues
                SET name = ?, organizer = ?, earnings = ?
                WHERE id = ? 
            ''', (self.name, self.organizer, self.earnings, self.id))
            CONN.commit()

    @classmethod
    def create(cls, name, organizer, earnings):
        venue = cls(name, organizer, earnings)
        venue.save()
        return venue
    
    def delete(self):
        if self.id is not None:
            CURSOR.execute('DELETE FROM venues WHERE id = ?', (self.id,))
            CONN.commit()
            if self.id in type(self).all:
                del type(self).all[self.id]
            self.id = None
        else:
            raise ValueError("venue does not exist in the data base")

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute('SELECT * FROM venues').fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, venue_id):
        row = CURSOR.execute('SELECT * FROM venues WHERE id = ?', (venue_id,)).fetchone()
        if row: 
            return cls.instance_from_db(row)
        return None

    @classmethod
    def instance_from_db(cls, row):
        venue_id = row[0]
        if venue_id in cls.all:
            return cls.all[venue_id]
        venue = cls(id=row[0], name=row[1], organizer=row[2], earnings=row[3])
        cls.all[venue.id] = venue
        return venue

    @classmethod 
    def find_events_by_venue_id(cls, venue_id):
        from .event import Event
        events = CURSOR.execute('SELECT * FROM events WHERE venue_id =?', (venue_id,)).fetchall()
        return [Event.instance_from_db(event) for event in events] if events else []

 