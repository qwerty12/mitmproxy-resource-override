'''
In order to use this script, you need to have a file named overrides.txt exist in
the same dir that you run mitmproxy. An example of this file might look like:

http:\/\/example.com\/js/.* , src/js/file.ext

Usage: mitmproxy -s "mitmResourceOverride.py [file1 [file2 [..]]]"
(this script works best with --anticache)
'''
import optparse
import os
import re
import sys
from urllib.request import URLopener



def getOverrideData():

	overridesText = ""
	with open("overrides.txt") as f:
		overridesText += f.read() + "\n"

	overridesText = overridesText.replace("\r\n", "\n")
	lines = re.split(r"\n+", overridesText)

	urlData = []

	for line in lines:
		if line.find(",") > -1:
			urlData.append(list(map(lambda s: s.strip(), line.split(","))))

	return urlData


def tryToReadFile(filePath, urlData):
	contents = ""
	try:
		fileHandle = URLopener().open(filePath)
		contents = fileHandle.read()
	except IOError:
		contents = "mitmProxy - Resource Override: Could not open " + filePath + \
			" Came from rule: " + urlData[0] + " , " + urlData[1]

	return contents

def request(flow):
	
	overrideData = getOverrideData()

	url = flow.request.pretty_url

	urlMatches = False
	for urlData in overrideData:
		urlMatches = match(urlData[0], url)
		if urlMatches:
			break
	if urlMatches:
		flow.request.method = "HEAD"
		#flow.request.host = "www.google.de"
		#flow.request.path = "/"
		print("Changed to HEAD") #don't download stuff first
		

def response(flow):
	overrideData = getOverrideData()

	url = flow.request.pretty_url

	newResponseContent = ""
	urlMatches = False
	
	for urlData in overrideData:
		urlMatches = match(urlData[0], url)
		if urlMatches:
			filePath = urlData[1]
			newResponseContent = tryToReadFile(filePath, urlData)
			print("Matched " + filePath)
			break
	if urlMatches:
		flow.response.status_code = 200
		flow.response.reason = "OK"
		#flow.response.headers["Location"] = ""
		flow.response.content = newResponseContent
		#print(flow.response)
	
def match(rule, url):
	if re.match(rule, url) != None:
		return True
