import datetime
# import re
from clientApp import excel
from django.core.exceptions import ObjectDoesNotExist
# from django.contrib import messages
# from rest_framework.response import Response
from django.shortcuts import render
from random import randint
from clientApp.models import Customer, Record
from rest_framework.decorators import api_view
from .serializers import CustomerSerializer


# Create your views here.
# ******************** Logic for User Registration ***********************
def register(request):

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email'].lower()
        mno = request.POST['mno']
        pwd1 = request.POST['pwd1']
        pwd2 = request.POST['pwd2']
        address = request.POST['address']

        if Customer.objects.filter(email=email).exists():
            message = "This email address is already being used."
            return render(request, "registration.html", {"message": message})

        elif Customer.objects.filter(mno=mno).exists():
            message = "This phone number is already being used."
            return render(request, "registration.html", {"message": message})

        else:
            amnt = randint(1000000000000000, 9999999999999999)
            acn = randint(10000000000, 99999999999)

            if pwd1 == pwd2:
                cus = Customer(name=name,
                               email=email,
                               pwd=pwd1,
                               mno=mno,
                               address=address,
                               balance=0,
                               accno=acn,
                               atmno=amnt)
                cus.save()
                message = "Registration Successful."
                return render(request, "index.html", {"message": message})
            else:
                message = "Password doesn't match."
                return render(request, "registration.html", {"message": message})
    else:
        return render(request, "registration.html")


# *********************** Logic for User Login ***************************

def index(request):
    if request.method == 'POST':
        email = request.POST['email'].lower()
        pwd = request.POST['pwd']
        try:
            if Customer.objects.filter(email=email).exists():
                if Customer.objects.filter(email=email, pwd=pwd).exists():
                    customer = Customer.objects.get(email=email, pwd=pwd)
                    # Creating Session Here
                    request.session['cus_Id'] = customer.id
                    # Serializing customer object.
                    customer = Customer.objects.get(id=request.session['cus_Id'])
                    serializers = CustomerSerializer(customer)
                    return render(request, "home.html", {"serializers": serializers.data})

                else:
                    message = "Please enter valid login details!"
                    return render(request, "index.html", {"message": message})
            else:
                message = "The email address you've entered doesn't match any account."
                return render(request, "index.html", {"message": message})
        except ObjectDoesNotExist:
            message = "Requested object does not exists."
            return render(request, "index.html", {"message": message})

    else:
        return render(request, "index.html")


# ********************** Logic for User Logout ***************************
def logout(request):
    if request.session.has_key('cus_Id'):
        del request.session['cus_Id']
        return render(request, "index.html")
    else:
        return render(request, "index.html")


# ******************** Logic for User Home Page ************************
@api_view(['GET'])
def home(request):
    if request.session.has_key('cus_Id'):
        customer = Customer.objects.get(id=request.session['cus_Id'])
        serializers = CustomerSerializer(customer)
        # excel.excel_generator()
        return render(request, "home.html", {"serializers": serializers.data})
    else:
        return render(request, "index.html")


# ******************* Logic for account summary ************************
def summary(request):
    if request.session.has_key('cus_Id'):
        customer = Customer.objects.get(id=request.session['cus_Id'])

        if Record.objects.filter(accno=customer.accno).exists():
            records = Record.objects.filter(accno=customer.accno)
            return render(request, "summary.html", {"records": records})
        else:
            message = "Summary does not exists."
            return render(request, "home.html", {"message": message})
    else:
        print("Session is expired.")
        return render(request, "home.html")


# **********************Logic for Deposit Amount ***********************
def deposit(request):
    if request.session.has_key('cus_Id'):

        if request.method == 'POST':
            deposit_amount = int(request.POST['amount'])
            current_date = datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')
            customer_temp = Customer.objects.get(id=request.session['cus_Id'])

            if Record.objects.filter(cus_id=request.session['cus_Id']).exists():
                record_temp = Record(cus_id=request.session['cus_Id'],
                                     accno=customer_temp.accno,
                                     status='Deposit',
                                     rdate=current_date,
                                     amount=deposit_amount,
                                     bal=customer_temp.balance + deposit_amount
                                     )
                customer_temp.balance += deposit_amount
                record_temp.save()
                customer_temp.save()
                message = "Amount Deposited Successfully."
                return render(request, "deposit.html", {"message": message})

            else:
                print("Record doe's not exists.")
                record_temp = Record(cus_id=request.session['cus_Id'],
                                     accno=customer_temp.accno,
                                     status='Deposit',
                                     rdate=current_date,
                                     amount=deposit_amount,
                                     bal=deposit_amount
                                     )
                customer_temp.balance += deposit_amount
                record_temp.save()
                customer_temp.save()
                message = "Amount Deposited Successfully."
                return render(request, "deposit.html", {"message": message})

        else:
            return render(request, "deposit.html")

    else:
        print("Session is expired.")
        return render(request, "deposit.html")


