#!/usr/bin/env python
# Based on Andrea (theMiddle) Menin's work
# Twitter: https://twitter.com/Menin_TheMiddle

import sys
import json
import time
from datetime import date
from elasticsearch import Elasticsearch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

if len(sys.argv) != 3:
    print("Usage: ./logger.py <elastic_server> <logfile>")
    sys.exit(1)
server, basedir = sys.argv[1:]
es = Elasticsearch([server])
print("Server: %s - Path: %s" % (server, basedir))

def parseLogFile(file):
	# define the index mapping
	settings = {
		"settings": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		},
		"mappings": {
			"coraza": {
				"properties": {
				}
			}
		}
	}

	# set all dict keys to lower
	d = json.load(open(file))

	# create 1 index per day... you could change it
	# if you need to store all logs in a single index:
	index = 'coraza_' + str(date.today()).replace('-', '')

	# we have to remap the fields
	d = d["transaction"]
	tx = {
		"id": d["id"],
		"unix_timestamp": d["unix_timestamp"],
		"timestamp": d["timestamp"],
		"client_ip": d["client_ip"],
		"client_port": d["client_port"],
		"host_ip": d["host_ip"],
		"host_port": d["host_port"],
		"server_id": d["server_id"],
		"request.method": d["request"]["method"],
		"request.uri": d["request"]["uri"],
		"request.protocol": d["request"]["protocol"],
		"request.http_version": d["request"]["http_version"],
		"request.headers": dict([k.lower(), ", ".join(vs)] for k, vs in d["request"]["headers"].items()),
		"request.body": d["request"]["body"],
		"request.files": None,
		"response.http_version": d["response"]["protocol"],
		"response.status": d["response"]["status"],
		"response.headers": dict([k.lower(), ", ".join(vs)] for k, vs in d["response"]["headers"].items()),
		"response.body": d["response"]["body"],
		"producer.connector": "%s/%s" % (d["producer"]["connector"], d["producer"]["version"]),
		"producer.server": d["producer"]["server"],
		"producer.rule_engine": d["producer"]["rule_engine"],
		"stopwatch": d["producer"]["stopwatch"],
		"rulesets": ", ".join(d["producer"]["rulesets"]),
		"messages": [m["message"] for m in d["messages"] if m["message"] != ""] if "messages" in d else []
	}

	# if index exists noop, else create it with mapping
	if not es.indices.exists(index=index):
		es.indices.create(index=index, ignore=400, body=settings)
	# write the log
	res = es.index(index=index, id=d['id'], document=tx)

	# check if log has been created
	print(res)
	if res['result'] == 'created':
		print("Parsed "+str(file))
	else:
		print("Warning: log not created:")
		print(res)


class handler(FileSystemEventHandler):
	def on_any_event(self, event):
		if not event.is_directory and event.event_type == 'created':
			print("Got %s" % event.src_path)
			parseLogFile(event.src_path)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(handler(), basedir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
