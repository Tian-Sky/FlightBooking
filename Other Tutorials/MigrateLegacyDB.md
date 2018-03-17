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