# app.py
from flask import Flask, jsonify, request, session, abort
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from associations import attendee_events, attendee_favorites, artist_favorites, tour_events
from sqlalchemy_serializer import SerializerMixin  # Import SerializerMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey  # Add this line
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv  # Import load_dotenv
import os  # Import os
import re

load_dotenv()

db = SQLAlchemy()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Initialize the db with the app
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

attendee_events = Table('attendee_events', db.metadata,
    Column('attendee_id', Integer, ForeignKey('attendees.id'), primary_key=True),
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True)
)

attendee_favorites = Table(
    'attendee_favorites', db.metadata,
    Column('attendee_id', Integer, ForeignKey('attendees.id'), primary_key=True),
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True)
)
# Association table for artist and events
artist_events = Table('artist_events', db.Model.metadata,
    Column('artist_id', Integer, ForeignKey('artists.id'), primary_key=True),
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True)
)
# Association table for artist and attendees
artist_favorites = db.Table('artist_favorites',
    db.Column('attendee_id', db.Integer, db.ForeignKey('attendees.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
)
tour_events = db.Table('tour_events',
    db.Column('tour_id', db.Integer, db.ForeignKey('tours.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True)
)

# ------------------------Venue----------------------------------#
class Venue(db.Model, SerializerMixin):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    earnings = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # Added description column
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'organizer': self.organizer,
            'email': self.email,
            'earnings': self.earnings,
            'description': self.description,  # Include description in the dictionary
            'events': [{'id': event.id, 'name': event.name} for event in self.events] if self.events else []
        }
# Update the decorators to use @app.route() instead of app.get()
@app.get("/venues")
def index():
    return jsonify([
        { 
            "id": venue.id, 
            "name": venue.name, 
            "organizer": venue.organizer, 
            "email": venue.email, 
            "earnings": venue.earnings, 
            "description": venue.description  # Include description
        }
        for venue in Venue.query.all()
    ]), 200

@app.post("/venues")
def create_venue():
    data = request.get_json()
    try:
        # Create a new venue object
        new_venue = Venue(
            name=data['name'],
            organizer=data['organizer'],
            email=data['email'],
            earnings=data['earnings'],
            description=data.get('description')  # Get description, defaulting to None if not provided
        )
        # Add to the database
        db.session.add(new_venue)
        db.session.commit()

        # Return the newly added venue
        return jsonify(Venue.query.order_by(Venue.id.desc()).first().to_dict()), 201
    except Exception as exception:
        return jsonify({"error": str(exception)}), 400
    
@app.get("/venues/<int:id>")
def get_venue_by_id(id):
    venue = db.session.get(Venue, id)
    if venue:
        return jsonify(venue.to_dict()), 200
    else:
        return jsonify({"error":"Venue ID not Found"}), 404

@app.patch("/venues/<int:id>")
def update_venue(id):
    data = request.json
    venue = Venue.query.filter(Venue.id == id).first()
    if venue:
        try:
            for key in data:
                setattr(venue, key, data[key])
            db.session.add(venue)
            db.session.commit()
            return jsonify(venue.to_dict()), 200
        except Exception as exception:
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Venue ID not found"}), 404

@app.delete('/venues/<int:id>')
def delete_venue(id):
    venue = Venue.query.filter(Venue.id == id).first()
    if venue:
        try:
            # Delete all associated events first
            for event in venue.events:
                db.session.delete(event)

            # Now delete the venue
            db.session.delete(venue)
            db.session.commit()
            return jsonify({}), 204
        except Exception as exception:
            db.session.rollback()  # Rollback in case of error
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Venue ID not found."}), 404
@app.get("/venues/search")
def search_venues_by_name():
    venue_name = request.args.get('name')
    if venue_name:
        # Normalize the input: strip spaces and convert to lowercase
        venue_name_normalized = venue_name.strip().lower()
        
        # Use ilike for case-insensitive search and strip spaces on database values too
        venues = Venue.query.filter(Venue.name.ilike(f'%{venue_name_normalized}%')).all()
        
        if venues:
            return jsonify([venue.to_dict() for venue in venues]), 200
        else:
            return jsonify({"error": "No venues found with that name"}), 404
    return jsonify({"error": "Venue name not provided"}), 400
# ------------------------Events----------------------------------#
class Event(db.Model, SerializerMixin):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=True)
    event_type = db.Column(db.String(50), nullable=False)

    venue = db.relationship('Venue', backref='events')
    attendees = db.relationship('Attendee', secondary='attendee_events', back_populates='attended_events')
    favorited_by = db.relationship('Attendee', secondary='attendee_favorites', back_populates='favorite_events')
    artists = db.relationship('Artist', secondary='artist_events', back_populates='events')
    tours = db.relationship('Tour', secondary='tour_events', back_populates='events')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'description': self.description,
            'event_type': self.event_type,
            'venue': {'id': self.venue.id, 'name': self.venue.name},
            'attendees': [{'id': attendee.id, 'first_name': attendee.first_name} for attendee in self.attendees],
            'artists': [{'id': artist.id, 'name': artist.name} for artist in self.artists],  # Avoid deep references
        }
# GET all events
@app.get("/events")
def get_events():
    return jsonify([
        event.to_dict()
        for event in Event.query.all()
    ]), 200

# POST a new event with a venue
@app.post("/events")
def create_event():
    data = request.get_json()
    
    try:
        if 'venue_id' in data and data['venue_id'] is not None:
       
        # Verify if the venue exists
            venue = Venue.query.get(data['venue_id'])
        if not venue:
            return jsonify({"error": "Venue not found"}), 404
        
        # Check for duplicate event names
        existing_event = Event.query.filter(Event.name == data['name']).first()
        if existing_event:
            return jsonify({"error": "Event name must be unique."}), 400

        # Parse date and time to proper datetime format
        event_date = datetime.strptime(data['date'], '%Y-%m-%d')
        event_time = data['time']  # Assuming time remains a string (HH:MM format)

        # Create a new event object
        new_event = Event(
            name=data['name'],
            date=event_date,
            time=event_time,
            location=data['location'],
            description=data['description'],
            venue_id=data['venue_id'],
            event_type=data['event_type']  # Add this line
        )

        # Assign artists (if provided)
        if 'artist_ids' in data:
            artists = Artist.query.filter(Artist.id.in_(data['artist_ids'])).all()
            new_event.artists.extend(artists)  # Assuming the Event model has a relationship with Artist

        db.session.add(new_event)
        db.session.commit()

        return jsonify(new_event.to_dict()), 201
    except Exception as exception:
        return jsonify({"error": str(exception)}), 400
# GET a specific event by ID
@app.get("/events/<int:id>")
def get_event_by_id(id):
    event = db.session.get(Event, id)
    if event:
        return jsonify(event.to_dict()), 200
    else:
        return jsonify({"error": "Event ID not found"}), 404

@app.patch("/events/<int:id>")
def update_event(id):
    data = request.json
    event = Event.query.filter(Event.id == id).first()
    if event:
        try:
            # If date is provided, ensure it's in the correct format
            if 'date' in data:
                event.date = datetime.strptime(data['date'], '%Y-%m-%d')

            # Update the other fields
            for key in data:
                if key != "date":  # Skip date since we already handled it
                    setattr(event, key, data[key])
            
            # Update artists if artist_ids is provided
            if 'artist_ids' in data:
                # Clear existing artists
                event.artists.clear()
                # Fetch new artists based on provided artist_ids
                artists = Artist.query.filter(Artist.id.in_(data['artist_ids'])).all()
                event.artists.extend(artists)  # Add new artists

            db.session.commit()
            return jsonify(event.to_dict()), 200
        except Exception as exception:
            db.session.rollback()  # Rollback on error
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Event ID not found"}), 404
# DELETE an event by ID
@app.delete('/events/<int:id>')
def delete_event(id):
    event = Event.query.filter(Event.id == id).first()
    if event:
        try:
            db.session.delete(event)
            db.session.commit()
            return jsonify({}), 204
        except Exception as exception:
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Event ID not found"}), 404

@app.get("/events/search")
def search_events_by_name():
    search_term = request.args.get('searchTerm')  # Accept a single search parameter
    if search_term:
        # Normalize the input: strip spaces and convert to lowercase
        search_term_normalized = search_term.strip().lower()
        
        # Search for events by name, location, or event type
        events = Event.query.filter(
            (Event.name.ilike(f'%{search_term_normalized}%')) |
            (Event.location.ilike(f'%{search_term_normalized}%')) |
            (Event.event_type.ilike(f'%{search_term_normalized}%'))
        ).all()
        
        if events:
            return jsonify([event.to_dict() for event in events]), 200
        else:
            return jsonify({"error": "No events found with that search term"}), 404
    return jsonify({"error": "Search term not provided"}), 400


#---------------------------------ATTENDEES----------------------------#


class Attendee(db.Model, SerializerMixin):
    __tablename__ = "attendees"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    preferred_event_type = db.Column(db.String(100), nullable=True)
    favorite_event_types = db.Column(db.Text, nullable=True)
    social_media = db.Column(db.JSON, nullable=True)  # Change to JSON type
    
    favorite_artists = db.relationship('Artist', secondary='artist_favorites', back_populates='favorited_by')
    attended_events = db.relationship('Event', secondary='attendee_events', back_populates='attendees')
    favorite_events = db.relationship('Event', secondary='attendee_favorites', back_populates='favorited_by', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'favorite_events': [{'id': event.id, 'name': event.name} for event in self.favorite_events] if self.favorite_events else [],
            'favorite_event_types': (
            self.favorite_event_types.split(',') if isinstance(self.favorite_event_types, str) and self.favorite_event_types else []
            ),
            'favorite_artists': [{'id': artist.id, 'name': artist.name} for artist in self.favorite_artists] if self.favorite_artists else [],
            'social_media': self.social_media  # This will now return an array of objects
        }
# POST: Create new attendee with favorite events
@app.post("/attendees")
def create_attendee():
    data = request.get_json()

    # Check for existing attendee with the same email
    existing_attendee = Attendee.query.filter_by(email=data['email']).first()
    if existing_attendee:
        return jsonify({"error": "An attendee with this email already exists."}), 400

    try:
        # Create a new attendee object
        new_attendee = Attendee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            preferred_event_type=data.get('preferred_event_type'),  # Optional
            social_media=data.get('social_media')  # Get social media, defaulting to None if not provided
        )

        # Assign favorite events (if provided)
        if 'favorite_event_ids' in data:
            favorite_events = Event.query.filter(Event.id.in_(data['favorite_event_ids'])).all()
            new_attendee.favorite_events.extend(favorite_events)

        # Assign favorite event types (if provided)
        if 'favorite_event_types' in data:
            new_attendee.favorite_event_types = ','.join(data['favorite_event_types'])  # Store as a string

        # Assign favorite artists (if provided)
        if 'favorite_artist_ids' in data:
            favorite_artists = Artist.query.filter(Artist.id.in_(data['favorite_artist_ids'])).all()
            new_attendee.favorite_artists.extend(favorite_artists)

        db.session.add(new_attendee)
        db.session.commit()
        return jsonify(new_attendee.to_dict()), 201

    except Exception as exception:
        return jsonify({"error": str(exception)}), 400
