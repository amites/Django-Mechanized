from django.db import models

class ProxyServer(models.Model):
    '''
    Model to hold proxy servers to be used.
    '''
    address = models.CharField(max_length=40)
    port = models.IntegerField(max_length=10)
    proxy_type = models.CharField(max_length=10, default='http')
    active = models.BooleanField(default=True)
    source = models.ForeignKey('ProxySource', null=True)
    anonymous = models.BooleanField(default=False)
    country = models.CharField(max_length=30, null=True)
    last_checked = models.DateTimeField(null=True)
    response_time = models.IntegerField(null=True)
    connection_time = models.IntegerField(null=True)
    errror = models.CharField(max_length=250, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class ProxySource(models.Model):
    '''
    Web-site sources of proxy lists. Often used to clean up database with updated lists.
    '''
    url = models.CharField(max_length=250)
    proxy_type = models.CharField(max_length=10, default='http')
    anonymous = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

