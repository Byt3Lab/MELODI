import { createApp } from '/static/base/melodiJS/melodijs.js'
import { MelodiRouter } from '/static/base/melodiJS/router.js'

function getUrlTemplate(template) {
    return "/static_templates_melodijs/base/"+template+".html"
}

const components = {
    props:["title"],
    "h-hello": {
        template:"<h1>welcome {{ title }}</h1>"
    },
    methods:{
        talk(){
            alert("hello world")
        }
    }
}

const options = {
    components,
    template:{url:getUrlTemplate("install/step1")},
    methods:{
        talk(){
            alert("hello world")
        }
    },
    hooks:{
        mounted(){
            alert("sds")
        }
    }
}

const app = createApp(options)

app.mount("#app")