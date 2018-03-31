import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from ..models import Flight, FlightOccupiedSeat, Airline, Airport, Customer, Account, RfRelation, ReservationInfo


@login_required(login_url='/polls/')
def buy(request):
    '''
    Write new reservation data into DB
    First, Check db for duplicate names
    Then, 1.Reservation-Info - 2.Account - 3.RF-Relation - 4.Reservation-Flight
    '''
    # First we need to check if that flight already have thsoe customers
    try:
        # check how many passengers this time
        loop_times = int(request.session['passenger'])
    except ValueError:
        loop_times = 1
    # If direct flight
    if request.session['book_type'] == 0:
        fid = request.POST['fid']  # Flight ID, unique
        request.session['book_fid'] = fid
        leave_date = request.POST['leave_date']  # Flight leave date
        request.session['leave_date'] = leave_date
        name_duplicate, duplicate_name = check_duplicate(
            fid, leave_date, loop_times, request)
        # If name has duplication, we redirect it to buy page with warning
        if name_duplicate:
            request.session['duplicate_name'] = duplicate_name
            return HttpResponseRedirect(reverse('polls:book'))
    # If one stop flight
    else:
        fid1 = request.POST['fid1']  # Flight ID, unique
        request.session['book_fid1'] = fid1
        leave_date1 = request.POST['leave_date1']  # Flight leave date
        request.session['leave_date1'] = leave_date1
        fid2 = request.POST['fid2']  # Flight ID, unique
        request.session['book_fid2'] = fid2
        leave_date2 = request.POST['leave_date2']  # Flight leave date
        request.session['leave_date2'] = leave_date2
        name_duplicate1, duplicate_name1 = check_duplicate(
            fid1, leave_date1, loop_times, request)
        if name_duplicate1:
            request.session['duplicate_name'] = duplicate_name1
            return HttpResponseRedirect(reverse('polls:book'))
        name_duplicate2, duplicate_name2 = check_duplicate(
            fid2, leave_date2, loop_times, request)
        if name_duplicate2:
            request.session['duplicate_name'] = duplicate_name2
            return HttpResponseRedirect(reverse('polls:book'))

    if request.session['book_type'] == 0:
        fid = request.POST['fid']
        cost = request.POST['cost']
        leave_date = request.POST['leave_date']
        save_to_db(fid, cost, loop_times, leave_date, request)
    else:
        fid1 = request.POST['fid1']
        cost1 = request.POST['cost1']
        leave_date1 = request.POST['leave_date1']
        save_to_db(fid1, cost1, loop_times, leave_date1, request)
        fid2 = request.POST['fid2']
        cost2 = request.POST['cost2']
        leave_date2 = request.POST['leave_date2']
        save_to_db(fid2, cost2, loop_times, leave_date2, request)

    return HttpResponseRedirect(reverse('polls:customer'))


def save_to_db(fid, cost, loop_times, leave_date, request):
    # No duplication of names, start to write to db
    # First fetch data from POST and write to Reservation-Info
    # Create order date, which is todyday
    order_date = str(datetime.datetime.now().date())
    # Total cost for this reservation
    total_cost = loop_times * \
        int(float(cost)*request.session['discount'])
    book_fee = int(total_cost*0.1)
    RI = ReservationInfo(order_date=order_date, total_cost=total_cost,
                         book_fee=book_fee, leave_date=leave_date, representative_id="Xinzhang")
    RI.save()

    # Then write to Account
    account_id, credit_card = request.POST['account_id_and_credit_card'].split(
        ",")
    user = request.user
    cus = Customer.objects.get(email=user.username)
    A = Account(customer=cus, account_id=account_id, reservation=RI,
                create_date=order_date, credit_card=credit_card)
    A.save(force_insert=True)

    # Now write to RF-Relation
    F = Flight.objects.get(fid=fid)
    RR = RfRelation(reservation=RI, fid=F, leave_date=leave_date)
    RR.save(force_insert=True)

    # Finally write to Reservation-Flight
    # Get available seat from that flight
    try:
        f_occupied_object = FlightOccupiedSeat.objects.get(
            fid=F.fid, date=leave_date)
    except:
        f_occupied_object = FlightOccupiedSeat(
            fid=F, date=leave_date, occupied_seat=0)
    seat_index = f_occupied_object.occupied_seat
    for i in range(loop_times):
        index = i+1
        seat_index = seat_index + 1
        name = str(request.POST["name"+str(index)])
        meal = request.POST["meal"+str(index)]
        cla = request.POST["class"+str(index)]
        final_price = int(
            float(cost)*float(request.session['discount']))
        insert_passenger_info(RI.reservation_id, F.fid,
                              name, seat_index, meal, cla, final_price)

    # Do not forget to update FlightOccupiedSeat object
    f_occupied_object.occupied_seat = seat_index
    f_occupied_object.save()


def check_duplicate(fid, leave_date, loop_times, request):
    # check db get all names in that flight
    exist_passengers = exist_passenger(fid, leave_date)
    new_passengers = []
    for i in range(loop_times):  # Get new passengers this time
        index = i+1
        new_passengers.append(str(request.POST["name"+str(index)]))
    name_duplicate = False
    duplicate_name = ""
    if exist_passengers:
        for ex_name in exist_passengers:
            for new_name in new_passengers:
                if ex_name[0].lower() == new_name.lower():
                    name_duplicate = True
                    duplicate_name = new_name
                    break
            if name_duplicate:
                break
    return name_duplicate, duplicate_name


def exist_passenger(fid, leave_date):
    query = RAW_SQL['SEARCH_EXIST_PASSENGER'].format(
        fid=fid, leave_date=leave_date)
    return execute_custom_sql(query)


def insert_passenger_info(RID, FID, name, seat, meal, cla, price):
    query = RAW_SQL['INSERT_RES_FLIGHT'].format(
        Reservation_ID=RID, FID=FID, P_name=name, P_seat=seat, P_meal=meal, P_class=cla, Price=price)
    cursor = connection.cursor()
    cursor.execute(query)


def execute_custom_sql(s):
    cursor = connection.cursor()
    try:
        cursor.execute(s)
    except:
        return set()
    return cursor.fetchall()


RAW_SQL = {
    'INSERT_RES_FLIGHT': '''
                INSERT INTO Reservation_Flight (Reservation_ID, FID, P_name, P_seat, P_meal, P_class, Price)
                VALUES ({Reservation_ID}, {FID}, "{P_name}", {P_seat}, "{P_meal}", "{P_class}", {Price})
            ''',
    'SEARCH_EXIST_PASSENGER': '''
                Select rf.P_name
                from Reservation_Flight rf
                Join RF_Relation rr USING (Reservation_ID, FID)
                WHERE rr.FID={fid} and rr.leave_date = "{leave_date}";
            ''',
}
