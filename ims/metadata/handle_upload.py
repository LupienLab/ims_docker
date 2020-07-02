'''
Created on Jul 1, 2020

@author: nanda
'''
def handle_uploaded_experiments(uploaded_csv):
    for chunk in uploaded_csv.chunks():
        print(chunk)