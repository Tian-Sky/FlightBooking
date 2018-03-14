# MySql for flight ticket booking website

This project is used for 2018 Spring class CS539 Database Implementation. This project needs to use AWS MySql service. Then build a flight ticket booking website with that database.

First you need to install Django:

```
pip install django
```

Then clone the project and run:

```
cd FlightBooking
python manage.py runserver
```
You should now able to see the website index page at localhost:8000

By default, Django use sqlite as database. For this project, we need to use MySql. So we need to first install mysql:

```
brew install mysql
pip instal mysqlclient
```

After install mysql, you need to set a user name and password for it. Do not use default root name, that's a bad idea. Lon in mysql with new user name and password, and create a database for Django to use later. Now, we need to change mysite/settings.py file.

```
DATABASES = {
	'default': {
		#Change default ENGINE and NAME
		'ENGINE': 'django.db.backends.mysql',
       'NAME': 'YOUR DATABASE NAME',
       'USER': 'USER NAME FOR MYSQL',
       'PASSWORD': 'PASSWORD FOR MYSQL',
       'HOST': '127.0.0.1',
       'PORT': '3306',
	}
}
```
