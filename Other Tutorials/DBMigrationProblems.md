# Migrate with exist DB

If you want to migrate Django with an exsit Database. There are some matters need attention. 

The official tutorial can be found [here](https://docs.djangoproject.com/en/2.0/howto/legacy-databases/). Here is what I did:

First you need to change YOURPORJECT/settings.py, set new db database, name and so on. Then, execute

```
python manage.py inspectdb > models.py

```

If you have your own new apps, e.g. with official tutorial, we create new app called polls. You will need to use

```
python manage.py inspectdb > polls/models.py
```

***You will have errors*** if you already migrate with database before. E.g., with official tutorial polls app, you will have some models under polls/models.py, and you probably already registered it under polls/admin.py. You will need to delete them all. (You can cut them to other files, and paste them back after you execute the inspectdb.)

Now, in your polls/models.py, you should have all the models you just get from your database. Run:

```
python manage.py makemigrations polls
```

By running makemigrations, you’re telling Django that you’ve made some changes to your models (in this case, you’ve made new ones) and that you’d like the changes to be stored as a migration.

***You may have errors called  reverse accessor clashes***. It is raised by foreign key. You need to go to polls/models.py, find the problem line, add `related_name="NEWNAME"`. E.g., originally it looks like:

```
airline = models.ForeignKey(
        Flights, 
        on_delete=models.CASCADE, 
        db_column='Airline_ID')
```

Change it to:

```
airline = models.ForeignKey(
        Flights, 
        on_delete=models.CASCADE, 
        db_column='Airline_ID', 
        related_name="airline_related")
```

Also, you need to delete `managed = False` if you want Django able to change your database. You may also want to replace `models.donothing` with `on_delete=cascade` for your foreign key. Do not modify db_table values or field names.

After makemigrations, you should find a python file name start with 0001(maybe 0002, if you migrate second time) under polls/migrations. Assuming it is polls/migrations/0001_initial.py, run

```
python manage.py sqlmigrate polls 0001
```

Now add content back to polls/admin.py, include your new models in admin.py. You can see it on localhost:8080/admin page now.