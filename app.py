# app.py
from flask import Flask, jsonify, request, session, abort
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
# from associations import attendee_events, attendee_favorites, artist_favorites, tour_events
from sqlalchemy_serializer import SerializerMixin  # Import SerializerMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey  # Add this line
from sqlalchemy.ext.associationproxy import association_proxy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv  # Import load_dotenv
import os  # Import os
import re

load_dotenv()

db = SQLAlchemy()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL') or 'sqlite:///local_database.db'
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///main.db'
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

# ------------------------AttendeeVenue----------------------------------#
class AttendeeVenue(db.Model):
    __tablename__ = 'attendee_venue'
    attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
    rating = db.Column(db.Integer)

    attendee = db.relationship('Attendee', back_populates='venues')
    venue = db.relationship('Venue', back_populates='attendees')

@app.post('/api/venues/<int:venue_id>/rate')
def rate_venue(venue_id):
    data = request.get_json()
    attendee_id = data.get('attendee_id')
    rating = data.get('rating')

    if not attendee_id or rating is None:
        return jsonify({'error': 'Attendee ID and rating are required.'}), 400

    attendee = Attendee.query.get(attendee_id)
    venue = Venue.query.get(venue_id)

    if not attendee or not venue:
        return jsonify({'error': 'Attendee or Venue not found.'}), 404

    # Check if the AttendeeVenue association already exists
    av = AttendeeVenue.query.filter_by(attendee_id=attendee_id, venue_id=venue_id).first()

    if not av:
        # Create a new association
        av = AttendeeVenue(attendee_id=attendee_id, venue_id=venue_id, rating=rating)
        db.session.add(av)

    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5.'}), 400

    else:
        # Update existing rating
        av.rating = rating

    db.session.commit()

    return jsonify({'message': 'Rating submitted successfully.'}), 200

