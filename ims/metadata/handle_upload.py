'''
Created on Jul 1, 2020

@author: nanda
'''
from metadata.models import *
from django.contrib import messages
from django.db import IntegrityError
import json
import re
from django.db.models import Q
import pandas as pd
import datetime

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None

def get_or_none_multiple(classmodel, **kwargs):
    try:
        return classmodel.objects.filter(**kwargs)
    except classmodel.DoesNotExist:
        return None
    
def handle_uploaded_experiments(request,uploaded_csv):
    c=1
    errorList=[]
    for line in uploaded_csv:
        v=line.decode("utf-8")
        v=v.rstrip()
        values=v.split(",")
        if(c==1):
            headers=values
            indx_biosource=headers.index("biosource")
            indx_oldbiosample=headers.index("biosampleToClone")
            indx_newbiosample=headers.index("new_biosample_name")
            indx_biosample_description=headers.index("biosample_description")
            indx_oldexperiment=headers.index("experimentToClone")
            indx_biono=headers.index("bio_rep_no")
            indx_tecno=headers.index("tec_rep_no")
            indx_newexperiment=headers.index("new_experiment_name")
            indx_date=headers.index("library_preparation_date(yyyy-mm-dd)")
            indx_experiment_description=headers.index("experiment_description")
        else:
            source = get_or_none(Biosource,name=values[indx_biosource])
            sample = get_or_none(Biosample,name=values[indx_oldbiosample])
            exp = get_or_none(Experiment,name=values[indx_oldexperiment])
            
            if(source==None):
                messages.add_message(request, messages.WARNING, 'Biosource does not exist in line '+str(c))
                return
            if(sample==None):
                messages.add_message(request, messages.WARNING, 'Biosample to clone is not given in line '+str(c))
                return
            if(exp==None):
                messages.add_message(request, messages.WARNING, 'Experiment to clone is not given in line '+str(c))
                return
            
            
            if(source):
                if(sample) and (values[indx_newbiosample]):
                    try:
                        new_biosample=sample.make_clone(attrs={'name':values[indx_newbiosample],
                                                               'description': values[indx_biosample_description]
                                                               })
                    except IntegrityError:
                            messages.add_message(request, messages.WARNING, 'Same biosample name exists in the database, should be unique name.')
                            return
                    if(exp):
                        try:
                            new_exp=exp.make_clone(attrs={'name': values[indx_newexperiment],
                                                      'biosample': new_biosample,
                                                      'bio_rep_no': values[indx_biono],
                                                      'tec_rep_no': values[indx_tecno],
                                                      'created_by': request.user,
                                                      'edited_by': request.user,
                                                      'description': values[indx_experiment_description] })
                            json_vals=json.loads(new_exp.json_fields)
                            json_vals["library_preparation_date"]=values[indx_date]
                            new_exp.json_fields=json.dumps(json_vals)
                            new_exp.save()
                            print("New experiment cloned pk: "+str(new_exp.pk))
                            
                        except IntegrityError:
                            messages.add_message(request, messages.WARNING, 'Same experiment name exists in the database, should be unique name.')
                            return
                            
                    else:
                        print("Error in given experiment to clone in line "+ str(c))
                        errorList.append(str(c))
                elif(sample) and (not(values[indx_newbiosample])):
                    if(exp):    
                        try:
                            new_exp=exp.make_clone(attrs={'name': values[indx_newexperiment],
                                                          'bio_rep_no': values[indx_biono],
                                                          'tec_rep_no': values[indx_tecno],
                                                          'created_by': request.user,
                                                          'edited_by': request.user,
                                                          'description': values[indx_experiment_description] })
                            json_vals=json.loads(new_exp.json_fields)
                            json_vals["library_preparation_date"]=values[indx_date]
                            new_exp.json_fields=json.dumps(json_vals)
                            new_exp.save()
                            
                            print("New experiment cloned pk: "+str(new_exp.pk))
                        except IntegrityError:
                            messages.add_message(request, messages.WARNING, 'Same experiment name exists in the database, should be unique name.')
                            return
                    else:
                        print("Error in given experiment to clone in line "+ str(c))
                        errorList.append(str(c))
                else:
                    print("Error in given biosample to clone in line "+ str(c))
                    errorList.append(str(c))
            else:
                print("Error in given biosource to clone in line "+ str(c))
                errorList.append(str(c))
        c+=1
        
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in lines '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All experiments are added successfully')
                    
