from flask import Blueprint, request, jsonify

from api_services import EventService, BookingService


event_apis = Blueprint('event_apis', __name__, url_prefix='/api/v1')


@event_apis.route('/events/create/', methods=['POST'])
@event_apis.route('/events/update/<int:event_id>/', methods=['PUT'])
def create_update_event(event_id=None):
    request_object = request.json
    service = EventService()
    if event_id:
        event_object = service.update_event(
            request_data=request_object, event_id=event_id)
    else:
        event_object = service.create_event(request_data=request_object)
    return jsonify(id=event_object.id, event_name=event_object.event_name)


# ToDo: Pagination parameters
@event_apis.route('/events/', methods=['GET'])
@event_apis.route('/events/<int:event_id>/', methods=['GET'])
def get_events(event_id=None):
    service = EventService()
    event_details = service.get_events(event_id=event_id)
    return jsonify(data=event_details)


@event_apis.route('/events/add/tickets/', methods=['POST'])
def add_tickets():
    request_object = request.json
    service = EventService()
    booking_ticket_details = service.add_tickets(request_data=request_object)
    return jsonify(msg='Tickets added. Please verify in events listing/details api')


@event_apis.route('/events/<int:event_id>/redeem/tickets/', methods=['POST'])
def redeem_tickets(event_id):
    request_object = request.json
    service = BookingService()
    booking_ticket_details = service.redeem_tickets(
        event_id=event_id, request_data=request_object)
    return jsonify(data=[{'ticket_id': booking.id, 'seat': booking.seat_id} for booking in booking_ticket_details])


@ event_apis.route('/events/cancel/tickets/', methods=['POST'])
def cancel_tickets():
    request_object = request.json
    service = BookingService()
    booking_ticket_details = service.cancel_tickets(
        request_data=request_object)
    return jsonify(data=request_object.get('ticket_ids'), msg='Succesfully cancelled.')
