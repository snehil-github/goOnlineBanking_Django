# import xlsxwriter
import json
from datetime import date
from .models import Customer
from .serializers import CustomerSerializer
from clientApp import views


def excel_generator():

    # time_ = date.today()
    # workbook = xlsxwriter.Workbook("Account Statement_"+str(time_)+".xlsx")
    # worksheet = workbook.add_worksheet("Sheet First")

    customer = Customer.objects.get(id=1)
    print(customer)
    json_data = json.dumps(list(customer))
    print(json_data)


    # workbook.close()

