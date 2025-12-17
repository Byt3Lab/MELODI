class RenderURLTemplate {
    constructor(module){
        this.module = module

        return this.getURLTemplate.bind(this)
    }

    getURLTemplate(template){
        return "/static_templates_melodijs/"+this.module+"/"+template+".html"
    }
}

export { RenderURLTemplate }