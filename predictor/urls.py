from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('profile/', views.profile, name='profile'),
    path('heart/', views.heart, name='heart'),
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    path('patient/<int:id>/', views.patient_detail, name='patient_detail'),
    path('patient/<int:patient_id>/add_recommendation/', 
         views.add_recommendation_to_patient, name='add_recommendation'),
    path('recommendation/delete/<int:recommendation_id>/', 
         views.delete_recommendation, name='delete_recommendation'),
]