# *********************Logic for Withdrawal Amount********************
def withdrawal(request):
    if request.session.has_key('cus_Id'):

        if request.method == 'POST':
            current_date = datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')
            withdrawal_amount = int(request.POST['amount'])
            customer_temp = Customer.objects.get(id=request.session['cus_Id'])
            # balance = customer_.balance - withdrawal_amount

            if customer_temp.balance != 0 and customer_temp.balance >= withdrawal_amount:
                if Record.objects.filter(cus_id=request.session['cus_Id']).exists():
                    record_temp = Record(cus_id=request.session['cus_Id'],
                                         accno=customer_temp.accno,
                                         status='Withdrawal',
                                         rdate=current_date,
                                         amount=withdrawal_amount,
                                         bal=customer_temp.balance - withdrawal_amount
                                         )
                    customer_temp.balance -= withdrawal_amount
                    record_temp.save()
                    customer_temp.save()
                    message = "Amount Withdrawal Successfully."
                    return render(request, "withdrawal.html", {"message": message})

            else:
                message = "Insufficient Amount!!"
                return render(request, "withdrawal.html", {"message": message})
        else:
            return render(request, "withdrawal.html")

    else:
        print("Session is expired.")
        return render(request, "withdrawal.html")


# *********************Logic for Transfer Amount ***********************
def transfer(request):
    if request.session.has_key('cus_Id'):

        if request.method == 'POST':
            rcr_account_num = request.POST['account']
            rcr_account_num_temp = request.POST['account_temp']

            if rcr_account_num == rcr_account_num_temp:

                if Customer.objects.filter(accno=rcr_account_num).exists():
                    transfer_amount = int(request.POST['amount'])
                    sender_temp = Customer.objects.get(id=request.session['cus_Id'])
                    receiver_temp = Customer.objects.get(accno=rcr_account_num)

                    if transfer_amount > 0:

                        if sender_temp.balance != 0 and sender_temp.balance >= transfer_amount:
                            current_date = datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')

                            if Record.objects.filter(cus_id=request.session['cus_Id']).exists():
                                record_temp_from = Record(cus_id=request.session['cus_Id'],
                                                          accno=sender_temp.accno,
                                                          status='Transfer',
                                                          rdate=current_date,
                                                          amount=transfer_amount,
                                                          bal=sender_temp.balance - transfer_amount
                                                          )
                                record_temp_to = Record(cus_id=receiver_temp.id,
                                                        accno=receiver_temp.accno,
                                                        status='Deposit',
                                                        rdate=current_date,
                                                        amount=transfer_amount,
                                                        bal=receiver_temp.balance + transfer_amount
                                                        )
                                sender_temp.balance -= transfer_amount
                                receiver_temp.balance += transfer_amount
                                record_temp_from.save()
                                record_temp_to.save()
                                sender_temp.save()
                                receiver_temp.save()
                                message = "Amount Transferred Successfully."
                                return render(request, "transfer.html", {"message": message})

                            else:
                                message = "Insufficient Amount!!!"
                                return render(request, "transfer.html", {"message": message})
                        else:
                            message = "Insufficient Amount!!!"
                            return render(request, "transfer.html", {"message": message})
                    else:
                        message = "Amount is invalid."
                        return render(request, "transfer.html", {"message": message})
                else:
                    message = "Receiver account does not exists."
                    return render(request, "transfer.html", {"message": message})
            else:
                message = "Account number doesn't match."
                return render(request, "transfer.html", {"message": message})
        else:
            return render(request, "transfer.html")
    else:
        print("Session is expired.")
        return render(request, "transfer.html")



def services(request):
    return render(request, "services.html")


def contacts(request):
    return render(request, "contacts.html")


def about(request):
    return render(request, "about.html")
