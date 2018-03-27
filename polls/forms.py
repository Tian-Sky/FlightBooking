from django import forms


class RegisterForm(forms.Form):
    email = forms.CharField(
        label='email', max_length=45)
    password1 = forms.CharField(
        label='password1', max_length=20)
    password2 = forms.CharField(
        label='password2', max_length=20)
    card1 = forms.IntegerField(
        label='card1')
    card2 = forms.IntegerField(
        label='card2', required=False)
    card3 = forms.IntegerField(
        label='card3', required=False)
    firstName = forms.CharField(
        label='firstName', max_length=20)
    lastName = forms.CharField(
        label='lastName', max_length=20)
    address = forms.CharField(
        label='address', max_length=45, required=False)
    city = forms.CharField(
        label='city', max_length=20, required=False)
    state = forms.CharField(
        label='state', max_length=20, required=False)
    zip = forms.IntegerField(
        label='zip', required=False)
    phone = forms.IntegerField(
        label='phone', required=False)