# GET: Retrieve all attendees
@app.get("/attendees")
def get_all_attendees():
    try:
        attendees = Attendee.query.all()
        print(f"Number of attendees retrieved: {len(attendees)}")  # Log the count
        return jsonify([attendee.to_dict() for attendee in attendees]), 200
    except Exception as e:
        print("Error retrieving attendees:", str(e))
        return jsonify({"error": str(e)}), 500  



# PATCH: Update an attendee by ID
@app.patch("/attendees/<int:id>")
def update_attendee(id):
    data = request.json
    attendee = Attendee.query.filter(Attendee.id == id).first()
    
    if attendee:
        try:
            # Update direct fields
            for key in ['first_name', 'last_name', 'email', 'preferred_event_type', 'social_media']:
                if key in data:
                    setattr(attendee, key, data[key])

            # Update favorite events if provided
            if 'favorite_event_ids' in data:
                favorite_events = Event.query.filter(Event.id.in_(data['favorite_event_ids'])).all()
                attendee.favorite_events = favorite_events

            # Update favorite event types
            if 'favorite_event_types' in data:
                attendee.favorite_event_types = ','.join(data['favorite_event_types'])  # Convert list to string

            # Update favorite artists if provided
            if 'favorite_artist_ids' in data:
                favorite_artists = Artist.query.filter(Artist.id.in_(data['favorite_artist_ids'])).all()
                attendee.favorite_artists = favorite_artists

            db.session.commit()  # Commit the changes
            return jsonify(attendee.to_dict()), 200
        except Exception as exception:
            db.session.rollback()  # Rollback in case of error
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Attendee ID not found"}), 404
# DELETE: Remove an attendee by ID
@app.delete('/attendees/<int:id>')
def delete_attendee(id):
    attendee = Attendee.query.filter(Attendee.id == id).first()
    if attendee:
        try:
            db.session.delete(attendee)
            db.session.commit()
            return jsonify({}), 204
        except Exception as exception:
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Attendee ID not found"}), 404
    
