# Service Portal Sample

This example shows the the usage of Service Portal with widgets and dependencies

## Example Location
Source Code: [assets/samples/service-portal-sample](../assets/samples/service-portal-sample)

## Code Samples

### `sp_portal.now.ts`
Path: [service-portal-sample/fluent/portal/sp_portal.now.ts](../assets/samples/service-portal-sample/fluent/portal/sp_portal.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

Record({
    $id: Now.ID['sample-portal'],
    table: 'sp_portal',
    data: {
        title: 'Sample Portal',
        url_suffix: 'sample',
        logo: Now.attach('../../../assets/servicenow.svg'),
        icon: Now.attach('../../../assets/servicenow.jpg'),
    },
})

```

### `sp_instance_7ab692caffd4b210fd87ffffffffffeb.now.ts`
Path: [service-portal-sample/fluent/page/sp_instance_7ab692caffd4b210fd87ffffffffffeb.now.ts](../assets/samples/service-portal-sample/fluent/page/sp_instance_7ab692caffd4b210fd87ffffffffffeb.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

Record({
    $id: Now.ID['7ab692caffd4b210fd87ffffffffffeb'],
    table: 'sp_instance',
    data: {
        active: true,
        advanced_placeholder_dimensions: 'false',
        async_load: 'false',
        async_load_device_type: 'desktop,tablet,mobile',
        async_load_trigger: 'viewport',
        color: 'default',
        order: 1,
        placeholder_dimensions:
            '{&#13;	"mobile": {&#13;		"height": "250px",&#13;		"width": "100%"&#13;	},&#13;	"desktop": {&#13;		"height": "250px",&#13;		"width": "100%"&#13;	},&#13;	"tablet": {&#13;		"height": "250px",&#13;		"width": "100%"&#13;	}&#13;}',
        placeholder_dimensions_script:
            'function evaluateConfig(options) { return {	"mobile": {		"height": "250px",		"width": "100%"	},	"desktop": {		"height": "250px",		"width": "100%"	},	"tablet": {		"height": "250px",		"width": "100%"	}}; }',
        placeholder_template: `<!--
	AngularJS template with configurable options.
	Use the \`options\` object to control dynamic behavior.
	Example: Display an element when max row count is 10:
	<div ng-if="options.maxRowCount === 10"></div>
	The \`skeleton-container\` class is used for loading placeholders.
-->
	<div class="skeleton-container">
	<!-- Header Skeleton -->
	<div class="skeleton-box skeleton-header"></div>
	<!-- Body Skeleton -->
	<div class="skeleton-box skeleton-line"></div>
	<div class="skeleton-box skeleton-line small"></div>
	<div class="skeleton-box skeleton-line medium"></div>
</div>`,
        preserve_placeholder_size: 'false',
        size: 'md',
        sp_column: '60b69e8affd4b210fd87ffffffffff27',
        sp_widget: '58ddf4df40894f298a720955cc549b03',
    },
})

```

### `sp_page_8e66560affd4b210fd87ffffffffffe6.now.ts`
Path: [service-portal-sample/fluent/page/sp_page_8e66560affd4b210fd87ffffffffffe6.now.ts](../assets/samples/service-portal-sample/fluent/page/sp_page_8e66560affd4b210fd87ffffffffffe6.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

Record({
    $id: Now.ID['8e66560affd4b210fd87ffffffffffe6'],
    table: 'sp_page',
    data: {
        category: 'custom',
        draft: false,
        id: 'sample_page',
        internal: false,
        omit_watcher: false,
        public: false,
        title: 'sample-page',
        use_seo_script: false,
    },
})

```

### `sys_scope_privilege_6d109a82ff54b210fd87ffffffffff8e.now.ts`
Path: [service-portal-sample/fluent/page/sys_scope_privilege_6d109a82ff54b210fd87ffffffffff8e.now.ts](../assets/samples/service-portal-sample/fluent/page/sys_scope_privilege_6d109a82ff54b210fd87ffffffffff8e.now.ts)

```typescript
import { CrossScopePrivilege } from '@servicenow/sdk/core'

CrossScopePrivilege({
    $id: Now.ID['6d109a82ff54b210fd87ffffffffff8e'],
    operation: 'execute',
    status: 'allowed',
    targetName: 'GlideQuery',
    targetScope: 'global',
    targetType: 'sys_script_include',
})

```

### `sp_row_24b69e8affd4b210fd87ffffffffff24.now.ts`
Path: [service-portal-sample/fluent/page/sp_row_24b69e8affd4b210fd87ffffffffff24.now.ts](../assets/samples/service-portal-sample/fluent/page/sp_row_24b69e8affd4b210fd87ffffffffff24.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

Record({
    $id: Now.ID['24b69e8affd4b210fd87ffffffffff24'],
    table: 'sp_row',
    data: {
        order: '1',
        sp_container: '8186164affd4b210fd87ffffffffff11',
    },
})

```

### `sp_column_60b69e8affd4b210fd87ffffffffff27.now.ts`
Path: [service-portal-sample/fluent/page/sp_column_60b69e8affd4b210fd87ffffffffff27.now.ts](../assets/samples/service-portal-sample/fluent/page/sp_column_60b69e8affd4b210fd87ffffffffff27.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

Record({
    $id: Now.ID['60b69e8affd4b210fd87ffffffffff27'],
    table: 'sp_column',
    data: {
        order: '1',
        size: '12',
        sp_row: '24b69e8affd4b210fd87ffffffffff24',
    },
})

```

### `sp_container_8186164affd4b210fd87ffffffffff11.now.ts`
Path: [service-portal-sample/fluent/page/sp_container_8186164affd4b210fd87ffffffffff11.now.ts](../assets/samples/service-portal-sample/fluent/page/sp_container_8186164affd4b210fd87ffffffffff11.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

Record({
    $id: Now.ID['8186164affd4b210fd87ffffffffff11'],
    table: 'sp_container',
    data: {
        background_style: 'default',
        bootstrap_alt: 'false',
        name: 'sample-page - Container 1',
        order: '1',
        sp_page: '8e66560affd4b210fd87ffffffffffe6',
        subheader: 'false',
        width: 'container',
    },
})

```

### `sample-widget.now.ts`
Path: [service-portal-sample/fluent/widgets/sample-widget.now.ts](../assets/samples/service-portal-sample/fluent/widgets/sample-widget.now.ts)

```typescript
import { SPWidget } from '@servicenow/sdk/core'

const CHARTJS = 'a7a8754347011200ba13a5554ee4905c'
const SP_ELLIPSIS_TOOLTIP = '1d2b40e07323201081d3738234f6a714'

SPWidget({
    $id: Now.ID['sample-widget'],
    name: 'Sample Widget',
    id: 'sample-widget',
    clientScript: Now.include('sample-widget.client.js'),
    serverScript: Now.include('sample-widget.server.js'),
    htmlTemplate: Now.include('sample-widget.html'),
    customCss: Now.include('sample-widget.scss'),
    demoData: {
        data: {
            incidents: [99, 59, 80, 81, 56, 55, 40, 0, 5, 21, 11, 30],
        },
    },
    hasPreview: true,
    linkScript: `function link(scope, element, attrs, controller) {
}`,
    dependencies: [CHARTJS],
    angularProviders: [SP_ELLIPSIS_TOOLTIP],
})

```
