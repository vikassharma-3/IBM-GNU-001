from .models import *
import django_filters

class DataFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    filename = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Data
        fields = ['title', 'filename', 'universal','user','description',]