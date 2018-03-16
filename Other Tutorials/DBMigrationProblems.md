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

## Problems with exist table before migration

I met another problem when migrating. Before migrate, as I followed the official tutorial, I have two models called Question and Choice under polls/model.py, and I already did migration once. Then I ceate a new Database in mysql, and try to migrate with that new database. 

The problem is the original table Question and Choice won't be created in new database, even though the new models do have tables created in the new database. The following comman can fix this problem.

1. Drop tables. (If you start with a new database, you can ignore this)
2. comment-out the problem models in model.py(in my example, it is Question and Choice). You probably need to comment-out other places if you import the model in other files. 
3. Run 

	```
	python manage.py makemigrations
	python manage.py migrate --fake
	```

4. Comment-in all places you comment-out before
5. Run

	```
	python manage.py makemigrations
	python manage.py migrate
	``` 
	
That's it. You should have the table created in your database now.

This tutorial [here](https://docs.djangoproject.com/en/1.8/topics/migrations/#upgrading-from-south) may also be helpful.