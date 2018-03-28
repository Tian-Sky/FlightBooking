'''Views for app polls'''
import datetime
from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.template import loader
from django.shortcuts import get_object_or_404
from django.views import generic
from django.utils import timezone
from django.db import connection
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Flight, Airline, Customer, Airport, Customer, Account, ReservationInfo, RfRelation, ReservationFlight
from .forms import RegisterForm
# from .models import Question_new, Choice_new


def index_default(request):
    '''Substitiued by IndexView, which is a template provide by Django'''
    # latest_question_list = Question_new.objects.order_by('-pub_date')[:5]
    airports = Airport.objects.filter()
    template = loader.get_template('polls/index.html')
    context = {
        'airports': airports,
        'states': USA_STATE,
    }
    return HttpResponse(template.render(context, request))


def index_warning(request, warning_id):
    '''Substitiued by IndexView, which is a template provide by Django'''
    airports = Airport.objects.filter()
    template = loader.get_template('polls/index.html')
    warning_info = ""
    if warning_id == 1:
        warning_info = "Wrong email and password combination!"
    if warning_id == 2:
        warning_info = "That email address already exist!"
    context = {
        'airports': airports,
        'states': USA_STATE,
        'warning': True,
        'warning_info': warning_info,
    }
    return HttpResponse(template.render(context, request))


def register(request):
    '''
    Register a new user
    '''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("form valid")
            email = form.cleaned_data['email']
            email = email.lower().strip()
            # No duplciate email are allowed
            exist = Customer.objects.get(email=email)
            if exist:
                return HttpResponseRedirect(reverse('polls:index_warning', args=(2,)))
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            card1 = form.cleaned_data['card1']
            card2 = form.cleaned_data['card2']
            card3 = form.cleaned_data['card3']
            firstName = form.cleaned_data['firstName']
            lastName = form.cleaned_data['lastName']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zip']
            phone = form.cleaned_data['phone']
            # Save cutomer
            cus = Customer(
                first_name=firstName,
                last_name=lastName,
                password=password1,
                email=email,
                address=address,
                city=city,
                state=state,
                zip=zipcode,
                phone=phone,
            )
            cus.save()
            reservation_default = ReservationInfo.objects.get(
                reservation_id=-1)
            acc_id = 1
            # Save account with credit card
            account_1 = Account(
                customer=cus,
                account_id=acc_id,
                reservation=reservation_default,
                create_date=str(datetime.datetime.now().date()),
                credit_card=card1
            )
            account_1.save()
            acc_id = acc_id+1
            if card2:
                account_2 = Account(
                    customer=cus,
                    account_id=acc_id,
                    reservation=reservation_default,
                    create_date=str(datetime.datetime.now().date()),
                    credit_card=card2
                )
                account_2.save()
                acc_id = acc_id+1
            if card3:
                account_3 = Account(
                    customer=cus,
                    account_id=acc_id,
                    reservation=reservation_default,
                    create_date=str(datetime.datetime.now().date()),
                    credit_card=card3
                )
                account_3.save()
            # Create user in Django authentication syste,
            user = User.objects.create_user(email, email, password1)
            user.first_name = firstName
            user.last_name = lastName
            user.save()
            # Login new register user
            login(request, user)
            print("correct")
        else:
            print("error: "+form.errors.as_json())
            form = RegisterForm()
    return HttpResponseRedirect(reverse('polls:index_default'))


def login_page(request):
    '''
    Login page logic, can login as customer or manager
    '''
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect(reverse('polls:index_default'))
    else:
        # Return an 'invalid login' error message.
        return HttpResponseRedirect(reverse('polls:index_warning', args=(1,)))


def logout_page(request):
    '''
    Log out and delete all session data
    '''
    logout(request)
    return HttpResponseRedirect(reverse('polls:index_default'))


