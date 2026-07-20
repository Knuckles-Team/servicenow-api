# Svelte UI Example

No description provided.

## Example Location
Source Code: [assets/samples/svelte-ui-page-sample](../assets/samples/svelte-ui-page-sample)

## Code Samples

### `index.now.ts`
Path: [svelte-ui-page-sample/fluent/index.now.ts](../assets/samples/svelte-ui-page-sample/fluent/index.now.ts)

```typescript
//Add your Fluent APIs here and in other now.ts files under src/fluent

```

### `svelte-hello-world.now.ts`
Path: [svelte-ui-page-sample/fluent/ui-pages/svelte-hello-world.now.ts](../assets/samples/svelte-ui-page-sample/fluent/ui-pages/svelte-hello-world.now.ts)

```typescript
import '@servicenow/sdk/global'
import { UiPage } from '@servicenow/sdk/core'
import incidentPage from '../../client/index.html'

UiPage({
    $id: Now.ID['svelte-sample-ui-page'],
    endpoint: 'x_svelteuisample_sample.do',
    description: 'Svelte Sample UI Page',
    category: 'general',
    html: incidentPage,
    direct: true,
})

```
