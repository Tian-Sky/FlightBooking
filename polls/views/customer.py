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
    'RES_HISTORY': '''
                SELECT t2.reservation_id, t2.fid, t2.order_date, t2.total_cost, t2.leave_date, t2.da, t2.aa, rf.p_name, rf.p_seat, 
				rf.p_meal, rf.p_class, rf.price, t2.representative_id
                FROM Reservation_Flight rf
                JOIN (
                SELECT t1.Reservation_id, t1.fid, ri.order_date, ri.total_cost, t1.leave_date, t1.da, t1.aa, ri.Representative_ID
                FROM Reservation_Info ri
                JOIN(
                SELECT rr.reservation_id, rr.fid, rr.leave_date, f.Depart_Airport as da, f.Arrive_Airport as aa
                FROM RF_Relation rr
                JOIN Flight f using (fid)
                WHERE rr.reservation_id in 
                (
                SELECT Reservation_ID
                FROM Account a
                WHERE a.Customer_ID = {customer_id}
                ) 
                ) t1 USING (reservation_id)
                WHERE ri.order_date < '2018-01-01'
                ) t2 USING (reservation_id, fid)
                ORDER BY Reservation_ID desc, p_name;
            ''',
    'RES_CURRENT': '''
                SELECT t2.reservation_id, t2.fid, t2.order_date, t2.total_cost, t2.leave_date, t2.da, t2.aa, rf.p_name, rf.p_seat, 
				rf.p_meal, rf.p_class, rf.price, t2.representative_id
                FROM Reservation_Flight rf
                JOIN (
                SELECT t1.Reservation_id, t1.fid, ri.order_date, ri.total_cost, t1.leave_date, t1.da, t1.aa, ri.Representative_ID
                FROM Reservation_Info ri
                JOIN(
                SELECT rr.reservation_id, rr.fid, rr.leave_date, f.Depart_Airport as da, f.Arrive_Airport as aa
                FROM RF_Relation rr
                JOIN Flight f using (fid)
                WHERE rr.reservation_id in 
                (
                SELECT Reservation_ID
                FROM Account a
                WHERE a.Customer_ID = {customer_id}
                ) 
                ) t1 USING (reservation_id)
                WHERE ri.order_date > '2018-01-01'
                ) t2 USING (reservation_id, fid)
                ORDER BY Reservation_ID desc, p_name;
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