@app.get("/attendees/search")
def search_attendees_by_name():
    attendee_name = request.args.get('name')
    if attendee_name:
        # Normalize the input: strip spaces and convert to lowercase
        attendee_name_normalized = attendee_name.strip().lower()
        
        # Search for attendees using ilike for case-insensitive matching
        attendees = Attendee.query.filter(
            Attendee.first_name.ilike(f'%{attendee_name_normalized}%') | 
            Attendee.last_name.ilike(f'%{attendee_name_normalized}%')
        ).all()
        
        # Instead of returning an error when no attendees are found, return an empty array
        return jsonify([attendee.to_dict() for attendee in attendees]), 200

    return jsonify({"error": "Attendee name not provided"}), 400
@app.get("/event-types")
def get_event_types():
    event_types = [
        "Drag Shows",
        "Live Lip Syncing",
        "Live Singing",
        "Comedy Nights",
        "Open Mic",
        "Karaoke",
        "DJ Sets",
        "Dance Performances",
        "Themed Parties",
        "Fundraising Events",
        "Talent Show",
        "Variety Show",
        "Music Festival",
        "Art Exhibitions",
        "Spoken Word Performances",
        "Fashion Shows"
    ]
    return jsonify(event_types), 200
def favorite_artist(attendee_id, artist_id):
    attendee = Attendee.query.get(attendee_id)
    artist = Artist.query.get(artist_id)

    if attendee and artist:
        attendee.favorite_artists.append(artist)
        db.session.commit()
        return jsonify({"message": "Artist favorited successfully"}), 201
    else:
        return jsonify({"error": "Attendee or Artist not found"}), 404



