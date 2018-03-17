from django.contrib import admin

# Register your models here.
from .models import Airport, Account, Airline, Customer, Delay, FareRestriction
from .models import Flight, ReservationFlight, ReservationInfo


class AirportAdmin(admin.ModelAdmin):
    list_display = ('airport_id', 'airport_name',
                    'city', 'country', 'time_zone')


class FareRestrictionAdmin(admin.ModelAdmin):
    list_display = ('fare_id', 'type', 'discount')


class FlightAdmin(admin.ModelAdmin):
    list_display = ('airline', 'flight_id', 'capacity', 'fare', 'workday', 'depart_time',
                    'depart_airport', 'arrive_time', 'arrive_airport', 'fare_0')
    list_display_links = None


class AirlineAdmin(admin.ModelAdmin):
    list_display = ('airline_id', 'airline_name')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'first_name', 'last_name', 'address', 'city', 'state',
                    'zip', 'phone', 'email', 'password', 'preference')


admin.site.register(Airport, AirportAdmin)
admin.site.register(FareRestriction, FareRestrictionAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Airline, AirlineAdmin)
admin.site.register(Customer, CustomerAdmin)
