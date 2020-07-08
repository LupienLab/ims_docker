'''
Created on Jul 1, 2020

@author: nanda
'''
from metadata.models import *
from django.contrib import messages
from django.db import IntegrityError
import json
import re
import pandas as pd

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None

    
def handle_uploaded_experiments(request,uploaded_csv):
    c=0
    errorList=[]
    for line in uploaded_csv:
        v=line.decode("utf-8")
        v=v.rstrip()
        values=v.split(",")
        if(c==0):
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
            c+=1
        else:
            source = get_or_none(Biosource,name=values[indx_biosource])
            sample = get_or_none(Biosample,name=values[indx_oldbiosample])
            exp = get_or_none(Experiment,name=values[indx_oldexperiment])
            
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
    c=0
    errorList=[]
    df = pd.read_csv(uploaded_csv)
    df=df.sort_values(by=['file_path'])
    
    for line in uploaded_csv:
        v=line.decode("utf-8")
        v=v.rstrip()
        values=v.split(",")
        if(c==0):
            headers=values
            indx_experiment_name=headers.index("experiment_name")
            indx_sequencing_run_name=headers.index("sequencing_run_name")
            indx_file_path=headers.index("file_path")
            indx_md5sum=headers.index("md5sum")
            indx_read=headers.index("read_length")
            c+=1
        else:
            exp = get_or_none(Experiment,name=values[indx_experiment_name])
            run = get_or_none(SequencingRun,name=values[indx_sequencing_run_name])
            prj = get_or_none(Project,pk=prj_pk)
            if(values[indx_file_path]):
                file_name=re.split('.fastq|.fq',values[indx_file_path].split("/")[-1])
                
                if(values[indx_md5sum] and len(values[indx_md5sum]==32)):
                    new_f = SeqencingFile(
                        name=file_name, 
                        project = prj,
                        created_by=request.user,
                        edited_by=request.user,
                        file_format=get_or_none(Choice,name='fastq'),
                        cluster_path=values[indx_file_path],
                        md5sum=values[indx_md5sum],
                        run=run,
                        experiment=exp,
                        read_length=values[indx_read]
                        )
                else:
                    errorList.append(str(c))
                    print("Error in given file md5sum"+ str(c))
                    
            else:
                errorList.append(str(c))
                print("Error in given file path in line "+ str(c))
        c+=1       
            
                
            
            
            
    if len(errorList)>0:
        messages.add_message(request, messages.WARNING, 'Error in lines '+",".join(set(errorList)))
    else:
        messages.add_message(request, messages.SUCCESS, 'All files are added successfully')   
            
            
            
            
            
            
            
