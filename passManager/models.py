from django.contrib.auth.models import User
from django.db import models
from passManager.functions import passEncr
import time
import pytz
import datetime
from django.utils.translation import ugettext_lazy as _

class ITService(models.Model):
    class Meta:
        verbose_name = 'IT Service'

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=500,unique=True)
    notes = models.TextField(null=True, blank=True, default = "")

class ITConfigurationItem(models.Model):
    class Meta:
        verbose_name = 'IT Configuration Item'

    def __unicode__(self):
        try:
            service_str = self.service.__unicode__()
        except Exception:
            service_str = "no Service"

        return self.service.__unicode__() + "::" + self.name

    name = models.CharField(max_length=100)
    notes = models.TextField(null=True, blank=True, default = "")
    service = models.ForeignKey(ITService)

class PasswordType(models.Model):
    class Meta:
        verbose_name = 'Type of credential'

    def __unicode__(self):
        try:
            return self.name
        except Exception:
            return super(PasswordType, self).__unicode__(*args, **kwargs)

    name = models.CharField(max_length=100,unique=True)
    notes = models.TextField(null=True, blank=True, default = "")

class passDb(models.Model):
    class Meta:
        verbose_name = 'Password'

    deprecated = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    account = models.CharField(max_length=100)
    name = models.CharField(max_length=500)
    version = models.IntegerField(default=1)
    password_type = models.ForeignKey(PasswordType)
    ci = models.ForeignKey(ITConfigurationItem)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    server = models.CharField(max_length=60,null=True, blank=True, default= "")
    service_name = models.CharField(max_length=500)
    uploader = models.ForeignKey(User)
    notes = models.TextField(null=True, blank=True, default = "")
    creation_date = models.DateTimeField(editable=False)
    modification_date = models.DateTimeField(auto_now=True, null=True,
            blank=True)
    # valid_since_date = models.DateTimeField(null=True, blank=True, default = None)
    valid_until_date = models.DateTimeField(null=True, blank=True, default = None)

    def __unicode__(self):
        try:
            ci_str = self.ci.__unicode__()
        except Exception:
            ci_str = "no CI"
        return ci_str + \
                "::" + self.account + "::" + str(self.version)

    def getClickMe(self):
        password = passEncr('decrypt', self.password)
        idrow = self.id
        return '<font color="red"><span id=\"%s\" onClick=\"cambiar(\'%s\',\'%s\');\">ClickME</span></font>' % (idrow, idrow, password)
    getClickMe.allow_tags = True
    getClickMe.short_description = "Password"
    
    def _get_password(self):
        if len(self.password) != 0:
            password = passEncr('decrypt', self.password)
        else:
            password = ""
        return password

    def save(self, *args, **kwargs):

        self.name = self.__unicode__()

        self.service_name = self.ci.service.__unicode__()

        v = self.version
        while True:
            passwd_list = passDb.objects.filter(ci=self.ci, account=self.account,
                version=v)
            if not self.id:
                if len(passwd_list) > 0:
                    v = v + 1
                else:
                     break
            else:
                if len(passwd_list) > 1:
                    v = v + 1
                else:
                     break
        self.version = v

        d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
        if not self.creation_date:
            self.creation_date = d
        if self.valid_until_date and self.valid_until_date < d:
            self.deprecated = True
        else:
            self.deprecated = False

        self.active = not self.deprecated

        super(passDb, self).save(*args, **kwargs)

