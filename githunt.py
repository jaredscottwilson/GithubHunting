#! python3

#Python commandline script to search and parse external github for internal keywords

import getopt, sys
import os
import requests
import json
import re
import datetime
import time

fullCmdArguments = sys.argv
argumentList = fullCmdArguments[1:]

unixOptions = "e:p:l:"	
gnuOptions = ["email", "password", "list"]  

try:  
	arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:	 
	print (str(err))
	sys.exit(2)

EMAIL = ""
PASSWORD = ""
LIST = ""

for currentArgument, currentValue in arguments:
	if currentArgument in ("-e", "--email"):
		EMAIL = currentValue
	elif currentArgument in ("-p", "--password"):
		PASSWORD = currentValue	
	elif currentArgument in ("-l", "--list"):
		LIST = currentValue

if not EMAIL:
	print ("This requires an email")
	sys.exit(2)
	
if not PASSWORD:
	print ("This requires an password")
	sys.exit(2)

dirpath = os.getcwd()
my_path = dirpath+"/"+LIST

if not (os.path.exists(my_path) and os.path.getsize(my_path) > 0):
	print ("Your list file does not exist or is not in the working directory.")
	sys.exit(2)

if not LIST:
	print ("This requires an filename of a list of search params")
	sys.exit(2)

try:
	runningtotalpath = dirpath+'/runningtotal.txt'

	if not (os.path.exists(runningtotalpath) and os.path.getsize(runningtotalpath) > 0):
		mode = 'a+'
	else:
		mode = 'r'
	runningfile = open(dirpath+'/runningtotal.txt',mode)
	runningtotal=runningfile.readlines()
	runningfile.close()
	date=datetime.datetime.now()
	filename = str(date.strftime("%Y-%m-%d"))+"_github.txt"
	
	searchfile = open(my_path,'r')
	searchparams = searchfile.readlines()
	searchfile.close()
	searchcount = len(searchparams)
	
	mod = searchcount%4
	kcount = (searchcount-mod)/4
	
	searchterms = []
	for term in searchparams:
		searchterms.append(str(term).rstrip())
		searchterms.append('+OR+')

	searchstring = ""	
	i = 0
	k = 0
	for string in searchterms:
		searchstring = searchstring+'"'+string
		i+=1
		if (i == 8) or (i==(mod+1) and k==kcount):
			searchstring = searchstring[0:-4]
			results={}
			response = requests.get('https://api.github.com/search/code?q='+searchstring, auth=(EMAIL, PASSWORD))
			headers=response.headers
			if not 'link' in headers:
				print("there are no results for this search string, moving to the next")
				i = 0
				searchstring = ""
				k+=1
				continue
			if 'Retry-After' in headers:
				wait = int(headers['Retry-After'])
				print("waiting "+str(wait)+" to retry....")
				time.sleep(wait+5)
			link=headers['link']
			pages=re.findall(r'page\=[0-9]{1,1000}',link)
			end=pages[1]
			totalpages=int(re.findall(r'[0-9]{1,1000}',str(end))[0])
			json_response = response.json()
			j = 1
			while j <= totalpages:
				for i in json_response['items']:
					results[str(i['repository']['full_name'])] = str(i['html_url'])
				j += 1
				while True:
					response = requests.get('https://api.github.com/search/code?q='+searchstring+'&page='+str(j), auth=(EMAIL, PASSWORD))
					json_response = response.json()
					header=response.headers
					if not 'link' in header:
						print("there are no results for this search string, moving to the next")
						i = 0
						searchstring = ""
						k+=1
						break
					if 'Retry-After' in header:
						wait = int(header['Retry-After'])
						print("waiting "+str(wait)+" to retry....")
						time.sleep(wait+5)
					else:
						break
				if j > totalpages:
					output = open(dirpath+'/'+filename,'a+')
					total = open(dirpath+'/runningtotal.txt','a+')
					for r in results:
						s = r+"\t"+results[r]+"\n"
						if s in runningtotal:
							continue
						else:
							print(r+"\t"+results[r],file=output)
							print(r+"\t"+results[r],file=total)
					output.close()
					total.close()
					break
			i = 0
			searchstring = ""
			k+=1
	
except Exception as e: print(e)
