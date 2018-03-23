# Use Django authentication system

The official tutorial is [here](https://docs.djangoproject.com/en/2.0/topics/auth/default/#user-objects).

When we build the website, we may need to build the log in system, and to check if the user already logged in. This tutorial mainly talk about how to do this in a simple way.

## User object

Firstly, Django provides User object to represent each user. If we want to use the default authentication system, we need to use this User object. This user object can later tell us if the user already logged in easily. A few main points abour User object:

* Different user has different permissions. Django provides 'superuser', 'staff' and comman user. Superuser has all permissions without explicitly assigning them. Staff can access the admin site. User object has boolean vairable is_staff and is_superuser to indicate those.
* Primay attributes of User obejcts are 'username', 'password', 'email', 'first_name', 'last_name'. Once you have the User object, you can directly access them. 
* To create user, you can use 'create_user()' helper function.

```python
from django.contrib.auth.models import User

user = User.objects.create_user('tian', 'tian@test.com', 'tianpassword')
user.last_name = sky
user.save()
```

You can also create user from Django admin page.

To create superuser:

```shell
python manage.py createsuperuser --username=joe --email=joe@example.com
```

## Authentication in view.

To authenticate with Django authentication system, you will need a form in html template and a corresponding view method in view.py. You also need to set url in your url.py file.

In html template:

```html
<form action="{% url 'polls:login' %}" method="post">{% csrf_token %}
    <div class="form-group">
        <label for="exampleInputEmail1">Email address</label>
        <input type="email" class="form-control" id="exampleInputEmail1" name="email" aria-describedby="emailHelp" placeholder="Enter email">
    </div>
    <div class="form-group">
        <label for="exampleInputPassword1">Password</label>
        <input type="password" class="form-control" id="exampleInputPassword1" name="password" placeholder="Password">
    </div>
    <button type="submit" class="btn btn-primary" style="background-color:green">Submit</button>
</form>
```

Here I use email address as log in user name. You can change it to pure string. In my url.py file, I have

```python
path('login', views.login_page, name='login'),
```

So in my view.py file, I have:

```python
from django.contrib.auth import authenticate, login

def login_page(request):
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user) #Log in user
        # Redirect to a success page.
        if user.is_superuser:
            return HttpResponseRedirect(reverse('polls:manager'))
        else:
            return HttpResponseRedirect(reverse('polls:index_default'))
    else:
        # Return an 'invalid login' error message.
        return HttpResponseRedirect(reverse('polls:index_warning'))
```

If the user is superuser, I redirect it to a manager page. If otherwise it is a common user, I redirect it to original page. If I cannot find the user, I redirect it to index page with warning.

Once you have user log in, in html page you can directly check it by using 

```html
{% if user.is_authenticated %}
```

To log user out:

```python
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    # Redirect to a success page.
```

If you want to redirect unloged user to other page, in views.py you can do:

```python
user = request.user
if not user.is_authenticated:
        return HttpResponseRedirect(reverse('polls:index_default'))
```

Django also provides power other function, like limiting access, default view template. For thsoe imformation please check [official document](https://docs.djangoproject.com/en/2.0/topics/auth/default/#user-objects).