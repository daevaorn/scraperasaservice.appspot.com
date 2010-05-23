# API Reference

## Create session

### POST /session/
Create session with auto id
#### Params _{application/json}_
 - **host** � target host _{string}_
 - **headers** � default headers _{hash}_
 - **cookies** � default cookies _{hash}_
#### Returns
##### Status
201 Created
##### Headers
 - **location** � session url
___
### PUT /session/[id]
Create session with explicit id
#### Params _{application/json}_
 - **host** � target host _{string}_
 - **headers** � default headers _{hash}_
 - **cookies** � default cookies _{hash}_
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
 - **created_at** � session creation time _{string}_
 - **headers** � default request headers _{list}_
 - **cookies** � default request cookies _{hash}_
 - **request_count** � count of request with current session _{int}_
 - **last_request_at** � time when was performed last request with current session _{string}_

## Performing request (scraping)

### POST /session/[id]
Scrape url
#### Params _{application/json}_
 - **headers** � request headers _{list}_
 - **cookies** � request cookies _{hash}_
 - **urls** � requested urls _{hash}_:
    - _**key**_ � concrete url _{string}_
    - _**value**_ _{hash}_:
        - **raw** � do not convert result to json _{boolean}_
        - **match** � XPath expression info _{hash}_:
            - **pattern** � XPath expression to match _{string}_
            - **default_namespace** � setting default namesapce _{string}_
            - **namespaces** � namespaces map _{hash}_:
                - _**key**_ � prefix _{string}_
                - _**value**_ � namespace _{string}_
            - **variables** � expression variables _{hash}_
 - **return_content** � must return whole content _{boolean}_
 - **follow_redirects** � must handle redirects _{boolean}_
#### Returns
##### Status
200 OK
##### Body _{application/json}_
 - _**key**_ � url _{string}_
 - _**value**_ _{hash}_:
     - **status** � http status code _{int}_
     - **headers** � http headers _{list}_
     - **cookies** � http cookies _{hash}_
     - **content** � url content _{string}_
     - **matched** � list of success matched content _{hash}_:
        - _**key**_ � pattern _{string}_
        - _**value**_ � content _{string or json}_