@app.get('/api/venues/<int:venue_id>/ratings')
def get_venue_ratings(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        return jsonify({'error': 'Venue not found.'}), 404

    ratings = [
        {
            'attendee_id': av.attendee.id,
            'attendee_name': av.attendee.first_name + ' ' + av.attendee.last_name,
            'rating': av.rating
        } for av in venue.attendees
    ]

    return jsonify(ratings), 200

@app.get('/api/attendees/<int:attendee_id>/ratings')
def get_attendee_ratings(attendee_id):
    attendee = Attendee.query.get(attendee_id)
    if not attendee:
        return jsonify({'error': 'Attendee not found.'}), 404

    ratings = [
        {
            'venue_id': av.venue.id,
            'venue_name': av.venue.name,
            'rating': av.rating
        } for av in attendee.venues
    ]

    return jsonify(ratings), 200

@app.patch('/api/venues/<int:venue_id>/rate')
def update_venue_rating(venue_id):
    data = request.get_json()
    attendee_id = data.get('attendee_id')
    new_rating = data.get('rating')

    if not attendee_id or new_rating is None:
        return jsonify({'error': 'Attendee ID and new rating are required.'}), 400

    av = AttendeeVenue.query.filter_by(attendee_id=attendee_id, venue_id=venue_id).first()

    if not av:
        return jsonify({'error': 'Rating not found.'}), 404

    av.rating = new_rating
    db.session.commit()

    return jsonify({'message': 'Rating updated successfully.'}), 200

@app.delete('/api/venues/<int:venue_id>/rate')
def delete_venue_rating(venue_id):
    data = request.get_json()
    attendee_id = data.get('attendee_id')

    if not attendee_id:
        return jsonify({'error': 'Attendee ID is required.'}), 400

    av = AttendeeVenue.query.filter_by(attendee_id=attendee_id, venue_id=venue_id).first()

    if not av:
        return jsonify({'error': 'Rating not found.'}), 404

    db.session.delete(av)
    db.session.commit()

    return jsonify({'message': 'Rating deleted successfully.'}), 200



# ------------------------Venue----------------------------------#
class Venue(db.Model, SerializerMixin):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    earnings = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # Added description column
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_venue_created_by'), nullable=True)

    attendees = db.relationship('AttendeeVenue', back_populates='venue', cascade='all, delete-orphan')
    attendee_list = association_proxy('attendees', 'attendee')
    creator = db.relationship('User', back_populates='venues')

    @property
    def average_rating(self):
        ratings = [av.rating for av in self.attendees if av.rating is not None]
        if ratings:
            return round(sum(ratings) / len(ratings), 2)  # Rounded to 2 decimal places
        else:
            return None  # Or return 0 if you prefer
    
    def to_dict(self):
        print("Converting venue to dict:", self.name)  # Log venue name
        print("Creator:", self.creator)
        print("Events:", self.events)
        print("Attendees:", self.attendees)
        print("Debug - Creator type:", type(self.creator))
        print("Debug - Creator value:", self.creator)


        return {
            'id': self.id,
            'name': self.name,
            'organizer': self.organizer,
            'email': self.email,
            'earnings': self.earnings,
            'description': self.description,  # Include description in the dictionary
            'created_by': {'id': self.creator.id, 'username': self.creator.username} if self.creator else None,
            'events': [{'id': event.id, 'name': event.name} for event in self.events] if self.events else [],
            'attendees': [
                {
                    'attendee_id': av.attendee.id,
                    'first_name': av.attendee.first_name,
                    'rating': av.rating
                } for av in self.attendees
            ],
            'average_rating': self.average_rating  # Include average_rating here
        }
# Update the decorators to use @app.route() instead of app.get()
@app.get("/api/venues")
def index():
    venues = Venue.query.all()
    return jsonify([venue.to_dict() for venue in venues]), 200

@app.post("/api/venues")
def create_venue():
    data = request.get_json()
    user_id = session.get('user_id')  # Retrieve user_id from session

    try:
        # Create a new venue object
        new_venue = Venue(
            name=data['name'],
            organizer=data['organizer'],
            email=data['email'],
            earnings=data['earnings'],
            description=data.get('description'),  # Get description, defaulting to None if not provided
            created_by_id=user_id  # Track the creator
        )
        # Add to the database
        db.session.add(new_venue)
        db.session.commit()

        # Return the newly added venue
        return jsonify(Venue.query.order_by(Venue.id.desc()).first().to_dict()), 201
    except Exception as exception:
        return jsonify({"error": str(exception)}), 400
    
@app.get("/api/venues/<int:id>")
def get_venue_by_id(id):
    venue = db.session.get(Venue, id)
    if venue:
        return jsonify(venue.to_dict()), 200
    else:
        return jsonify({"error":"Venue ID not Found"}), 404

@app.patch("/api/venues/<int:id>")
def update_venue(id):
    user_id = session.get('user_id')

    # Retrieve the venue
    venue = Venue.query.get(id)
    if not venue:
        return jsonify({"error": "Venue ID not found"}), 404

    # Check if the user is an admin or the creator of the venue
    if not (is_admin_user(user_id) or venue.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    # Proceed with the update if authorized
    data = request.json
    try:
        for key, value in data.items():
            setattr(venue, key, value)  # Update each attribute
        db.session.commit()
        return jsonify(venue.to_dict()), 200

    except Exception as exception:
        db.session.rollback()
        return jsonify({"error": str(exception)}), 400
    
@app.delete('/api/venues/<int:id>')
def delete_venue(id):
    user_id = session.get('user_id')

    # Retrieve the venue
    venue = Venue.query.get(id)
    if not venue:
        return jsonify({"error": "Venue ID not found"}), 404

    # Check if the user is an admin or the creator of the venue
    if not (is_admin_user() or venue.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    # Proceed with deletion if authorized
    try:
        # Delete all associations with the venue
        AttendeeVenue.query.filter_by(venue_id=id).delete()

        # Delete all associated events first
        for event in venue.events:
            db.session.delete(event)

        # Now delete the venue itself
        db.session.delete(venue)
        db.session.commit()
        return jsonify({}), 204

    except Exception as exception:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": str(exception)}), 400


@app.get("/api/venues/search")
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
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # For creator tracking

    creator = db.relationship('User')  # Relationship to User model
    venue = db.relationship('Venue', backref='events')
    attendees = db.relationship('Attendee', secondary='attendee_events', back_populates='attended_events')
    favorited_by = db.relationship('Attendee', secondary='attendee_favorites', back_populates='favorite_events')
    artists = db.relationship('Artist', secondary='artist_events', back_populates='events')
    tours = db.relationship('Tour', secondary='tour_events', back_populates='events')

    def to_dict(self):
        print("Creator:", self.creator)

        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'description': self.description,
            'event_type': self.event_type,
            'created_by': {'id': self.creator.id, 'username': self.creator.username} if self.creator else None,
            'venue': {'id': self.venue.id, 'name': self.venue.name},
            'attendees': [{'id': attendee.id, 'first_name': attendee.first_name} for attendee in self.attendees],
            'artists': [{'id': artist.id, 'name': artist.name} for artist in self.artists],  # Avoid deep references
        }
# GET all events
@app.get("/api/events")
def get_events():
    return jsonify([
        event.to_dict()
        for event in Event.query.all()
    ]), 200

# POST a new event with a venue
@app.post("/api/events")
def create_event():
    data = request.get_json()
    user_id = session.get('user_id')

    
    try:
        # Optional venue check
        venue = None
        if 'venue_id' in data and data['venue_id'] is not None:
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

        # Create a new event object, setting venue_id to None if not provided
        new_event = Event(
            name=data['name'],
            date=event_date,
            time=event_time,
            location=data['location'],
            description=data['description'],
            venue_id=data.get('venue_id', None),  # Allow venue_id to be None
            event_type=data['event_type'],
            created_by_id=user_id  # Track the creator

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
@app.get("/api/events/<int:id>")
def get_event_by_id(id):
    event = db.session.get(Event, id)
    if event:
        return jsonify(event.to_dict()), 200
    else:
        return jsonify({"error": "Event ID not found"}), 404

@app.patch("/api/events/<int:id>")
def update_event(id):
    user_id = session.get('user_id')

    # if not (is_admin_user() or event.created_by_id == user_id):
    #     return jsonify({"error": "Unauthorized access"}), 403

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
@app.delete('/api/events/<int:id>')
def delete_event(id):
    user_id = session.get('user_id')

    # Retrieve the event first
    event = Event.query.get(id)
    if not event:
        return jsonify({"error": "Event ID not found"}), 404

    # Check if the user is an admin or the creator of the event
    if not (is_admin_user() or event.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    # Proceed with deletion if authorized
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({}), 204
    except Exception as exception:
        db.session.rollback()
        return jsonify({"error": str(exception)}), 400

@app.get("/api/events/search")
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
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator = db.relationship('User', backref='attendees_created')
    favorite_artists = db.relationship('Artist', secondary='artist_favorites', back_populates='favorited_by')
    attended_events = db.relationship('Event', secondary='attendee_events', back_populates='attendees')
    favorite_events = db.relationship('Event', secondary='attendee_favorites', back_populates='favorited_by', lazy='dynamic')
    venues = db.relationship('AttendeeVenue', back_populates='attendee', cascade='all, delete-orphan')
    venue_list = association_proxy('venues', 'venue')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'created_by': {
                'id': self.creator.id,
                'username': self.creator.username
            } if self.creator else None,
            'favorite_events': [{'id': event.id, 'name': event.name} for event in self.favorite_events] if self.favorite_events else [],
            'favorite_event_types': (
            self.favorite_event_types.split(',') if isinstance(self.favorite_event_types, str) and self.favorite_event_types else []
            ),
            'favorite_artists': [{'id': artist.id, 'name': artist.name} for artist in self.favorite_artists] if self.favorite_artists else [],
            'social_media': self.social_media,  # This will now return an array of objects
            'venues': [
                {
                    'venue_id': av.venue.id,
                    'name': av.venue.name,
                    'rating': av.rating
                } for av in self.venues
            ]
        }
# POST: Create new attendee with favorite events
@app.post("/api/attendees")
def create_attendee():
    data = request.get_json()
    user_id = session.get('user_id')

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
            social_media=data.get('social_media'),  # Get social media, defaulting to None if not provided
            created_by_id=user_id  # Track the creator

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
        
        if 'favorite_venues' in data:
            for venue_data in data['favorite_venues']:
                venue_id = venue_data['venue_id']
                rating = venue_data.get('rating')
                av = AttendeeVenue(attendee=new_attendee, venue_id=venue_id, rating=rating)
                db.session.add(av)

        db.session.add(new_attendee)
        db.session.commit()
        return jsonify(new_attendee.to_dict()), 201

    except Exception as exception:
        return jsonify({"error": str(exception)}), 400
# GET: Retrieve all attendees
@app.get("/api/attendees")
def get_all_attendees():
    try:
        attendees = Attendee.query.all()
        print(f"Number of attendees retrieved: {len(attendees)}")  # Log the count
        return jsonify([attendee.to_dict() for attendee in attendees]), 200
    except Exception as e:
        print("Error retrieving attendees:", str(e))
        return jsonify({"error": str(e)}), 500  



# PATCH: Update an attendee by ID
# PATCH: Update an attendee by ID
@app.patch("/api/attendees/<int:id>")
def update_attendee(id):
    user_id = session.get('user_id')

    # Retrieve the attendee
    attendee = Attendee.query.get(id)
    if not attendee:
        return jsonify({"error": "Attendee ID not found"}), 404

    # Check if the user is an admin or the creator of the attendee
    if not (is_admin_user() or attendee.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    # Proceed with the update if authorized
    data = request.json
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

        # Update favorite venues with ratings if provided
        if 'favorite_venues' in data:
            attendee.venues.clear()
            for venue_data in data['favorite_venues']:
                venue_id = venue_data['venue_id']
                rating = venue_data.get('rating', 1)
                venue = Venue.query.get(venue_id)
                if venue:
                    av = AttendeeVenue(venue=venue, rating=rating)
                    attendee.venues.append(av)
                else:
                    return jsonify({"error": f"Venue with id {venue_id} not found"}), 404

        db.session.commit()
        return jsonify(attendee.to_dict()), 200

    except Exception as exception:
        db.session.rollback()
        return jsonify({"error": str(exception)}), 400

# DELETE: Remove an attendee by ID
@app.delete('/api/attendees/<int:id>')
def delete_attendee(id):
    user_id = session.get('user_id')
    attendee = Attendee.query.get(id)
    if not attendee:
        return jsonify({"error": "Attendee ID not found"}), 404

    # Check if the user is an admin or the creator of the attendee
    if not (is_admin_user() or attendee.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    # Proceed with deletion if authorized
    try:
        AttendeeVenue.query.filter_by(attendee_id=id).delete()  # Delete associated venues
        db.session.delete(attendee)
        db.session.commit()
        return jsonify({}), 204
    except Exception as exception:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": str(exception)}), 400
    
@app.get("/api/attendees/search")
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
@app.get("/api/event-types")
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
    songs = db.Column(db.Text, nullable=True)  # Store song names or video URLs+
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
 

    # Link to events
    events = db.relationship('Event', secondary='artist_events', back_populates='artists')

    favorited_by = db.relationship('Attendee', secondary='artist_favorites', back_populates='favorite_artists')
    creator = db.relationship('User', back_populates='artists')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'background': self.background,
            'events': [{'id': event.id, 'name': event.name} for event in self.events],
            'songs': self.songs.split(',') if self.songs else [],
            'favorited_by': [{'id': attendee.id, 'name': attendee.first_name} for attendee in self.favorited_by],  # Limit fields returned
            'created_by': {'id': self.creator.id, 'username': self.creator.username} if self.creator else None,

        }

@app.get("/api/artists")
def get_all_artists():
    
    artists = Artist.query.all()
    return jsonify([artist.to_dict() for artist in artists]), 200

@app.get("/api/attendees/<int:id>")
def get_attendee_by_id(id):
    attendee = Attendee.query.get(id)  # Use get() for single ID lookup
    if attendee:
        return jsonify(attendee.to_dict()), 200
    else:
        return jsonify({"error": "Attendee ID not found"}), 404

@app.post("/api/artists")
def create_artist():
    data = request.get_json()
    user_id = session.get('user_id')  # Retrieve user_id from session
    print('USER ID IN CREATE ARTIST IS:', user_id)
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    try:
        # Create the new artist
        new_artist = Artist(
            name=data['name'],
            age=data.get('age'),  # Optional
            background=data.get('background'),  # Optional
            songs=data.get('songs', ''),  # Store songs as a comma-separated string
            created_by_id=data.get('user_id')

        )
        print(new_artist.created_by_id)
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
@app.patch("/api/artists/<int:id>")
def update_artist(id):
    
    data = request.json
    artist = Artist.query.filter(Artist.id == id).first()
    user_id = session.get('user_id')  # Retrieve user_id from session
    
        # Check if the user is an admin or the creator of the artist
    if not (is_admin_user(user_id) or artist.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403
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


@app.delete("/api/artists/<int:id>")
def delete_artist(id):

    # Retrieve the artist
    artist = Artist.query.get(id)
    user_id = session.get('user_id')  # Retrieve user_id from session

    if not artist:
        return jsonify({"error": "Artist ID not found"}), 404

    # Check if the user is an admin or the creator of the artist
    if not (is_admin_user(user_id) or artist.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    # Proceed with deletion if authorized
    try:
        db.session.delete(artist)
        db.session.commit()
        return jsonify({}), 204
    except Exception as exception:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": str(exception)}), 400


@app.get("/api/artists/search")
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

@app.get("/api/artists/<int:id>")
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
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Track the creator by user ID
    social_media_handles = db.Column(db.String(255), nullable=True)
    creator = db.relationship("User", back_populates="tours")  # Establish relationship with User

    events = relationship("Event", secondary=tour_events, back_populates='tours')

    def to_dict(self):

        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.strftime('%m/%d/%Y'),
            'end_date': self.end_date.strftime('%m/%d/%Y'),
            'description': self.description,
            'created_by': {
                'id': self.creator.id,
                'username': self.creator.username
            } if self.creator else None, # Use the name instead of ID
            'social_media_handles': self.social_media_handles,
            'events': [{'name': event.name} for event in self.events] if self.events else [],
        }

@app.post("/api/tours")
def create_tour():
    data = request.get_json()
    user_id = session.get('user_id')  # Retrieve user ID from session


    try:
        
        new_tour = Tour(
            name=data['name'],
            start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),  # Adjusted to parse YYYY-MM-DD
            end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
            description=data['description'],
            social_media_handles=data.get('social_media_handles'),  # Optional
            created_by_id=user_id  # Track the creator
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


@app.get("/api/tours")
def get_all_tours():
    try:
        tours = Tour.query.all()
        return jsonify([tour.to_dict() for tour in tours]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.patch("/api/tours/<int:id>")
def update_tour(id):
    user_id = session.get('user_id')
    tour = Tour.query.get(id)
    if not tour:
        return jsonify({"error": "Tour ID not found"}), 404
    if not (is_admin_user() or tour.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403
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

@app.delete("/api/tours/<int:id>")
def delete_tour(id):
    user_id = session.get('user_id')
    tour = Tour.query.get(id)
    if not tour:
        return jsonify({"error": "Tour ID not found"}), 404
    if not (is_admin_user() or tour.created_by_id == user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        db.session.delete(tour)
        db.session.commit()
        return jsonify({}), 204
    except Exception as exception:
        return jsonify({"error": str(exception)}), 400

@app.get("/api/tours/<int:id>")
def get_tour(id):
    tour = Tour.query.get(id)
    if tour:
        return jsonify(tour.to_dict()), 200
    else:
        return jsonify({"error": "Tour not found"}), 404
    
@app.get("/api/tours/search")
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
    venues = db.relationship('Venue', back_populates='creator')
    artists = db.relationship('Artist', back_populates='creator')
    events = db.relationship('Event', back_populates='creator')  # Link to Event model
    tours = db.relationship("Tour", back_populates="creator")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation time
    last_login = db.Column(db.DateTime)  # Updated on each login
    @property
    def is_admin(self):
        return self.user_type == 'admin'

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
            'profile_completed': self.profile_completed,  # Include this in the response
            'created_at': self.created_at.strftime('%m/%d/%Y %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%m/%d/%Y %H:%M:%S') if self.last_login else None
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

    
@app.post('/api/signup')
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    if not all([username, password, user_type]):
        return jsonify({'error': 'Username, password, and user type are required.'}), 400
    
    if user_type == 'admin' and session.get('user_type') != 'admin':
        return jsonify({'error': 'Only admins can create admin accounts.'}), 403

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


@app.post('/api/signin')
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': 'Username and password are required.'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.verify_password(password):
        # Log the user in by setting the session
        session['user_id'] = int(user.id)
        session['user_type'] = user.user_type
        
        # Update the last_login field to the current time
        user.last_login = datetime.utcnow()
        db.session.add(user)  # Ensure user is added to the session before committing
        db.session.commit()

        # Return user details including profile_completed status
        return jsonify({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'profile_completed': user.profile_completed,
            'last_login': user.last_login.astimezone(timezone.utc).strftime('%m/%d/%Y %H:%M:%S %Z')
        }), 200
    else:
        return jsonify({'error': 'Invalid username or password.'}), 401


@app.post('/api/signout')
def signout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return jsonify({'message': 'Signed out successfully.'}), 200

@app.patch('/api/complete-profile/<int:user_id>')
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
@app.get('/api/admin-only')
def admin_only():
    user = User.query.get(session.get('user_id'))
    if user and user.is_admin:
        # Admin-specific logic here
        return jsonify({'message': 'Welcome, Admin!'}), 200
    else:
        return jsonify({'error': 'Unauthorized access'}), 403


def is_admin_user(id = ''):
    """Helper function to check if the currently logged-in user is an admin."""
    user_id = id
    if id == '' or id == None:
        user_id = session.get('user_id')
    if not user_id:
        return False  # No user_id in session means user is not logged in

    user = User.query.get(user_id)
    if user.user_type == 'admin':
        return True
    else:
        return False

@app.delete('/api/users/<int:user_id>')
def delete_user(user_id):
    # Check if the current user is an admin
    # if not is_admin_user():
    #     return jsonify({'error': 'Unauthorized access'}), 403

    # Retrieve the user to be deleted
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({'error': 'User not found'}), 404

    # Optional: Prevent admins from deleting themselves
    if user_to_delete.id == session.get('user_id'):
        return jsonify({'error': 'You cannot delete your own account'}), 400

    try:

        for artist in user_to_delete.artists:  # Assuming a one-to-many relationship
            db.session.delete(artist)
        for venue in user_to_delete.venues:  # Assuming a one-to-many relationship
            db.session.delete(venue)
        for event in user_to_delete.events:  # Assuming a one-to-many relationship
            db.session.delete(event)
        # Delete the user
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Error deleting user: {str(e)}"}), 500

@app.get('/api/all-users')
def get_all_users():
    user_id = request.args.get('user_id')
    # Check if the current user is an admin
    if not is_admin_user(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403

    # Get query parameters for filtering
    role = request.args.get('role')
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)  # Default to page 1 if not provided
    per_page = request.args.get('per_page', 10, type=int)  # Default to 10 users per page

    # Start with the base query
    query = User.query

    # Apply filters if parameters are provided
    if role:
        query = query.filter_by(user_type=role)
    if status is not None:
        query = query.filter_by(profile_completed=(status.lower() == 'active'))

    # Apply pagination
    paginated_users = query.paginate(page=page, per_page=per_page, error_out=False)

    # Serialize results and add pagination metadata
    users_data = [user.to_dict() for user in paginated_users.items]
    response = {
        'users': users_data,
        'total': paginated_users.total,
        'page': paginated_users.page,
        'pages': paginated_users.pages,
        'per_page': paginated_users.per_page
    }

    return jsonify(response), 200

@app.get('/api/whoami')
def who_am_i():
    user_id = session.get('user_id')
    # if not user_id:
    #     return jsonify({'error': 'No user is signed in'}), 403
    
    user = User.query.get(user_id)
    return jsonify({'id': user.id, 'username': user.username, 'user_type': user.user_type})


@app.patch('/api/users/<int:user_id>/role')
def update_user_role(user_id):
    print('USER ID IS:', user_id)
    # Check if the current user is an admin
    # if not is_admin_user():
    #     return jsonify({'error': 'Unauthorized access'}), 403

    # Retrieve the new role from the request body
    data = request.get_json()
    new_role = data.get('user_type')
    print('NEW ROLE IS', new_role)
    # Validate the new role
    valid_roles = ['admin', 'attendee', 'artist', 'venue']
    if new_role not in valid_roles:
        return jsonify({'error': 'Invalid role specified.'}), 400

    # Find the user to update
    user = User.query.get(user_id)
    print('USER AFTER NEW ROLE IS:', user)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    # Update the user's role
    user.user_type = new_role
    db.session.commit()

    return jsonify({'message': 'User role updated successfully.', 'user': user.to_dict()}), 200

@app.get('/api/admin/metrics')
def get_admin_metrics():
    # Ensure the current user is an admin


    # Set the date ranges
    now = datetime.now(timezone.utc)  # Change here to make it timezone-aware
    last_30_days = now - timedelta(days=30)
    last_7_days = [now - timedelta(days=i) for i in range(7)]

    # Calculate total active users (logged in within the last 30 days)
    active_users_count = User.query.filter(User.last_login >= last_30_days).count()

    # Calculate new registrations within the last 30 days
    new_registrations_count = User.query.filter(User.created_at >= last_30_days).count()

    # Calculate daily logins for the past 7 days
    daily_logins = {}
    for day in last_7_days:
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        daily_login_count = User.query.filter(User.last_login >= day_start, User.last_login <= day_end).count()
        daily_logins[day.strftime('%m/%d/%Y')] = daily_login_count

    # Prepare and return the response
    metrics = {
        'active_users_last_30_days': active_users_count,
        'new_registrations_last_30_days': new_registrations_count,
        'daily_logins_last_7_days': daily_logins
    }

    return jsonify(metrics), 200








@app.get('/api/admin/dashboard')
def get_admin_dashboard():
    # Ensure the current user is an admin
    # if not is_admin_user():
    #     return jsonify({'error': 'Unauthorized access'}), 403

    # Get metrics
    now = datetime.now(timezone.utc)  # Change here to make it timezone-aware
    last_30_days = now - timedelta(days=30)
    last_7_days = [now - timedelta(days=i) for i in range(7)]

    active_users_count = User.query.filter(User.last_login >= last_30_days).count()
    new_registrations_count = User.query.filter(User.created_at >= last_30_days).count()

    daily_logins = {}
    for day in last_7_days:
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        daily_login_count = User.query.filter(User.last_login >= day_start, User.last_login <= day_end).count()
        daily_logins[day.strftime('%m/%d/%Y')] = daily_login_count

    metrics = {
        'active_users_last_30_days': active_users_count,
        'new_registrations_last_30_days': new_registrations_count,
        'daily_logins_last_7_days': daily_logins
    }

    # Get users
    users_data = User.query.all()
    users_response = [user.to_dict() for user in users_data]

    # Combine metrics and users into one response
    response = {
        'metrics': metrics,
        'users': users_response
    }

    return jsonify(response), 200

@app.get('/api/search-users')
def search_users():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username not provided"}), 400

    username_normalized = username.strip().lower()
    
    # Start with the base query
    query = User.query

    # Apply filters if parameters are provided
    query = query.filter(User.username.ilike(f'%{username_normalized}%'))  # Case-insensitive search

    # Execute the query and get results
    users_data = query.all()

    # Serialize results
    if not users_data:
        return jsonify({"error": "No users found"}), 404

    users_response = [user.to_dict() for user in users_data]

    return jsonify({'users': users_response}), 200