from sqlalchemy import Table, Column, Integer, ForeignKey
from lib.models.database import db  # Import db from the new database module

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