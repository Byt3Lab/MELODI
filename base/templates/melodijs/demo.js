import { createApp } from '/static/base/melodiJS/melodijs.js'

function getUrlTemplate(template) {
    return "/static_templates_melodijs/base/"+template+".html"
}

const app = createApp({
        components:{
            "c-demo":{
                data(){
                    return {
                        name: "gaetant"
                    }
                },
                template:{url:getUrlTemplate("demo")},
                hooks:{
                    mounted(){
                    }
                },
                methods:{
                    hello(){
                        alert("helllo")
                    }
                }
            },
            "c-demo2":{
                data(){
                    return {
                    }
                },
                template:"hello 2  <button @click='hello'>click 2</button>",
                methods:{
                    hello(){
                        alert("helllo 2")
                    }
                }
            },
            "c-demo3":{
                data(){
                    return {
                    }
                },
                template:{el:"#tpl"},
            },
               "c-demo4":{
                props:["name"],
                data(){
                    return {
                    }
                },
                template:{url:getUrlTemplate("demo2")},
            }
        }
    })

app.mount("#app")