#--------------------------------------------------ARTISTS---------------------------------------------------#
class Artist(db.Model, SerializerMixin):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    background = db.Column(db.Text, nullable=True)
    songs = db.Column(db.Text, nullable=True)  # Store song names or video URLs

    # Link to events
    events = db.relationship('Event', secondary='artist_events', back_populates='artists')

    favorited_by = db.relationship('Attendee', secondary='artist_favorites', back_populates='favorite_artists')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'background': self.background,
            'events': [{'id': event.id, 'name': event.name} for event in self.events],
            'songs': self.songs.split(',') if self.songs else [],
            'favorited_by': [{'id': attendee.id, 'name': attendee.first_name} for attendee in self.favorited_by]  # Limit fields returned
        }
@app.get("/artists")
def get_all_artists():
    artists = Artist.query.all()
    return jsonify([artist.to_dict() for artist in artists]), 200

@app.get("/attendees/<int:id>")
def get_attendee_by_id(id):
    attendee = Attendee.query.get(id)  # Use get() for single ID lookup
    if attendee:
        return jsonify(attendee.to_dict()), 200
    else:
        return jsonify({"error": "Attendee ID not found"}), 404

@app.post("/artists")
def create_artist():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    try:
        # Create the new artist
        new_artist = Artist(
            name=data['name'],
            age=data.get('age'),  # Optional
            background=data.get('background'),  # Optional
            songs=data.get('songs', '')  # Store songs as a comma-separated string
        )

        # Handle event associations
        if 'event_ids' in data:
            # Assuming you have a many-to-many relationship table for artist_events
            for event_id in data['event_ids']:
                event = Event.query.get(event_id)
                if event:
                    new_artist.events.append(event)  # Link the artist to the event

        if 'favorited_by' in data:
            favorite_attendees = Attendee.query.filter(Attendee.id.in_(data['favorited_by'])).all()
            new_artist.favorited_by.extend(favorite_attendees)

        db.session.add(new_artist)
        db.session.commit()
        return jsonify(new_artist.to_dict()), 201
    except Exception as exception:
        return jsonify({"error": str(exception)}), 400
