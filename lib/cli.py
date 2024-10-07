# lib/cli.py
#importing all classes necessary
from .models.event import Event
from .models.attendee import Attendee
from .models.venue import Venue
from .models.tour import Tour
from .models.artist import Artist  # Add the Artist import
from rich.console import Console
from rich.table import Table
from .models.song import Song  # Add the Song import

#initialize the Rich console for styled outputs
console = Console()

#Function to exit the program with a print to confirm program exiting. 
def exit_program():
    console.print("[bold red]Exiting the program[/bold red]")
    exit()

#Function to create a new event with a prompt for the user to enter the event details.
def validate_integer_input(prompt):
    """Prompts the user for an integer input and retries if not valid."""
    while True:
        user_input = input(prompt).strip()
        if user_input.isdigit():
            return int(user_input)
        console.print("[red]Invalid input. Please enter a valid integer.[/red]")

def create_event():
    while True:  # Keep prompting the user until valid input is provided
        try:
            # Get event details
            name = input("Enter Event Name: ").strip()
            date = input("Enter Event Date: ").strip()
            location = input("Enter Event Location: ").strip()
            description = input("Enter Event Description: ").strip()

            # Select Venue for the Event
            venues = Venue.get_all()
            if venues:
                console.print("[blue] Available Venues: [/blue]")
                for venue in venues:
                    console.print(f"ID: {venue.id}, Name: {venue.name}")
                venue_id = validate_integer_input("Enter Venue ID for This Event: ")
                venue = Venue.find_by_id(venue_id)
                if not venue:
                    console.print("[yellow]Invalid Venue ID. Please try again.[/yellow]")
                    continue  # Go back to prompt
            else:
                console.print("[yellow]No available Venues. Please create a venue first.[/yellow]")
                return
            
            # Create the event
            event = Event.create(name, date, location, description, venue_id)
            console.print(f"[green]Event Created: {event}[/green]")

            # Prompt to assign attendees to the event
            attendees = Attendee.get_all()
            if attendees:
                console.print("[blue]Available Attendees:[/blue]")
                for attendee in attendees:
                    console.print(f"ID: {attendee.id}, Name: {attendee.name}")
                
                # Allow the user to select multiple attendees (comma-separated input)
                attendee_ids = input("Enter comma-separated Attendee IDs to add to this event (or leave blank to skip): ").split(',')
                attendee_ids = [attendee_id.strip() for attendee_id in attendee_ids if attendee_id.strip().isdigit()]
                
                # Assign selected attendees to the event
                for attendee_id in attendee_ids:
                    attendee = Attendee.find_by_id(attendee_id)
                    if attendee:
                        attendee.add_to_event(event.id)
                        console.print(f"[green]Attendee {attendee.name} added to event {event.name}.[/green]")
                    else:
                        console.print(f"[yellow]Attendee ID {attendee_id} not found.[/yellow]")
            else:
                console.print("[yellow]No attendees available. Please create an attendee first.[/yellow]")

            break  # Exit loop on success

        except ValueError as e:
            console.print(f"[red]Error: {e}. Please try again with valid input.[/red]")
#function to list all events 
def list_events():
    #Fetch all events from the DB 
    events = Event.get_all()
    if events: #Check if there are any events
        #Create a table with styled columns to display the event details
        table = Table(title="[bold red]Events List[/bold red ]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Date", justify="center", style="green")
        table.add_column("Location", style="blue")
        table.add_column("Description", style="magenta")
        table.add_column("Attendees", style="yellow")
        table.add_column("Venue ID", style="blue")
        #Loop through each event and display its details in the table
        for event in events:
            attendees = Attendee.find_by_event_id(event.id) #find all attendees for the current event
            attendees_str = ", ". join([attendee.name for attendee in attendees]) if attendees else "No Attendees, sorry!" #create a string of attendee names or a message if no attendees are found 
            table.add_row(str(event.id), event.name, event.date, event.location, event.description, attendees_str, str(event.venue_id)) #add a row to the table for each event            
        console.print(table)#display table in the console
    else:
        console.print("[yellow]No events found.[/yellow]")#if no events are found display error message.

