from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Doctor, Patient, Prescription, passwordHasher, emailHasher
from django.db.models import Count, Q
from django.http import FileResponse

def index(request):
    response = render(request,"HealthCentre/index.html")
    return responseHeadersModifier(response)
def logout(request):
    request.session['isDoctor'] = ""
    request.session['isLoggedIn'] = False
    request.session['userEmail'] = ""
    request.session['Name'] = ""
    request.session['numberNewPrescriptions'] = ""

    response = HttpResponseRedirect(reverse('login'))
    return responseHeadersModifier(response)
def requestSessionInitializedChecker(request):
    try:
        if request.session['isDoctor'] and request.session['isLoggedIn'] and request.session['userEmail'] and request.session['Name'] and request.session['numberNewPrescriptions']:
           
            pass
    except:
        request.session['isDoctor'] = ""
        request.session['isLoggedIn'] = False
        request.session['userEmail'] = ""
        request.session['Name'] = ""
        request.session['numberNewPrescriptions'] = ""

    return request
def login(request):

    request = requestSessionInitializedChecker(request)

    if request.method == "GET":
        try:

            if request.session['isLoggedIn'] and request.session['isDoctor']:

                doctor = Doctor.objects.get(emailHash = request.session['userEmail'])
                records = doctor.doctorRecords.all()
                numberNewPendingPrescriptions = doctor.doctorRecords.aggregate(newPendingPrescriptions = Count('pk', filter =( Q(isNew = True) & Q(isCompleted = False) ) ))['newPendingPrescriptions']

                request.session['numberNewPrescriptions'] = numberNewPendingPrescriptions

                context = {
                    "message" : "Successfully Logged In.",
                    "isAuthenticated" : True,
                    "user": records.order_by('-timestamp')
                }

                response = render(request,"HealthCentre/userDoctorProfilePortal.html", context)
                return responseHeadersModifier(response)

            elif request.session['isLoggedIn'] and (not request.session['isDoctor']):

                patient = Patient.objects.get(emailHash = request.session['userEmail'])
                records = patient.patientRecords.all()
                numberNewPrescriptions = patient.patientRecords.aggregate(newCompletedPrescriptions = Count('pk', filter =( Q(isNew = True) & Q(isCompleted = True) ) ) )['newCompletedPrescriptions']

                request.session['numberNewPrescriptions'] = numberNewPrescriptions

                for record in records:
                    if record.isCompleted:
                        record.isNew = False
                        record.save()

                context = {
                    "message" : "Successfully Logged In.",
                    "isAuthenticated" : True,
                    "user": records.order_by('-timestamp')
                    }

                response = render(request,"HealthCentre/userPatientProfilePortal.html", context)
                return responseHeadersModifier(response)

            else:
                response = render(request,"HealthCentre/loginPortal.html")
                return responseHeadersModifier(response)

        except:

            response = render(request,"HealthCentre/loginPortal.html")
            return responseHeadersModifier(response)

    elif request.method == "POST":

        userName = request.POST["useremail"]
        userPassword = request.POST["userpassword"]

        try:
            patient = Patient.objects.get(email = userName)

            request.session['isDoctor'] = False

        except Patient.DoesNotExist:
            try:
                doctor = Doctor.objects.get(email = userName)

                request.session['isDoctor'] = True

            except Doctor.DoesNotExist:

                context = {
                    "message":"User does not exist.Please register first."
                }

                response = render(request,"HealthCentre/loginPortal.html", context)
                return responseHeadersModifier(response)

        passwordHash = passwordHasher(userPassword)

        if request.session['isDoctor']:

            records = doctor.doctorRecords.all()
            numberNewPendingPrescriptions = doctor.doctorRecords.aggregate(newPendingPrescriptions = Count('pk', filter =( Q(isNew = True) & Q(isCompleted = False) ) ))['newPendingPrescriptions']

            request.session['numberNewPrescriptions'] = numberNewPendingPrescriptions

            if passwordHash == doctor.passwordHash:

                request.session['isLoggedIn'] = True
                request.session['userEmail'] = doctor.emailHash
                request.session['Name'] = doctor.name

                response = HttpResponseRedirect(reverse('index'))
                return responseHeadersModifier(response)
            else:

                context = {
                    "message":"Invalid Credentials.Please Try Again."
                }

                response = render(request,"HealthCentre/loginPortal.html", context)
                return responseHeadersModifier(response)

        else:

            records = patient.patientRecords.all()
            numberNewPrescriptions = patient.patientRecords.aggregate(newCompletedPrescriptions = Count('pk', filter =( Q(isNew = True) & Q(isCompleted = True) ) ))['newCompletedPrescriptions']

            request.session['numberNewPrescriptions'] = numberNewPrescriptions

            for record in records:
                if record.isCompleted :
                    record.isNew = False
                    record.save()

            if passwordHash == patient.passwordHash:
                request.session['isLoggedIn'] = True
                request.session['userEmail'] = patient.emailHash
                request.session['Name'] = patient.name
                request.session['isDoctor'] = False

                response = HttpResponseRedirect(reverse('index'))
                return responseHeadersModifier(response)

            else:

                context = {
                    "message":"Invalid Credentials.Please Try Again."
                }

                response = render(request,"HealthCentre/loginPortal.html", context)
                return responseHeadersModifier(response)
    else:
        response = render(request,"HealthCentre/loginPortal.html")
        return responseHeadersModifier(response)

