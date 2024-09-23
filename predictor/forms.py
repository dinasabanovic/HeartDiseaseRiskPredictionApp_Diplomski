from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Patient, Doctor
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

    
CustomUser = get_user_model()

  
class HeartDiseaseForm(forms.Form):
    age = forms.IntegerField(label='Age')
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], label='Gender')
    cp = forms.ChoiceField(choices=[('TA', 'Typical Angina'), ('ATA', 'Atypical Angina'), ('NAP', 'Non-Anginal Pain'), ('ASY', 'Asymptomatic')], label='Chest Pain Type')
    trestbps = forms.IntegerField(label='Resting BP')
    chol = forms.IntegerField(label='Cholesterol [mg/dl]')
    fbs = forms.ChoiceField(choices=[(1, 'Yes'), (0, 'No')], label='Fasting BS (> 120 mg/dl)')  # 1 if FastingBS > 120 mg/dl, 0 otherwise
    restecg = forms.ChoiceField(choices=[('Normal', 'Normal'), ('ST', 'ST'), ('LVH', 'LVH')], label='Resting ECG')
    maxhr = forms.IntegerField(label='Max HR')
    exang = forms.ChoiceField(choices=[('Y', 'Yes'), ('N', 'No')], label='Exercise Angina')
    oldpeak = forms.FloatField(label='Oldpeak')
    slope = forms.ChoiceField(choices=[('Up', 'Upsloping'), ('Flat', 'Flat'), ('Down', 'Downsloping')], label='ST Slope')


def validate_doctor_id(value):
    if len(value) != 10 or not value.isdigit():
        raise ValidationError('Doctor ID must be exactly 10 digits.')

class DoctorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    email = forms.EmailField(required=True, label='Email')
    doctor_id = forms.CharField(max_length=10, label='Doctor ID', validators=[validate_doctor_id])
    usable_password = None 

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'doctor_id')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Set username to email to avoid duplicate usernames
        user.user_type = 'doctor'  # Set user type to doctor
        if commit:
            user.save()
        doctor = Doctor(user=user, doctor_id=self.cleaned_data['doctor_id'])
        if commit:
            doctor.save()
        return user

class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    email = forms.EmailField(required=True, label='Email')
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)), label='Date of Birth')
    usable_password = None

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  
        user.user_type = 'patient'  
        if commit:
            user.save()
        patient = Patient(user=user, date_of_birth=self.cleaned_data['date_of_birth'])
        if commit:
            patient.save()
        return user
    
class SelectDoctorForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['doctor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['doctor'].label_from_instance = self.get_doctor_name

    def get_doctor_name(self, doctor):
        return f"Dr. {doctor.user.first_name} {doctor.user.last_name}"
    

class RecommendationForm(forms.Form):
    recommendations = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    custom_recommendation = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        recommendations_choices = kwargs.pop('recommendations_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['recommendations'].choices = recommendations_choices


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email') 



