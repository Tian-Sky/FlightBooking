from django.contrib import admin

# Register your models here.
from .models import Question_new, Choice_new
from .models import Airport, Account, Airline, Customer, Delay, FareRestriction
from .models import Flights, ReservationFlight, ReservationInfo

admin.site.register(Question_new)
admin.site.register(Choice_new)
admin.site.register(Airport)
