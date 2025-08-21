'''
Created on Sep. 11, 2020

@author: ankita
'''
from dal import autocomplete
from metadata.models import *


class BiosourceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        print("BiosourceAutocomplete")
        print(self.request.user.is_authenticated)
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Biosource.objects.none()

        qs = Biosource.objects.all()
        print(qs)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)
            print(qs)

        return qs


class BiosampleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Biosample.objects.none()

        qs = Biosample.objects.all()

        source_pk = self.forwarded.get('f4')

        if source_pk:
            qs = qs.filter(biosource=source_pk)

        if self.q:

            qs = qs.filter(name__istartswith=self.q)


        return qs


class ProjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Project.objects.none()

        qs = Project.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
