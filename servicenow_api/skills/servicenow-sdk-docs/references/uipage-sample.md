# UI Page Sample

This example shows the the usage of `UiPage` (`sys_ui_page`)

## Example Location
Source Code: [assets/samples/uipage-sample](../assets/samples/uipage-sample)

## Code Samples

### `ui-page.now.ts`
Path: [uipage-sample/fluent/ui-page.now.ts](../assets/samples/uipage-sample/fluent/ui-page.now.ts)

```typescript
import { UiPage } from '@servicenow/sdk/core'

UiPage({
    $id: Now.ID['ui-page-sample'],
    category: 'general',
    endpoint: 'x_uipagesample_mypage.do',
    description: 'This is a sample UI Page created with the SDK',
    html: Now.include('./ui-page.html'),
    clientScript: Now.include('./ui-page.client-script.client.js'),
    processingScript: Now.include('./ui-page.processing-script.server.js'),
})

```