def search(request):
    '''
    Logic to search flight
    '''
    template = loader.get_template('polls/search.html')
    from_location = request.POST['from']
    from_location = from_location[1:4]
    to_location = request.POST['to']
    to_location = to_location[1:4]
    # Put passenger number into session for book use
    passenger = request.POST['passenger_number']
    request.session['passenger'] = passenger

    leave_date = timezone.now(
    ) if request.POST['leave'] is None else request.POST['leave']
    leave_date_tom = getTomorrowDate(leave_date)
    leave_day = getDayFromDate(leave_date)

    return_date = (timezone.now() + datetime.timedelta(days=1)
                   ) if request.POST['return'] is None else request.POST['return']
    return_day = getDayFromDate(return_date)

    # Get direct flight
    request.session['direct_flight'] = {}
    direct_result = Flight.objects.filter(Q(depart_airport=from_location) &
                                          Q(arrive_airport=to_location) & (Q(workday=((leave_day+1) % 2)) | Q(workday=(leave_day % 2))),)
    for i, d_f in enumerate(direct_result):
        if d_f.workday == leave_day % 2:
            d_f.workday = leave_date
        else:
            d_f.workday = leave_date_tom
        d_f.id = str(i)
        # Put direct flight FID into into session for book use
        # We also need to save leave date
        request.session['direct_flight'][i] = str(d_f.fid)+","+d_f.workday
        request.session.modified = True

    # Get one_stop flight
    one_stop = one_stop_flight(
        from_location, to_location, leave_day % 2, (leave_day+1) % 2)
    one_stop_result = set()
    for f in one_stop:
        airline1 = Airline.objects.get(airline_id=f[0]).airline_name
        airline2 = Airline.objects.get(airline_id=f[8]).airline_name
        date1 = leave_date if f[3] == leave_day % 2 else leave_date_tom
        date2 = leave_date if f[11] == leave_day % 2 else leave_date_tom
        d1 = str(Airport.objects.get(airport_id=f[5]))
        a1 = str(Airport.objects.get(airport_id=f[7]))
        d2 = str(Airport.objects.get(airport_id=f[13]))
        a2 = str(Airport.objects.get(airport_id=f[15]))
        f = (airline1,) + f[1:3] + (str(date1),) + (str(f[4]),) + (d1,) + \
            (str(f[6]),) + (a1,) + (airline2,) + f[9:11] + (str(date2),) + \
            (str(f[12]),) + (d2,) + (str(f[14]),) + (a2,)
        one_stop_result.add(f)
    # Distinguish between jump from search to book and buy to book(back due to duplicate names)
    request.session['duplicate_name'] = None
    request.session['book_fid'] = None
    request.session['leave_date'] = None
    context = {
        'direct_flight': direct_result,
        'one_stop_flight': one_stop_result,
        'leave_date': leave_date,
        'return_date': return_date,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='/polls/')
def book(request):
    template = loader.get_template('polls/book.html')
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
    context = {
        'flight': flight,
        'passenger_loop_times': range(loop_times),
        'accounts': account_unique,
        'duplicate_name': request.session['duplicate_name']
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='/polls/')
def buy(request):
    '''
    Write new reservation data into DB
    1.Reservation-Info - 2.Account - 3.RF-Relation - 4.Reservation-Flight
    '''
    # First we need to check if that flight already have thsoe customers
    fid = request.POST['fid']  # Flight ID, unique
    request.session['book_fid'] = fid
    leave_date = request.POST['leave_date']  # Flight leave date
    request.session['leave_date'] = leave_date
    try:
        # check how many passengers this time
        loop_times = int(request.session['passenger'])
    except ValueError:
        loop_times = 1
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
    # If name has duplication, we redirect it to buy page with warning
    if name_duplicate:
        request.session['duplicate_name'] = duplicate_name
        return HttpResponseRedirect(reverse('polls:book'))

    # First fetch data from POST and write to Reservation-Info
    # Order date, which is todyday
    order_date = str(datetime.datetime.now().date())
    # Total cost for this reservation
    total_cost = loop_times * int(request.POST['cost'])
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
    for i in range(loop_times):
        index = i+1
        name = str(request.POST["name"+str(index)])
        meal = request.POST["meal"+str(index)]
        cla = request.POST["class"+str(index)]
        insert_passenger_info(
            RI.reservation_id, F.fid, name, index, meal, cla, request.POST['cost'])
    return HttpResponseRedirect(reverse('polls:customer'))


