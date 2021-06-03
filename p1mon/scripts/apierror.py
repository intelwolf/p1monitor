"""
200 (OK) must not be used to communicate errors in the response body
Always make proper use of the HTTP response status codes as specified by the rules in this section. In particular, a REST API must not be compromised in an effort to accommodate less sophisticated HTTP clients.

400 (Bad Request) may be used to indicate nonspecific failure
400 is the generic client-side error status, used when no other 4xx error code is appropriate. For errors in the 4xx category, the response body may contain a document describing the client’s error (unless the request method was HEAD).

500 (Internal Server Error) should be used to indicate API malfunction 500 is the generic REST API error response.
Most web frameworks automatically respond with this response status code whenever they execute some request handler code that raises an exception. A 500 error is never the client’s fault and therefore it is reasonable for the client to retry the exact same request that triggered this response, and hope to get a different response.
"""
import falcon

API_GENERAL_ERROR =  {  
    "status"        : falcon.HTTP_500,
    "title"         : "ERROR: unexpected error.",
    "description"   : "Got the following message: ",
    "code"          : "00001"
}

API_DB_ERROR =  {  
    "status"        : falcon.HTTP_500,
    "title"         : "ERROR: database query.",
    "description"   : "Could not query the database got the following message: ",
    "code"         : "00002"
}

API_PARAMETER_ERROR =  {  
    "status"        : falcon.HTTP_500,
    "title"         : "ERROR: parameter not valid.",
    "description"   : "Could not process your input, parameter(s) : ",
    "code"          : "00003"
}

API_TIMESTAMP_ERROR =  {  
    "status"        : falcon.HTTP_500,
    "title"         : "ERROR: timestamp value.",
    "description"   : "timestamp has wrong format: ",
    "code"          : "00004"
}

API_PARAMETER_MISSING_ERROR =  {  
    "status"        : falcon.HTTP_500,
    "title"         : "ERROR: parameter missing.",
    "description"   : "Could not process your input, parameter(s) is missing: ",
    "code"          : "00005"
}

