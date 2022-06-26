## Note: Currently I am using windows so some steps might differ during setup
- Install virtualenv
    -  py -m pip install virtualenv
- Activate virtualenv
    - .\venv\Scripts\activate.bat
- Install flask, sqlalchemy
- Clone repository
- cd to project folder
    - Open database.py and change path for DB creation to your workspace path.
- Run application
    - python .\application.py

### Database Architecture
- An Event can be at more than one venues
- A Venue can have more than one Events
- A Location can have more than one venues
- Events can be of different types
- Tickets, Prices will be in EventTicketDetails linked to EventVenue, to support event hosted at many venues.
- BookingDetail will have all details.
- BookingTicketDetail will have ticket id and seat id




### Postman collection:
https://gitlab.com/monish-lalchandani/flask_events_backend_app/-/blob/master/Flask%20-%20backend%20-%20code%20assessment.postman_collection.json