#function to add an attendee to an event with a prompt to the user to enter attendee and event details. 
def add_attendee():
    try:
        # Step 1: Prompt the user for attendee details
        name = input("Enter attendee name: ").strip()
        email = input("Enter attendee Email: ").strip()

        # Step 2: Create the attendee
        attendee = Attendee.create(name, email)
        console.print(f"[green]Attendee {attendee.name} created successfully.[/green]")

        # Step 3: Prompt the user to assign favorite artists
        artists = Artist.get_all()  # Get all available artists
        if artists:
            console.print("[blue]Available Artists to add as favorites:[/blue]")
            for artist in artists:
                console.print(f"ID: {artist.id}, Name: {artist.name}")

            # Allow the user to select multiple artists (comma-separated input)
            artist_ids = input("Enter comma-separated Artist IDs to add to favorites (or leave blank to skip): ").split(',')
            artist_ids = [artist_id.strip() for artist_id in artist_ids if artist_id.strip().isdigit()]

            # Add selected artists to the attendee's favorites
            for artist_id in artist_ids:
                artist = Artist.find_by_id(artist_id)
                if artist:
                    attendee.add_favorite_artist(artist)
                    console.print(f"[green]Artist {artist.name} added to {attendee.name}'s favorites.[/green]")
                else:
                    console.print(f"[yellow]Artist ID {artist_id} not found.[/yellow]")
        else:
            console.print("[yellow]No artists available to add to favorites. Please create an artist first.[/yellow]")

        # Step 4: After favorite artists are added, associate the attendee with an event
        events = Event.get_all()
        if events:
            console.print("[blue]Available Events:[/blue]")
            for event in events:
                console.print(f"ID: {event.id}, Name: {event.name}")

            # Ask for event assignment
            event_id = input("Enter the event ID to associate the attendee with (or leave blank to skip): ").strip()
            if event_id and event_id.isdigit():
                event = Event.find_by_id(event_id)
                if event:
                    attendee.add_to_event(event.id)
                    console.print(f"[green]Attendee {attendee.name} added to event {event.name}.[/green]")
                else:
                    console.print("[yellow]Event not found.[/yellow]")
            else:
                console.print("[yellow]No event assigned. Skipping event association.[/yellow]")
        else:
            console.print("[yellow]No events available. Please create an event first.[/yellow]")

    except ValueError as e:
        # Handle any errors during the process
        console.print(f"[red]Error: {e}. Please try again with valid input.[/red]")
#function to delete an attendee with a promt for attendee ID. if attendee exists, delete it and confirm it's deletion. If it's doesn't exist, raise an error. 
def delete_attendee():
    attendee_id = input("Enter the Attendee ID to delete: ")
    attendee = Attendee.find_by_id(attendee_id)
    if attendee:
        attendee.delete()
        console.print(f"[red] Attendee {attendee.name} has been deleted.[/red]")
    else:
        console.print("[yellow]Attendee Not found. [/yellow]")

#function to delete an event with a prompt for the event ID to delete a specified event. if it exists, show a confirmation it's deleted. if not raise a user error.
def delete_event():
    event_id = input("Enter Event ID to delete: ")
    event = Event.find_by_id(event_id)
    if event:
        event.delete()
        console.print(f"[red]Event {event.name} deleted.[/red]")
    else:
        console.print("[yellow]Event not found[/yellow]")

    #function to find an event by name prompting a user enter the event name. 
    # Then get all of the events from the database and find any matching the entry. if they match, display it. if not display a warning
# Function to find an event by name and display in a table
def find_event_by_name():
    # Fetch all events to display available options
    events = Event.get_all()
    if events:
        console.print("[blue]Available Events:[/blue]")
        for event in events:
            console.print(f"ID: {event.id}, Name: [bold magenta]{event.name}[/bold magenta]")
    else:
        console.print("[yellow]No events found. Please create an event first.[/yellow]")
        return

    # Prompt user for event name to search
    name = input("Enter event name to search: ").strip()

    # Find matching events based on the name provided
    matching_events = [event for event in events if name.lower() in event.name.lower()]
    if matching_events:
        # Create a table with styled columns to display the matching events
        table = Table(title=f"[bold green]Events Matching: '{name}'[/bold green]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Date", style="green")
        table.add_column("Location", style="blue")
        table.add_column("Description", style="magenta")
        table.add_column("Attendees", style="yellow")
        table.add_column("Artists", style="cyan")  # New column for artists
        table.add_column("Venue ID", style="blue")

        # Loop through matching events and display them in the table
        for event in matching_events:
            attendees = Attendee.find_by_event_id(event.id)
            attendees_str = ", ".join([attendee.name for attendee in attendees]) if attendees else "No Attendees"
            artists = event.artists  # Assuming event has an attribute `artists`
            artists_str = ", ".join([artist.name for artist in artists]) if artists else "No Artists"
            
            table.add_row(
                str(event.id), event.name, event.date, event.location, event.description, 
                attendees_str, artists_str, str(event.venue_id)
            )

        console.print(table)
    else:
        console.print(f"[yellow]No event found with the name '{name}'.[/yellow]")

