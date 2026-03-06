# Scripted Rest API Module Sample

This example shows the the usage of the `RestApi` fluent interface for creating scripted rest APIs in ServiceNow with sys modules for scripts

## Example Location
Source Code: [assets/samples/restapi-sample](../assets/samples/restapi-sample)

## Code Samples

### `rest-api-module.now.ts`
Path: [restapi-sample/fluent/rest-api-module.now.ts](../assets/samples/restapi-sample/fluent/rest-api-module.now.ts)

```typescript
import { RestApi } from '@servicenow/sdk/core'
import { process } from '../server/rest-api-handler'

/**
 * This is a simple example of a REST API build using fluent that has 4 routes (GET, POST, PUT, DELETE)
 * scripts are enclosed in the `script` tag to allow for inline syntax highlighting for server code
 * /api/restapi-hello
 */

RestApi({
    $id: Now.ID['restapi-modules'],
    name: 'rest api fluent modules sample',
    service_id: 'restapi_modules',
    consumes: 'application/json',
    routes: [
        {
            $id: Now.ID['restapi-modules-get'],
            name: 'get',
            method: 'GET',
            script: process,
        },
    ],
})

```

### `rest-api-simple.now.ts`
Path: [restapi-sample/fluent/rest-api-simple.now.ts](../assets/samples/restapi-sample/fluent/rest-api-simple.now.ts)

```typescript
import { RestApi } from '@servicenow/sdk/core'

/**
 * This is a simple example of a REST API build using fluent that has 4 routes (GET, POST, PUT, DELETE)
 * scripts are enclosed in the `script` tag to allow for inline syntax highlighting for server code
 * /api/restapi-hello
 */

RestApi({
    $id: Now.ID['restapi-hello'],
    name: 'rest api fluent sample',
    service_id: 'restapi_hello',
    consumes: 'application/json',
    routes: [
        {
            $id: Now.ID['restapi-hello-get'],
            name: 'get',
            method: 'GET',
            script: script`
              (function process( /*RESTAPIRequest*/ request, /*RESTAPIResponse*/ response) {
                response.setBody({ message: 'Hello, World!' })
              })(request, response)
            `,
        },
        {
            $id: Now.ID['restapi-hello-post'],
            name: 'post',
            method: 'POST',
            script: script`
              (function process( /*RESTAPIRequest*/ request, /*RESTAPIResponse*/ response) {
				            var reqbody = request.body.dataString;
                    var parser = new global.JSON();
                    var parsedData = parser.decode(reqbody);

                    response.setBody({ post: parsedData })
              })(request, response)
            `,
        },
        {
            $id: Now.ID['restapi-hello-put'],
            name: 'put',
            method: 'PUT',
            script: script`
              (function process( /*RESTAPIRequest*/ request, /*RESTAPIResponse*/ response) {
                var reqbody = request.body.dataString;
                var parser = new global.JSON();
                var parsedData = parser.decode(reqbody);

                response.setBody({ put: parsedData })
              })(request, response)
            `,
        },
        {
            $id: Now.ID['restapi-hello-delete'],
            name: 'delete',
            method: 'DELETE',
            script: script`
              (function process( /*RESTAPIRequest*/ request, /*RESTAPIResponse*/ response) {
                response.setBody({ delete: { msg: "DELETED" } })
              })(request, response)
            `,
        },
    ],
})

```
