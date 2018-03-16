# Problems and errors with html page and Django server

Here I describe all the erros I met when I write html page with html and Django. Also try to provide solutions to them.

#### CSRF verification failed. Request aborted.

You need to add the {% csrf_token %} template tag as a child of the form element in your Django template. Official guide [here](https://docs.djangoproject.com/en/dev/ref/csrf/).


#### Pass newly defined key value pair to form when submit

```
$("#form").submit( function(eventObj) {
      $('<input />').attr('type', 'hidden')
          .attr('name', "something")
          .attr('value', "something")
          .appendTo(this);
      return true;
  });
```