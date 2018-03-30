# Change DB in MySQL and migrate in Django

Sometimes, you may want to make changes in MySQL and then migrate with Django. Although it is not a good idea, but you may need to do it. E.g., Django does not support composite primary key, but you want your table in MySQL do have composite primay key. Or maybe you already start your Django project, then you realize you want to change something in MySQL. The following may hlep you to remedy:

Run
```
python manage.py runserver
```

First under you app folder, cut all everything out from views.py, models.py, admin.py. Also in urls.py file, cut all content from "urlpatterns". Fix all bugs until your terminal indicate your server is running without any problems.

Then run 

```
python manage.py inspectdb > YourApp/models.py
```

This will create new models, which use the adapted DB information. Now go to YourApp/models.py file, adapt your model. Delete all "managed=false". For all "clashes with reverse error", add "related_name=YourTag". You may also want to change "models.DO_NOTHING" to "on_delete=models.CASCADE".

Now, go to YourApp/migrations, delete everything except __init__.py file. Then run 


```
python manage.py migrate
```

Done, your app is now ready to use you new models from adapated DB. You can test in shell.

Don't forget to paste your content back and fix all possible bugs. (As you may changed the name of table in your DB)

You also need to reset superuser for your admin page.

Related tutorial [here](https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html).

## Add new models to models.py

After you migrate your legacy db, you may want to add new models to your models.py, i.e., you may need to create new tables in you db. Do the following:

run:

```
python manage.py makemigrations
```

This will create a file called 0001_initial.py. This file will contains the sql to create all the table that you already have in your db. Now run:

```
python manage.py migrate polls --fake
```

This will fake migrations. We already have those tables in db, so we don't want Django to create them again. But we need to tell Django so that Django know those table exist. In terminal info you should see a file with prefix 0002 created. Then run:

```
python manage.py migrate
```

No errors should show up. Then add your new model in mondels.py. Make sure you save your file after you change it.

Run:

```
python manage.py makemigrations polls
python manage.py sqlmigrate polls 0002
python manage.py migrate
```

That's it, your new model should have corresponding table created in db now. But its table name in db will have a prefix, which is your Django application name.