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
import binascii
import os
from django.shortcuts import render, get_object_or_404, redirect

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

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def checkSanity(obj,request,row,c):
    if(row[obj]==None or str(row[obj])=="nan" or str(row[obj])=="" or str(row[obj])==" "):
        return False
    
    return True

def createJSON(json_type,row):
    json_object = json_type.json_fields
    data = {}
    for keys in json_object:
        formVal = row[keys]
        if (str(formVal)=="nan" or str(formVal)=="NAN"):
            formVal=""
        if((json_object[keys]["data"]=="IntegerField") and (len(str(formVal))>0)):
            formVal=int(formVal)
        data[keys] = formVal
    json_data = json.dumps(data)
    return(json_data)

def removeStar(old_cols):
    newList=[]
    for i in old_cols:
        if("*" in i):
            newList.append(i[:-1])
        else:
            newList.append(i)
    return newList
    
def handle_uploaded_experiments(request,inputdf):
    df = inputdf
    df=df.sort_values(by=['experiment_name'])
    
    c=2
    errorList=[]
    for index, row in df.iterrows():
        if(not(row['experiment_name'] =="#") and checkSanity("experiment_name",request,row,c)):
            source = get_or_none(Biosource,name=row['biosource'])
            sample = get_or_none(Biosample,name=row["biosample_name"])
            exp = get_or_none(Experiment,name=row["experimentToClone"])
            if(row["experiment_label"] and not(str(row["experiment_label"])=="nan")):
                uid = row["experiment_label"]
            else:
                uid = binascii.hexlify(os.urandom(3)).decode()
            
            if(source==None):
                messages.add_message(request, messages.WARNING, 'Biosource is incorrect in line '+str(c))
                return
            if(sample==None):
                messages.add_message(request, messages.WARNING, 'Biosample is incorrect in line '+str(c))
                return
            if(exp==None):
                messages.add_message(request, messages.WARNING, 'Experiment to clone is incorrect in line '+str(c))
                return
            
            
            if(source):
                if(sample):
                    if(exp):
                        try:
                            new_exp=exp.make_clone(attrs={'name': row["experiment_name"],
                                                      'uid':uid,
                                                      'biosample': sample,
                                                      'bio_rep_no': row["bio_rep_no"],
                                                      'tec_rep_no': row["tec_rep_no"],
                                                      'created_by': request.user,
                                                      'edited_by': request.user,
                                                      'description': row["experiment_description"] })
                            json_vals=json.loads(new_exp.json_fields)
                            if(checkSanity("library_preparation_date",request,row,c) and  validate(row['library_preparation_date'])):
                                json_vals["library_preparation_date"]=row["library_preparation_date"]
                            if(new_exp.json_type.name=="ChIP-seq") and checkSanity("antibody",request,row,c):
                                json_vals["antibody"]=row["antibody"]
                                json_vals["antibody_dilution"]=row["antibody_dilution"]
                                json_vals["targeted_factor"]=row["targeted_factor"]
                            new_exp.json_fields=json.dumps(json_vals)
                            new_exp.save()
                            #print("New experiment cloned pk: "+str(new_exp.pk))
                            
                        except IntegrityError:
                            messages.add_message(request, messages.WARNING, 'Same experiment name exists in the database, should be unique name.')
                            return
                            
                    else:
                        print("Error in given experiment to clone in line "+ str(c))
                        errorList.append(str(c))
                elif(sample) and (not(checkSanity("new_biosample_name",request,row,c))):
                    if(exp):    
                        try:
                            new_exp=exp.make_clone(attrs={'name': row["experiment_name"],
                                                          'uid':uid,
                                                          'bio_rep_no': row["bio_rep_no"],
                                                          'tec_rep_no': row["tec_rep_no"],
                                                          'created_by': request.user,
                                                          'edited_by': request.user,
                                                          'description': row["experiment_description"] })
                            json_vals=json.loads(new_exp.json_fields)
                            if(checkSanity("library_preparation_date",request,row,c) and  validate(row['library_preparation_date'])):
                                json_vals["library_preparation_date"]=row["library_preparation_date"]
                            if(new_exp.json_type.name=="ChIP-seq") and checkSanity("antibody",request,row,c):
                                json_vals["antibody"]=row["antibody"]
                                json_vals["antibody_dilution"]=row["antibody_dilution"]
                                json_vals["targeted_factor"]=row["targeted_factor"]
                            new_exp.json_fields=json.dumps(json_vals)
                            new_exp.save()
                            
                            print("New experiment cloned pk: "+str(new_exp.pk))
                        except IntegrityError:
                            messages.add_message(request, messages.WARNING, 'Not unique experiment name in line '+ str(c))
                            return
                    else:
                        messages.add_message(request, messages.WARNING, 'Error in given experiment to clone in line '+ str(c))
                        return
                else:
                    messages.add_message(request, messages.WARNING, 'Error in given biosample to clone in line '+ str(c))
                    return
            else:
                messages.add_message(request, messages.WARNING, 'Error in given biosource to clone in line '+ str(c))
                return
        c+=1
        
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in lines '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All experiments are added successfully')
                    