@login_required(login_url='/polls/')
def customer(request):
    """For customer page"""
    template = loader.get_template('polls/customer.html')
    user = request.user
    # In original db Customer table, we use email as username to log in
    # But in Django auth.user, by default it uses only username and password to log in
    # So we first import all data in Customer table to default auth.user table
    # and set email as username
    cus = Customer.objects.get(email=user.username)
    his_query = RAW_SQL['RES_HISTORY'].format(customer_id=cus.customer_id)
    res_history = execute_custom_sql(his_query)
    cur_query = RAW_SQL['RES_CURRENT'].format(customer_id=cus.customer_id)
    res_current = execute_custom_sql(cur_query)
    passengers = set()
    for his in res_history:
        passengers.add(his[7])
    for cur in res_current:
        passengers.add(cur[7])
    context = {
        'customer': cus,
        'history': res_history,
        'current': res_current,
        'states': USA_STATE,
        'passengers': passengers,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='/polls/')
def update_info(request):
    '''
    Update user information
    Customer cannot change email address
    '''
    # Get current user
    user = request.user
    cus = Customer.objects.get(email=user.username)
    password = request.POST['password']
    if password:
        cus.password = password
        user.set_password(password)
    first_name = request.POST['first_name']
    if first_name:
        cus.first_name = first_name
        user.first_name = first_name
    last_name = request.POST['last_name']
    if last_name:
        cus.last_name = last_name
        user.last_name = last_name
    phone = request.POST['phone']
    if phone:
        cus.phone = phone
    address = request.POST['address']
    if address:
        cus.address = address
    city = request.POST['city']
    print(city)
    if city:
        cus.city = city
    state = request.POST['state']
    if state:
        cus.state = state
    zip = request.POST['zip']
    if zip:
        cus.zip = zip
    preference = request.POST['preference']
    if preference:
        cus.preference = preference
    user.save()
    cus.save()
    return HttpResponseRedirect(reverse('polls:customer'))


@login_required(login_url='/polls/')
def manager(request):
    """For manager page"""
    template = loader.get_template('polls/manager.html')
    # For all customers
    cus = Customer.objects.order_by('customer_id')
    month = request.session.get('sales_report_month', "03")
    # For sales report
    sales_report_month = "2016-"+month+"%"
    sales_report = get_sales_report(sales_report_month)
    # For flights by airline company
    airline_query = Flight.objects.values_list(
        'airline__airline_name').distinct()
    airlines = set()
    for air in airline_query:
        airlines.add(air[0])
    if request.session.get('airline', None) is not None:
        flights = Flight.objects.filter(
            airline__airline_name=request.session['airline'])
    else:
        flights = set()
    # For reservations search with flight
    fid = request.session.get('reservation_search_flights', -1)
    reservation_search_flights = query_reservations_with_flight(fid)
    # For reservations search with customer
    first_name = request.session.get(
        'reservation_search_customer_first_name', "")
    last_name = request.session.get(
        'reservation_search_customer_last_name', "")
    reservation_search_customer = query_reservation_with_customer(
        first_name, last_name)
    # For delay flights
    delay_month = request.session.get('delay_month', "08")
    delay_flights = query_delay_flights(delay_month)
    context = {
        'customers': cus,
        'sales_data': sales_report,
        'sales_month': MONTH[month],
        'airlines': airlines,
        'flights': flights,
        'delay_flights': delay_flights,
        'reservation_search_flights': reservation_search_flights,
        'reservation_search_customer': reservation_search_customer,
        'tag': manager_tag(request.session['manager_tag']),
        'TABLE_COLUMNS': TABLE_COLUMNS,
    }
    request.session['manager_tag'] = 0
    return HttpResponse(template.render(context, request))


@login_required(login_url='/polls/')
def sales_month(request):
    request.session['sales_report_month'] = request.POST['salesMonth']
    request.session['manager_tag'] = 1
    return HttpResponseRedirect(reverse('polls:manager'))


@login_required(login_url='/polls/')
def get_all_flights(request):
    request.session['airline'] = request.POST['airline']
    request.session['manager_tag'] = 2
    return HttpResponseRedirect(reverse('polls:manager'))


@login_required(login_url='/polls/')
def get_reservations_with_flight(request):
    request.session['reservation_search_flights'] = request.POST['reservation_search_flights']
    request.session['manager_tag'] = 3
    return HttpResponseRedirect(reverse('polls:manager'))