def responseHeadersModifier(response):
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
def register(request):
    if request.method == "GET":

        response =  render(request,"HealthCentre/registrationPortal.html")
        return responseHeadersModifier(response)

    elif request.method == "POST":

        userFirstName = request.POST["userFirstName"]
        userLastName = request.POST["userLastName"]
        userEmail = request.POST["userEmail"]
        userRollNo = request.POST["userRollNo"]
        userAddress = request.POST["userAddress"]
        userContactNo = request.POST["userContactNo"]
        userPassword = request.POST["userPassword"]
        userConfirmPassword = request.POST["userConfirmPassword"]

        if userPassword == userConfirmPassword:

            name = userFirstName + " " + userLastName

            passwordHash = passwordHasher(userPassword)

            emailHash = emailHasher(userEmail)

            patient = Patient(name = name,rollNumber = userRollNo, email = userEmail, passwordHash = passwordHash, address = userAddress, contactNumber = userContactNo, emailHash = emailHash )
            patient.save()

            context = {
                "message":"User Registration Successful. Please Login."
            }

            response = render(request, "HealthCentre/registrationPortal.html",context)
            return responseHeadersModifier(response)

        else:
            context = {
                "message":"Passwords do not match.Please register again."
            }

            response = render(request,"HealthCentre/registrationPortal.html",context)
            return responseHeadersModifier(response)

    else:

        response = render(request,"HealthCentre/registrationPortal.html")
        return responseHeadersModifier(response)
def onlineprescription(request):

    request = requestSessionInitializedChecker(request)

    if request.method == "GET":

        if request.session['isLoggedIn']:

            if request.session['isDoctor']:

                context = {
                        "message":"Only for patients."
                }

                response = render(request, "HealthCentre/prescriptionPortal.html", context)
                return responseHeadersModifier(response)

            else:

                context = {
                    "doctors" : Doctor.objects.all().order_by('specialization')
                }

                response = render(request, "HealthCentre/prescriptionPortal.html", context)
                return responseHeadersModifier(response)

        else:

            context = {
                    "message":"Please Login First."
            }

            response = render(request, "HealthCentre/prescriptionPortal.html", context)
            return responseHeadersModifier(response)

    elif request.method == "POST":

        if request.session['isLoggedIn']:

            if request.session['isDoctor']:

                prescriptionText = request.POST['prescription']

                prescription = Prescription.objects.get(pk = request.POST['prescriptionID'])
                prescription.prescriptionText = prescriptionText
                prescription.isCompleted = True
                prescription.isNew = True
                prescription.save()

                records = Doctor.objects.get(emailHash = request.session['userEmail']).doctorRecords.all()

                context = {
                    "user" : records,
                    "successPrescriptionMessage" : "Prescription Successfully Submitted."
                }

                response = render(request, "HealthCentre/userDoctorProfilePortal.html", context)
                return responseHeadersModifier(response)

            else:

                doctor = Doctor.objects.get(pk = request.POST["doctor"])
                symptoms = request.POST["symptoms"]

                prescription = Prescription(doctor = doctor, patient = Patient.objects.get(emailHash = request.session['userEmail']), symptoms = symptoms)
                prescription.save()

                context = {
                    "successPrescriptionMessage" : "Prescription Successfully Requested.",
                    "doctors"  : Doctor.objects.all().order_by('specialization')
                }

                response = render(request, "HealthCentre/prescriptionPortal.html", context)
                return responseHeadersModifier(response)

        else:

            context = {
                    "successPrescriptionMessage":"Please Login First.",
            }

            response = render(request, "HealthCentre/loginPortal.html", context)
            return responseHeadersModifier(response)

    else:

        response = render(request, "HealthCentre/prescriptionPortal.html")
        return responseHeadersModifier(response)
def doctors(request):

    context = {
        "doctors" : Doctor.objects.all()
    }
    response = render(request,"HealthCentre/doctors.html",context)
    return responseHeadersModifier(response)
def contactus(request):

    response = render(request, "HealthCentre/contactus.html")
    return responseHeadersModifier(response)
def pre(request):
    response=render(request,"HealthCentre/userDoctorProfilePortal.html")
    return responseHeadersModifier(response)
