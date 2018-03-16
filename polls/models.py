# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import datetime
from django.db import models
from django.utils import timezone

# Create your models here.


class Question_new(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice_new(models.Model):
    question = models.ForeignKey(Question_new, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

# Project models-------


class Airline(models.Model):
    # Field name made lowercase.
    airline_id = models.CharField(
        db_column='Airline_ID', primary_key=True, max_length=5)
    # Field name made lowercase.
    airline_name = models.CharField(
        db_column='Airline_name', max_length=100, blank=True, null=True)

    def __str__(self):
        return self.airline_name

    class Meta:
        db_table = 'Airline'


class Airport(models.Model):
    # Field name made lowercase.
    airport_id = models.CharField(
        db_column='Airport_ID', primary_key=True, max_length=3)
    # Field name made lowercase.
    airport_name = models.CharField(
        db_column='Airport_name', max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=45, blank=True, null=True)
    # Field name made lowercase.
    time_zone = models.CharField(
        db_column='Time_zone', max_length=45, blank=True, null=True)

    def __str__(self):
        return self.airport_name+"("+self.airport_id+")"

    class Meta:
        db_table = 'Airport'


class Customer(models.Model):
    # Field name made lowercase.
    customer_id = models.AutoField(db_column='Customer_ID', primary_key=True)
    # Field name made lowercase.
    first_name = models.CharField(
        db_column='First_name', max_length=20, blank=True, null=True)
    # Field name made lowercase.
    last_name = models.CharField(
        db_column='Last_name', max_length=20, blank=True, null=True)
    # Field name made lowercase.
    address = models.CharField(
        db_column='Address', max_length=45, blank=True, null=True)
    # Field name made lowercase.
    city = models.CharField(
        db_column='City', max_length=20, blank=True, null=True)
    # Field name made lowercase.
    state = models.CharField(
        db_column='State', max_length=10, blank=True, null=True)
    # Field name made lowercase.
    zip = models.IntegerField(db_column='Zip', blank=True, null=True)
    # Field name made lowercase.
    phone = models.CharField(
        db_column='Phone', max_length=11, blank=True, null=True)
    # Field name made lowercase.
    email = models.CharField(
        db_column='Email', max_length=45, blank=True, null=True)
    # Field name made lowercase.
    password = models.CharField(
        db_column='Password', max_length=20, blank=True, null=True)
    # Field name made lowercase.
    preference = models.CharField(
        db_column='Preference', max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'Customer'


class Delay(models.Model):
    # Field name made lowercase.
    airline = models.ForeignKey(
        'Flights', on_delete=models.CASCADE, db_column='Airline_ID', related_name="Delay_Airline", primary_key=True)
    # Field name made lowercase.
    flight = models.ForeignKey(
        'Flights', on_delete=models.CASCADE, db_column='Flight_ID', related_name="Delay_Flight")
    # Field name made lowercase.
    delay_date = models.DateField(
        db_column='Delay_date', blank=True, null=True)
    # Field name made lowercase.
    delay_time = models.TimeField(
        db_column='Delay_time', blank=True, null=True)

    class Meta:
        db_table = 'Delay'
        unique_together = (('airline', 'flight'),)


class FareRestriction(models.Model):
    # Field name made lowercase.
    fare_id = models.AutoField(db_column='Fare_ID', primary_key=True)
    # Field name made lowercase.
    type = models.CharField(
        db_column='Type', max_length=3, blank=True, null=True)
    # Field name made lowercase.
    discount = models.FloatField(db_column='Discount', blank=True, null=True)

    def __str__(self):
        return "type: "+str(self.type)+" discount: "+str(self.discount)

    class Meta:
        db_table = 'Fare_Restriction'


class Flights(models.Model):
    # Field name made lowercase.
    airline = models.OneToOneField(
        Airline, on_delete=models.CASCADE, db_column='Airline_ID', related_name="Flight_Airline", primary_key=True)
    # Field name made lowercase.
    flight_id = models.IntegerField(db_column='Flight_ID')
    # Field name made lowercase.
    capacity = models.IntegerField(db_column='Capacity', blank=True, null=True)
    # Field name made lowercase.
    fare = models.IntegerField(db_column='Fare', blank=True, null=True)
    # Field name made lowercase.
    workday = models.IntegerField(db_column='Workday', blank=True, null=True)
    # Field name made lowercase.
    depart_time = models.TimeField(
        db_column='Depart_time', blank=True, null=True)
    # Field name made lowercase.
    depart_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, db_column='Depart_Airport', related_name="Flight_Depart_Airport", blank=True, null=True)
    # Field name made lowercase.
    arrive_time = models.TimeField(
        db_column='Arrive_time', blank=True, null=True)
    # Field name made lowercase.
    arrive_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, db_column='Arrive_Airport', related_name="Flight_Arrive_Airport", blank=True, null=True)
    # Field name made lowercase. Field renamed because of name conflict.
    fare_0 = models.ForeignKey(
        FareRestriction, on_delete=models.CASCADE, db_column='Fare_ID', blank=True, null=True)

    class Meta:
        db_table = 'Flights'
        unique_together = (('airline', 'flight_id'),)


class Account(models.Model):
    # Field name made lowercase.
    customer = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, db_column='Customer_ID', primary_key=True)
    # Field name made lowercase.
    account_id = models.IntegerField(db_column='Account_ID')
    # Field name made lowercase.
    create_date = models.DateField(
        db_column='Create_date', blank=True, null=True)
    # Field name made lowercase.
    credit_card = models.CharField(
        db_column='Credit_card', max_length=45, blank=True, null=True)
    # Field name made lowercase.
    reservation = models.ForeignKey(
        'ReservationInfo', on_delete=models.CASCADE, db_column='Reservation_ID')
    # Field name made lowercase.
    airline = models.ForeignKey(
        'ReservationInfo', on_delete=models.CASCADE, related_name="Account_Airline", db_column='Airline_ID', blank=True, null=True)
    # Field name made lowercase.
    flight = models.ForeignKey(
        'ReservationInfo', on_delete=models.CASCADE, related_name="Account_flight", db_column='Flight_ID', blank=True, null=True)

    def __str__(self):
        return self.account_id

    class Meta:
        db_table = 'Account'
        unique_together = (
            ('customer', 'account_id', 'reservation', 'airline', 'flight'),)


