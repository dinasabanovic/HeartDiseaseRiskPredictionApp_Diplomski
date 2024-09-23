from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'))
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor')
    doctor_id = models.CharField(max_length=10, unique=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if len(self.doctor_id) != 10:
            raise ValidationError("Doctor ID must be exactly 10 characters long.")

class Prediction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='predictions')
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    chest_pain_type = models.CharField(max_length=3, 
                                       choices=[('TA', 'Typical Angina'), 
                                                ('ATA', 'Atypical Angina'), 
                                                ('NAP', 'Non-Anginal Pain'), 
                                                ('ASY', 'Asymptomatic')])
    restingbp = models.IntegerField()
    cholesterol = models.IntegerField()
    fastingbs = models.IntegerField()  
    restingecg = models.CharField(max_length=6, choices=[('Normal', 'Normal'), ('ST', 'ST'), 
                                                         ('LVH', 'LVH')])
    maxhr = models.IntegerField()
    exerciseangina = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')])
    oldpeak = models.FloatField()
    st_slope = models.CharField(max_length=4, choices=[('Up', 'Upsloping'), ('Flat', 'Flat'), 
                                                       ('Down', 'Downsloping')])
    heart_disease_risk = models.CharField(max_length=20)  
    prediction_date = models.DateTimeField(auto_now_add=True)

class Recommendation(models.Model):
    content = models.TextField()
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    recommendation = models.CharField(max_length=255, blank=True, null=True)  

    class Meta:
        ordering = ['-created_at']

