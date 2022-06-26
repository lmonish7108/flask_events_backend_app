from sqlalchemy import (
    Column,
    Integer,
    func,
    String,
    DateTime,
    ForeignKey,
)
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import backref, relationship


class AuditFields(Base):
    __abstract__ = True

    created_on = Column(DateTime, default=func.now())
    updated_on = Column(DateTime, default=func.now(),
                        onupdate=func.now())


class TypeMetaData(AuditFields):
    __tablename__ = 'typemetadata'

    id = Column(Integer, primary_key=True)
    model_name = Column(String(30), nullable=False)
    column_name = Column(String(30), nullable=False)
    value = Column(String(30), nullable=False)

    def __repr__(self):
        return '<TypeMetadata %r>' % self.value


class Event(AuditFields):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    event_name = Column(String(80), unique=True, nullable=False)
    event_type_id = Column(Integer, ForeignKey("typemetadata.id"))

    event_type = relationship("TypeMetaData")

    def __repr__(self):
        return '<Event name %r>' % self.event_name


class Location(AuditFields):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    # venues = relationship('Venue', backref='venues')

    def __repr__(self):
        return '<Location %r>' % self.name


class Venue(AuditFields):
    __tablename__ = 'venue'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"))

    location = relationship('Location')

    def __repr__(self):
        return '<Venue %r>' % self.name


class EventVenue(AuditFields):
    __tablename__ = 'eventvenue'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("event.id"))
    venue_id = Column(Integer, ForeignKey("venue.id"))

    event = relationship('Event')
    venue = relationship('Venue')

    # event_ticket_details = relationship(
    #     'EventTicketDetail', backref='event_ticket_details')

    def __repr__(self):
        return '<EventVenue %r>' % self.id


class EventTicketDetail(AuditFields):
    __tablename__ = 'eventticketdetail'

    id = Column(Integer, primary_key=True)
    event_venue_id = Column(Integer, ForeignKey("eventvenue.id"))
    total_tickets = Column(Integer, nullable=False)
    available_tickets = Column(Integer, nullable=False)
    per_ticket_price = Column(Integer, nullable=False)

    # bookings = relationship('BookingDetail', backref="bookings")
    event_venue = relationship('EventVenue')

    def __repr__(self):
        return '<EventTicketDetail %r>' % self.id


class PaymentDetail(AuditFields):
    __tablename__ = 'paymentdetail'

    id = Column(Integer, primary_key=True)
    payment_type_id = Column(Integer, ForeignKey("typemetadata.id"))
    description = Column(String(80), nullable=False)

    # bookings = relationship('BookingDetail', backref='bookings')
    payment_type = relationship('TypeMetaData')

    def __repr__(self):
        return '<PaymentDetail %r>' % self.id


class BookingDetail(AuditFields):
    __tablename__ = 'bookingdetail'

    id = Column(Integer, primary_key=True)
    event_ticket_detail_id = Column(
        Integer, ForeignKey("eventticketdetail.id"))
    booked_by = Column(String(80), nullable=False)
    quantity = Column(Integer, nullable=False)
    payment_detail_id = Column(Integer, ForeignKey("paymentdetail.id"))
    amount_paid = Column(Integer, nullable=False)

    # booking_ticket_details = relationship(
    #     'BookingTicketDetail', backref='booking_ticket_details')
    event_ticket_detail = relationship('EventTicketDetail')
    payment_detail = relationship('PaymentDetail')

    def __repr__(self):
        return '<BookingDetail %r>' % self.id


class BookingTicketDetail(AuditFields):
    __tablename__ = 'bookingdetaildetail'

    id = Column(Integer, primary_key=True)
    booking_detail_id = Column(Integer, ForeignKey("bookingdetail.id"))
    seat_id = '2A'  # To be implemented

    booking_detail = relationship('BookingDetail')

    def __repr__(self):
        return '<BookingTicketDetail %r>' % self.id


class SeatsMapping:
    # To be implemented, will be foreign key to BookingTicketDetail
    # While creating event a script will run to create SeatsMapping records
    # and event and seats details will be records
    pass
