import { Record } from '@servicenow/sdk/core'


Record({
    $id: Now.ID['si-module-1'],
    table: 'sys_script_include',
    data: {
        access: 'public',
        active: true,
        api_name: 'x_sysmodulesample.SampleScriptInclude',
        client_callable: false,
        mobile_callable: false,
        name: 'SampleScriptInclude',
        sandbox_callable: false,
        script: Now.include('./script-include.server.js'),
        sys_name: 'SampleClass',
    },
})
