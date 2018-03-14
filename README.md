# MySQL for flight ticket booking website

This project is used for 2018 Spring class CS539 Database Implementation. It includes RDS Service on AWS as database, and Django website host on AWS Elastic Beanstalk. The website and database is designed for flight ticket booking system.

Before you start the whole project, you probably want to creat a virtual environment so that your project environment won't mess up your computer default environment.

To do so, you need to install anaconda first. Download page [here](https://www.anaconda.com/download/#macos). Remember to include conda path to your ./bash_profile, otherwise you cannot use command conda in terminal.

To create a virtual environment:

```
conda create -n YourEnvName python=x.x anaconda
```

To activate:

```
source activate YourEnvName
```

Make sure you actviate under the folder where you create the environment. For installation in the environment, directly use pip install.

## Set local Django repository

First you need to install Django:

```
pip install django
```

Then clone the project and run:

```
cd FlightBooking
python manage.py runserver
```
You should now able to see the website index page at localhost:8000. If you directly start with files here, you will have errors, please go to [Django document page](https://docs.djangoproject.com/en/2.0/intro/tutorial01/) for start tutorial.

By default, Django use sqlite as database. For this project, we need to use MySQL. So we need to first install MySQL:

```
brew install mysql
pip instal mysqlclient
```

After install MySQL, you need to set a user name and password for it. Do not use default root name, that's a bad idea. Lon in MySQL with new user name and password, and create a database for Django to use later. Now, we need to change mysite/settings.py file.

```
DATABASES = {
	'default': {
		#Change default ENGINE and NAME
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'YOUR DATABASE NAME',
		'USER': 'USER NAME FOR MySQL',
		'PASSWORD': 'PASSWORD FOR MySQL',
		'HOST': '127.0.0.1',
		'PORT': '3306',
	}
}
```

More tutorial about database set for Django can be find [here](https://docs.djangoproject.com/en/2.0/intro/tutorial02/).

## Set AWS RDS Server

Go to AWS, in console, click "Launch DB instance". For AWS services, we use RDS. 

Then select MySQL as the engine. In the same page, make sure you select "Only enable option eligible for RDS Free Usage Tier" at bottom.

Here we use the following for "Specify DB Details":

* License model: general-public-license
* DB engine version: mysql 5.6.37
* DB Instance Class: db.t2.micro -- 1 vCPU, 1 GiB RAM
* Allocated Storage: 20 GB

Just set user name and password for your database in next page.

For "Network & security":

* Virtual Private Cloud: Default VPC (vpc-<unique number>)
* Public accessibility: Yes
* Availability zone: No preference
* VPC Security groups: Create new VPC security group

Leave it as it is for Database options page.

For Encryption page, use following for backup:

* Backup retention period: 7 Days
* Backup window: No preference 

For Monitoring:

* Enhanced monitoring: Disable enhanced monitoring

For Log exports page, Maintenance:

* Auto minor version upgrade: Enable auto minor version upgrade
* Maintenance window: No preference

Now your RDS server is created. We need it to allow connection from anywhere. Scroll down on your instance's page and find "security Group Rules". Click on the security group for type CIDR/IP - Inbound. Change "Source" to "Anywhere" and click save.

Done. You can scroll down the page to "Connect" section, where you wil find the Endpoint for you RDS Server. That's the host name you will use to connect to your database.

## Hosting Django website on AWE Elastic Beanstalk

You can find *clear* AWS official tutorial [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html). Pay attention to following points:

You need first to install Elastic Beanstalk Command Line Interface (EB CLI). [Tutorial here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html).

When you create .ebextensions/django.config, make sure to change the WSGIPath to YourProjectName/wsgi.py, otherwise it won't work.

If you use git as version control for your project, you must commit before you run eb deploy. The new changes work only after commit.

If this is the first time you use AWS, you will be asked to provide access key. Follow [this tutoral](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to create IAM group.

Make sure you change database settings to RDS Server and migrate. Also, for static files to work, you need to add STATIC_ROOT as mentioend in the tutorial.

If you cannot find your environment in EB Console, you may need to change region at the upper right corner.

After all the settings, `db open` will open your index page in the browser.

## Point Google domain to Elastic Beanstalk

In terminal, use `eb status` to find CNAME of your current Django application.

Go to google domain, scroll down to the bottom. Find "Custom resource records" category. In NAME, enter www. Select CNAME for type, TTL for default. Fill the CNAME you find from terminal to DATA column. Click add. Now you can use www.example.com to visit your website hold on elastic beanstalk.

An alternative way to do so can be find [here](https://medium.com/@limichelle21/connecting-google-domains-to-amazon-s3-d0d9da467650). But then you cannot use Google DNS. Instead, you use Amazon Route 53 and Amazon DNS. Not quite sure which one is faster.