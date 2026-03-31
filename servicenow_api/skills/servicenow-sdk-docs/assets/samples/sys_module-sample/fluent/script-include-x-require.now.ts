import { Record } from '@servicenow/sdk/core'


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


const x_require = (function() {
    if (typeof require == "undefined") {
        return function(path) {
			
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