def emergency(request):
    
    if request.method == "GET":

        response = render(request,"HealthCentre/emergencyPortal.html")
        return responseHeadersModifier(response)

    
    elif request.method == "POST":

       
        emergencyLocation = request.POST['emergencyLocation']

        
        if emergencyLocation != "":

            
            print("------------------------------------------------------------------------")
            print("\n\nEMERGENCY !! AMBULANCE REQUIRED AT " + emergencyLocation + " !!\n\n")
            print("------------------------------------------------------------------------")

            
            context = {
                "message" : "Ambulance reaching " + emergencyLocation + " in 2 minutes."
            }

            
            response = render(request, "HealthCentre/emergencyPortal.html", context)
            return responseHeadersModifier(response)

        
        else:

           
            context = {
                "message" : "No location entered.Invalid input."
            }

            
            response = render(request, "HealthCentre/emergencyPortal.html", context)
            return responseHeadersModifier(response)

    
    else:

        
        response = render(request,"HealthCentre/emergencyPortal.html")
        return responseHeadersModifier(response)
def doclogin(request):
    request=requestSessionInitializedChecker(request)
    if request.method =='GET':
        try:

            if request.session['isLoggedIn'] :

                doctor = Doctor.objects.get(emailHash = request.session['userEmail'])
                records = doctor.doctorRecords.all()
                numberNewPendingPrescriptions = doctor.doctorRecords.aggregate(newPendingPrescriptions = Count('pk', filter =( Q(isNew = True) & Q(isCompleted = False) ) ))['newPendingPrescriptions']

                request.session['numberNewPrescriptions'] = numberNewPendingPrescriptions

                context = {
                    "message" : "Successfully Logged In.",
                    "isAuthenticated" : True,
                    "user": records.order_by('-timestamp')
                }

                response = render(request,"HealthCentre/userDoctorProfilePortal.html", context)
                return responseHeadersModifier(response)
            else:
                response = render(request,"HealthCentre/doctorlogin.html")
                return responseHeadersModifier(response)
        except:
            response = render(request,"HealthCentre/doctorlogin.html")
            return responseHeadersModifier(response)
    elif request.method =='POST':
        userName = request.POST["email"]
        userPassword = request.POST["password"]
        try:
                doctor = Doctor.objects.get(email = userName)

                request.session['isDoctor'] = True

        except Doctor.DoesNotExist:

                context = {
                    "message":"User does not exist.Please register first."
                }

                response = render(request,"HealthCentre/doctorlogin.html", context)
                return responseHeadersModifier(response) 
        
        passwordHash = passwordHasher(userPassword)
        records = doctor.doctorRecords.all()
        numberNewPendingPrescriptions = doctor.doctorRecords.aggregate(newPendingPrescriptions = Count('pk', filter =( Q(isNew = True) & Q(isCompleted = False) ) ))['newPendingPrescriptions']

        request.session['numberNewPrescriptions'] = numberNewPendingPrescriptions

        if passwordHash == doctor.passwordHash:

                request.session['isLoggedIn'] = True
                request.session['Email'] = doctor.emailHash
                request.session['Name'] = doctor.name

                response = HttpResponseRedirect(reverse('udp'))
                return responseHeadersModifier(response)
        else:

                context = {
                    "message":"Invalid Credentials.Please Try Again."
                }

                response = render(request,"HealthCentre/doctorlogin.html", context)
                return responseHeadersModifier(response)
    else:
        response = render(request,"HealthCentre/doctorlogin.html")
        return responseHeadersModifier(response)




def docregister(request):
    
    if request.method == "GET":

        response =  render(request,"HealthCentre/doctorRegistration.html")
        return responseHeadersModifier(response)
    elif request.method=='POST':
        userName = request.POST["Name"]
        userEmail = request.POST["Email"]
        userspec = request.POST["Specialization"]
        userAddress = request.POST["Address"]
        userContactNo = request.POST["ContactNo"]
        userPassword = request.POST["Password"]
        if userPassword:

            name = userName

            passwordHash = passwordHasher(userPassword)

            emailHash = emailHasher(userEmail)

            doctor = Doctor(name = name,specialization = userspec, email = userEmail, passwordHash = passwordHash, address = userAddress, contactNumber = userContactNo, emailHash = emailHash )
            doctor.save()

            context = {
                "message":"Registration Successful. Please Login."
            }

            response = render(request, "HealthCentre/doctorRegistration.html",context)
            return responseHeadersModifier(response)
        else:
            context = {
                "message":"Passwords do not match.Please register again."
            }

            response = render(request,"HealthCentre/doctorRegistration.html",context)
            return responseHeadersModifier(response)

    else:

        response = render(request,"HealthCentre/doctorRegistration.html")
        return responseHeadersModifier(response)
def udp(request):
       
        response = render(request,"HealthCentre/userDoctorProfile.html")
        return responseHeadersModifier(response)