@login_required(login_url='/polls/')
def get_reservations_with_customer(request):
    request.session['reservation_search_customer_first_name'] = request.POST['reservation_search_customer_first_name']
    request.session['reservation_search_customer_last_name'] = request.POST['reservation_search_customer_last_name']
    request.session['manager_tag'] = 4
    return HttpResponseRedirect(reverse('polls:manager'))


@login_required(login_url='/polls/')
def get_delay_flights(request):
    request.session['delay_month'] = request.POST['delay_month']
    request.session['manager_tag'] = 5
    return HttpResponseRedirect(reverse('polls:manager'))


def one_stop_flight(start, end, workday1, workday2):
    query = RAW_SQL['ONE_STOP_FLIGHT'].format(start_airport=start, end_airport=end, workday1=workday1,
                                              workday2=workday2)
    # print(query)
    return execute_custom_sql(query)


def exist_passenger(fid, leave_date):
    query = RAW_SQL['SEARCH_EXIST_PASSENGER'].format(
        fid=fid, leave_date=leave_date)
    return execute_custom_sql(query)


def get_sales_report(month):
    query = RAW_SQL['SALES_REPORT'].format(month=month)
    return execute_custom_sql(query)


def query_reservations_with_flight(fid):
    query = RAW_SQL['RESERVATION_WITH_FLIGHT'].format(fid=fid)
    return execute_custom_sql(query)


def query_reservation_with_customer(first_name, last_name):
    query = RAW_SQL['RESERVATION_WITH_CUSTOMER'].format(
        first_name=first_name, last_name=last_name)
    return execute_custom_sql(query)


def query_delay_flights(month):
    query = RAW_SQL['DELAY_FLIGHTS'].format(month=month)
    return execute_custom_sql(query)


def insert_passenger_info(RID, FID, name, seat, meal, cla, price):
    query = RAW_SQL['INSERT_RES_FLIGHT'].format(
        Reservation_ID=RID, FID=FID, P_name=name, P_seat=seat, P_meal=meal, P_class=cla, Price=price)
    cursor = connection.cursor()
    cursor.execute(query)


def execute_custom_sql(s):
    cursor = connection.cursor()
    cursor.execute(s)
    return cursor.fetchall()


def manager_tag(tag):
    return {
        1: "sales_report",
        2: "flights",
        3: "reservations_flight",
        4: "reservations_customer",
        5: "delay_flights",
    }.get(tag, "customers")


