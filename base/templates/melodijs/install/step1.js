import { createApp } from '/static/base/melodiJS/melodijs.js'
import { MelodiRouter } from '/static/base/melodiJS/router.js'
import { RenderURLTemplate } from '/static/base/melodiJS/render_url_template.js'
import { RenderURLAPI } from '/static/base/melodiJS/render_url_api.js'

const getUrlTemplate =  new RenderURLTemplate("base")
const getUrlAPI =  new RenderURLAPI("base")

const components = {
    "init-app": {
        template:{url:getUrlTemplate("install/step1")},
        data () {
            return {
                db_provider:"sqlite",
                db_user:"",
                db_password:"",
                db_host:"",
                db_port:"",
                db_name:"",
                loading_btn:false
            }
        },
        hooks:{
            async mounted(){
                
            }
        },
        methods:{
            async submit(){

                this.loading_btn = true

                const res = await fetch(  getUrlAPI("install"), {
                    method:"post",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        db_provider:this.db_provider,
                        db_user:this.db_user,
                        db_password:this.db_password,
                        db_host:this.db_host,
                        db_port:this.db_port,
                        db_name:this.db_name
                    })
                })
                const b = await res.text()

                console.log(b);

                setTimeout(() => {
                    this.loading_btn = false
                }, 500);
            }
        }
    }
}

const options = {
    components,
    template:"<init-app></init-app>",
}

const app = createApp(options)

app.mount("#app")