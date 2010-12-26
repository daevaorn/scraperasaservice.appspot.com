# Idea

 - Сервис который по запросам из вне идет на какие-то сервисы и скрапит их, возвращает контент уже в полу-структурированном виде.
 - Умеет возвращать JSON с элементами
 - принимает задачи как JSON
 - Принимает Xpath на входе
 - Принимает множество урлов
 - Умеет пушить результат клиенту - асинхронный скрапинг
 - Умеет прокидывать и возвращать заголовки
 - Поддерживате кеширование?
 - Поддерживать сценарии - заранее прописанные последовательности фетчинга урлов (например для процедуры логина):
    - мало эффективно -- обычно требуется как-то дополнительная логиа на каждом шаге

## Implementation

 - GAE
 - restish
    - http://www.evilchuck.com/2009/02/restish-on-app-engine.html)
 - раздает API токены для авторизации
    - OAuth?
 - py-dom-xpath

 - minidom -> dict
    - http://nonplatonic.com/ben.php?title=python_xml_to_dict_bow_to_my_recursive_g&more=1&c=1&tb=1&pb=1
    - отщеплять задачи на отдельные таски
       - http://code.google.com/intl/en/appengine/articles/deferred.html

## Formats

 - html -> minidom (через html5lib)
 - json -> minidom
    - нет реализации - http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    - неймспейсы
 - xml -> minidom

## Pipelines

  1. загрузка документа (html, xml, json)
  2. парсинг (html5lib, minidom, simplejson->minidom)
  3. матчинг (xpath)
  4. сериализация дерева (raw, json, xml, yaml?)
Проблемы:

 - Как скрапить страницы за логином?
    - Заставлять клиента логиниться по обычной процедуре
    - Прокидывать заголовки и куки
 - Как хендлить куки?
    - http://everydayscripting.blogspot.com/2009/08/google-app-engine-cookie-handling-with.html
    - Что делать с неймспейсами при сериализации дерева?
       - Для дефолтного убирать префикс
       - Для остальных ставить префикс
       - Возвращать мапинг префиксов

# API Reference

## Create session

### POST /session/
Create session with auto id
#### Params _{application/json}_
 - **host** &mdash; target host _{string}_
 - **headers** &mdash; default headers _{hash}_
 - **cookies** &mdash; default cookies _{hash}_
#### Returns
##### Status
201 Created
##### Headers
 - **location** &mdash; session url
___
### PUT /session/[id]
Create session with explicit id
#### Params _{application/json}_
 - **host** &mdash; target host _{string}_
 - **headers** &mdash; default headers _{hash}_
 - **cookies** &mdash; default cookies _{hash}_
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
 - **created_at** &mdash; session creation time _{string}_
 - **headers** &mdash; default request headers _{list}_
 - **cookies** &mdash; default request cookies _{hash}_
 - **request_count** &mdash; count of request with current session _{int}_
 - **last_request_at** &mdash; time when was performed last request with current session _{string}_

## Performing request (scraping)

### POST /session/[id]
Scrape url
#### Params _{application/json}_
 - **headers** &mdash; request headers _{list}_
 - **cookies** &mdash; request cookies _{hash}_
 - **urls** &mdash; requested urls _{list of hashes}_:
        - **url** &mdash; concrete url _{string}_
        - **match** &mdash; XPath expression info _{hash}_:
            - **raw** &mdash; do not convert result to json _{boolean}_
            - **pattern** &mdash; XPath expression to match _{string}_
            - **default_namespace** &mdash; setting default namesapce _{string}_
            - **namespaces** &mdash; namespaces map _{hash}_:
                - _**key**_ &mdash; prefix _{string}_
                - _**value**_ &mdash; namespace _{string}_
            - **variables** &mdash; expression variables _{hash}_
 - **return_content** &mdash; must return whole content _{boolean}_
 - **follow_redirects** &mdash; must handle redirects _{boolean}_
#### Returns
##### Status
200 OK
##### Body _{application/json}_
 - _**key**_ &mdash; url _{string}_
 - _**value**_ _{hash}_:
     - **status** &mdash; http status code _{int}_
     - **headers** &mdash; http headers _{list}_
     - **cookies** &mdash; http cookies _{hash}_
     - **content** &mdash; url content _{string}_
     - **matched** &mdash; list of success matched content _{hash}_:
        - _**key**_ &mdash; pattern _{string}_
        - _**value**_ &mdash; content _{string or json}_
