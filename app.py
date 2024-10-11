# app.py
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
from lib.models.database import db  # Import db from the new database module
from associations import attendee_events, attendee_favorites
from sqlalchemy_serializer import SerializerMixin  # Import SerializerMixin


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize the db with the app
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)


class Venue(db.Model, SerializerMixin):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    organizer = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    earnings = db.Column(db.String(100), nullable = False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'organizer': self.organizer,
            'email': self.email,
            'earnings': self.earnings,
            'events': [{'id': event.id, 'name': event.name} for event in self.events]  # Simplified event details
        }
# Update the decorators to use @app.route() instead of app.get()

@app.get("/venues")
def index():
    return jsonify ([
        { "id": venue.id, "name": venue.name, "organizer": venue.organizer, "email": venue.email, "earnings": venue.earnings}
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
            earnings=data['earnings']
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
    venue = Venue.query.filter(Venue.id ==id).first()
    if venue:
        try:
            for key in data:
                setattr(venue, key, data[key])
            db.session.add(venue)
            db.session.commit()
            return jsonify(Venue.query.filter(Venue.id ==id).first().to_dict()), 200
        except Exception as exception:
            return jsonify({"error": str(exception)}), 400
    else:
        return jsonify({"error": "Venue ID not found"}), 404

@app.delete('/venues/<int:id>')
def delete_venue(id):
    venue = Venue.query.filter(Venue.id == id).first()
    if venue:
        try:
            db.session.delete(venue)
            db.session.commit()
            return jsonify({}), 204
        except Exception as exception:
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
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

    venue = db.relationship('Venue', backref='events')
    attendees = db.relationship('Attendee', secondary='attendee_events', back_populates='attended_events')
    favorited_by = db.relationship('Attendee', secondary='attendee_favorites', back_populates='favorite_events')

    def to_dict(self):
        # Limit attendee details to prevent recursion
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'description': self.description,
            'venue': {'id': self.venue.id, 'name': self.venue.name},
            'attendees': [{'id': attendee.id, 'first_name': attendee.first_name} for attendee in self.attendees],  # Simplified attendee details
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
        # Verify if the venue exists
        venue = Venue.query.get(data['venue_id'])
        if not venue:
            return jsonify({"error": "Venue not found"}), 404

        # Parse date and time to proper datetime format
        event_date = datetime.strptime(data['date'], '%Y-%m-%d')
        event_time = data['time']  # Assuming time remains a string (HH:MM format)

        # Create a new event object
        new_event = Event(
            name=data['name'],
            date=event_date,  # Store date as a datetime object
            time=event_time,  # Store time as a string or adjust as needed
            location=data['location'],
            description=data['description'],
            venue_id=data['venue_id']
        )
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

# PATCH to update an event by ID
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
                    
            db.session.add(event)
            db.session.commit()
            return jsonify(event.to_dict()), 200
        except Exception as exception:
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
    event_name = request.args.get('name')
    if event_name:
        # Normalize the input: strip spaces and convert to lowercase
        event_name_normalized = event_name.strip().lower()
        
        # Use ilike for case-insensitive search and strip spaces on database values too
        events = Event.query.filter(Event.name.ilike(f'%{event_name_normalized}%')).all()
        
        if events:
            return jsonify([event.to_dict() for event in events]), 200
        else:
            return jsonify({"error": "No events found with that name"}), 404
    return jsonify({"error": "Event name not provided"}), 400


#---------------------------------ATTENDEES----------------------------#


# Attendee Model
class Attendee(db.Model, SerializerMixin):
    __tablename__ = "attendees"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    preferred_event_type = db.Column(db.String(100), nullable=True)

    # Relationships
    attended_events = db.relationship('Event', secondary='attendee_events', back_populates='attendees')
    favorite_events = db.relationship('Event', secondary='attendee_favorites', back_populates='favorited_by', lazy='dynamic')

    def to_dict(self):
        # Limit event details to prevent recursion
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'preferred_event_type': self.preferred_event_type,
            'favorite_events': [{'id': event.id, 'name': event.name} for event in self.favorite_events],  # Simplified event details
        }
# POST: Create new attendee with favorite events
@app.post("/attendees")
def create_attendee():
    data = request.get_json()

    try:
        # Create new attendee object
        new_attendee = Attendee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            preferred_event_type=data.get('preferred_event_type')  # Optional
        )

        # Assign favorite events (if provided)
        if 'favorite_event_ids' in data:
            favorite_events = Event.query.filter(Event.id.in_(data['favorite_event_ids'])).all()
            new_attendee.favorite_events.extend(favorite_events)  # Use extend to add the events

        db.session.add(new_attendee)
        db.session.commit()
        return jsonify(new_attendee.to_dict()), 201
    except Exception as exception:
        return jsonify({"error": str(exception)}), 400
# GET: Retrieve all attendees
@app.get("/attendees")
def get_all_attendees():
    attendees = Attendee.query.all()
    return jsonify([attendee.to_dict() for attendee in attendees]), 200

@app.patch("/attendees/<int:id>")
def update_attendee(id):
    data = request.json
    attendee = Attendee.query.filter(Attendee.id == id).first()
    if attendee:
        try:
            # Update fields
            for key in data:
                if key != 'favorite_event_ids':  # We'll handle favorite_event_ids separately
                    setattr(attendee, key, data[key])

            # Update favorite events
            if 'favorite_event_ids' in data:
                favorite_events = Event.query.filter(Event.id.in_(data['favorite_event_ids'])).all()
                attendee.favorite_events = favorite_events  # Update the relationship

            db.session.add(attendee)
            db.session.commit()
            return jsonify(attendee.to_dict()), 200
        except Exception as exception:
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
if __name__ == '__main__':
    app.run(port=5001, debug=True)