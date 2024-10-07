# Phase4-Final-Project
 # Event Planner Command-Line-Interface Application!

##Overview

The ** Performance Event Planner** is a Python-based command-line interface application designed to help growing artists manage events and attendees.
I personally created this to track my singing performances and friends and family that helped support me along the way!

The application allows users to create events, add attendees, view all events, and manage attendees for a specific event. (i.e. delete attendees)
                    All through the terminal!
                    
                        
## Installation

To use the Event Planner CLI, you need Python installed on your machine. Follow these steps:

1. Clone this repository:
    git clone https://github.com/your-username/event-planner-cli.git

2. Navigate to the project directory:
    FINAL-PROJECT

3. OPEN TERMINAL:
    with your terminal open confirm you have the latest versions of the systems necessary to operate installed. you will need the following:
    
    A. Python: test to see if you have this by running|| python --version
    B. pipenv --version 
    C. Sql extension for VS code. (this is an extension in VS code you can add)


4. Next in your terminal 
run: pip install rich  
This will set a prompt pop up asking to set this up in a virtual environment, click confirm to allow this.

5. Now that we have everything installed and set up enter the following into the command:

    python -m lib.main

after that runs and creates the database you can now open up the event planner with:

    python -m lib.cli

## Using the Event Planner: A Guide.

After installation, you can run the application by following these steps:

**FEATURES Quick Overview**
0. Exit: Exit the program.
1. Create a New Venue: Create a venue for events.
2. Add an Existing Venue to an Event: Assign an existing venue to an event.
3. List All Venues: View a list of all created venues.
4. Search Venue by Name: Search for a venue by name.
5. Delete a Venue: Remove a venue from the system.
6. Create a New Event: Create events by providing event details.
7. Assign Artist to Event: Assign an artist to a specific event.
8. List All Events: View a list of all created events.
9. Search Event by Name: Search for events by name.
10. Delete an Event: Remove an event from the system.
11. Add a New Attendee: Add a new attendee to an event.
12. Add an Existing Attendee to an Event: Assign an attendee to an existing event.
13. Remove an Attendee from an Event: Unassign an attendee from a specific event.
14. List All Attendees: View a list of all attendees in the database.
15. Search Attendee by Name: Search for attendees by name.
16. Delete an Attendee: Remove an attendee from the system.
17. Create a Tour: Create a new tour and assign events to it.
18. Search Tour by Name: Find tours by name.
19. List All Tours: View a list of all tours.
20. Remove an Event from a Tour: Unassign an event from a tour.
21. Delete a Tour: Delete a tour from the system.
22. Create an Artist: Create an artist profile by entering details.
23. Find Artist by Name: Search for an artist by name.
24. List All Artists: View a list of all artists in the system.
25. Create a Song: Create a song and assign it to an artist.
26. List Songs by Artist: View a list of songs by a specific artist.
27. Delete a Song: Remove a song from the system.
99. Reset Database: Reset the entire database to start fresh.
**FEATURES GUIDE EXPANDED**
# Option 1:
Create a New Venue
Select option 1 in the menu.
You will be prompted to enter:

Venue Name: The name of the venue.
Event Organizer: The name of the person organizing the event.
Venue Earnings: The total earnings for the venue. A confirmation message will indicate that the venue has been created.

# Option 2: 
Add an Existing Venue to an Event
Select option 2 in the menu.
You can assign an existing venue to an event by:

Selecting the Event ID.
Selecting the Venue ID. A confirmation message will indicate that the venue has been assigned to the event.

# Option 3: 
List All Venues
Select option 3 to view a list of all venues.
The table will show the following details:

ID: The unique ID of the venue.
Name: The name of the venue.
Organizer: The event organizer.
Earnings: The venue's earnings.

# Option 4: 
Search Venue by Name
Select option 4 to search for venues by name.
You will be prompted to enter a venue name, and all matching venues will be displayed in a table.

# Option 5: 
Delete a Venue
Select option 5 to delete a venue.
Provide the Venue ID, and the venue will be deleted if it exists.

# Option 6: 
Create a New Event
Select option 6 in the menu.
You will be prompted to enter:

Event Name: The name of the event.
Event Date: The date of the event.
Event Location: The venue where the event will take place.
Event Description: A description of the event.
You will also be prompted to assign attendees from a list of available attendees to the event. A confirmation message will indicate that the event has been created.
# Option 7: 
Assign Artist to Event
Select option 7 in the menu.
You can assign an artist to an event by:

Selecting the Event ID.
Selecting the Artist ID. A confirmation message will indicate that the artist has been assigned to the event.
# Option 8: 
List All Events
Select option 8 to view a list of all events.
The table will display details for each event, including the attendees and the artists performing.

# Option 9:  
Search Event by Name
Select option 9 to search for an event by its name.
Matching events will be displayed in a table.

# Option 10: 
Delete an Event
Select option 10 to delete an event.
Provide the Event ID, and the event will be deleted if it exists.

# Option 11: 
Add a New Attendee
Select option 11 in the menu.
You will be prompted to enter:

Event ID: The ID of the event.
Attendee Name: The name of the attendee.
Attendee Email: The email of the attendee. A confirmation message will indicate that the attendee has been added to the event.
# Option 12: 
Add an Existing Attendee to an Event
Select option 12 in the menu.
You can assign an attendee already in the system to another event by:

Selecting the Event ID.
Selecting the Attendee ID.
# Option 13: 
Remove an Attendee from an Event
Select option 13 to remove an attendee from a specific event.
Provide the Event ID and Attendee ID, and the attendee will be unassigned from the event.

# Option 14: 
List All Attendees
Select option 14 to view a list of all attendees in the database.
The table will show each attendee's ID, name, and email.

# Option 15: 
Search Attendee by Name
Select option 15 to search for an attendee by their name.
Matching attendees will be displayed in a table.

# Option 16: 
Delete an Attendee
Select option 16 to delete an attendee from the system.
Provide the Attendee ID, and the attendee will be deleted if they exist.

# Option 17: 
Create a Tour
Select option 17 to create a new tour.
You will be prompted to enter the tour name, description, and date range. You can then assign multiple events to the tour.

# Option 18: 
Search Tour by Name
Select option 18 to search for a tour by its name.
Matching tours will be displayed in a table.

# Option 19: 
List All Tours
Select option 19 to view a list of all tours.
The table will display details for each tour, including the events assigned to it.

# Option 20: Remove an Event from a Tour
Select option 20 to unassign an event from a tour.
You will be prompted to provide the Tour ID and Event ID.

# Option 21: 
Delete a Tour
Select option 21 to delete a tour.
Provide the Tour ID, and the tour will be deleted if it exists.

# Option 22: 
Create an Artist
Select option 22 to create a new artist profile.
You will be prompted to enter details like name, hometown, bio, and social media handles.

# Option 23: 
Find Artist by Name
Select option 23 to search for an artist by their name.
Matching artists will be displayed in a table.

# Option 24: 
List All Artists
Select option 24 to view a list of all artists in the system.
The table will display artist details, including their name, hometown, and social media.

# Option 25: 
Create a Song
Select option 25 to create a new song.
You will be prompted to enter the song title, genre, and release date, and assign it to an artist.

# Option 26: 
List Songs by Artist
Select option 26 to view a list of all songs by a specific artist.
The table will show the song title, genre, and release date.

# Option 27: 
Delete a Song
Select option 27 to delete a song from the system.
Provide the Song ID, and the song will be deleted if it exists.

# Option 99: 
Reset Database
Select option 99 to reset the entire database, deleting all existing data and starting fresh.# Phase4Project
