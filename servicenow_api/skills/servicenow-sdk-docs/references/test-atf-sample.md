# Automated Test Framework (ATF) API Samples

This example shows usage of the `Test` fluent interface for creating ATF Tests in ServiceNow.

## Example Location
Source Code: [assets/samples/test-atf-sample](../assets/samples/test-atf-sample)

## Code Samples

### `atf-record-rest.now.ts`
Path: [test-atf-sample/atf-record-rest.now.ts](../assets/samples/test-atf-sample/atf-record-rest.now.ts)

```typescript
import { Test } from '@servicenow/sdk/core'

export default Test(
    {
        $id: 'a29a37229f703200ef4afa7dc67fcf9e',
        active: true,
        description:
            'Create an incident and retrieve it via REST Table API.\r\n\r\n***IMPORTANT***\r\nPlease create/select basic auth profile for Send REST Request - Inbound test step to run the test',
        name: 'Get Newly Created Resource via REST API Test',
    },
    (atf) => {
        atf.server.recordInsert({
            $id: 'step1',
            assert: 'record_successfully_inserted',
            enforceSecurity: false,
            fieldValues: { short_description: 'REST Test Incident' },
            table: 'incident',
        })
        atf.rest.sendRestRequest({
            $id: 'step2',
            basicAuthentication: '',
            body: '',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            method: 'get',
            path: "/api/now/v2/table/incident/{{step['d42bb7229f703200ef4afa7dc67fcf46'].record_id}}",
            queryParameters: {},
        })
        atf.rest.assertStatusCode({  $id: 'step3', operation: 'equals', statusCode: 200 })
        atf.rest.assertResponseJSONPayloadIsValid({ $id: 'step4',})
        atf.rest.assertJsonResponsePayloadElement({
            $id: 'step5',
            elementName: '/result/short_description',
            elementValue: 'REST Test Incident',
            operation: 'equals',
        })
    }
)

```

### `atf-record-query.now.ts`
Path: [test-atf-sample/atf-record-query.now.ts](../assets/samples/test-atf-sample/atf-record-query.now.ts)

```typescript
import { Test } from '@servicenow/sdk/core'

export default Test(
    {
        $id: '132888e4731030104a905ee515f6a74e',
        active: true,
        description:
            'This test validates that AWA Service Channels, Queues and their related records are configured in a way that should allow routing and assignment to run smoothly.',
        name: 'AWA: Check Configuration',
    },
    (atf) => {
        atf.server.recordQuery({ $id: 'step1',
            assert: 'records_match_query',
            enforceSecurity: false,
            fieldValues: 'active=true^EQ',
            table: 'awa_service_channel',
        })
    }
)

```

### `atf-output-variable.now.ts`
Path: [test-atf-sample/atf-output-variable.now.ts](../assets/samples/test-atf-sample/atf-output-variable.now.ts)

```typescript
import { Test } from '@servicenow/sdk/core'

/**
 * This example of an ATF Test uses an output variable to be used in subsequent steps
 */

Test(
    {
        active: true,
        failOnServerError: true,
        name: 'Simple example',
        description: 'An illustrative test written in fluent',
        $id: Now.ID[1],
    },
    (atf) => {
        atf.form.openNewForm({ $id: 'step1', table: 'incident', view: '', formUI: 'standard_ui' })
        atf.form.setFieldValue({ $id: 'step2', fieldValues: { short_description: 'test' }, formUI: 'standard_ui', table: 'incident' })
        const step3 = atf.form.submitForm({ $id: 'step3', formUI: 'standard_ui', assert: 'form_submitted_to_server' })
        atf.form.openExistingRecord({ $id: 'step4',
            formUI: 'standard_ui',
            recordId: step3.record_id,
            selectedTabIndex: 1,
            table: 'incident',
            view: '',
        })
        atf.server.log({ $id: 'ste5', log: `Finished opening a record with ${step3.record_id} as an id` })
    }
)

```

### `atf-impersonate.now.ts`
Path: [test-atf-sample/atf-impersonate.now.ts](../assets/samples/test-atf-sample/atf-impersonate.now.ts)

