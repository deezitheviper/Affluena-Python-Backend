import uuid
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail,EmailMultiAlternatives
from uuid import uuid4
from django.core.files import File
from django.conf import settings

def generate_ref_code():
    code = str(uuid.uuid4()).replace("-","")[:12]
    return code 

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result,encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None




def sendEmailUtil(instance,user,inv):
    
    subject, from_email  = 'New Contribution Receipt and Agreement', settings.DEFAULT_FROM_EMAIL
    text_content = 'Your Contribution of {}, has been approved.'.format(instance.amount)
    html_content = '<p>Your Contribution of <strong>{}</strong>, has been approved.</p>'.format(instance.amount)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.attach('invoice.pdf', inv,"application/pdf")
    msg.send()

def create_simple_pdf(instance):
        user = instance.user
        txid = instance.txid
        invoice = { 
            'date': instance.date_requested.strftime('%Y-%m-%d'),
            "no":txid, 
            'amount': "{:,.2f}". format(instance.amount),
            'contribution': "Simple Interest",
            "account_name" : user.account_name,
            "email":user.email
           
        } 
       
        invoice_context = {"instance": invoice}
        inv = render_to_pdf('pdf/invoices.html', invoice_context)
        instance.ticket.save("Receipt.pdf", File(BytesIO(inv.content)),False)
        filename = "Agreement.pdf" 
        instance.pdf.save(filename, File(BytesIO(pdf.content)),False)
        pd = instance.pdf.read() 
        inv = instance.ticket.read()
        #sendEmailUtil(instance,user,inv,pd)

def create_compound_pdf(instance):
        user = instance.user
        txid = instance.txid
        invoice = {
            'date': instance.date_requested.strftime('%Y-%m-%d'),
            "no":txid,
            'amount': "{:,.2f}". format(instance.amount),
            'contribution': "Compound Interest",
            "account_name" : user.account_name,
            "email":user.email
           
        }
       
        invoice_context = {"instance": invoice} 
        inv = render_to_pdf('pdf/invoices.html', invoice_context)
        instance.ticket.save("Receipt.pdf", File(BytesIO(inv.content)),False)
        inv = instance.ticket.read()
        sendEmailUtil(instance,user,inv)
   
    