"""
Convert URLs
"""
from django.urls import path

from . import views

# Set app_name so that different apps' urls can be used in html
app_name = 'polls'
urlpatterns = [
    # path('', views.IndexView.as_view(), name='index'),
    path('', views.index_default, name='index_default'),
    path('<int:warning_id>/warning', views.index_warning, name='index_warning'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:question_id>/', views.detail, name='detail'),
    # path('<int:question_id>/results/', views.results, name='results'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
    path('validate_register_email', views.validate_register_email,
         name='validate_register_email'),
    path('search', views.search, name='search'),
    path('customer', views.customer, name='customer'),
    path('manager', views.manager, name="manager"),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('book', views.book, name='book'),
    path('book_one_stop', views.book_one_stop, name='book_one_stop'),
    path('buy', views.buy, name="buy"),
    path('register', views.register, name="register"),
    path('update_info', views.update_info, name="update_info"),
    path('sales_month', views.sales_month, name="sales_month"),
    path('get_all_flights', views.get_all_flights, name="get_all_flights"),
    path('get_reservations_with_flight', views.get_reservations_with_flight,
         name='get_reservations_with_flight'),
    path('get_reservations_with_customer', views.get_reservations_with_customer,
         name='get_reservations_with_customer'),
    path('get_delay_flights', views.get_delay_flights,
         name='get_delay_flights'),
    path('get_airport_flights', views.get_airport_flights,
         name='get_airport_flights'),
    path('get_reserved_customers', views.get_reserved_customers,
         name='get_reserved_customers'),
    path('manager_update_user', views.manager_update_user,
         name='manager_update_user'),
    path('get_manage_customer_id', views.get_manage_customer_id,
         name='get_manage_customer_id'),
    path('manager_delete_customer', views.manager_delete_customer,
         name='manager_delete_customer'),
    path('manager_most_active_flight', views.manager_most_active_flight,
         name='manager_most_active_flight'),
]
