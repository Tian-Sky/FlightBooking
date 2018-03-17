from django.contrib import admin

# Register your models here.
from .models import Airport, Account, Airline, Customer, Delay, FareRestriction
from .models import Flight, ReservationFlight, ReservationInfo


class AirportAdmin(admin.ModelAdmin):
    fields = ['airport_id', 'airport_name',
              'city', 'country', 'time_zone']
    list_display = ('airport_id', 'airport_name',
                    'city', 'country', 'time_zone')


class FareRestrictionAdmin(admin.ModelAdmin):
    fields = ['fare_id', 'type', 'discount']
    list_display = ('fare_id', 'type', 'discount')


class FlightAdmin(admin.ModelAdmin):
    list_display = ('airline', 'flight_id', 'capacity', 'fare', 'workday', 'depart_time',
                    'depart_airport', 'arrive_time', 'arrive_airport', 'fare_0')
    list_display_links = None


admin.site.register(Airport, AirportAdmin)
admin.site.register(FareRestriction, FareRestrictionAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Airline)
