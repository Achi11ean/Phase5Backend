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