def handle_uploaded_sequencingfiles(request, prj_pk, inputdf):
    df = inputdf
    df=df.sort_values(by=['file_path'])
    c=2
    errorList=[]
    for index, row in df.iterrows():
        if(not(row['file_path'] =="#") and checkSanity("file_path",request,row,c)):
            exp = get_or_none(Experiment,name=row['experiment_name'])
            run = get_or_none(SequencingRun,name=row['sequencing_run_name'])
            prj = get_or_none(Project,pk=prj_pk)
            assay = get_or_none(Choice,name=row['assay'])
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
            archived_path = row['archived_path']
            read_length = row['read_length']
            if( str(read_length)=="nan"):
                read_length=None
            md5sum = row['md5sum']
            pair= row['paired']
            
            
            if(path):
                    file_name=re.split('.fastq|.fq',path.split("/")[-1])[0]
                    #file_name_values=file_name.split("_")
                    if(checkSanity("md5sum",request,row,c)):
                        if(not(len(md5sum)==32)):
                            messages.add_message(request, messages.WARNING, 'md5sum is incorrect in line '+str(c))
                            return
                    
                    try:
                        similar_name=re.split('_I\d|_R\d',file_name)
                        related_files=SeqencingFile.objects.filter(name__icontains=similar_name[0])
                        new_f = SeqencingFile(
                            name=file_name, 
                            project = prj,
                            created_by=request.user,
                            edited_by=request.user,
                            file_format=get_or_none(Choice,name='fastq'),
                            cluster_path=path,
                            archived_path=archived_path,
                            md5sum=md5sum,
                            run=run,
                            experiment=exp,
                            read_length=read_length,
                            paired_end=pair,
                            assay=assay
                            )
                        new_f.save()
                        
                        if(len(related_files)>0):
                            new_f.related_files.set(related_files)
                            new_f.save()
                            for f in related_files:
                                f.related_files.add(SeqencingFile.objects.get(pk=new_f.pk))
                                f.save()
                        
                    except IntegrityError:
                        messages.add_message(request, messages.WARNING, 'Same file md5sum exists in the database, should be unique md5sum in line '+str(c))
                        return
                    
                        
            else:
                errorList.append(str(c))
                messages.add_message(request, messages.WARNING, 'Error in given file path in line '+str(c))
                
            c+=1
    
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in lines '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All files are added successfully')


 
def handle_uploaded_biosource(request, inputdf):
    df = inputdf
    c=2
    errorList=[]
    for index, row in df.iterrows():
        if(not(row['biosource_name'] =="#") and checkSanity("biosource_name",request,row,c)):
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
         

     
def handle_uploaded_sequencingruns(request,prj_pk,inputdf):
    df = inputdf
    print(df)
    c=2
    errorList=[]
    
    for index, row in df.iterrows():
        if(not(row['run_name'] =="#") and checkSanity("run_name",request,row,c)):
            run_name=get_or_none_multiple(SequencingRun,name=row['run_name'])
            prj = get_or_none(Project,pk=prj_pk)
            center = get_or_none(Choice,name=row['sequencing_center'])
            instrument = get_or_none(Choice,name=row['sequencing_instrument'])
            exp = get_or_none(Experiment,name=row['experiment'])
            submission_date = row['submission_date']
            
            if(prj==None):
                messages.add_message(request, messages.WARNING, 'Project does not exist in line '+str(c))
                return
            if(exp==None):
                messages.add_message(request, messages.WARNING, 'experiment name does not exist in line '+str(c))
                return
            if(submission_date==None) or not(validate(submission_date)):
                messages.add_message(request, messages.WARNING, 'submission_date is incorrect in line'+str(c))
                return
            if(len(run_name)>0):
                try:
                    run_existing=SequencingRun.objects.get(name=row['run_name'],project__pk=prj_pk)
                except ObjectDoesNotExist:
                    run_existing=None
                if(not(run_existing)==None):
                    run_existing.experiment.add(exp)
                    run_existing.save()
                    continue
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
    
    

