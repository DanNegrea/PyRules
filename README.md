# PyRules v0.1
[@sec3ty](https://twitter.com/sec3ty)

PyRules is a Burp Suite extension that provides a simple way to manipulate requests and responses with Python. The state between multiple requests/responses is saved using persistent variables, this way you can create complex rules in a flexible way.

The extension has three panels:
1. Console screen: to display short messages and the logged data.

2. Variable screen: Here the persistent variables are initialized (optional).

3. Rules screen: the place were the Python script is defined.

Once the setup is complete, you only need to enable the extension and it will do it's job.

# Installation

For Manual installation, download PyRules.py and PyUtil.py from this repository. From within Burp Suite, select Extender, click Add button, change the Extension type to Python and select PyRules.py.

## Requirements for usage
Jython version 2.7.0 or greater needs to be imported. More infos here:
https://portswigger.net/burp/help/extender.html#options_pythonenv

# Usage

## Variables screen (bottom-left)

Initial values for persistant variables go here.

* Every edit of the code in intialization screen (actually focus lost) triggers the execution of the code listed here.
* The state will be maintained when disabling / enabling the extension through the `PyRules` checkbox

## Rules screen (right)

Python script goes here. This code will be executed with each request and response.

Available variables are:
* `extender` 
* `callbacks` 
* `helpers` 
* `toolFlag` 
* `messageIsRequest` 
* `messageInfo` 
* `log` 
To understand how to use them see the provided examples and the api [docs](https://portswigger.net/burp/extender/api).

**Notice** The code from the simple example should be used for quick tasks. In advanced example the called functions make sure that the content type of the request gets updated. 

## Tipps

1. `log(<variable>)` can be used to inspect variables. Strings are displayed directly, pprint is used for other objects.

2. Expressions that need to be computed only once should be moved in the variables screen.
Example: The reqular expressions from simple and advanced examples can be compiled only once:

```
import re
search_request = re.compile("CSRFtoken=([a-zA-Z0-9]*)")
search_response = re.compile("name=\"CSRFtoken\" value=\"([a-zA-Z0-9]*)\">")
token = ""
```

3. To test if the request/response originates from a certain tool use
`if toolFlag == callbacks.<tool>`, where `<tool>`can be:
- `TOOL_PROXY`
- `TOOL_REPEATER`
- `TOOL_INTRUDER`
- `TOOL_SCANNER`
- or other value defined [here](https://portswigger.net/burp/extender/api/burp/IBurpExtenderCallbacks.html)

Questions or suggestions?
[@sec3ty](https://twitter.com/sec3ty)

## Inspired by
[mwielgoszewski/burpscript.py](https://gist.github.com/mwielgoszewski/7026954)
