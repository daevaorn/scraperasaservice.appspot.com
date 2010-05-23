# API Reference

## Create session

### POST /session/
Create session with auto id
#### Params _{application/json}_
 - **host** Ñ target host _{string}_
 - **headers** Ñ default headers _{hash}_
 - **cookies** Ñ default cookies _{hash}_
#### Returns
##### Status
201 Created
##### Headers
 - **location** Ñ session url
___
### PUT /session/[id]
Create session with explicit id
#### Params _{application/json}_
 - **host** Ñ target host _{string}_
 - **headers** Ñ default headers _{hash}_
 - **cookies** Ñ default cookies _{hash}_
#### Returns
##### Status
200 OK

## Delete session

### DELETE /session/[id]
Delete existing session
#### Params
None
#### Returns
##### Status
200 OK

## Session status

### GET /session/[id]
Get session status and statistic
#### Params
None
#### Returns
##### Status
200 OK
##### Body _{application/json}_
 - **created_at** Ñ session creation time _{string}_
 - **headers** Ñ default request headers _{list}_
 - **cookies** Ñ default request cookies _{hash}_
 - **request_count** Ñ count of request with current session _{int}_
 - **last_request_at** Ñ time when was performed last request with current session _{string}_

## Performing request (scraping)

### POST /session/[id]
Scrape url
#### Params _{application/json}_
 - **headers** Ñ request headers _{list}_
 - **cookies** Ñ request cookies _{hash}_
 - **urls** Ñ requested urls _{hash}_:
    - _**key**_ Ñ concrete url _{string}_
    - _**value**_ _{hash}_:
        - **raw** Ñ do not convert result to json _{boolean}_
        - **match** Ñ XPath expression info _{hash}_:
            - **pattern** Ñ XPath expression to match _{string}_
            - **default_namespace** Ñ setting default namesapce _{string}_
            - **namespaces** Ñ namespaces map _{hash}_:
                - _**key**_ Ñ prefix _{string}_
                - _**value**_ Ñ namespace _{string}_
            - **variables** Ñ expression variables _{hash}_
 - **return_content** Ñ must return whole content _{boolean}_
 - **follow_redirects** Ñ must handle redirects _{boolean}_
#### Returns
##### Status
200 OK
##### Body _{application/json}_
 - _**key**_ Ñ url _{string}_
 - _**value**_ _{hash}_:
     - **status** Ñ http status code _{int}_
     - **headers** Ñ http headers _{list}_
     - **cookies** Ñ http cookies _{hash}_
     - **content** Ñ url content _{string}_
     - **matched** Ñ list of success matched content _{hash}_:
        - _**key**_ Ñ pattern _{string}_
        - _**value**_ Ñ content _{string or json}_
