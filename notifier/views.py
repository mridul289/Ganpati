from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.urls import reverse_lazy, reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import *
import requests
from requests.structures import CaseInsensitiveDict

def whatsapp_send(number, salesman, amount):
    url = "https://graph.facebook.com/v14.0/101165502755328/messages"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer EAASJZBQ7hCpQBAKfjiwKdgaQumBrrbh8ehevGyBBirkLtkycug71MDqt77mvWhIUDpGmm4ZCvZAwo2yimEwpjGM72XIpZClVzjqEssj2WtkxPD3qtsOAzZA9qDGyBzOqpCFaxVAUIzZBYeZCrZBIyFvZBIi5YAwWiZC3uafF3D2YluayGcuKEJ1yNW0AZAac9XlH3oMBvDDqV6hLAZDZD"
    headers["Content-Type"] = "application/json"
    data = '{ "messaging_product": "whatsapp", "to": "91' + str(number) + '", "type": "template", "template": { "name": "notifier_message", "language": { "code": "en_US" }, "components": [ { "type": "body", "parameters": [ { "type": "text", "text": "' + salesman + '" }, { "type": "text", "text": "' + str(amount) + '" } ] } ] } }'
    resp = requests.post(url, headers=headers, data=data)
    print(resp.status_code)


class InvoiceForm(forms.Form):

    retailer = forms.ModelChoiceField(queryset=Retailer.objects.all(), required=True)
    amount = forms.IntegerField(label="Amount accepted", min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))              #submit button
        
    def getretailer(self):
        return self.retailer

    def getsalesman(self):
        return self.salesman

#---------------------------------------------------------------------------

def index(request):                                                #Page to enter the invoice
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    
    context = {
        'invoiceform' : InvoiceForm(),
        'invoices' : list(Retailer.objects.all()),
        'current' : str(request.user)
    }

    if request.method == 'POST' :
        iform = InvoiceForm(request.POST)
        if iform.is_valid():
            curr_retailer = Retailer.objects.get(name = str(iform.cleaned_data["retailer"]))
            curr_amount = int(iform.cleaned_data["amount"])
            salesman = str(request.user)
            try:
                curr_invoice = Invoice(retailer = curr_retailer, amount= curr_amount, salesman= Salesman.objects.get(name = salesman))
            except:
                return render(request, "notifier/error.html")
            curr_invoice.save()
            whatsapp_send(curr_retailer.number_1, salesman, curr_amount)
            
            return render(request, "notifier/index.html", {**context, **{"current_invoice": curr_invoice}})
        else: 
            return HttpResponse("NONE")

    return render(request, "notifier/index.html", context)          #on load



def invoices_list(request, ):                                        #absoultely no clue...
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    
    context = {}

    if request.method == "POST":
        iform = InvoiceForm(request.POST)
        if iform.is_valid():
            retailer = str(iform.cleaned_data["retailer"])
            amount = iform.cleaned_data["amount"]
            date = str(iform.cleaned_data["date"])
            request.session["invoices_list"] += [(retailer, amount, date)]
            return HttpResponseRedirect(reverse("notifier:invoice"))
        else:
            render(request, "notifier/invoice.html", context)

    return render(request, "notifier/invoice.html", context)
