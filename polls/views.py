'''Views for app polls'''
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
import datetime
from .models import Flight, Airline, Customer, Airport, Customer
# from .models import Question_new, Choice_new


def index_default(request):
    '''Substitiued by IndexView, which is a template provide by Django'''
    # latest_question_list = Question_new.objects.order_by('-pub_date')[:5]
    airports = Airport.objects.filter()
    template = loader.get_template('polls/index.html')
    context = {
        'airports': airports,
    }
    return HttpResponse(template.render(context, request))


def index_warning(request):
    '''Substitiued by IndexView, which is a template provide by Django'''
    airports = Airport.objects.filter()
    template = loader.get_template('polls/index.html')
    context = {
        'airports': airports,
        'warning': True,
    }
    return HttpResponse(template.render(context, request))


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
        if user.is_superuser:
            return HttpResponseRedirect(reverse('polls:manager'))
        else:
            return HttpResponseRedirect(reverse('polls:index_default'))
            # c_id = Customer.objects.get(
            #     email=email, password=password).customer_id
            # return HttpResponseRedirect(reverse('polls:customer', args=(c_id,)))
    else:
        # Return an 'invalid login' error message.
        return HttpResponseRedirect(reverse('polls:index_warning'))

    # if email == "tian@test.com" and password == "riverroad2017":
    #     return HttpResponseRedirect(reverse('polls:manager'))
    # try:
    #     c_id = Customer.objects.get(email=email, password=password).customer_id
    # except Customer.DoesNotExist:
    #     c_id = None
    # if c_id is None:
    #     return HttpResponseRedirect(reverse('polls:index_warning'))
    # else:
    #     return HttpResponseRedirect(reverse('polls:customer', args=(c_id,)))


def logout_page(request):
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
    passenger = request.POST['passenger']

    leave_date = timezone.now(
    ) if request.POST['leave'] is None else request.POST['leave']
    leave_date_tom = getTomorrowDate(leave_date)
    leave_day = getDayFromDate(leave_date)

    return_date = (timezone.now() + datetime.timedelta(days=1)
                   ) if request.POST['return'] is None else request.POST['return']
    return_day = getDayFromDate(return_date)

    # Get direct flight
    direct_result = Flight.objects.filter(Q(depart_airport=from_location) &
                                          Q(arrive_airport=to_location) & (Q(workday=((leave_day+1) % 2)) | Q(workday=(leave_day % 2))),)
    for d_f in direct_result:
        if d_f.workday == leave_day % 2:
            d_f.workday = leave_date
        else:
            d_f.workday = leave_date_tom

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

    context = {
        'direct_flight': direct_result,
        'one_stop_flight': one_stop_result,
        'leave_date': leave_date,
        'return_date': return_date,
    }
    return HttpResponse(template.render(context, request))


def customer(request):
    """For customer page"""
    template = loader.get_template('polls/customer.html')
    user = request.user
    # In original db Customer table, we want to use email as username to log in
    # But in Django auth.user, by default it uses only username and password to log in
    # So we first import all data in Customer table to default auth.user table
    # and set email as username
    cus = Customer.objects.get(email=user.username)
    his_query = RAW_SQL['RES_HISTORY'].format(customer_id=cus.customer_id)
    res_history = execute_custom_sql(his_query)
    context = {
        'customer': cus,
        'history': res_history,
    }
    return HttpResponse(template.render(context, request))


def manager(request):
    """For manager page"""
    template = loader.get_template('polls/manager_index.html')
    cus = Customer.objects.order_by('customer_id')
    context = {
        'customers': cus,
    }
    return HttpResponse(template.render(context, request))


def one_stop_flight(start, end, workday1, workday2):
    query = RAW_SQL['ONE_STOP_FLIGHT'].format(start_airport=start, end_airport=end, workday1=workday1,
                                              workday2=workday2)
    # print(query)
    return execute_custom_sql(query)


def execute_custom_sql(s):
    cursor = connection.cursor()
    cursor.execute(s)
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
                WHERE rf.Reservation_ID={customer_id};
            ''',
}


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
