import const
import glob
import inspect
import sys
import hashlib
import subprocess
import string
import os
import fcntl
import struct
import shutil
import util

from logger import *
from subprocess import check_output
from shutil import *
from util import getUtcTime

def readSemaphoreFiles(flog):
	li = []
	for name in glob.glob(const.DIR_FILESEMAPHORE+'*.p1mon'):
		if checkSemaphoreFile(name,flog):
			_head,tail = os.path.split(name)  
			li.append(tail)
			os.remove(name)
		else:
			os.remove(name)
			flog.critical(inspect.stack()[0][3]+" controle gefaald.")
	if len(li) > 0:    
		flog.debug(inspect.stack()[0][3]+" gevonden semafoor files: "+str(li))
	return li

def checkSemaphoreFile(name,flog):
	#print "###"+name
	try:
		fo = open(name, "r")
		l1=fo.readline().encode('utf-8').strip()
		l2=fo.readline().encode('utf-8').strip()
		l3=fo.readline().encode('utf-8').strip().decode('utf-8')
		fo.close()
		#print ( l1 )
		#print ( l2 )
		#print ( l3 )
		#print ( hashlib.sha1(l1+l2).hexdigest() )

		if hashlib.sha1(l1+l2).hexdigest() == l3:
			flog.debug(inspect.stack()[0][3]+" Hash match: "+l3.strip())
			return True #hash ok
	except Exception as e:
		flog.error(inspect.stack()[0][3]+": check semafoor file error ->"+str(e))
	return False

# .p1mon is added to the file name.
def writeSemaphoreFile(name, flog):
	try:
		filename = name+'.p1mon'
		if os.path.isfile(const.DIR_FILESEMAPHORE+filename):
			flog.warning(inspect.stack()[0][3]+": semafoor file "+filename+" bestaat al, gestopt.")
			return False # semaphore file already exist.
		time 	  = str(getUtcTime()).encode('utf-8')
		filename  = str(filename).encode('utf-8')
		hashvalue = hashlib.sha1( filename + time ).hexdigest()

		#print ( time )
		#print ( filename )
		#print (hashvalue)

		fo = open(const.DIR_FILESEMAPHORE+filename.decode('utf-8'), "w")
		fo.write( filename.decode('utf-8') + '\n' )
		fo.write( time.decode('utf-8')     + '\n' )
		fo.write( hashvalue + '\n' )
		fo.close()

		flog.info(inspect.stack()[0][3]+" semafoor file " + const.DIR_FILESEMAPHORE + filename.decode('utf-8') + " gemaakt." )
		 
		return True
	except Exception as e:
		flog.error(inspect.stack()[0][3]+": semafoor file error ->"+str(e))
	return False
	

def testSemaphore(flog):
	if writeSemaphoreFile('p1montest',flog): 
		print ("writeSemaphoreFile('p1montest',flog) gelukt")
	else:
		print ("writeSemaphoreFile('p1montest',flog) gefaald")
	readSemaphoreFiles(flog)	
		
	