def handle_uploaded_sequencingfiles(request, prj_pk, uploaded_csv):
    c=1
    errorList=[]
    df = pd.read_csv(uploaded_csv)
    df=df.sort_values(by=['file_path'])
    for index, row in df.iterrows():
        c+=index+1
        exp = get_or_none(Experiment,name=row['experiment_name'])
        run = get_or_none(SequencingRun,name=row['sequencing_run_name'])
        prj = get_or_none(Project,pk=prj_pk)
        if(exp==None):
            messages.add_message(request, messages.WARNING, 'Experiment name does not exist in line '+str(c))
            return
        if(run==None):
            messages.add_message(request, messages.WARNING, 'Sequencing run name does not exist  in line '+str(c))
            return
        if(prj==None):
            messages.add_message(request, messages.WARNING, 'Incorrect project name  in line '+str(c))
            return
        path = row['file_path']
        read_length = row['read_length']
        md5sum = row['md5sum']
        paired = row['paired'].lower()
        related_file=None
        pair=None
        if(path):
                file_name=re.split('.fastq|.fq',path.split("/")[-1])[0]
                file_name_values=file_name.split("_")
                if(md5sum and len(md5sum)==32):
                    try:
                        if(paired in ["yes","y"]):
                            if("R1" in file_name_values) or ("1" in file_name_values):
                                pair="1"
                            else:
                                pairfile=re.split('R2|_2',file_name)
                                query = Q()
                                for i in range(len(pairfile)):
                                    query &= Q(name__contains=pairfile[i])
                                try:
                                    related_file=SeqencingFile.objects.get(query)
                                except:
                                    messages.add_message(request, messages.WARNING, 'Related file query found more than one files in line '+str(c)+". Filename not unique.")
                                    return
                                pair="2"
                        new_f = SeqencingFile(
                            name=file_name, 
                            project = prj,
                            created_by=request.user,
                            edited_by=request.user,
                            file_format=get_or_none(Choice,name='fastq'),
                            cluster_path=path,
                            md5sum=md5sum,
                            run=run,
                            experiment=exp,
                            read_length=read_length,
                            paired_end=pair,
                            related_files=related_file
                            )
                        new_f.save()
                        if(related_file):
                            related_file.related_files=SeqencingFile.objects.get(pk=new_f.pk)
                            related_file.save()
                        
                    except IntegrityError:
                        messages.add_message(request, messages.WARNING, 'Same file name exists in the database, should be unique name in line '+str(c))
                        return
                else:
                    errorList.append(str(c))
                    print("Error in given file md5sum"+ str(c))
                    
        else:
            errorList.append(str(c))
            print("Error in given file path in line "+ str(c))
    
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in lines '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All files are added successfully')


def createJSON(json_type,row):
    json_object = json_type.json_fields
    data = {}
    for keys in json_object:
        formVal = row[keys]
        data[keys] = formVal
    json_data = json.dumps(data)
    return(json_data)
 
def handle_uploaded_biosource(request, uploaded_csv):
    df = pd.read_csv(uploaded_csv)
    c=2
    errorList=[]
    for index, row in df.iterrows():
        if(not(row['biosource_name'] =="#") and not(row['biosource_name']=="")):
            json_type=get_or_none(JsonObj,name=row['biomaterial_type'])
            if(json_type==None):
                messages.add_message(request, messages.WARNING, 'biomaterial_type is incorrect in line '+str(c))
                return
            bio = get_or_none(Biosource,name=row['biosource_name'])
            if(not(bio==None)):
                messages.add_message(request, messages.WARNING, 'biosource name is not unique in line '+str(c))
                return
            elif(bio==None):
                try:
                    new_b = Biosource(
                    name=row['biosource_name'],
                    disease=row['disease'],
                    source_organism=get_or_none(Choice,name=row['source_organism']),
                    description=row['biosource_description'],
                    json_type=json_type,
                    json_fields=createJSON(json_type,row),
                    created_by=request.user,
                    edited_by=request.user
                    )
                    new_b.save()
                except:
                    errorList.append(str(c))
        c+=1
        
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in lines '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All biosource objects are added successfully')
         
def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

     
def handle_uploaded_sequencingruns(request, prj_pk, uploaded_csv):
    df = pd.read_csv(uploaded_csv)
    c=2
    errorList=[]
    
    for index, row in df.iterrows():
        if(not(row['run_name'] =="#") and not(row['run_name']=="")):
            run_name=get_or_none_multiple(SequencingRun,name=row['run_name'])
            if(len(run_name)>0):
                run_in_prj=SequencingRun.objects.filter(name=row['run_name'],project__pk=prj_pk)
                if(not(len(run_in_prj)==0)):
                    messages.add_message(request, messages.WARNING, 'Run name not unique in line '+str(c))
                    return
            prj = get_or_none(Project,pk=prj_pk)
            center = get_or_none(Choice,name=row['sequencing_center'])
            instrument = get_or_none(Choice,name=row['sequencing_instrument'])
            exp = get_or_none(Experiment,name=row['experiment'])
            submission_date = row['submission_date']
            
            if(prj==None):
                messages.add_message(request, messages.WARNING, 'Project does not exist in line '+str(c))
                return
            if(center==None):
                messages.add_message(request, messages.WARNING, 'sequencing_center name does not exist in line '+str(c))
                return
            if(instrument==None):
                messages.add_message(request, messages.WARNING, 'sequencing_instrument name does not exist in line '+str(c))
                return
            if(exp==None):
                messages.add_message(request, messages.WARNING, 'experiment name does not exist in line '+str(c))
                return
            if(submission_date==None) or not(validate(submission_date)):
                messages.add_message(request, messages.WARNING, 'submission_date is incorrect in line'+str(c))
                return
            try:
                if(not(isinstance(row['description'], str))):
                    desc=""
                else:
                    desc=row['description']
                new_r = SequencingRun(
                        name=row['run_name'],
                        project=prj,
                        sequencing_center=center,
                        sequencing_instrument=instrument,
                        submission_date=submission_date,
                        created_by=request.user,
                        edited_by=request.user,
                        description=desc
                        )
                new_r.save()
                new_r.experiment.add(exp)
                new_r.save()
            except:
                errorList.append(str(c))
        c+=1
        
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in line '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All sequecing run objects are added successfully')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
