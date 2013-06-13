# -*- coding: utf-8 -*-
from django.db import models
import datetime

# Create your models here.

class Show(models.Model):
	name=models.CharField(max_length=30)
	location=models.CharField(max_length=30, default='Theatre')
	
	# def all_ticket_types(self):
	# 	ticket_types=[]
	# 	for o in self.occurrence_set.all():
	# 		for t in o.tickets_available.all():
	# 			if not t in ticket_types:
	# 				ticket_types.append(t)
	# 	return ticket_types

	def is_current(self):
		today=datetime.date.today()
		occs=Occurrence.objects.filter(show=self).filter(date__gt=today)

		if len(occs)==0:
			return False
		else:
			return True

	def __unicode__(self):
		return self.name;

class OccurrenceManager(models.Manager):
	def get_avaliable(self,show):
		today=datetime.date.today()
		occs=Occurrence.objects.filter(show=show).filter(date__gt=today).all()
		ret=[]
		for oc in occs:
			if oc.sold_out():
				pass
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
