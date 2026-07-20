# Simple Sys Module Sample

These examples show two techniques to call a module cross-scope.
## Expose a class
Sample Class demonstrates creating a server side script to expose and wrap a module in a class so that it can be used similarly to traditional script includes.
```javascript
var sample = new SampleClass();
sample.getTestOne();
```
## Expose "require" using x_require
Create a script include to expose "require" so that modules can be referenced cross-scope. You will need to modify the `api_name` property to use your application's scope.
Once installed use the script by calling {scope_name}.x_require with the path that you copied from the module in the sys_module table.
```javascript
// ES6+:
const { methodA, propertyB } = x_snc_scope_name.x_require("full/path/of/es_module/in/sys_module/table");
// ES5:
var myModule = x_snc_scope_name.x_require("full/path/of/es_module/in/sys_module/table");
myModule.methodA();
myModule.propertyB;
```

## Example Location
Source Code: [assets/samples/sys_module-sample](../assets/samples/sys_module-sample)

## Code Samples

### `script-include-module-one.now.ts`
Path: [sys_module-sample/fluent/script-include-module-one.now.ts](../assets/samples/sys_module-sample/fluent/script-include-module-one.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

/**
 * This will expose a sys_module through a script include so that it can be used in other application scopes through this script include
 */
Record({
    $id: Now.ID['si-module-1'],
    table: 'sys_script_include',
    data: {
        access: 'public',
        active: true,
        api_name: 'x_sysmodulesample.SampleClass',
        client_callable: false,
        mobile_callable: false,
        name: 'SampleClass',
        sandbox_callable: false,
        script: script`const sinc = require('./dist/server/sample-class.js');
var SampleClass = sinc.SampleClass;
`,
        sys_name: 'SampleClass',
    },
})

```

### `script-include-x-require.now.ts`
Path: [sys_module-sample/fluent/script-include-x-require.now.ts](../assets/samples/sys_module-sample/fluent/script-include-x-require.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

/**
 * This will expose require through a script include so that modules may be used across scope
 */
Record({
    $id: Now.ID['x_sysmodulesample.x_require'],
    table: 'sys_script_include',
    data: {
        access: 'public',
        active: true,
        api_name: 'x_sysmodulesample.x_require',
        client_callable: false,
        mobile_callable: false,
        name: 'x_require',
        sandbox_callable: false,
        script: script`
// Polyfill due to an error (fixed in Xanadu Patch 2 and Washington DC Patch 9) where "require"
// is undefined when calling scripts with require statements.
const x_require = (function() {
    if (typeof require == "undefined") {
        return function(path) {
			// **Use the API Name value of this script**
			const API_NAME = "x_sysmodulesample.x_require";
            var nowGr = new GlideRecord("sys_script_include");
            nowGr.get("api_name", API_NAME);
            nowGr.script = "require('" + path + "')";

            var evaluator = new GlideScopedEvaluator();
            var obj = evaluator.evaluateScript(nowGr, "script");

            return obj;
        };
    } else {
        return function(path) {
            return require(path);
        };
    }
})();
        `,
        sys_name: 'x_require',
    },
})

```
