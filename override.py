'''
In order to use this script, you need to have a file named overrides.txt exist in
the same dir that you run mitmproxy. An example of this file might look like:

http:\/\/example.com\/js/.* , src/js/file.ext

Usage: mitmproxy -s "mitmResourceOverride.py [file1 [file2 [..]]]"
(this script works best with --anticache)
'''
import re

def getOverrideData():

	overridesText = ""
	with open("overrides.txt", mode="r", encoding="utf-8") as f:
		overridesText += f.read() + "\n"

	overridesText = overridesText.replace("\r\n", "\n")
	lines = re.split(r"\n+", overridesText)

	urlData = []

	for line in lines:
		if line.find(",") > -1:
			x = list(map(lambda s: s.strip(), line.split(",")))
			x[0] = re.compile(x[0].strip())
			urlData.append(x)

	return urlData

overrideData = getOverrideData()

def tryToReadFile(filePath, urlData):
	contents = ""
	try:
		with open(filePath, mode="rb") as fileHandle:
			contents = fileHandle.read()
	except IOError:
		contents = "mitmProxy - Resource Override: Could not open " + filePath + \
			" Came from rule: " + urlData[0] + " , " + urlData[1]

	return contents

def request(flow):
	global overrideData
	url = flow.request.pretty_url

	for urlData in overrideData:
		if urlData[0].match(url) is not None:
			flow.request.method = "HEAD"
			#flow.request.host = "www.google.de"
			#flow.request.path = "/"
			#print("Changed to HEAD") #don't download stuff first
			return


def response(flow):
	global overrideData

	url = flow.request.pretty_url

	newResponseContent = ""
	
	for urlData in overrideData:
		if urlData[0].match(url) != None:
			filePath = urlData[1]
			newResponseContent = tryToReadFile(filePath, urlData)
			#print("Matched " + filePath)
			flow.response.status_code = 200
			flow.response.reason = "OK"
			#flow.response.headers["Location"] = ""
			flow.response.content = newResponseContent
			#print(flow.response)
			return

