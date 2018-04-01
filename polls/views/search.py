import datetime

from django.template import loader
from django.utils import timezone
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from ..models import Flight, FlightOccupiedSeat, Airline, Airport


def search(request):
    '''
    Logic to search flight
    '''
    template = loader.get_template('polls/search.html')
    current_date = datetime.datetime.now()

    # If we jump back for second trip of round trip
    if request.session.get('round_way', False):
        request.session['round_way'] = True
        # back trip of round trip, reverse from and to location
        from_location = request.session['to_location']
        to_location = request.session['from_location']
        passenger = request.session['passenger']
        # Although we still call it leave_date, but it is actully return date
        leave_date = request.session['return_date_search']
        leave_date_tom = getTomorrowDate(leave_date)
        leave_day = getDayFromDate(leave_date)
    # One way trip or first search of round trip
    else:
        from_location = request.POST['from']
        from_location = from_location[1:4]
        to_location = request.POST['to']
        to_location = to_location[1:4]
        request.session['from_location'] = from_location
        request.session['to_location'] = to_location
        # Get trip type
        if request.POST['trip_type'] == "0":
            request.session['trip_type'] = 0  # one way
        else:
            request.session['trip_type'] = 1  # round trip
        request.session['round_way'] = False
        # Put passenger number into session for book use
        passenger = request.POST['passenger_number']
        request.session['passenger'] = passenger
        # leave date
        leave_date = timezone.now(
        ) if request.POST['leave'] is None else request.POST['leave']
        leave_date_tom = getTomorrowDate(leave_date)
        leave_day = getDayFromDate(leave_date)
        request.session['leave_date_search'] = leave_date
        # return date
        return_date = (timezone.now() + datetime.timedelta(days=1)
                       ) if request.POST['return'] is None else request.POST['return']
        request.session['return_date_search'] = return_date
        # return_day = getDayFromDate(return_date)

    # Get discount
    date_delta = datetime.datetime.strptime(
        leave_date, '%Y-%m-%d')-current_date
    request.session['discount'] = getDiscount(date_delta.days)

    # Get direct flight
    request.session['direct_flight'] = {}
    direct_result = Flight.objects.filter(Q(depart_airport=from_location) &
                                          Q(arrive_airport=to_location) & (Q(workday=(getDayFromDate(leave_date_tom) % 2)) | Q(workday=(leave_day % 2))),)
    # Check if each result has available seat
    available_result = set()
    for d_f in direct_result:
        # Change workday from 0,1 to real date
        if d_f.workday == leave_day % 2:
            d_f.workday = leave_date
        else:
            d_f.workday = leave_date_tom
        if flight_capacity_full_check(d_f.fid, d_f.workday, d_f.capacity):
            available_result.add(d_f)
    direct_result = available_result
    for i, d_f in enumerate(direct_result):
        d_f.id = str(i)
        d_f.fare = d_f.fare*request.session['discount']
        # Put direct flight FID into into session for book use
        # We also need to save leave date
        request.session['direct_flight'][i] = str(d_f.fid)+","+d_f.workday
        request.session.modified = True

    # Get one_stop flight
    request.session['one_stop_flight'] = {}
    # As in db we use 0 and 1 represent workday. So if it is 0, then it only works on even day
    # If it is 1, it only works on odd day
    one_stop_today = one_stop_flight(
        from_location, to_location, leave_day % 2, (leave_day+1) % 2)
    one_stop_tomorrow = one_stop_flight(
        from_location, to_location, (leave_day+1) % 2, (leave_day+2) % 2)
    one_stop_result = set()
    index = 0
    # One flight today and one flight tomorrow
    index = fetch_one_stop_flights(
        one_stop_today, index, one_stop_result, leave_date, leave_date_tom, request, 1)
    # One stop tomorrow and one stop the day after tomorrow
    index2 = fetch_one_stop_flights(
        one_stop_tomorrow, index, one_stop_result, leave_date, leave_date_tom, request, 0)

    # Distinguish between jump from search to book and buy to book(back due to duplicate names)
    request.session['duplicate_name'] = None
    request.session['book_fid'] = None
    request.session['leave_date'] = None
    context = {
        'direct_flight': direct_result,
        'one_stop_flight': one_stop_result,
        'leave_date': leave_date,
    }
    return HttpResponse(template.render(context, request))


