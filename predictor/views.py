from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import HeartDiseaseForm, PatientRegistrationForm, DoctorRegistrationForm, SelectDoctorForm, RecommendationForm, EmailLoginForm
from .models import Doctor, Patient, Recommendation, Prediction
from django.contrib.auth import get_user_model
import pandas as pd
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from .utils import *
import joblib
import os


CustomUser = get_user_model()

def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('profile')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'register_doctor.html', {'form': form})

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('profile')
    else:
        form = PatientRegistrationForm()
    return render(request, 'register_patient.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = EmailLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  
            return redirect('home') 
    else:
        form = EmailLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    context = {}

    if user.user_type == 'doctor':
        try:
            profile = Doctor.objects.get(user=user)
            context['profile'] = profile
            context['doctor_id'] = profile.doctor_id
        except Doctor.DoesNotExist:
            context['error'] = "Doctor profile not found."

    elif user.user_type == 'patient':
        try:
            profile = Patient.objects.get(user=user)
            context['profile'] = profile
            predictions = Prediction.objects.filter(patient=profile).order_by('-prediction_date')
            if predictions.exists():
                latest_prediction = predictions.first()
                context['latest_prediction'] = latest_prediction
                context['predictions'] = predictions

            recommendations = Recommendation.objects.filter(patient=profile)
            context['recommendations'] = recommendations

            if request.method == 'POST':
                form = SelectDoctorForm(request.POST, instance=profile)
                if form.is_valid():
                    form.save()
                    return redirect('profile')
            else:
                form = SelectDoctorForm(instance=profile)

            context['form'] = form

        except Patient.DoesNotExist:
            context['error'] = "Patient profile not found."

    else:
        context['error'] = "User profile not found."

    return render(request, 'profile.html', context)


@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

models_path = os.path.join(os.path.dirname(__file__), 'trained_models')

model = joblib.load(os.path.join(models_path, 'best_rf_model.pkl'))
scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))
poly = joblib.load(os.path.join(models_path, 'poly.pkl'))
label_encoders = joblib.load(os.path.join(models_path, 'label_encoders.pkl'))

with open(os.path.join(models_path, 'model_accuracy.txt'), 'r') as f:
    accuracy = float(f.read().strip())


@login_required
def heart(request):
    user = request.user
    try:
        patient_profile = Patient.objects.get(user=user)
    except Patient.DoesNotExist:
        return HttpResponse("Patient profile not found.", status=404)

    if request.method == 'POST':
        form = HeartDiseaseForm(request.POST)
        if form.is_valid():
            user_data = {
                'Age': form.cleaned_data['age'],
                'Gender': form.cleaned_data['gender'],
                'ChestPainType': form.cleaned_data['cp'],
                'RestingBP': form.cleaned_data['trestbps'],
                'Cholesterol': form.cleaned_data['chol'],
                'FastingBS': form.cleaned_data['fbs'],
                'RestingECG': form.cleaned_data['restecg'],
                'MaxHR': form.cleaned_data['maxhr'],
                'ExerciseAngina': form.cleaned_data['exang'],
                'Oldpeak': form.cleaned_data['oldpeak'],
                'ST_Slope': form.cleaned_data['slope']
            }
            user_data_df = pd.DataFrame([user_data])

            # Preprocess the user data
            user_data_encoded = preprocessing(user_data_df, is_training=False, 
                                              label_encoders=label_encoders)
            user_data_poly = poly.transform(user_data_encoded)
            user_data_scaled = scaler.transform(user_data_poly)

            # Make prediction
            prediction = model.predict(user_data_scaled)[0]
            result = 'have' if prediction == 1 else "don't have"

            Prediction.objects.create(
                patient=patient_profile,
                age=form.cleaned_data['age'],
                gender=form.cleaned_data['gender'],
                chest_pain_type=form.cleaned_data['cp'],
                restingbp=form.cleaned_data['trestbps'],
                cholesterol=form.cleaned_data['chol'],
                fastingbs=form.cleaned_data['fbs'],
                restingecg=form.cleaned_data['restecg'],
                maxhr=form.cleaned_data['maxhr'],
                exerciseangina=form.cleaned_data['exang'],
                oldpeak=form.cleaned_data['oldpeak'],
                st_slope=form.cleaned_data['slope'],
                heart_disease_risk=result,
                prediction_date=timezone.now().date()
            )
            return redirect('profile')

    else:
        form = HeartDiseaseForm()

    return render(request, 'heart.html', {
        'form': form,
        'accuracy': accuracy,  
    })

def home(request):
    return render(request, 'home.html')


@login_required
def doctor_patients(request):
    if request.user.user_type != 'doctor':
        return redirect('profile')  
    doctor = get_object_or_404(Doctor, user=request.user)
    patients = Patient.objects.filter(doctor=doctor)

    return render(request, 'doctor_patients.html', {'patients': patients})



@login_required
def add_recommendation_to_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    latest_prediction = Prediction.objects.filter(patient=patient).order_by('-prediction_date').first()
    
    if not latest_prediction:
        return redirect('patient_detail', id=patient.id) 

    recommendations = get_recommendations(latest_prediction)

    if request.user.user_type != 'doctor':
        return redirect('profile')  

    if request.method == 'POST':
        selected_recommendations = request.POST.getlist('recommendations')
        custom_recommendation = request.POST.get('custom_recommendation', '').strip()

        recommendation_content = "\n".join(selected_recommendations)

        if custom_recommendation:
            recommendation_content += custom_recommendation

        Recommendation.objects.create(
            doctor=request.user.doctor,
            patient=patient,
            content=recommendation_content
        )
        return redirect('patient_detail', id=patient.id)  
    else:
        form = RecommendationForm()  
    return render(request, 'add_recommendation.html', {
        'form': form,
        'patient': patient,
        'recommendations': recommendations,
    })



@login_required
def patient_detail(request, id):
    patient = get_object_or_404(Patient, id=id)
    
    if (request.user.user_type == 'doctor' and patient.doctor == request.user.doctor) or (request.user.user_type == 'patient' and patient.user == request.user):
        recommendations = Recommendation.objects.filter(patient=patient).order_by('-created_at')  
        predictions = Prediction.objects.filter(patient=patient).order_by('-prediction_date')  
        
        return render(request, 'patient_detail.html', {
            'profile': patient,
            'recommendations': recommendations,
            'predictions': predictions
        })
    return redirect('profile')

@login_required
def delete_recommendation(request, recommendation_id):
    recommendation = get_object_or_404(Recommendation, id=recommendation_id)
    
    if request.user.user_type == 'doctor' and request.user.doctor == recommendation.doctor:
        recommendation.delete()
        return redirect('patient_detail', id=recommendation.patient.id)  
    else:
        return HttpResponseForbidden("You do not have permission to delete this note.")