@app.patch("/artists/<int:id>")
def update_artist(id):
    data = request.json
    artist = Artist.query.filter(Artist.id == id).first()
    
    if artist:
        try:
            # Log the incoming data for debugging
            print("Incoming data for artist update:", data)

            for key in data:
                if key == 'event_ids':
                    # Handle event associations separately
                    artist.events.clear()  # Clear current events
                    for event_id in data['event_ids']:
                        event = Event.query.get(event_id)
                        if event:
                            artist.events.append(event)  # Re-link events
                else:
                    # Ensure we only set valid attributes
                    if hasattr(artist, key):
                        setattr(artist, key, data[key])  # Update artist fields
                    else:
                        print(f"Warning: {key} is not a valid attribute of Artist")
            
            db.session.commit()
            return jsonify(artist.to_dict()), 200
        except Exception as e:
            print("Error updating artist:", e)  # Log the error for debugging
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({"error": "Artist ID not found"}), 404

@app.delete("/artists/<int:id>")
def delete_artist(id):
    artist = Artist.query.filter(Artist.id == id).first()
    if artist:
        db.session.delete(artist)
        db.session.commit()
        return jsonify({}), 204
    else:
        return jsonify({"error": "Artist ID not found."}), 404

@app.get("/artists/search")
def search_artists_by_name():
    artist_name = request.args.get('name')
    if artist_name:
        # Normalize the input: strip spaces and convert to lowercase
        artist_name_normalized = artist_name.strip().lower()
        
        # Search for artists using ilike for case-insensitive matching
        artists = Artist.query.filter(
            Artist.name.ilike(f'%{artist_name_normalized}%')
        ).all()
        
        if artists:
            return jsonify([artist.to_dict() for artist in artists]), 200
        else:
            return jsonify({"error": "No artists found with that name"}), 404
    return jsonify({"error": "Artist name not provided"}), 400

@app.get("/artists/<int:id>")
def get_artist_by_id(id):
    artist = Artist.query.get(id)
    if artist:
        return jsonify(artist.to_dict()), 200
    else:
        return jsonify({"error": "Artist ID not found"}), 404

#-------------------------------#Tours--------------------#
class Tour(db.Model, SerializerMixin):
    __tablename__ = "tours"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('venues.id'))  # For venues
    created_by_artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))  # For artists
    social_media_handles = db.Column(db.String(255), nullable=True)

    events = relationship("Event", secondary=tour_events, back_populates='tours')

    def to_dict(self):
        # Fetch the creator names
        created_by_name = None
        if self.created_by_id:
            venue = Venue.query.get(self.created_by_id)
            created_by_name = venue.name if venue else None  # Get the venue name
        elif self.created_by_artist_id:
            artist = Artist.query.get(self.created_by_artist_id)
            created_by_name = artist.name if artist else None  # Get the artist name

        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.strftime('%m/%d/%Y'),
            'end_date': self.end_date.strftime('%m/%d/%Y'),
            'description': self.description,
            'created_by': created_by_name,  # Use the name instead of ID
            'social_media_handles': self.social_media_handles,
            'events': [{'name': event.name} for event in self.events] if self.events else [],
        }

@app.post("/tours")
def create_tour():
    data = request.get_json()

    try:
        # Ensure either created_by_id or created_by_artist_id is provided
        if not data.get('created_by_id') and not data.get('created_by_artist_id'):
            return jsonify({"error": "Either a venue or an artist must be specified as the creator."}), 400
        
        new_tour = Tour(
            name=data['name'],
            start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),  # Adjusted to parse YYYY-MM-DD
            end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
            description=data['description'],
            social_media_handles=data.get('social_media_handles'),  # Optional
            created_by_id=data.get('created_by_id'),  # Venue
            created_by_artist_id=data.get('created_by_artist_id')  # Artist
        )

        # Assign events to the tour
        if 'event_ids' in data:
            events = Event.query.filter(Event.id.in_(data['event_ids'])).all()
            new_tour.events.extend(events)

        db.session.add(new_tour)
        db.session.commit()

        return jsonify(new_tour.to_dict()), 201

    except Exception as exception:
        return jsonify({"error": str(exception)}), 400


