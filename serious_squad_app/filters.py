from .models import *
import django_filters

class DataFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    filename = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    uploaded_at = django_filters.DateFilter(lookup_expr='gt')
    uploaded_at_1 = django_filters.DateFilter(lookup_expr='lt')

    class Meta:
        model = Data
        fields = ['title', 'filename', 'universal','user','description','uploaded_at','uploaded_at_1']

class UserActivityFilter(django_filters.FilterSet):
    activity = django_filters.CharFilter(lookup_expr='icontains')
    time = django_filters.DateFilter(lookup_expr='gt')
    time_1 = django_filters.DateFilter(lookup_expr='lt')

    class Meta:
        model = UserActivity
        fields = ['activity','time','time_1']