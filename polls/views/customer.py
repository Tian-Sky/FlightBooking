from django.urls import reverse
from django.db import connection
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from ..models import Flight, FlightOccupiedSeat, Airline, Airport, Customer


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
    best_seller_list = get_best_seller()[:10]
    best_list = set()
    for data in best_seller_list:
        a_n = Airline.objects.get(airline_id=data[2]).airline_name
        d_name = Airport.objects.get(airport_id=data[4]).airport_name
        d_p = "("+str(data[4])+") "+str(d_name)
        p_name = Airport.objects.get(airport_id=data[5]).airport_name
        a_p = "("+str(data[5])+") "+str(p_name)
        best_list.add(data[0:2]+(a_n,)+(data[3],)+(d_p,)+(a_p,))
    best_list = sorted(best_list, key=lambda best: best[1], reverse=True)
    context = {
        'customer': cus,
        'history': res_history,
        'current': res_current,
        'states': USA_STATE,
        'passengers': passengers,
        'best_seller_list': best_list,
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


def get_best_seller():
    query = RAW_SQL['BEST_SELLER']
    return execute_custom_sql(query)


def execute_custom_sql(s):
    cursor = connection.cursor()
    try:
        cursor.execute(s)
    except:
        return set()
    return cursor.fetchall()


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
    'AIRPORT_FLIGHTS': '''
                SELECT f.FID, f.Depart_Airport, f.Arrive_Airport 
                FROM Flight f
                WHERE f.Depart_Airport = '{airport}' OR f.Arrive_Airport = '{airport}';
            ''',
    'RESERVED_CUSTOMERS': '''
                SELECT c.Customer_ID, c.First_name, c.Last_name, c.Email 
                FROM Customer c
                WHERE c.Customer_ID IN
                    (
                    SELECT a.Customer_ID 
                    FROM Account a 
                    where a.Reservation_ID IN
                    (
                    SELECT DISTINCT rf.Reservation_ID 
                    FROM Reservation_Flight rf
                    WHERE rf.FID = {fid}
                    )
                );
            ''',
    'CUSTOMER_REVENUE': '''
                SELECT c.Customer_ID, c.First_name, c.Last_name, c.Email, t1.cost
                FROM Customer c,
                (
                    SELECT a.Customer_ID AS CID, SUM(ri.Total_cost) AS cost
                    FROM Account a, Reservation_Info ri
                    WHERE a.Reservation_ID = ri.Reservation_ID
                    GROUP BY a.Customer_ID
                ) t1
                WHERE c.Customer_ID = t1.CID
                ORDER BY cost DESC;
            ''',
    'BEST_SELLER': '''
                SELECT t.fid, t.popularity, f.Airline_ID, f.Flight_ID, f.Depart_Airport, f.Arrive_Airport
                FROM(
                SELECT fid, count(*) as popularity from Reservation_Flight
                group by FID
                ) t 
                JOIN Flight f
                USING (fid)
                ORDER BY t.popularity DESC, t.fid
                LIMIT 100;
            ''',
    'REVENUE_BY_FLIGHTS': '''
                SELECT DISTINCT rf.FID, a.airline_id, a.airline_name, f.flight_id, sum(ri.total_cost) as total_revenue
                FROM Reservation_Flight rf
                JOIN RF_Relation rl ON rl.Reservation_ID = rf.Reservation_ID
                JOIN Reservation_Info ri ON ri.Reservation_ID = rf.Reservation_ID
                JOIN Flight f ON f.FID = rf.FID
                JOIN Airline a on a.Airline_ID = f.airline_id
                group by rf.fid, a.airline_name, f.Flight_ID
                order by total_revenue desc, rf.FID, a.airline_id
                LIMIT 100;
            ''',
    'REVENUE_BY_AIRPORTS': '''
                SELECT ap.Airport_ID, ap.Airport_name, ap.city, ap.country, sum(ri.total_cost) as total_revenue
                FROM Reservation_Flight rf
                JOIN RF_Relation rl ON rl.Reservation_ID = rf.Reservation_ID
                JOIN Reservation_Info ri ON ri.Reservation_ID = rf.Reservation_ID
                JOIN Flight f ON f.FID = rf.FID
                JOIN Airport ap on ap.Airport_ID = f.Arrive_Airport
                group by ap.Airport_ID, ap.Airport_name, ap.city, ap.country
                order by total_revenue desc, ap.Airport_ID;
            ''',
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
