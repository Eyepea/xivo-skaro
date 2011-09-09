#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, time, os
import psycopg2

log = open('/var/log/fakesvc', 'a+')

# connecting to DB
print >>log, '[fakesvc] starting'
pid = os.fork()
if pid != 0:
	# parent process
	f = open('/var/run/fakesvc.pid', 'w')
	f.write(str(pid))
	f.close()
	sys.exit(0)

print >>log, '[fakesvc] child process', os.getpid()
try:
	conn = psycopg2.connect("host='127.0.0.1' dbname='xivo' user='xivo' password='proformatique'")
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM \"user\"")
	print >>log, cursor.fetchall()
except Exception, e:
	print >>log, e
	sys.exit(1)

print >>log, '[fakesvc] query ok'
while True:
	time.sleep(10)
