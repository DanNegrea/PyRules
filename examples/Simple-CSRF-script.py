## Simple example for tracking a "CSRFtoken" token that demonstrates:
#  * how to disable the plug in for a certain tool
#  * how to handle a request / response
#  * how log information
# Notice: the request must have the same length as prior the replace. Another advanced example demonstrates how get the "Content-Length" updated.

#Python rules go here
import re

if toolFlag == callbacks.TOOL_PROXY:
	exit()

if messageIsRequest:
	# Refresh the request: search if the request contains a token and replace it with the new/stored value
	log("\n Request - processing")
	request = helpers.bytesToString( messageInfo.getRequest() )
	
	search  = re.compile("CSRFtoken=([a-zA-Z0-9]*)")
	replace = "CSRFtoken="+token
	
	log("Updating parameter:")
	log(replace)
	
	request = re.sub( search, replace, request )

	messageInfo.setRequest( helpers.stringToBytes(request) )
else:
	#Capture the new token: if the response contains a new value, capture it and stored it in a persistent variable
	log("\n Response - processing")
	response = helpers.bytesToString( messageInfo.getResponse() )
	
	search = re.compile("name=\"CSRFtoken\" value=\"([a-zA-Z0-9]*)\">")
	match = search.findall(response)

	if match:
		token = match[0]
		log("New token:")
		log(token)
	else:
		log("No token found!")
		