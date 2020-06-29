
######################
REST Response Handling
######################

Response Processors are called upon when data comes back from the server and needs to be modified into
a native style. For example, if the response is  expected to be tabular, it could be framed into a 
pandas dataframe before providing it to the user.
The simplest approach is basically handling of JSON responses that need to be translated into native
python classes, such as lists and dictionaries


***************
Module Response
***************

.. automodule:: qrest.response

.. autoclass:: Response
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: JSONResponse
	:members:
	:private-members:
	:special-members: __init__

.. autoclass:: CSVRestResponse
	:members:
	:private-members:
	:special-members: __init__


