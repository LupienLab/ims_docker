'''
Created on Dec. 8, 2020

@author: ankita
'''
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect, JsonResponse
from metadata.models import *
from metadata.forms import *
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Color, Fill
from openpyxl.utils.cell import get_column_letter
from datetime import datetime
from datetime import date
from metadata.excelRow import insert_rows

now = datetime.now()
today = date.today()

ROOTFOLDER="/Users/ankita/Documents/eclipse-workspace/imsDB/ims_docker/ims"
#ROOTFOLDER="/Users/ankita/Documents/eclipse-workspace/imsDB/ims_docker/ims/"



def handle_exportSequencingform(request,prj_pk):
    experimentList=request.POST.getlist('choose_experiments')
    buffer=request.POST.get('buffer')
    instructions=request.POST.get('instructions')
    data_recipient_contact_name=request.POST.get('data_recipient_contact_name')
    data_recipient_contact_email=request.POST.get('data_recipient_contact_email')
    grant=request.POST.get('grant')
    bp_length=request.POST.get('bp_length')
    low_diversity_sample=request.POST.get('low_diversity_sample')
    sequencing_type=request.POST.get('sequencing_type')
    multiplexing_sequencing=request.POST.get('multiplexing_sequencing')
    
    
    
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    dt_today = today.strftime("%Y-%m-%d")
    project_id=prj_pk
    prj = Project.objects.get(pk=project_id)
      
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = "attachment; filename=Epigenetics_Initiative_Sample_Submission_Form_"+dt_string+".xlsx"
    file_path_new = 'static/Epigenetics_Initiative_Sample_Submission_Form_v3.1.xlsx'
 
    wb = load_workbook(file_path_new)
    ws = wb.worksheets[0]
    ws.insert_rows = insert_rows
    
    contributor1 = prj.created_by
    contributor2 = prj.contributor.all().order_by('first_name')
    
    membersList = []
    membersList.append(contributor1.get_full_name())
    for values in contributor2:
        membersList.append(values.get_full_name())
    m=list(set(membersList))
    
    emailList=[]
    emailList.append(contributor1.email)
    for values in contributor2:
        emailList.append(values.email)
    e=list(set(emailList))
    
    
    ws.cell(row=5, column=5).value = dt_today
    ws.cell(row=7, column=2).value = " / ".join(m)
    ws.cell(row=8, column=2).value = " / ".join(e)
    ws.cell(row=9, column=2).value = data_recipient_contact_name
    ws.cell(row=10, column=2).value = data_recipient_contact_email
    ws.cell(row=14, column=2).value = grant
    
    sampleRowNo=18
    count=0
    for ep in experimentList:
        #insert_rows(ws, sampleRowNo, 1, above=True, copy_style=True)
        insert_rows(ws, row_idx= sampleRowNo, cnt = 1, above=False, copy_style=True)
        exp=Experiment.objects.get(pk=int(ep))
        #ws.insert_rows(sampleRowNo, amount=1,)
        ws.cell(row=sampleRowNo, column=1).value = exp.uid
        ws.cell(row=sampleRowNo, column=2).value = exp.name
        ws.cell(row=sampleRowNo, column=3).value = exp.json_type.name
        
        ws.cell(row=sampleRowNo, column=4).value = exp.biosample.biosource.source_organism.name
        
        if(exp.biosample.sample_type):
            ws.cell(row=sampleRowNo, column=5).value = exp.biosample.sample_type.name
            
        if(exp.biosample_quantity_units):
            ws.cell(row=sampleRowNo, column=6).value = str(exp.biosample_quantity)+" "+str(exp.biosample_quantity_units.name)
        elif(exp.biosample_quantity):
            ws.cell(row=sampleRowNo, column=6).value = str(exp.biosample_quantity)
        else:
            ws.cell(row=sampleRowNo, column=6).value = "value not filled in db"
        
        ws.cell(row=sampleRowNo, column=12).value = buffer

        
        sampleRowNo += 1
        count += 1
    
    ws.cell(row=23+count, column=2).value = bp_length
    ws.cell(row=24+count, column=2).value = low_diversity_sample
    ws.cell(row=25+count, column=2).value = sequencing_type
    ws.cell(row=26+count, column=2).value = multiplexing_sequencing
    ws.cell(row=28+count, column=1).value = instructions
    
    
    wb.save(response)    
    return response



def exportSequencingform(request,prj_pk):
    if request.method == 'POST':
        form = SequencingForm(request.POST,initial={'prj_pk':prj_pk})
        if form.is_valid():
            res= handle_exportSequencingform(request,prj_pk)
            return res

    else:
        form = SequencingForm(initial={'prj_pk':prj_pk})
     
    pageContext = {
        'form': form,
        'form_name':'Export genomic core sequencing form'
        }
    return render(request, 'export.html', pageContext)
