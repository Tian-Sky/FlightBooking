import datetime

from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..models import Flight, Airline, Customer, Airport, Customer, Account, ReservationInfo, RfRelation, ReservationFlight, FlightOccupiedSeat


@login_required(login_url='/polls/')
def book(request):
    '''
    Book logic for direct flight
    '''
    template = loader.get_template('polls/book.html')
    request.session['book_type'] = 0
    # Get flight related data
    # We may jump back because passenger name duplicate
    # In this case we do not get fid and date by POST
    if request.session['duplicate_name'] is None:
        fid, date = request.session['direct_flight'][request.POST['id']].split(
            ",")
    else:
        fid = request.session['book_fid']
        date = request.session['leave_date']
    flight = Flight.objects.get(fid=fid)
    flight.fare = flight.fare*request.session['discount']
    flight.workday = date
    if flight.arrive_time.hour < flight.depart_time.hour:
        flight.arrive_date = getTomorrowDate(flight.workday)
        flight.fly_hour = flight.arrive_time.hour + 24 - flight.depart_time.hour
    else:
        flight.arrive_date = flight.workday
        flight.fly_hour = flight.arrive_time.hour - flight.depart_time.hour
    # Get account data
    user = request.user
    # In original db Customer table, we use email as username to log in
    # But in Django auth.user, by default it uses only username and password to log in
    # So we first import all data in Customer table to default auth.user table
    # and set email as username
    cus = Customer.objects.get(email=user.username)
    accounts = Account.objects.filter(customer__customer_id=cus.customer_id)
    # Need to get unique account id and account credit card
    account_hash = set()
    for acc in accounts:
        account_hash.add(str(acc.account_id)+","+str(acc.credit_card))
    account_unique = list()
    for hash in account_hash:
        id, credit_card = hash.split(",")
        ac = {}
        ac['account_id'] = id
        ac['credit_card'] = credit_card
        account_unique.append(ac)
    try:
        loop_times = int(request.session['passenger'])
    except ValueError:
        loop_times = 1
    if flight.depart_airport.city != flight.arrive_airport.city:
        national_info = "International  Travel"
    else:
        national_info = "Domestic  Travel"
    context = {
        'flight': flight,
        'passenger_loop_times': range(loop_times),
        'accounts': account_unique,
        'duplicate_name': request.session['duplicate_name'],
        'national_info': national_info,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='/polls/')
def book_one_stop(request):
    '''
    Book logic for on stop flight
    '''
    template = loader.get_template('polls/book.html')
    request.session['book_type'] = 1  # One stop flight book
    # Get flight related data
    # We may jump back because passenger name duplicate
    # In this case we do not get fid and date by POST
    if request.session['duplicate_name'] is None:
        fid1, date1, fid2, date2 = request.session['one_stop_flight'][request.POST['id']].split(
            ",")
    else:
        fid1 = request.session['book_fid1']
        fid2 = request.session['book_fid1']
        date1 = request.session['leave_date1']
        date2 = request.session['leave_date1']

    f1 = process_flight(fid1, date1, request)
    f2 = process_flight(fid2, date2, request)
    flights = set()
    flights.add(f1)
    flights.add(f2)

    # Get account data
    user = request.user
    # In original db Customer table, we use email as username to log in
    # But in Django auth.user, by default it uses only username and password to log in
    # So we first import all data in Customer table to default auth.user table
    # and set email as username
    cus = Customer.objects.get(email=user.username)
    accounts = Account.objects.filter(customer__customer_id=cus.customer_id)
    # Need to get unique account id and account credit card
    account_hash = set()
    for acc in accounts:
        account_hash.add(str(acc.account_id)+","+str(acc.credit_card))
    account_unique = list()
    for hash in account_hash:
        id, credit_card = hash.split(",")
        ac = {}
        ac['account_id'] = id
        ac['credit_card'] = credit_card
        account_unique.append(ac)
    try:
        loop_times = int(request.session['passenger'])
    except ValueError:
        loop_times = 1
    if f1.depart_airport.city != f2.arrive_airport.city:
        national_info = "International  Travel"
    else:
        national_info = "Domestic  Travel"
    context = {
        'flights': flights,
        'passenger_loop_times': range(loop_times),
        'accounts': account_unique,
        'duplicate_name': request.session['duplicate_name'],
        'national_info': national_info,
        'start': f1,
        'end': f2,
    }
    return HttpResponse(template.render(context, request))


def process_flight(fid, date, request):
    flight = Flight.objects.get(fid=fid)
    flight.fare = flight.fare*request.session['discount']
    flight.workday = date
    if flight.arrive_time.hour < flight.depart_time.hour:
        flight.arrive_date = getTomorrowDate(flight.workday)
        flight.fly_hour = flight.arrive_time.hour + 24 - flight.depart_time.hour
    else:
        flight.arrive_date = flight.workday
        flight.fly_hour = flight.arrive_time.hour - flight.depart_time.hour
    return flight


def getTomorrowDate(date):
    date = list(map(int, date.split("-")))
    date[2] = date[2] + 1
    if date[2] > MONTH_DAY[date[1]]:
        date[2] = 1
        date[1] = date[1]+1
    if date[1] > 12:
        date[1] = 1
        date[0] = date[0]+1
    result = str(date[0])+"-"
    if date[1] < 10:
        result = result + "0"
    result = result + str(date[1])+"-"
    if date[2] < 10:
        result = result + "0"
    result = result + str(date[2])
    return result


MONTH_DAY = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}
