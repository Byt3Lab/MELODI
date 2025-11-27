function getUrlTemplate(template) {
    return "/static_templates_melodijs/base/"+template+".html"
}

app = createMelodiApp({
        components:{
            "h-a":{
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
            "h-a2":{
                data(){
                    return {
                    }
                },
                template:{url:getUrlTemplate("demo2")},
            },
            "h-a3":{
                data(){
                    return {
                    }
                },
                template:{url:getUrlTemplate("demo3")},
            },
            "h-a4":{
                data(){
                    return {
                    }
                },
                template:{el:"#tpl"},
            }
        }
    })

app.mount("#app")