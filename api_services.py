from database import db_session

from api_daos import EventDAO, EventVenueDAO, EventTicketDetailDAO, BookingDetailDAO, BookingTicketDetailDAO, PaymentDetailDAO


class EventService:

    dao = EventDAO

    def get_events(self, event_id=None):
        events = self.dao.get_event_details(event_id)
        if not events:
            return {}
        if event_id:
            return events._asdict()
        return [row._asdict() for row in self.dao.get_event_details(event_id)]

    def create_event(self, request_data):
        event_record = self.dao.create_record(request_data)
        db_session.commit()
        return event_record

    def update_event(self, request_data, event_id):
        event_record = self.dao.update_record(request_data, event_id)
        db_session.commit()
        return event_record

    def add_tickets(self, request_data):
        event_venue = EventVenueDAO.get_or_create_record(
            {'event_id': request_data.get('event_id'), 'venue_id': request_data.get('venue_id')})
        event_ticket_detail = EventTicketDetailDAO.add_tickets(
            event_venue_id=event_venue.id, num_of_tickets=request_data.get('num_of_tickets'))
        db_session.commit()
        return event_ticket_detail


class BookingService:

    def redeem_tickets(self, event_id, request_data):
        event_venue = EventVenueDAO.get_or_create_record(
            {'event_id': event_id, 'venue_id': request_data.get('venue_id')})
        event_ticket_detail = EventTicketDetailDAO.redeem_tickets(
            event_venue_id=event_venue.id, num_of_tickets=request_data.get(
                'num_of_tickets'), amount_paid=request_data.get('amount_paid'))
        # Once tickets are redeemed create booking details
        payment_detail = PaymentDetailDAO.get_or_create_record({})
        booking_detail = BookingDetailDAO.get_or_create_record(
            {'event_ticket_detail_id': event_ticket_detail.id, 'booked_by': request_data.get('booked_by'),
             'quantity': request_data.get('num_of_tickets'), 'payment_detail_id': payment_detail.id,
             'amount_paid': request_data.get('amount_paid')})
        booking_ticket_details = []
        for _ in range(request_data.get('num_of_tickets')):
            booking_ticket_details.append(BookingTicketDetailDAO.create_record(
                booking_detail_id=booking_detail.id))
        db_session.commit()
        return booking_ticket_details

    def cancel_tickets(self, request_data):
        tickets_cancelled = BookingTicketDetailDAO.cancel_tickets(
            ticket_ids=request_data.get('ticket_ids'))
        db_session.commit()
        return tickets_cancelled
