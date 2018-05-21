'''
In order to use this script, you need to have a file named overrides.txt exist in
the same dir that you run mitmproxy. An example of this file might look like:

http://example.com/js/* , src/js/*
*example.com/static/** , static/**

View the README to see how override rules work.

Usage: mitmproxy -s "mitmResourceOverride.py [file1 [file2 [..]]]"
(this script works best with --anticache)
'''
import optparse
import os
import re
import sys
from urllib.request import URLopener

#from libmproxy.protocol.http import decoded


def getOverrideData():
    # find arg begin with mitmResourceOverride.py
    args = []

    # TODO: find a better way to handle filename
    #       p.s. __file__ is not working if passed to mitmproxy
    for arg in sys.argv:
        if re.findall("mitmResourceOverride.py ", arg):
            args = re.split(r"(?<!\\) ", arg)[1:]
            break

    # Duplicated, read overrides.txt from current directory
    if os.path.exists("overrides.txt"):
        args.append("overrides.txt")

    overridesText = ""
    for fn in args:
        with open(fn) as f:
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
    newResponseContent = ""
    
    urlMatches = False
    for urlData in overrideData:
        urlMatches, freeVars = match(urlData[0], url)
        break;
    if urlMatches:
        flow.request.method = "HEAD" #don't download stuff first
        
def response(flow):
    overrideData = getOverrideData()

    #with decoded(flow.response):  # automatically decode gzipped responses.
    url = flow.request.pretty_url

    newResponseContent = ""
    urlMatches = False
    for urlData in overrideData:
        urlMatches, freeVars = match(urlData[0], url)

        if urlMatches:
            filePath = matchReplace(urlData[0], urlData[1], url)
            newResponseContent = tryToReadFile(filePath, urlData)
            print("Matched " + filePath)
            break
    if urlMatches:
        flow.response.content = newResponseContent


### URL Matching stuff below ###


def tokenize(myStr):
    ans = re.split(r'(\*+)', myStr)

    if ans[0] == "":
        ans.pop(0)

    if ans[-1] == "":
        ans.pop()

    return ans


def match(pattern, myStr):
    patternTokens = tokenize(pattern)
    freeVars = {}
    varGroup = 0
    strParts = myStr
    matchAnything = False
    completeMatch = True
    matches = None
    possibleFreeVar = ""

    for token in patternTokens:
        if token[0] == "*":
            matchAnything = True
            varGroup = len(token)
            if not varGroup in freeVars:
                freeVars[varGroup] = []
        else:
            matches = strParts.split(token)
            if len(matches) > 1:
                # The token was found in the string.
                possibleFreeVar = matches.pop(0)
                if possibleFreeVar != "":
                    # Found a possible candidate for the *.
                    if not matchAnything:
                        # But if we haven't seen a * for this freeVar,
                        # the string doesnt match the pattern.
                        completeMatch = False
                        break
                    freeVars[varGroup].append(possibleFreeVar)
                matchAnything = False
                # We matched up part of the pattern to the string
                # prepare to look at the next part of the string.
                strParts = token.join(matches)
            else:
                # The token wasn't found in the string. Pattern doesn't match.
                completeMatch = False
                break

    if strParts != "":
        if not matchAnything:
            # There is still some string part that didn't match up to the pattern.
            completeMatch = False
        else:
            # If we still need to match a string part up to a star,
            # match the rest of the string.
            freeVars[varGroup].append(strParts)

    return (completeMatch, freeVars)


def replaceAfter(myStr, idx, match, replace):
    return myStr[:idx] + myStr[idx:].replace(match, replace, 1)


def safeShift(arr):
    ans = None
    try:
        ans = arr.pop(0)
    except IndexError:
        ans = None
    return ans


def matchReplace(pattern, replacePattern, myStr):
    matched, freeVars = match(pattern, myStr)

    if not matched:
        # If the pattern didn't match.
        return myStr

    # Plug in the freevars in place of the stars.
    starGroups = re.findall(r"\*+", replacePattern)
    currentStarGroupIdx = 0
    freeVar = ""
    starGroupLen = 0
    freeVarGroup = None
    for starGroup in starGroups:
        starGroupLen = len(starGroup)
        if starGroupLen in freeVars:
            freeVarGroup = freeVars[starGroupLen]
        else:
            freeVarGroup = []
        freeVar = safeShift(freeVarGroup) or starGroup
        replacePattern = replaceAfter(replacePattern, currentStarGroupIdx,
                                      starGroup, freeVar)
        currentStarGroupIdx = replacePattern.find(freeVar) + len(freeVar)

    return replacePattern
