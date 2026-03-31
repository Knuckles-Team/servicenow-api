import { RestApi } from '@servicenow/sdk/core'
import { process } from '../server/rest-api-handler'



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