#function to list all attendees for a specific event. user enters ID. fin the event by that ID and if attendees found create a table to display the details - adding a row for each attendee
def list_event_attendees():
    event_id = input("Enter the event ID:")
    event = Event.find_by_id(event_id)
    if event:
        attendees = Attendee.find_by_event_id(event.id)
        if attendees:
            table = Table(title=f"[bold green]Attendees for Event: {event.name}[/bold green]")
            table.add_column("ID", justify="right", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Email", style="yellow")
            for attendee in attendees:
                table.add_row(str(attendee.id), attendee.name, attendee.email)
            console.print(table)
        else:
            console.print("[yellow]No attendees found for this event.[/yellow]")
    else:
        console.print("[yellow]Event Not found[/yellow]")

def find_attendee_by_name():
    name = input("Enter attendee name to search: ").strip()
    attendees = Attendee.get_all()

    matching_attendees = [attendee for attendee in attendees if name.lower() in attendee.name.lower()]
    if matching_attendees:
        table = Table(title=f"[bold green]Attendees Matching: '{name}'[/bold green]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Email", style="yellow")
        table.add_column("Favorite Artists", style="green")

        for attendee in matching_attendees:
            favorite_artists = attendee.get_favorite_artists()
            favorite_artists_str = ", ".join([artist.name for artist in favorite_artists]) if favorite_artists else "None"
            table.add_row(str(attendee.id), attendee.name, attendee.email, favorite_artists_str)

        console.print(table)

        assign_favorite_artist_to_attendee(matching_attendees[0])

    else:
        console.print(f"[yellow]No attendee found with the name '{name}'.[/yellow]")

def add_existing_attendee_to_event():
    # List all events to select from
    events = Event.get_all()
    if not events:
        console.print("[yellow]No events found.[/yellow]")
        return
    console.print("[blue]Available Events:[/blue]")
    for event in events:
        console.print(f"ID: {event.id}, Name: {event.name}")
    # Get event ID from the user
    event_id = validate_integer_input("Enter the Event ID to add the attendee to: ")
    event = Event.find_by_id(event_id)
    
    if not event:
        console.print("[red]Event not found.[/red]")
        return
    # List all attendees to select from
    attendees = Attendee.get_all()
    if not attendees:
        console.print("[yellow]No attendees found.[/yellow]")
        return
    console.print("[blue]Available Attendees:[/blue]")
    for attendee in attendees:
        console.print(f"ID: {attendee.id}, Name: {attendee.name}, Email: {attendee.email}")
    # Get attendee ID from the user
    attendee_id = validate_integer_input("Enter the Attendee ID to add to the event: ")
    attendee = Attendee.find_by_id(attendee_id)
    if not attendee:
        console.print("[red]Attendee not found.[/red]")
        return
    try:
    # Add the attendee to the event
        attendee.add_to_event(event.id)
        console.print(f"[green]Attendee {attendee.name} added to event {event.name}.[/green]")
    except ValueError as e:
        console.print(f"[yellow]{str(e)}[/yellow]")

def list_all_attendees():
    attendees = Attendee.get_all()  # Retrieve all attendees from the database
    if attendees:
        # Create a table to display attendee information
        table = Table(title="[bold blue]All Attendees[/bold blue]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Email", style="yellow")
        # Add each attendee to the table
        for attendee in attendees:
            table.add_row(str(attendee.id), attendee.name, attendee.email)
        console.print(table)  # Display the table in the console
    else:
        console.print("[yellow]No attendees found.[/yellow]")

def remove_attendee_from_event():
    # List all events to select from
    events = Event.get_all()
    if not events:
        console.print("[yellow]No events found.[/yellow]")
        return
    console.print("[blue]Available Events:[/blue]")
    for event in events:
        console.print(f"ID: {event.id}, Name: {event.name}")
    # Get the event ID from the user
    event_id = validate_integer_input("Enter the Event ID to remove the attendee from: ")
    event = Event.find_by_id(event_id)
    if not event:
        console.print("[red]Event not found.[/red]")
        return
    # List all attendees in the event to select from
    attendees = Attendee.find_by_event_id(event.id)
    if not attendees:
        console.print("[yellow]No attendees found for this event.[/yellow]")
        return
    console.print("[blue]Attendees for Event:[/blue]")
    for attendee in attendees:
        console.print(f"ID: {attendee.id}, Name: {attendee.name}, Email: {attendee.email}")
    # Get the attendee ID from the user
    attendee_id = validate_integer_input("Enter the Attendee ID to remove from the event: ")
    attendee = Attendee.find_by_id(attendee_id)
    if not attendee:
        console.print("[red]Attendee not found.[/red]")
        return
    # Remove the attendee from the event
    try:
        attendee.remove_from_event(event.id)  # Call the method to remove the attendee from the event
        console.print(f"[green]Attendee {attendee.name} removed from event {event.name}.[/green]")
    except ValueError as e:
        console.print(f"[red]{str(e)}[/red]")

def assign_favorite_artist_to_attendee(attendee):
    artists = Artist.get_all()
    if not artists:
        console.print("[red]No artists available. Please create an artist first.[/red]")
        return

    console.print("[blue]Available Artists:[/blue]")
    for artist in artists:
        console.print(f"ID: {artist.id}, Name: {artist.name}")

    artist_id = input("Enter the Artist ID to add as a favorite (or leave blank to skip): ").strip()
    if artist_id:
        artist = Artist.find_by_id(artist_id)
        if artist:
            attendee.add_favorite_artist(artist)
            console.print(f"[green]Artist {artist.name} added to {attendee.name}'s favorites.[/green]")
        else:
            console.print(f"[red]Artist with ID {artist_id} not found.[/red]")
    else:
        console.print("[yellow]Skipping favorite artist assignment.[/yellow]")

def search_venue_events():
    venue_id = input("Enter Venue ID to Search for Events: ")
    venue = Venue.find_by_id(venue_id)
    if venue:
        events = Venue.find_events_by_venue_id(venue.id)
        if events:
            console.print(f"[green] Events for Venue {venue.name}: [/green]")
            table = Table(title=f"Events at {venue.name}")
            table.add_column("ID", justify="right", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Date", style="green")
            table.add_column("Location", style="blue")
            table.add_column("Description", style="yellow")
            for event in events:
                table.add_row(str(event.id), event.name, event.date, event.location, event.description)
            console.print(table)
        else:
            console.print("[yellow]No Events Found for this Venue.[/yellow]")
    else:
        console.print("[red]Venue not found.[/red]")
    
def list_venues():
    venues = Venue.get_all()
    if venues:
        table = Table(title="[bold blue] Venues List [/bold blue]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Organizer", style="yellow")
        table.add_column("Earnings", style="green")
        for venue in venues:
            table.add_row(str(venue.id), venue.name, venue.organizer, str(venue.earnings))
        console.print(table)
    else:
        console.print("[yellow] No Venues Found.")

def create_venue():
    try:
        # Get user inputs
        name = input("Enter Venue Name: ").strip()
        organizer = input("Enter Event Organizer Name: ").strip()
        earnings = input("Enter Venue Earnings: ").strip()
        # Check for empty name or organizer inputs
        if not name or not organizer:
            raise ValueError("Venue name and organizer must be non-empty strings.")
        # Create the venue using user inputs
        venue = Venue.create(name=name, organizer=organizer, earnings=earnings)
        console.print(f"[green]Venue Created Successfully:[/green] {venue}")
    # Catch the specific ValueError raised when inputs are invalid
    except ValueError as e:
        console.print(f"[red]Error: {e}. Please try again with valid input.[/red]")

def delete_venue():
    venue_id = input("Enter Venue ID to delete: ")
    venue = Venue.find_by_id(venue_id)
    if venue:
        venue.delete()
        console.print(f"[red]Venue {venue.name} deleted.[/red]")
    else:
        console.print("[yellow]Venue not found[/yellow]")

def add_existing_venue_to_event():
    # List all events to select from
    events = Event.get_all()
    if not events:
        console.print("[yellow]No events found.[/yellow]")
        return
    console.print("[blue]Available Events:[/blue]")
    for event in events:
        console.print(f"ID: {event.id}, Name: {event.name}")
    # Get event ID from the user
    event_id = validate_integer_input("Enter the Event ID to assign a venue to: ")
    event = Event.find_by_id(event_id)
    if not event:
        console.print("[red]Event not found.[/red]")
        return
    # List all venues to select from
    venues = Venue.get_all()
    if not venues:
        console.print("[yellow]No venues found.[/yellow]")
        return
    console.print("[blue]Available Venues:[/blue]")
    for venue in venues:
        console.print(f"ID: {venue.id}, Name: {venue.name}, Organizer: {venue.organizer}")
    # Get venue ID from the user
    venue_id = validate_integer_input("Enter the Venue ID to assign to the event: ")
    venue = Venue.find_by_id(venue_id)
    if not venue:
        console.print("[red]Venue not found.[/red]")
        return
    # Assign the venue to the event
    event.venue_id = venue.id
    event.save()  # Save the changes to the event
    console.print(f"[green]Venue {venue.name} assigned to event {event.name}.[/green]")

def create_tour():
    # Prompt user for tour details
    name = input("Enter Tour Name: ").strip()
    description = input("Enter Tour Description: ").strip()
    start_date = input("Enter Tour Start Date: ").strip()
    end_date = input("Enter Tour End Date: ").strip()
    # Create the tour
    tour = Tour.create(name, description, start_date, end_date)
    # List available events in cyan
    events = Event.get_all()
    if events:
        console.print("[cyan]Available Events:[/cyan]")
        for event in events:
            console.print(f"ID: [cyan] {event.id} [/cyan], Name: {event.name}, Date: {event.date}")
        # Prompt user to assign events to the tour
        event_ids = input("Enter comma-separated Event IDs to assign to this tour (or leave blank to skip): ").split(',')
        event_ids = [event_id.strip() for event_id in event_ids if event_id.strip().isdigit()]
        # Assign selected events to the tour
        if event_ids:
            for event_id in event_ids:
                event = Event.find_by_id(event_id)
                if event:
                    try:
                        tour.add_event(event.id)
                        console.print(f"[green]Event {event.name} assigned to tour {tour.name}.[/green]")
                    except ValueError as e:
                        console.print(f"[yellow]{str(e)}[/yellow]")
                else:
                    console.print(f"[red]Event ID {event_id} not found.[/red]")
        else:
            console.print("[yellow]No events selected for this tour.[/yellow]")
    else:
        console.print("[yellow]No existing events available to assign.[/yellow]")
    console.print(f"[green]Tour '{tour.name}' created from {tour.start_date} to {tour.end_date}.[/green]")

def assign_event_to_tour():
    try:
        # List all tours
        tours = Tour.get_all()
        if not tours:
            console.print("[yellow]No tours found.[/yellow]")
            return
        console.print("[blue]Available Tours:[/blue]")
        for tour in tours:
            console.print(f"ID: {tour.id}, Name: {tour.name}")
        # Get tour ID from the user
        tour_id = validate_integer_input("Enter the Tour ID to assign an event to: ")
        tour = Tour.find_by_id(tour_id)
        if not tour:
            console.print("[red]Tour not found.[/red]")
            return
        # List all events to select from
        events = Event.get_all()
        if not events:
            console.print("[yellow]No events found.[/yellow]")
            return
        console.print("[blue]Available Events:[/blue]")
        for event in events:
            console.print(f"ID: {event.id}, Name: {event.name}, Date: {event.date}")
        # Get event ID from the user
        event_id = validate_integer_input("Enter the Event ID to assign to the tour: ")
        event = Event.find_by_id(event_id)
        if not event:
            console.print("[red]Event not found.[/red]")
            return
        # Try to add the event to the tour
        tour.add_event(event.id)
        console.print(f"[green]Event {event.name} assigned to tour {tour.name}.[/green]")
    except ValueError as e:
        # Handle the ValueError when the event is already assigned to the tour
        console.print(f"[red]Error: {e}[/red]")

def list_tours():
    tours = Tour.get_all()  # Get all tours
    if tours:
        table = Table(title="[bold blue]All Tours[/bold blue]")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Start Date", style="yellow")
        table.add_column("End Date", style="yellow")
        table.add_column("Events", style="blue")
        for tour in tours:
            events = tour.get_events()  # Get events for each tour
            events_str = ", ".join([event.name for event in events]) if events else "No Events"
            table.add_row(str(tour.id), tour.name, tour.description, tour.start_date, tour.end_date, events_str)
        console.print(table)
    else:
        console.print("[yellow]No tours found.[/yellow]")

def view_tour_events():
    # List all tours
    tours = Tour.get_all()
    if not tours:
        console.print("[yellow]No tours found.[/yellow]")
        return
    console.print("[blue]Available Tours:[/blue]")
    for tour in tours:
        console.print(f"ID: {tour.id}, Name: {tour.name}")
    # Get tour ID from the user
    tour_id = validate_integer_input("Enter the Tour ID to view events: ")
    tour = Tour.find_by_id(tour_id)
    if not tour:
        console.print("[red]Tour not found.[/red]")
        return
    # Get events for the tour
    events = tour.get_events()
    if not events:
        console.print(f"[yellow]No events found for tour {tour.name}.[/yellow]")
        return
    # Display events in the tour
    console.print(f"[green]Events for Tour {tour.name}: [/green]")
    table = Table(title=f"Events in {tour.name}")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Date", style="green")
    table.add_column("Location", style="blue")
    table.add_column("Description", style="yellow")
    for event in events:
        table.add_row(str(event.id), event.name, event.date, event.location, event.description)
    console.print(table)

def search_tour_by_name():
    # Fetch all tours to display available options
    tours = Tour.get_all()
    if tours:
        console.print("[blue]Available Tours:[/blue]")
        for tour in tours:
            console.print(f"ID: {tour.id}, Name: [bold magenta]{tour.name}[/bold magenta]")
    else:
        console.print("[yellow]No tours found. Please create a tour first.[/yellow]")
        return
    # Prompt user for tour name to search
    name = input("Enter tour name to search: ").strip()
    # Find matching tours based on the name provided
    matching_tours = [tour for tour in tours if name.lower() in tour.name.lower()]
    if matching_tours:
        # Create a table with styled columns to display the matching tours
        table = Table(title=f"[bold green]Tours Matching: '{name}'[/bold green]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Start Date", style="yellow")
        table.add_column("End Date", style="yellow")
        table.add_column("Events", style="blue")
        # Loop through matching tours and display them in the table
        for tour in matching_tours:
            events = tour.get_events()  # Get events for each tour
            events_str = ", ".join([event.name for event in events]) if events else "No Events"
            table.add_row(
                str(tour.id), tour.name, tour.description, tour.start_date, tour.end_date, events_str)
        console.print(table)
    else:
        console.print(f"[yellow]No tour found with the name '{name}'.[/yellow]")

def create_artist():
    while True:  # Keep prompting the user until valid input is provided
        try:
            # Prompting user for artist information
            name = input("Enter Artist Name: ").strip()
            if len(name) == 0:
                raise ValueError("Artist Name must not be empty.")
            
            hometown = input("Enter Artist Hometown: ").strip()
            if len(hometown) == 0:
                raise ValueError("Artist Hometown must not be empty.")
            
            love_for_music = input("Why does the artist love music? ").strip()
            if len(love_for_music) == 0:
                raise ValueError("Love for music must not be empty.")
            
            future_goals = input("Where does the artist see themselves in 5 years? ").strip()
            if len(future_goals) == 0:
                raise ValueError("Future goals must not be empty.")
            
            social_media = input("Enter Artist's Social Media Handles (comma-separated): ").strip()
            if len(social_media) == 0:
                raise ValueError("Social media handles must not be empty.")
            
            # Prompt for artist email
            email = input("Enter Artist Email: ").strip()
            if len(email) == 0:
                raise ValueError("Artist Email must not be empty.")

            # Create the artist using the Artist model
            artist = Artist.create(name, hometown, love_for_music, future_goals, social_media, email)
            console.print(f"[green]Artist {artist.name} created successfully![/green]")

            # Now, prompt to assign events to the artist
            events = Event.get_all()
            if events:
                console.print("[blue]Available Events:[/blue]")
                for event in events:
                    console.print(f"ID: {event.id}, Name: {event.name}")
                
                # Allow the user to select multiple events (comma-separated input)
                event_ids = input("Enter comma-separated Event IDs to assign to this artist (or leave blank to skip): ").split(',')
                event_ids = [event_id.strip() for event_id in event_ids if event_id.strip().isdigit()]
                
                # Assign selected events to the artist
                for event_id in event_ids:
                    event = Event.find_by_id(event_id)
                    if event:
                        artist.add_event(event)  # Assuming the Artist model has an `add_event()` method
                        console.print(f"[green]Event {event.name} assigned to artist {artist.name}.[/green]")
                    else:
                        console.print(f"[yellow]Event ID {event_id} not found.[/yellow]")
            else:
                console.print("[yellow]No events available to assign. Please create an event first.[/yellow]")

            break  # Exit the loop on success
        
        except ValueError as e:
            # Catching the validation error and prompting user to try again
            console.print(f"[red]Error: {e}. Please provide valid input.[/red]")
def list_all_artists():
    artists = Artist.get_all()  # Retrieve all artists from the database
    if artists:
        # Create a table to display artist information
        table = Table(title="[bold blue]All Artists[/bold blue]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Hometown", style="green")
        table.add_column("Love for Music", style="yellow")
        table.add_column("Future Goals", style="cyan")
        table.add_column("Social Media", style="magenta")
        table.add_column("Email", style="blue")

        # Add each artist to the table
        for artist in artists:
            table.add_row(str(artist.id), artist.name, artist.hometown, artist.love_for_music,
                          artist.future_goals, artist.social_media, artist.email)

        console.print(table)  # Display the table in the console
    else:
        console.print("[yellow]No artists found.[/yellow]")  # If no artists are found, display a message

def list_events():
    events = Event.get_all()
    if events:
        table = Table(title="[bold red]Events List[/bold red]")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Date", justify="center", style="green")
        table.add_column("Location", style="blue")
        table.add_column("Description", style="magenta")
        table.add_column("Artists", style="yellow")  # Add a new column for artists

        for event in events:
            artists_names = ", ".join([artist.name for artist in event.artists]) if event.artists else "No Artists"
            table.add_row(str(event.id), event.name, event.date, event.location, event.description, artists_names)

        console.print(table)
    else:
        console.print("[yellow]No events found.[/yellow]")
def assign_artist_to_event():
    # List all events to select from
    events = Event.get_all()
    if not events:
        console.print("[yellow]No events found.[/yellow]")
        return

    console.print("[blue]Available Events:[/blue]")
    for event in events:
        console.print(f"ID: [cyan]{event.id}[/cyan], Name: {event.name}")

    # Get event ID from the user
    event_id = validate_integer_input("Enter the Event ID to assign an artist to: ")
    event = Event.find_by_id(event_id)

    if not event:
        console.print("[red]Event not found.[/red]")
        return

    # List all artists to select from
    artists = Artist.get_all()
    if not artists:
        console.print("[yellow]No artists found.[/yellow]")
        return

    console.print("[blue]Available Artists:[/blue]")
    for artist in artists:
        console.print(f"ID: [cyan]{artist.id}[/cyan], Name: {artist.name}")

    # Get artist ID from the user
    artist_id = validate_integer_input("Enter the Artist ID to add to the event: ")
    artist = Artist.find_by_id(artist_id)

    if not artist:
        console.print("[red]Artist not found.[/red]")
        return

    # Add the artist to the event
    try:
        event.add_artist(artist)
        console.print(f"[green]Artist {artist.name} assigned to event {event.name}.[/green]")
    except ValueError as e:
        console.print(f"[red]{str(e)}[/red]")

def normalize_name(name):
    """Helper function to remove spaces and convert to lowercase."""
    return name.replace(" ", "").lower()

def find_artist_by_name():
    # Fetch all artists to display available options
    artists = Artist.get_all()
    if artists:
        console.print("[blue]Available Artists:[/blue]")
        for artist in artists:
            console.print(f"ID: [cyan]{artist.id}[/cyan], Name: [bold magenta]{artist.name}[/bold magenta]")
    else:
        console.print("[yellow]No artists found. Please create an artist first.[/yellow]")
        return

    # Prompt user to enter artist name to search
    name = input("Enter artist name to search: ").strip()

    # Find matching artists based on the name provided
    matching_artists = [artist for artist in artists if name.lower() in artist.name.lower()]
    if matching_artists:
        # Create a table to display the matching artists and their associated details
        table = Table(title=f"[bold green]Artists Matching: '{name}'[/bold green]")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Hometown", style="green")
        table.add_column("Love for Music", style="yellow")
        table.add_column("Future Goals", style="cyan")
        table.add_column("Social Media", style="magenta")
        table.add_column("Email", style="blue")
        table.add_column("Events", style="green")  # Column for Events
        table.add_column("Favorited By", style="yellow")  # Column for Attendees
        table.add_column("Songs", style="red")  # New column for Songs

        # Loop through matching artists and display them in the table
        for artist in matching_artists:
            # Fetch the events the artist is attending
            events = artist.get_events()  # Assuming you have a method to fetch artist's events
            events_str = ", ".join([event.name for event in events]) if events else "No Events"

            # Fetch the attendees who favorited the artist
            favorite_by_attendees = artist.get_favorite_by_attendees()  # Fetch attendees who favorited the artist
            attendees_str = ", ".join([attendee.name for attendee in favorite_by_attendees]) if favorite_by_attendees else "No Favorites"

            # Fetch the songs associated with the artist
            songs = artist.get_songs()  # Assuming you have a method to fetch artist's songs
            songs_str = ", ".join([song.title for song in songs]) if songs else "No Songs"

            # Add the artist, their events, attendees, and songs to the table
            table.add_row(
                str(artist.id), 
                artist.name, 
                artist.hometown, 
                artist.love_for_music, 
                artist.future_goals, 
                artist.social_media, 
                artist.email, 
                events_str,  # Add events to the new column
                attendees_str,  # Add attendees who favorited the artist
                songs_str  # Add songs to the new column
            )

        # Display the table
        console.print(table)
    else:
        console.print(f"[yellow]No artist found with the name '{name}'.[/yellow]")

def create_song():
    while True:  # Keep prompting the user until valid input is provided
        try:
            # Fetch all artists to display
            artists = Artist.get_all()
            if not artists:
                console.print("[red]No artists available. Please create an artist before adding a song.[/red]")
                return  # Exit if no artists are available
            console.print("[blue]Available Artists:[/blue]")
            for artist in artists:
                console.print(f"ID: [cyan]{artist.id}[/cyan], Name: {artist.name}")
            # Prompt the user for the artist ID
            artist_id = validate_integer_input("Enter the Artist ID for this song: ")
            artist = Artist.find_by_id(artist_id)
            if not artist:
                console.print("[red]Artist not found. Please try again.[/red]")
                continue  # Go back to prompt for valid Artist ID
            title = input("Enter Song Title: ").strip()
            genre = input("Enter Song Genre: ").strip()
            release_date = input("Enter Release Date: ").strip()
            # Create the song using the Song model
            song = Song.create(title, genre, release_date, artist_id)
            console.print(f"[green]Song '{song.title}' created for artist {artist.name}.[/green]")
            break  # Exit loop on success
        except ValueError as e:
            console.print(f"[red]Error: {e}. Please try again with valid input.[/red]")
def list_songs_by_artist():
    # Fetch all artists to display
    artists = Artist.get_all()
    if not artists:
        console.print("[red]No artists available. Please create an artist before listing songs.[/red]")
        return  # Exit if no artists are available
    console.print("[blue]Available Artists:[/blue]")
    for artist in artists:
        console.print(f"ID: [cyan]{artist.id}[/cyan], Name: {artist.name}")
    # Prompt the user for the Artist ID
    artist_id = validate_integer_input("Enter the Artist ID to list songs: ")
    artist = Artist.find_by_id(artist_id)
    if artist:
        songs = artist.get_songs()
        if songs:
            table = Table(title=f"[bold blue]Songs by {artist.name}[/bold blue]")
            table.add_column("ID", justify="right", style="cyan")
            table.add_column("Title", style="magenta")
            table.add_column("Genre", style="green")
            table.add_column("Release Date", style="yellow")
            for song in songs:
                table.add_row(str(song.id), song.title, song.genre, song.release_date)
            console.print(table)
        else:
            console.print(f"[yellow]No songs found for artist {artist.name}.[/yellow]")
    else:
        console.print("[red]Artist not found.[/red]")

def delete_song():
    song_id = validate_integer_input("Enter Song ID to delete: ")
    song = Song.find_by_id(song_id)
    if song:
        song.delete()
        console.print(f"[red]Song '{song.title}' deleted.[/red]")
    else:
        console.print("[yellow]Song not found.[/yellow]")

def reset_database():
    console.print("[bold red]WARNING: This will reset the entire database and delete all data![/bold red]")
    confirm = input("Are you sure you want to reset the database? (yes/no): ").strip().lower()    
    if confirm == 'yes':
        console.print("[yellow]Resetting database...[/yellow]")
        # Drop existing tables
        Tour.drop_table()
        Event.drop_table()
        Attendee.drop_table()
        Venue.drop_table()
        Song.drop_table()  # Drop the songs table
        Artist.drop_table()  # Drop the artists table
        # Recreate the tables
        Tour.create_table()
        Event.create_table()
        Attendee.create_table()
        Venue.create_table()
        Song.create_table()  # Recreate the songs table
        Artist.create_table()  # Recreate the artists table
        console.print("[green]Database has been reset![/green]")
    else:
        console.print("[blue]Database reset canceled.[/blue]")

def delete_tour():
    # List all tours for the user to select from
    tours = Tour.get_all()
    if not tours:
        console.print("[yellow]No tours found.[/yellow]")
        return
    
    console.print("[blue]Available Tours:[/blue]")
    for tour in tours:
        console.print(f"ID: {tour.id}, Name: {tour.name}")

    # Prompt user to input the tour ID to delete
    tour_id = validate_integer_input("Enter the Tour ID to delete: ")
    tour = Tour.find_by_id(tour_id)

    if not tour:
        console.print("[red]Tour not found.[/red]")
        return

    # Delete the selected tour
    tour.delete()
    console.print(f"[red]Tour {tour.name} has been deleted.[/red]")

def main():
    while True:  # Infinite loop to keep the program running
        menu()   # Display the menu options
        choice = input("> ").strip()  # Get user's choice and strip any leading/trailing whitespace

        # Venue Options
        if choice == "1":
            create_venue()
        elif choice == "2":
            add_existing_venue_to_event()
        elif choice == "3":
            list_venues()
        elif choice == "4":
            search_venue_by_name()
        elif choice == "5":
            delete_venue()

        # Event Options
        elif choice == "6":
            create_event()
        elif choice == "7":
            assign_artist_to_event()  # Assign artist to event
        elif choice == "8":
            list_events()
        elif choice == "9":
            find_event_by_name()
        elif choice == "10":
            delete_event()

        # Attendee Options
        elif choice == "11":
            add_attendee()
        elif choice == "12":
            add_existing_attendee_to_event()
        elif choice == "13":
            remove_attendee_from_event()
        elif choice == "14":
            list_all_attendees()
        elif choice == "15":
            find_attendee_by_name()
        elif choice == "16":
            delete_attendee()

        # Tour Options
        elif choice == "17":
            create_tour()
        elif choice == "18":
            search_tour_by_name()
        elif choice == "19":
            list_tours()
        elif choice == "20":
            remove_event_from_tour()
        elif choice == "21":
            delete_tour()

        # Artist and Song Options
        elif choice == "22":
            create_artist()
        elif choice == "23":
            find_artist_by_name()
        elif choice == "24":
            list_all_artists()
        elif choice == "25":
            create_song()
        elif choice == "26":
            list_songs_by_artist()
        elif choice == "27":
            delete_song()

        # Reset/Delete Options
        elif choice == "0":
            exit_program()
        elif choice == "99":
            reset_database()

        # Invalid input handling
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

#function to display menu 
def menu():
    # Create a Table instance
    table = Table(title="CLI Application Menu")

    # Define the columns
    table.add_column("Venue Options", style="cyan", justify="left")
    table.add_column("Event & Attendee Options", style="magenta", justify="left")
    table.add_column("Tour Options", style="green", justify="left")
    table.add_column("Artist & Song Options", style="yellow", justify="left")

    # Add the venue options
    table.add_row(
        "1. Create Venue", 
        "6. Create Event", 
        "17. Create Tour", 
        "22. Create Artist"
    )
    table.add_row(
        "2. Add Existing Venue to Event", 
        "7. Assign Artist to Event", 
        "18. Search Tour by Name", 
        "23. Search Artist by Name"
    )
    table.add_row(
        "3. List All Venues", 
        "8. List All Events", 
        "19. List All Tours", 
        "24. List All Artists"
    )
    table.add_row(
        "4. Search Venue by Name", 
        "9. Search Event by Name", 
        "20. Remove Event from Tour", 
        "[green]--- Song Options ---[/green]"
    )
    table.add_row(
        "5. Delete Venue", 
        "10. Delete Event", 
        "21. Delete Tour", 
        "25. Create Song"
    )

    # Add a separator and then the attendee options under event column
    table.add_row("", "[yellow]--- attendee options ---[/yellow]", "", "")
    table.add_row("", "11. Add Attendee", "", "26. List Songs by Artist")
    table.add_row("", "12. Add Existing Attendee to Event", "", "27. Delete Song")
    table.add_row("", "13. Remove Attendee from Event", "", "")
    table.add_row("", "14. List All Attendees", "", "")
    table.add_row("", "15. Search Attendee by Name", "", "")
    table.add_row("", "16. Delete Attendee", "", "")

    # Add the reset/delete options
    table.add_row("[bold red]0. Exit Program[bold red]", "", "", "[bold red]99. Reset Database[/bold red]")

    # Display the table
    console.print(table)
if __name__ == "__main__":
    main()