class ReservationFlight(models.Model):
    # Field name made lowercase.
    reservation = models.ForeignKey(
        'ReservationInfo', on_delete=models.CASCADE, db_column='Reservation_ID', primary_key=True)
    # Field name made lowercase.
    airline_id = models.CharField(db_column='Airline_ID', max_length=5)
    # Field name made lowercase.
    flight_id = models.IntegerField(db_column='Flight_ID')
    # Field name made lowercase.
    p_name = models.CharField(db_column='P_name', max_length=20)
    # Field name made lowercase.
    p_seat = models.IntegerField(db_column='P_seat', blank=True, null=True)
    # Field name made lowercase.
    p_meal = models.CharField(
        db_column='P_meal', max_length=10, blank=True, null=True)
    # Field name made lowercase.
    p_class = models.CharField(
        db_column='P_class', max_length=10, blank=True, null=True)
    # Field name made lowercase.
    price = models.IntegerField(db_column='Price', blank=True, null=True)

    class Meta:
        db_table = 'Reservation_Flight'
        unique_together = (
            ('reservation', 'airline_id', 'flight_id', 'p_name'),)


class ReservationInfo(models.Model):
    # Field name made lowercase.
    reservation_id = models.AutoField(
        db_column='Reservation_ID', primary_key=True)
    # Field name made lowercase.
    order_date = models.DateField(
        db_column='Order_date', blank=True, null=True)
    # Field name made lowercase.
    total_cost = models.IntegerField(
        db_column='Total_cost', blank=True, null=True)
    # Field name made lowercase.
    book_fee = models.IntegerField(db_column='Book_fee', blank=True, null=True)
    # Field name made lowercase.
    leave_date = models.DateField(
        db_column='Leave_date', blank=True, null=True)
    # Field name made lowercase.
    representative_id = models.CharField(
        db_column='Representative_ID', max_length=10, blank=True, null=True)
    # Field name made lowercase.
    airline = models.ForeignKey(
        Flights, on_delete=models.CASCADE, db_column='Airline_ID', related_name="Reserve_Airline")
    # Field name made lowercase.
    flight = models.ForeignKey(
        Flights, on_delete=models.CASCADE, db_column='Flight_ID', related_name="Reserve_Flight")

    class Meta:
        db_table = 'Reservation_Info'
        unique_together = (
            ('reservation_id', 'airline', 'flight'),)