```typescript
import { Test } from '@servicenow/sdk/core'

Test(
    {
        $id: Now.ID['form-view-impersonate-test'],
        active: true,
        description:
            "A form that impersonates the user 'ATF User', and then uses the optional \"form view\" field of the 'open a new form' step to open a new 'User' form to its \"itil\" view, and then perform some actions on it.",
        name: 'Open a Form To a Specific View',
    },
    (atf) => {
        atf.server.impersonate({ $id: 'step1', user: 'd8f57f140b20220050192f15d6673a98' })
        atf.form.openNewForm({  $id: 'step2', table: 'sys_user', view: 'itil', formUI: 'standard_ui' })
        atf.form.fieldValueValidation({  $id: 'step3', conditions: 'first_name=^EQ', formUI: 'standard_ui', table: 'sys_user' })
        atf.form.fieldStateValidation({
            $id: 'step4',
            formUI: 'standard_ui',
            mandatory: [],
            notMandatory: ['title'],
            notReadOnly: [],
            notVisible: [],
            readOnly: [],
            table: 'sys_user',
            visible: [],
        })
        atf.form.setFieldValue({  $id: 'step5', fieldValues: { title: 'Senior Developer' }, formUI: 'standard_ui', table: 'sys_user' })
        atf.form.submitForm({  $id: 'step6', formUI: 'standard_ui' })
    }
)

```

### `atf-batching.now.ts`
Path: [test-atf-sample/atf-batching.now.ts](../assets/samples/test-atf-sample/atf-batching.now.ts)

```typescript
import { Test } from '@servicenow/sdk/core'

/**
 * This is an example ATF test that uses impesonation, form actions, and field state validation steps
 */

Test(
    {
        $id: Now.ID['Multi-Batch Test'],
        active: true,
        description:
            'A test that switches between UI steps and server-side steps to demonstrate the concept of batching. The server side step with order 500 breaks the test into three distinct "batches." Two in the UI step environment, and one in the server step environment.',
        name: 'Multi-Batch Test',
    },
    (atf) => {
        atf.server.impersonate({ $id: 'step1', user: 'd8f57f140b20220050192f15d6673a98' })
        atf.form.openNewForm({ $id: 'step2', table: 'sys_user', view: 'itil', formUI: 'standard_ui' })
        atf.form.fieldStateValidation({ $id: 'step3',
            formUI: 'standard_ui',
            mandatory: [],
            notMandatory: ['first_name', 'last_name'],
            notReadOnly: ['title'],
            notVisible: [],
            readOnly: [],
            table: 'sys_user',
            visible: [],
        })
        atf.form.setFieldValue({ $id: 'step4',
            fieldValues: { first_name: 'Emily', last_name: 'Employee' },
            formUI: 'standard_ui',
            table: 'sys_user',
        })
        atf.form.submitForm({ $id: 'step5', formUI: 'standard_ui', assert: 'form_submitted_to_server' })
        atf.form.openNewForm({ $id: 'step6', table: 'sc_task', view: '', formUI: 'standard_ui' })
        atf.form.setFieldValue({ $id: 'step7',
            fieldValues: {
                short_description: 'This is my second UI Batch',
                description: 'It is separated by the server side step. But each step will still run in order.',
            },
            formUI: 'standard_ui',
            table: 'sc_task',
        })
        atf.form.submitForm({ $id: 'step8', formUI: 'standard_ui', assert: 'form_submitted_to_server' })
    }
)

```

### `atf-sample.now.ts`
Path: [test-atf-sample/atf-sample.now.ts](../assets/samples/test-atf-sample/atf-sample.now.ts)

```typescript
import { Test } from '@servicenow/sdk/core'

export default Test(
    {
        $id: Now.ID['fail-description'],
        active: true,
        description:
            'A test that fails because the field "Description" has a value that does not match what we assert it to be',
        name: 'Fails Because an Assert Fails',
    },
    (atf) => {
        atf.server.impersonate({  $id: 'step1', user: 'd8f57f140b20220050192f15d6673a98' })
        atf.form.openNewForm({  $id: 'step2', table: 'sc_task', view: '', formUI: 'standard_ui' })
        atf.form.setFieldValue({
            $id: 'step3',
            fieldValues: {
                short_description: 'This is a task',
                description: 'About all the tasks that need to be discussed',
            },
            formUI: 'standard_ui',
            table: 'sc_task',
        })
        atf.form.fieldValueValidation({
            $id: 'step4',
            conditions: 'description=This is a different message than the one I just set^EQ',
            formUI: 'standard_ui',
            table: 'sc_task',
        })
        atf.form.submitForm({  $id: 'step5', formUI: 'standard_ui', assert: '' })
    }
)

```
