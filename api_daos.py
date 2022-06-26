from statistics import mode
from flask import request
from models import (Event, Venue, EventVenue, Location, EventTicketDetail,
                    TypeMetaData, BookingDetail, BookingTicketDetail, PaymentDetail)
from database import db_session


class BaseDAO:

    @classmethod
    def get_or_create_record(cls, filters):
        record = db_session.query(cls.model).filter_by(**filters).first()
        if not record:
            record = cls.create_record(filters)
        return record

    @classmethod
    def create_record(cls, request_data):
        record = cls.model(**request_data)
        db_session.add(record)
        db_session.flush()
        return record


class TypeMetaDataDAO(BaseDAO):

    model = TypeMetaData


class EventDAO(BaseDAO):

    model = Event

    @classmethod
    def get_event_details(cls, event_id=None):
        fields = [
            Event.id, Event.event_name, Venue.name.label('venue'),
            TypeMetaData.value.label('event_type'),
            Location.name.label('location'),
            EventTicketDetail.available_tickets, EventTicketDetail.total_tickets,
            EventTicketDetail.per_ticket_price
        ]

        event_details = db_session.query(*fields).select_from(Event).filter(
            Event.id == EventVenue.event_id,
            Event.event_type_id == TypeMetaData.id,
            EventVenue.venue_id == Venue.id,
            Venue.location_id == Location.id,
            EventVenue.id == EventTicketDetail.event_venue_id,
        )
        if event_id:
            event_details = event_details.filter_by(id=event_id).first()
            return event_details
        return event_details.all()

    @classmethod
    def get_or_create_record(cls, filters):
        raise NotImplementedError

    @classmethod
    def create_record(cls, request_data):
        event_record = db_session.query(
            cls.model).filter_by(event_name=request_data.get('event_name')).first()
        if event_record:
            raise Exception('Event already present')
        event_type_data = {
            'model_name': cls.model.__tablename__,
            'column_name': 'event_type_id',
            'value': request_data.get('event_type')
        }
        event_type = TypeMetaDataDAO.get_or_create_record(event_type_data)
        event_record = cls.model(
            event_name=request_data.get('event_name'),
            event_type=event_type
        )
        db_session.add(event_record)
        db_session.flush()
        event_location = LocationDAO.get_or_create_record(
            {'name': request_data.get('location')})
        venue = VenueDAO.get_or_create_record({'name': request_data.get(
            'venue'), 'location_id': event_location.id})
        event_venue = EventVenueDAO.get_or_create_record(
            {'event_id': event_record.id, 'venue_id': venue.id})
        event_ticket_detail = EventTicketDetailDAO.create_record(
            {'event_venue_id': event_venue.id, 'total_tickets': request_data.get('total_tickets'),
             'available_tickets': request_data.get('total_tickets'),
             'per_ticket_price': request_data.get('per_ticket_price')})
        return event_record

    # Assuming user is creating only unique events
    @classmethod
    def update_record(cls, request_data, event_id):
        event_record = db_session.query(
            cls.model).filter_by(id=event_id).first()
        if not event_record:
            raise Exception('Invalid ID')
        event_record.event_name = request_data.get('event_name')
        event_type_data = {
            'model_name': cls.model.__tablename__,
            'column_name': 'event_type',
            'value': request_data.get('event_type')
        }
        event_type = TypeMetaDataDAO.get_or_create_record(event_type_data)
        event_record.event_type = event_type
        db_session.add(event_record)
        db_session.flush()
        event_location = LocationDAO.get_or_create_record(
            {'name': request_data.get('location')})
        venue = VenueDAO.get_or_create_record({'name': request_data.get(
            'venue'), 'location_id': event_location.id})
        event_venue = EventVenueDAO.get_or_create_record(
            {'event_id': event_record.id, 'venue_id': venue.id})
        return event_record


class VenueDAO(BaseDAO):

    model = Venue


class EventVenueDAO(BaseDAO):

    model = EventVenue


class LocationDAO(BaseDAO):

    model = Location


class EventTicketDetailDAO(BaseDAO):

    model = EventTicketDetail

    @classmethod
    def add_tickets(cls, event_venue_id, num_of_tickets):
        event_ticket_detail_record = db_session.query(
            cls.model).filter_by(event_venue_id=event_venue_id).first()
        if not event_ticket_detail_record:
            raise Exception('Invalid ID')
        event_ticket_detail_record.total_tickets += num_of_tickets
        event_ticket_detail_record.available_tickets += num_of_tickets
        db_session.add(event_ticket_detail_record)
        db_session.flush()
        return event_ticket_detail_record

    @classmethod
    def redeem_tickets(cls, event_venue_id, num_of_tickets, amount_paid):
        event_ticket_detail_record = db_session.query(
            cls.model).filter_by(event_venue_id=event_venue_id).first()
        if not event_ticket_detail_record:
            raise Exception('Invalid ID')
        if num_of_tickets <= event_ticket_detail_record.available_tickets and event_ticket_detail_record.per_ticket_price*num_of_tickets == amount_paid:
            event_ticket_detail_record.available_tickets -= num_of_tickets
            db_session.add(event_ticket_detail_record)
            db_session.flush()
            return event_ticket_detail_record
        raise Exception('Tickets not available or price incorrect')


class BookingDetailDAO(BaseDAO):

    model = BookingDetail


class BookingTicketDetailDAO:

    model = BookingTicketDetail

    @classmethod
    def create_record(cls, booking_detail_id):
        booking_ticket_detail = BookingTicketDetail(
            booking_detail_id=booking_detail_id)
        db_session.add(booking_ticket_detail)
        db_session.flush()
        return booking_ticket_detail

    # Currently: assuming all ticket_ids are valid and belong to same booking id
    @classmethod
    def cancel_tickets(cls, ticket_ids):
        booking_ticket_details = db_session.query(EventTicketDetail.event_venue_id).select_from(
            cls.model).filter(cls.model.id.in_(ticket_ids),
                              cls.model.booking_detail_id == BookingDetail.id,
                              BookingDetail.event_ticket_detail_id == EventTicketDetail.id).all()
        EventTicketDetailDAO.add_tickets(
            booking_ticket_details[0].event_venue_id, len(ticket_ids))
        db_session.query(cls.model).filter(
            cls.model.id.in_(ticket_ids)).delete(synchronize_session=False)
        return ticket_ids


class PaymentDetailDAO(BaseDAO):

    model = PaymentDetail

    @classmethod
    def get_or_create_record(cls, request_data):  # hardcoded implementation for now
        payment_type_data = {
            'model_name': cls.model.__tablename__,
            'column_name': 'payment_type_id',
            'value': 'Internet banking'  # Harcoded for now
        }
        payment_type = TypeMetaDataDAO.get_or_create_record(payment_type_data)
        return super().get_or_create_record({
            'payment_type_id': payment_type.id,
            'description': 'Online Payment'
        })
