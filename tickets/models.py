# -*- coding: utf-8 -*-
from django.db import models
import datetime

from PIL import Image
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class Category(models.Model):
    name=models.CharField(max_length=50)
    def __unicode__(self): return self.name

class Show(models.Model):
    name=models.CharField(max_length=30)
    location=models.CharField(max_length=30, default='Theatre')
    description = models.TextField()
    long_description = models.TextField(blank=True)
    poster=models.ImageField(upload_to='posters', blank=True, null=True)
    poster_wall=models.ImageField(upload_to='posters', blank=True, null=True)
    poster_page=models.ImageField(upload_to='posters', blank=True, null=True)
    poster_tiny=models.ImageField(upload_to='posters', blank=True, null=True)


    category=models.ForeignKey('Category')

    IMAGE_SIZES = {'poster_wall'    : (126, 178),
                   'poster_page'    : (256, 362),       
                   'poster_tiny'    : (50, 71) }
    
    def is_current(self):
        today=datetime.date.today()
        occs=Occurrence.objects.filter(show=self).filter(date__gt=today)

        if len(occs)==0:
            return False
        else:
            return True

    def gen_thumbs(self):
        img = Image.open(self.poster.path)
        #Convert to RGB
        if img.mode not in ('L', 'RGB'):
            img = img.convert('RGB')
        for field_name, size in self.IMAGE_SIZES.iteritems():
            field = getattr(self, field_name)
            working = img.copy()
            working.thumbnail(size, Image.ANTIALIAS)
            fp = StringIO()
            working.save(fp, "JPEG", quality=95)
            cf = InMemoryUploadedFile(fp, None, self.poster.name, 'image/jpeg',
                                  fp.len, None)
            field.save(name=self.poster.name, content=cf, save=False);
    
    def __unicode__(self):
        return self.name;

class OccurrenceManager(models.Manager):
    def get_avaliable(self,show):
        today=datetime.date.today()
        occs=Occurrence.objects.filter(show=show).filter(date__gt=today).all()
        ret=[]
        for oc in occs:
            if oc.sold_out(): pass
            else:
                ret.append((oc.id,oc.datetime_formatted()))
        print ret
        return ret

class Occurrence(models.Model):
    show=models.ForeignKey(Show)
    date=models.DateField()
    time=models.TimeField()
    maximum_sell=models.PositiveIntegerField()
    hours_til_close=models.IntegerField(default=3)

    objects=OccurrenceManager()

    def day_formatted(self):
        return self.date.strftime('%A')
    def time_formatted(self):
        return self.time.strftime('%-I%p').lower()
    def datetime_formatted(self):
        return self.date.strftime('%A %d %B ')+self.time.strftime('%-I%p').lower()

    def tickets_sold(self):
        tickets=Ticket.objects.filter(occurrence=self).filter(cancelled=False)
        sold=0
        for ticket in tickets:
            sold+=ticket.quantity
        return sold
    def sold_out(self):
        if self.tickets_sold()>=self.maximum_sell:
            return True
        else: return False

    def __unicode__(self):
        return self.show.name+" on "+str(self.date)+" at "+str(self.time)

class Ticket(models.Model): 
    occurrence=models.ForeignKey(Occurrence)
    stamp=models.DateTimeField(auto_now=True)
    person_name=models.CharField(max_length=80)
    email_address=models.EmailField(max_length=80)
    quantity=models.IntegerField(default=1)
    cancelled=models.BooleanField(default=False)


    def __unicode__(self):
        return self.occurrence.show.name+" on "+str(self.occurrence.date)+" at "+str(self.occurrence.time)+" for "+self.person_name