@app.get("/tours")
def get_all_tours():
    try:
        tours = Tour.query.all()
        return jsonify([tour.to_dict() for tour in tours]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.patch("/tours/<int:id>")
def update_tour(id):
    data = request.get_json()
    tour = Tour.query.get_or_404(id)  # Automatically raises a 404 if not found
    
    try:
        # Update tour details
        for key in ['name', 'description', 'social_media_handles']:
            if key in data:
                setattr(tour, key, data[key])

        # Update dates if provided
        if 'start_date' in data:
            tour.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')  # Correct format
        if 'end_date' in data:
            tour.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')  # Correct format


        # Update created_by_id or created_by_artist_id
        if 'created_by_id' in data:
            tour.created_by_id = data['created_by_id']
        if 'created_by_artist_id' in data:
            tour.created_by_artist_id = data['created_by_artist_id']

        # Update event associations
        if 'event_ids' in data:
            events = Event.query.filter(Event.id.in_(data['event_ids'])).all()
            tour.events.clear()  # Clear existing associations
            tour.events.extend(events)  # Add new associations

        db.session.commit()
        return jsonify(tour.to_dict()), 200
    except Exception as exception:
        db.session.rollback()
        error_message = f"Error updating tour: {str(exception)}"
        print(error_message)  # Log the error
        return jsonify({"error": error_message}), 400

@app.delete("/tours/<int:id>")
def delete_tour(id):
    tour = Tour.query.get(id)
    if tour:
        try:
            db.session.delete(tour)
            db.session.commit()
            return jsonify({}), 204
        except Exception as exception:
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Tour ID not found"}), 404

@app.get("/tours/<int:id>")
def get_tour(id):
    tour = Tour.query.get(id)
    if tour:
        return jsonify(tour.to_dict()), 200
    else:
        return jsonify({"error": "Tour not found"}), 404
    
@app.get("/tours/search")
def search_tours_by_name():
    tour_name = request.args.get('name')
    if tour_name:
        # Normalize the input
        tour_name_normalized = tour_name.strip().lower()
        
        # Search for tours using ilike for case-insensitive matching
        tours = Tour.query.filter(Tour.name.ilike(f'%{tour_name_normalized}%')).all()
        
        return jsonify([tour.to_dict() for tour in tours]), 200
    return jsonify({"error": "Tour name not provided"}), 400
if __name__ == '__main__':
    app.run(port=5001, debug=True)

#-------------------------------#User--------------------#
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'artist', 'attendee', etc.
    profile_completed = db.Column(db.Boolean, default=False)  # New field

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, plaintext_password):
        self.password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

    def verify_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.password_hash, plaintext_password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'user_type': self.user_type,
            'profile_completed': self.profile_completed  # Include this in the response
        }
def validate_password(password):
    """
    Validates the password against the defined criteria.
    Raises a 400 Bad Request error with an appropriate message if validation fails.
    """
    if not password:
        abort(400, description="Password is required.")

    if len(password) < 8:
        abort(400, description="Password must be at least 8 characters long.")

    if len(password) > 128:
        abort(400, description="Password must not exceed 128 characters.")

    if not re.search(r'[A-Z]', password):
        abort(400, description="Password must contain at least one uppercase letter.")

    if not re.search(r'[a-z]', password):
        abort(400, description="Password must contain at least one lowercase letter.")

    if not re.search(r'\d', password):
        abort(400, description="Password must contain at least one digit.")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        abort(400, description="Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>).")

    
@app.post('/signup')
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    if not all([username, password, user_type]):
        return jsonify({'error': 'Username, password, and user type are required.'}), 400

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists.'}), 400
    
    try:
        validate_password(password)
    except Exception as e:
        # Flask's abort will handle sending the error response
        raise e

    new_user = User(
        username=username,
        user_type=user_type,
        profile_completed=False  # Set profile_completed to False initially
    )
    new_user.password = password  # This will hash the password

    db.session.add(new_user)
    db.session.commit()

    # Log the user in by setting the session
    session['user_id'] = new_user.id
    session['user_type'] = new_user.user_type

    return jsonify(new_user.to_dict()), 201


@app.post('/signin')
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': 'Username and password are required.'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.verify_password(password):
        # Log the user in by setting the session
        session['user_id'] = user.id
        session['user_type'] = user.user_type

        # Return user details including profile_completed status
        return jsonify({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'profile_completed': user.profile_completed
        }), 200
    else:
        return jsonify({'error': 'Invalid username or password.'}), 401


@app.post('/signout')
def signout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return jsonify({'message': 'Signed out successfully.'}), 200

@app.patch('/complete-profile/<int:user_id>')
def complete_profile(user_id):
    user = User.query.get(user_id)
    if user:
        user.profile_completed = True  # Mark profile as complete
        db.session.commit()
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": error.description}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": error.description}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": error.description}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "An unexpected error occurred."}), 500

    