def getTomorrowDate(date):
    date = list(map(int, date.split("-")))
    date[2] = date[2] + 1
    if date[2] > 30:
        date[2] = date[2]-30
        date[1] = date[1]+1
    if date[1] > 12:
        date[1] = date[1]-12
        date[0] = date[0]+1
    result = str(date[0])+"-"
    if date[1] < 10:
        result = result + "0"
    result = result + str(date[1])+"-"
    if date[2] < 10:
        result = result + "0"
    result = result + str(date[2])
    return result


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
                f2.Arrive_time as s_arrive_time, f2.Arrive_Airport as s_arrive_airport
                FROM Flight f1
                JOIN Flight f2
                WHERE f1.Arrive_Airport=f2.Depart_Airport
                AND f1.workday={workday1} AND f2.workday={workday2}
                ) res
                WHERE f_depart_airport="{start_airport}" AND s_arrive_airport="{end_airport}"
            ''',
    'RES_HISTORY': '''
                SELECT rf.Reservation_ID, rf.FID, ri.order_date, ri.total_cost, ri.Leave_date, f.Depart_Airport, f.Arrive_Airport,
                    rf.P_name, rf.P_seat, rf.P_meal, rf.P_class, rf.Price, ri.Representative_ID
                FROM Reservation_Flight rf
                JOIN RF_Relation r on r.Reservation_ID = rf.Reservation_ID
                JOIN Reservation_Info ri on ri.Reservation_ID = rf.Reservation_ID
                JOIN Flight f on f.FID = rf.FID
                WHERE ri.order_date < '2018-01-01' AND rf.Reservation_ID in (
                    SELECT Reservation_ID
                    FROM Account a
                    WHERE a.Customer_ID = {customer_id}
                ) ORDER BY rf.Reservation_ID DESC;
            ''',
    'RES_CURRENT': '''
                SELECT rf.Reservation_ID, rf.FID, ri.order_date, ri.total_cost, ri.Leave_date, f.Depart_Airport, f.Arrive_Airport,
                    rf.P_name, rf.P_seat, rf.P_meal, rf.P_class, rf.Price, ri.Representative_ID
                FROM Reservation_Flight rf
                JOIN RF_Relation r on r.Reservation_ID = rf.Reservation_ID
                JOIN Reservation_Info ri on ri.Reservation_ID = rf.Reservation_ID
                JOIN Flight f on f.FID = rf.FID
                WHERE ri.order_date > '2018-01-01' AND rf.Reservation_ID in (
                    SELECT Reservation_ID
                    FROM Account a
                    WHERE a.Customer_ID = {customer_id}
                ) ORDER BY rf.Reservation_ID DESC;
            ''',
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
    'SALES_REPORT': '''
                SELECT a.Airline_name, Airline_ID, SUM(cost) AS Total_sales
                FROM 
                    (
                    SELECT t2.Airline_ID, t2.Total_cost/COUNT(t2.Total_cost) AS cost, t2.dates
                    FROM
                        (
                        SELECT rl.Reservation_ID, t1.Total_cost, f.Airline_ID, t1.dates
                        FROM RF_Relation rl
                        JOIN
                            (
                            SELECT rf.Reservation_ID, rf.Total_cost, rf.Order_date AS dates
                            FROM  Reservation_Info rf
                            WHERE rf.order_date LIKE('{month}')
                            ) t1
                        ON rl.Reservation_ID = t1.Reservation_ID
                        JOIN Flight f ON f.FID = rl.FID
                        ) t2
                    GROUP BY t2.Reservation_ID, t2.Airline_ID, t2.dates
                    ) t3
                JOIN Airline a USING (Airline_ID)
                GROUP BY t3.Airline_ID
                ORDER BY a.Airline_name;
            ''',
    'RESERVATION_WITH_FLIGHT': '''
                SELECT rf.Reservation_ID, rf.FID, f.Airline_ID, f.Flight_ID, ri.order_date, ri.Total_cost,
                        ri.Leave_date, f.Depart_Airport, f.Arrive_Airport, rf.P_name, rf.P_seat,
                        rf.P_meal, rf.P_class, rf.Price, ri.Representative_ID
                FROM Reservation_Flight rf
                JOIN Flight f ON rf.FID = f.FID
                JOIN Reservation_Info ri ON rf.Reservation_ID = ri.Reservation_ID
                WHERE rf.FID = {fid};
            ''',
    'RESERVATION_WITH_CUSTOMER': '''
                SELECT rf.Reservation_ID, rf.FID, f.Airline_ID, f.Flight_ID, ri.order_date, 
                    ri.total_cost, ri.Leave_date, f.Depart_Airport, f.Arrive_Airport,
                    rf.P_name, rf.P_seat, rf.P_meal, rf.P_class, rf.Price, ri.Representative_ID
                FROM Reservation_Flight rf
                JOIN RF_Relation r ON r.Reservation_ID = rf.Reservation_ID
                JOIN Reservation_Info ri ON ri.Reservation_ID = rf.Reservation_ID
                JOIN Flight f ON f.FID = rf.FID
                JOIN
                    (
                    SELECT a.Reservation_ID, t1.First_name, t1.Last_name
                    FROM Account a
                    JOIN
                        (
                        SELECT c.Customer_ID, c.First_name, c.Last_name
                        FROM Customer c
                        WHERE c.First_name="{first_name}" and c.Last_name="{last_name}"
                        ) t1
                    ON a.Customer_ID = t1.Customer_ID
                    ) t3
                ON rf.Reservation_ID = t3.Reservation_ID
                ORDER BY rf.Reservation_ID DESC;
            ''',
    'DELAY_FLIGHTS': '''
                SELECT f.FID, d.Delay_date ,f.Depart_Airport, f.Arrive_Airport, d.Delay_time
                FROM Flight f, Delay d
                WHERE f.FID = d.FID and d.Delay_date LIKE('2017-{month}%')
                AND d.Delay_time <> '00:00:00'
                ORDER BY d.Delay_date, f.FID;
            ''',
}

MONTH = {
    "01": "January",
    "02": "Feburary",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": 'July',
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

USA_STATE = [
    "Alabama (AL)",
    "Alaska (AK)",
    "Arizona (AZ)",
    "Arkansas (AR)",
    "California (CA)",
    "Colorado (CO)",
    "Connecticut (CT)",
    "Delaware (DE)",
    "Florida (FL)",
    "Georgia (GA)",
    "Hawaii (HI)",
    "Idaho (ID)",
    "Illinois (IL)",
    "Indiana (IN)",
    "Iowa (IA)",
    "Kansas (KS)",
    "Kentucky (KY)",
    "Louisiana (LA)",
    "Maine (ME)",
    "Maryland (MD)",
    "Massachusetts (MA)",
    "Michigan (MI)",
    "Minnesota (MN)",
    "Mississippi (MS)",
    "Missouri (MO)",
    "Montana (MT)",
    "Nebraska (NE)",
    "Nevada (NV)",
    "New Hampshire (NH)",
    "New Jersey (NJ)",
    "New Mexico (NM)",
    "New York (NY)",
    "North Carolina (NC)",
    "North Dakota (ND)",
    "Ohio (OH)",
    "Oklahoma (OK)",
    "Oregon (OR)",
    "Pennsylvania (PA)",
    "Rhode Island (RI)",
    "South Carolina (SC)",
    "South Dakota (SD)",
    "Tennessee (TN)",
    "Texas (TX)",
    "Utah (UT)",
    "Vermont (VT)",
    "Virginia (VA)",
    "Washington (WA)",
    "West Virginia (WV)",
    "Wisconsin (WI)",
    "Wyoming (WY)"
]

TABLE_COLUMNS = {
    'Reservation_Info': [
        "Reservation_ID",
        "FID",
        "Airline_ID",
        "Flight_ID",
        "Order_date",
        "Total_cost",
        "Leave_date",
        "Depart_airport",
        "Arrive_Airport",
        "P_name",
        "p_seat",
        "P_meal",
        "P_class",
        "Price",
        "Representative"
    ],
    'Delay_Flights': [
        "FID",
        "Delay_Date",
        "Depart_Airport",
        "Arrive_Airport",
        "Delay_time"
    ]
}

# class IndexView(generic.ListView):  # pylint: disable=too-many-ancestors
#     """
#     New function, provided by Django, easier and short code
#     """
#     template_name = 'polls/index.html'
#     context_object_name = 'latest_question_list'

#     def get_queryset(self):
#         """
#         Return the last five published questions (not including those set to be
#         published in the future).
#         """
#         return Question_new.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


# def detail(request, question_id):
#     '''Orignal function for detail page. Replaced by DetailView'''
#     question = get_object_or_404(Question_new, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#  #      try:
#  #        question = Question_new.objects.get(pk=question_id)
#  #    except Question_new.DoesNotExist:
#  #        raise Http404("Question does not exist")
#  #    return render(request, 'polls/detail.html', {'question': question})


# class DetailView(generic.DetailView):  # pylint: disable=too-many-ancestors
#     '''
#     For detail page
#     '''
#     model = Question_new
#     template_name = 'polls/detail.html'

#     def get_queryset(self):
#         """
#         Excludes any questions that aren't published yet.
#         """
#         return Question_new.objects.filter(pub_date__lte=timezone.now())


# def results(request, question_id):
#     '''
#     Original for result page
#     '''
#     question = get_object_or_404(Question_new, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})


# class ResultsView(generic.DetailView):  # pylint: disable=too-many-ancestors
#     '''
#     For result page
#     '''
#     model = Question_new
#     template_name = 'polls/results.html'


# def vote(request, question_id):
#     '''
#     For vote page
#     '''
#     question = get_object_or_404(Question_new, pk=question_id)
#     try:
#         selected_choice = question.choice_new_set.get(
#             pk=request.POST['choice'])
#     except (KeyError, Choice_new.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a Choice_new.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
