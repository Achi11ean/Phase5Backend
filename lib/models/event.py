from .. import CURSOR, CONN  #import the cursor and connection objects from the database module
 

class Event:
    #dictionary to store all event objects in memory, mapped by their ID's
    all = {}
    #Constructor to initialize an event object with name, date, location description and optional ID
    def __init__(self, name, date, location, description, venue_id=None, id=None):
        self.id = id
        self.name = name
        self.date = date
        self.location = location
        self.description = description
        self.venue_id = venue_id
        self.artists = []  # List to hold associated artists
    
    #String representation of the Event object for easy debugging and display
    def __repr__(self):
        return f"<Event {self.id}: {self.name}, {self.date}, {self.location}, Venue: {self.venue_id}>"
    
    #property getter for the event's name
    @property
    def name(self):
        return self._name
    #Property setter for the event's name include's validation to ensure the name is a non-empty string
    @name.setter
    def name(self, name):
        if isinstance(name, str) and len(name.strip()) > 0:
            self._name = name
        else:
            raise ValueError(" Name Must be a string longer than 0 characters")
    
    #Property getter for the event's date.
    @property
    def date(self):
        return self._date
    #Property setter for the event's date including validation that it its a non-empty string
    @date.setter
    def date(self, date):
        if isinstance(date, str) and len(date.strip()) > 0:
            self._date = date
        else:
            raise ValueError("Date Must be a string longer than 0 characters")
    
    #Property getter for the event's location
    @property
    def location(self):
        return self._location 
    #Location setter for the event with validation that it is a non empty string
    @location.setter
    def location(self, location):
        if isinstance(location, str) and len(location.strip()) > 0:
            self._location = location
        else:
            raise ValueError("Must be a string longer than 0 characters")
    
    #Description Getter for the event's Description 
    @property
    def description(self):
        return self._description
    #Description setter for the event's description with validation that it is a non empty string.
    @description.setter
    def description(self, description):
        if isinstance(description, str) and len(description.strip()) > 0:
            self._description = description
        else:
            raise ValueError("Must be a string longer than 0 characters")

    #Class Method That creates the table in the database if it doesn't exist. auto-incrementing ID for the event, name of the event, date of the event, location of the event and description of the event
    #Then commit the changes to the database after executing the sql statement
    @classmethod
    def create_table(cls): 
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                name TEXT,
                date TEXT,
                location TEXT,
                description TEXT,
                venue_id INTEGER,
                tour_id INTEGER,
                FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE,
                FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
            )
        ''')
        CONN.commit()
    
    #Class method to drop the events table from the DB (useful for testing or resetting.)
    @classmethod
    def drop_table(cls):
        CURSOR.execute('DROP TABLE IF EXISTS events')
        CONN.commit()
    
    #method to save the current event to the DB , inserts if new, updates if it exists.
    #Insert new event into the DB and set the project's ID from the last inserted row or update an existing event in the DB
    #In the last line we are storing the event object in the in-memory dictionary for easy access.
    def save(self):
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO events (name, date, location, description, venue_id)
                VALUES(?, ?, ?, ?, ?)
            ''', (self.name, self.date, self.location, self.description, self.venue_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
        else:
            CURSOR.execute('''
                UPDATE events
                SET name = ?, date = ?, location = ?, description = ?, venue_id = ?
                WHERE id = ?
            ''', (self.name, self.date, self.location, self.description, self.venue_id, self.id,))
            CONN.commit()
        type(self).all[self.id] = self    
    #Method to delete the current event from the DB and remove it from memory
    #Delete the event from the DB based on it's own ID. Afterward reset the object's ID to None after deletion .
    def delete(self):
        if self.id is not None:
            CURSOR.execute('DELETE FROM events WHERE id = ?', (self.id,))
            CONN.commit()
            if self.id in type(self).all:
                del type(self).all[self.id]
            self.id = None
        else:
            raise ValueError("Event does not exist in the database")
    
    #Class method to retrieve all events from the DB and return them as event objects. 
    @classmethod
    def get_all(cls):
        rows = CURSOR.execute('SELECT * FROM events').fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    #class method to find an event by it's ID in the DB
    @classmethod
    def find_by_id(cls, event_id):
        row = CURSOR.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None
    
    #Helper method to create an event object from a database row.
    @classmethod
    def instance_from_db(cls, row):
        event_id = row[0] #event's Id From DB 
        if event_id in cls.all: #Check if the event is already loaded in memory to avoid duplication
            return cls.all[event_id]
        venue_id = row[5] if len(row) >5 else None
        #Create a new event object from the DB row and store it in the memory 
        event = cls(id=row[0], name=row[1], date=row[2], location=row[3], description=row[4], venue_id=venue_id)
        cls.all[event.id] = event
        return event
    
    #Class method to create a save a new event in the DB 
    @classmethod
    def create(cls, name, date, location, description, venue_id):
        event = cls(name, date, location, description, venue_id) #create an event object
        event.save() #save the event to the DB 
        return event #return the saved object

    def add_artist(self, artist):
        if artist not in self.artists:
            self.artists.append(artist)
        else:
            raise ValueError("Artist already assigned to this event.")

    def remove_artist(self, artist):
        if artist in self.artists:
            self.artists.remove(artist)
        else:
            raise ValueError("Artist not found in this event.")