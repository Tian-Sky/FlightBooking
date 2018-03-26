# Django Access Database Data

Django create all database table into its own model. For offical document about Model, please check [here](https://docs.djangoproject.com/en/2.0/topics/db/models/).

## Access data via model
To insert into db, we can do

```python
>>> from polls.models import Blog
>>> b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
>>> b.save()
```

### Create object with foreign key

Official tutorla [here](https://docs.djangoproject.com/en/2.0/ref/models/relations/).

```python
>>> b = Blog.objects.get(id=1)
>>> e = b.entry_set.create( #Entry is the name of your mode, you need to change it to YourModelName_set
...     headline='Hello',
...     body_text='Hi',
...     pub_date=datetime.date(2005, 1, 1)
... )

# No need to call e.save() at this point -- it's already been saved.
```

This is equivalent to (but much simpler than):

```python
>>> b = Blog.objects.get(id=1)
>>> e = Entry(
...     blog=b,
...     headline='Hello',
...     body_text='Hi',
...     pub_date=datetime.date(2005, 1, 1)
... )
>>> e.save(force_insert=True)
```

To add foreign key to exist record:

```python
>>> b = Blog.objects.get(id=1)
>>> e = Entry.objects.get(id=234)
>>> b.entry_set.add(e) # Associates Entry e with Blog b.
```


## Use manager
If you want to add particular query function to a model class, you can use manager, so that you can resue the query easily. Official doucment [here](https://docs.djangoproject.com/en/2.0/topics/db/managers/).

By default Django provides a manager called objects, it is used to provide all records in database. Recall you can get all data via Blog.objects.all().

You can create your own manager:

```python
from django.db import models

class PollManager(models.Manager):
    def with_counts(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.question, p.poll_date, COUNT(*)
                FROM polls_opinionpoll p, polls_response r
                WHERE p.id = r.poll_id
                GROUP BY p.id, p.question, p.poll_date
                ORDER BY p.poll_date DESC""")
            result_list = []
            for row in cursor.fetchall():
                p = self.model(id=row[0], question=row[1], poll_date=row[2])
                p.num_responses = row[3]
                result_list.append(p)
        return result_list

class OpinionPoll(models.Model):
    question = models.CharField(max_length=200)
    poll_date = models.DateField()
    objects = PollManager()

class Response(models.Model):
    poll = models.ForeignKey(OpinionPoll, on_delete=models.CASCADE)
    person_name = models.CharField(max_length=50)
    response = models.TextField()
```
With this example, you’d use OpinionPoll.objects.with_counts() to return that list of OpinionPoll objects with num_responses attributes.

## Raw sql
We can also use row sql in Django. If you have complex foreign keys, or you want to complex join, then Django default model function may not enough. You will need to use raw sql to fetch data from db to write data to db.

Offical doucment about raw sql [here](https://docs.djangoproject.com/en/2.0/topics/db/sql/).

### Use raw sql with model
You can use raw sql with mode together:

```python
Person.objects.raw('SELECT id, first_name, last_name, birth_date FROM myapp_person')
```

Pass parameter into raw:

```python
lname = 'Doe'
Person.objects.raw('SELECT * FROM myapp_person WHERE, last_name = %s', [lname])
```

### Execute raw sql directly

Fisrt you can write you sql into a map, and use it via key

```python
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
}
```

Then execute it like this:

```python
one_stop = one_stop_flight(
        from_location, to_location, leave_day % 2, (leave_day+1) % 2)

def one_stop_flight(start, end, workday1, workday2):
    query = RAW_SQL['ONE_STOP_FLIGHT'].format(start_airport=start, end_airport=end, workday1=workday1,
                                              workday2=workday2)
    # print(query)
    return execute_custom_sql(query)

def execute_custom_sql(s):
    cursor = connection.cursor()
    cursor.execute(s)
    return cursor.fetchall()
```

The function execute_custom_sql do not necessarily need to return a result, if you only insert data into db table.

PS: If you test write data to db, and want to delete it later, you may find you cannot delete it due to foreign key constrain. You can bypass it by using:

```sql
SET foreign_key_checks = 0;
DELETE FROM users where id > 45;
SET foreign_key_checks = 1;
```