def handle_uploaded_biosample(request, inputdf):
    df = inputdf
    c=2
    errorList=[]
    for index, row in df.iterrows():
        if(not(row['biosample_name'] =="#") and checkSanity("biosample_name",request,row,c)):
            biosource=get_or_none(Biosource,name=row['biosource_name'])
            if(biosource==None):
                messages.add_message(request, messages.WARNING, 'biosource name is incorrect in line '+str(c))
                return
            
            modification = get_or_none(Modification,name=row['modification'])
            if(checkSanity("modification",request,row,c) and modification==None):
                messages.add_message(request, messages.WARNING, 'modification name is incorrect in line '+str(c))
                return
            
            treatment = get_or_none(Treatment,name=row['treatment'])
            if(checkSanity("treatment",request,row,c) and treatment==None):
                messages.add_message(request, messages.WARNING, 'treatment name is incorrect in line '+str(c))
                return
            
            if(checkSanity("collection_date",request,row,c) and  not(validate(row['collection_date']))):
                messages.add_message(request, messages.WARNING, 'collection_date is incorrect in line '+str(c))
            elif(not(checkSanity("collection_date",request,row,c))):
                coll_date=None
            else:
                coll_date=row['collection_date']
            
            
            json_type = get_or_none(JsonObj,name="preprocessing details - Not Available")
            if(checkSanity("preprocessing_details",request,row,c)):
                json_type = get_or_none(JsonObj,name="preprocessing details - "+row['preprocessing_details'])
            
            if(checkSanity("culture_start_date",request,row,c) and  not(validate(row['culture_start_date']))):
                messages.add_message(request, messages.WARNING, 'culture_start_date is incorrect in line '+str(c))
                return 
            if(checkSanity("culture_harvest_date",request,row,c) and  not(validate(row['culture_harvest_date']))):
                messages.add_message(request, messages.WARNING, 'culture_harvest_date is incorrect in line '+str(c))
                return 
            
                
            sample = get_or_none(Biosample,name=row['biosample_name'])
            if(not(sample==None)):
                messages.add_message(request, messages.WARNING, 'biosample name is not unique in line '+str(c))
                return
            elif(sample==None):
                try:
                    if(row['preprocessing_details']=="Available"):
                        new_s = Biosample(
                        name=row['biosample_name'],
                        biosource=biosource,
                        sample_id=row['sample_id'],
                        modification=modification,
                        treatment=treatment,
                        collection_date=coll_date,
                        collection_method=row['collection_method'],
                        description=row['biosample_description'],
                        json_type=json_type,
                        json_fields=createJSON(json_type,row),
                        created_by=request.user,
                        edited_by=request.user
                        )
                    else:
                        new_s = Biosample(
                        name=row['biosample_name'],
                        biosource=biosource,
                        sample_id=row['sample_id'],
                        modification=modification,
                        treatment=treatment,
                        collection_date=coll_date,
                        collection_method=row['collection_method'],
                        description=row['biosample_description'],
                        json_type=json_type,
                        json_fields=json.dumps({"null": "null"}),
                        created_by=request.user,
                        edited_by=request.user
                        )
                    new_s.save()
                except:
                    errorList.append(str(c))
        c+=1
        
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in lines '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All biosample objects are added successfully')
    
def getdf(request,uploaded_csv):
    df = pd.read_csv(uploaded_csv)
    old_cols=list(df.columns)
    new_cols=removeStar(old_cols)
    df.columns=new_cols
    return(df)


