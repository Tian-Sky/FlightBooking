from django.contrib import admin

# Register your models here.
from .models import Question, Choice
from .models import Airport, Account, Airline, Customer, Delay, FareRestriction
from .models import Flights, ReservationFlight, ReservationInfo

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Airport)
