# Use Ajax with Django

Why I want to use Ajax? Assuming you have a form, which allow users to register new account. When user enter the username, you want to check if that username already exist in database. If so a warning show up and ask user to re-enter. You can definitely do this with just Django and jquery, but you will need to wait user fill each input area and click the submit button, then Django function in views.py check it and refresh the page with warning.

What if I want to show warning immediately once user finished entering username and go to other input tag? I can do this with ajax. Ajax can call functions in view.py wihtout refresh the page.

First, include jquery in your html. Pay attention here, if you use Bootstrap and use slim jqeury, then ajax may not work. You will need to replace it with full version jquery. E.g.:

```html
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
```

The html part looks like this:

```html

<!-- in some form -->
<form class="needs-validation" novalidate action="{% url 'polls:register' %}" method="post" id="register" data-validate-email-url="{% url 'polls:validate_register_email' %}">{% csrf_token %}
<input type="email" class="form-control" id="register_email" name="email" aria-describedby="emailHelp" placeholder="Enter email">
</form>

<script>
    $("#register_email").change(function () {
        var form = $(this).closest("form");
        $.ajax({
            url: form.attr("data-validate-email-url"),
            data: form.serialize(),
            type: 'post',
            dataType: 'json',
            success: function (data) {
                if (data.is_taken) {
                    alert("A user with this username already exists.");
                }
            }
        });

    });
</script>
```

Then in views.py:

```python
def validate_register_email(request):
    # You can also use get
    email = request.POST.get('email', None)
    data = {
        'is_taken': Customer.objects.filter(email=email).exists(),
    }
    return JsonResponse(data)
```

Don't forget to change url in url.py:

```python
path('validate_register_email', views.validate_register_email,
         name='validate_register_email'),
```

Done. Now if user enter a username that already exist in database, a warning will jump out immediately without refresh the page.

## Ajax with Bootstrap DataTable

You can find introduction to DataTable [here](https://datatables.net/). It's a very useful tool for large table data. With Datatable, you will have sort, search and pagination implemented automatically. 

One important use of DataTable is it can load data gradually. See [here](https://datatables.net/examples/ajax/defer_render.html) for official document. 

As official document mentioned: When deferred rendering is enabled, rather than having DataTables create all TR and TD nodes required for the table when the data is loaded, DataTables will only create the nodes required for each individual row at the time of that row being drawn on the page (these nodes are then retained in case they are needed again so they aren't created multiple times). This can give a significant performance increase, since a lot less work is done at initialisation time.

But most officialy document talk about how ajax can get data from a txt file, here we illustrate how to get data from Django function in views.py and pass it to Ajax.

First in html:

```html
<body>
    <table id="active_flights_table" class="table table-striped table-bordered" style="width:100%">
        <thead>
            <tr>
                <th scope="col">FID</th>
                <th scope="col">Activeness</th>
                <th scope="col">Airline iD</th>
                <th scope="col">Flight ID</th>
                <th scope="col">Depart Airport</th>
                <th scope="col">Arrive Airport</th>
            </tr>
        </thead>
        <tbody>
            {% for flight in active_list %}
            <tr>
                {% for data in flight %}
                <td scope="col">{{ data }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>

<script>
    $(document).ready(function () {
        $('#active_flights_table').DataTable({
            "ajax": {
                "url": '{% url "polls:manager_most_active_flight" %}',
                "dataSrc": ""
            },
            "deferRender": true,
            "order": [[1, "desc"]]
        });
</script>
```

In views.py:

```python
def manager_most_active_flight(reqeust):
    # For active flights
    print("get here")
    active_list_result = get_best_seller()
    active_list = []
    for data in active_list_result:
        a_n = Airline.objects.get(airline_id=data[2]).airline_name
        d_name = Airport.objects.get(airport_id=data[4]).airport_name
        d_p = "("+str(data[4])+") "+str(d_name)
        p_name = Airport.objects.get(airport_id=data[5]).airport_name
        a_p = "("+str(data[5])+") "+str(p_name)
        current = [data[0], data[1], a_n, data[3], d_p, a_p]
        active_list.append(current)
    print("get data")
    # Here we pass an array directly, which is not strictly a json format, so Django require us to set "safe" to False.
    # You can definitely write it in json format, like {myData: []}
    # But then in html page, you need to change dataSrc:"" to dataSrc:"myData"
    return JsonResponse(active_list, safe=False)

```