def fetch_one_stop_flights(data, index, one_stop_result, leave_date, leave_date_tom, request, flag):
    for f in data:
        fid1 = f[16]
        fid2 = f[17]
        cap1 = f[18]
        cap2 = f[19]
        date1 = leave_date if flag else leave_date_tom
        date2 = leave_date_tom if flag else getTomorrowDate(leave_date_tom)
        # Add it only if both flights still have seats available
        if flight_capacity_full_check(fid1, date1, cap1) and flight_capacity_full_check(fid2, date2, cap2):
            index = index + 1
            airline1 = Airline.objects.get(airline_id=f[0]).airline_name
            airline2 = Airline.objects.get(airline_id=f[8]).airline_name
            d1 = str(Airport.objects.get(airport_id=f[5]))
            a1 = str(Airport.objects.get(airport_id=f[7]))
            d2 = str(Airport.objects.get(airport_id=f[13]))
            a2 = str(Airport.objects.get(airport_id=f[15]))
            f = (airline1,) + f[1:3] + (str(date1),) + (str(f[4]),) + (d1,) + \
                (str(f[6]),) + (a1,) + (airline2,) + f[9:11] + (str(date2),) + \
                (str(f[12]),) + (d2,) + (str(f[14]),) + (a2,) + \
                (index,)  # Append index so that in html we know which one is selected
            one_stop_result.add(f)
            # Put it into sesson for later use
            request.session['one_stop_flight'][index] = str(
                fid1)+","+str(date1)+","+str(fid2)+","+str(date2)
            request.session.modified = True
    return index


def flight_capacity_full_check(fid, date, capacity):
    # If still available return true
    # Else return false
    try:
        f_occupied_object = FlightOccupiedSeat.objects.get(
            fid=fid, date=date)
    except:
        # Except means we get no results from db, which means that flight has no passengers yet
        return True
    if f_occupied_object.occupied_seat >= capacity:
        return False
    return True


def one_stop_flight(start, end, workday1, workday2):
    query = RAW_SQL['ONE_STOP_FLIGHT'].format(start_airport=start, end_airport=end, workday1=workday1,
                                              workday2=workday2)
    # print(query)
    return execute_custom_sql(query)


def execute_custom_sql(s):
    cursor = connection.cursor()
    try:
        cursor.execute(s)
    except:
        return set()
    return cursor.fetchall()


def getDiscount(delta):
    if delta < 3:
        return 1
    elif delta < 7:
        return 0.95
    elif delta < 14:
        return 0.9
    elif delta < 21:
        return 0.8
    elif delta < 30:
        return 0.75
    else:
        return 0.7


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


def getDayFromDate(date):
    '''
    Get day from date like 2018-03-01
    '''
    day = date.split("-")[2]
    i = int(day)
    return i


RAW_SQL = {
    'ONE_STOP_FLIGHT': '''
                SELECT *
                FROM(
                SELECT f1.Airline_ID as f_airline_id, f1.Flight_ID as f_flight_id, f1.Fare as f_fare, f1.Workday as f_workday,
                f1.Depart_time as f_depart_time,f1.Depart_Airport as f_depart_airport, f1.Arrive_time as f_arrive_time,
                f1.Arrive_Airport as f_arrive_airport,f2.Airline_ID as s_airline_id, f2.Flight_ID as s_flight_id, f2.Fare as s_fare,
                f2.Workday as s_worday, f2.Depart_time as s_depart_time,f2.Depart_Airport as s_depart_airport,
                f2.Arrive_time as s_arrive_time, f2.Arrive_Airport as s_arrive_airport, 
                f1.fid as f1_fid, f2.fid as f2_fid, f1.capacity as cap1, f2.capacity as cap2
                FROM Flight f1
                JOIN Flight f2
                WHERE f1.Arrive_Airport=f2.Depart_Airport
                AND f1.workday={workday1} AND f2.workday={workday2}
                ) res
                WHERE f_depart_airport="{start_airport}" AND s_arrive_airport="{end_airport}"
            ''',
}
