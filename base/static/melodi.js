// mini framework pour rendre l'application reative

(function () {
    if (!window.mljs) {
        console.log("mljs is not defined")
        return
    }

    class Melodi{
        constructor(options) {
            this.components = {}
            this.store = {}
            this.init(options)
        }

        init(options) {
            this.el = document.querySelector(options.el)
        }

        render(){

        }
    }

    class Component{
        constructor (options) {
            this.app = null
            this.children = {}
        }

        addComponent (name, component) {
            this.children[name] = component
        }

        init(options){
            
        }

        render () {

        }
    }

    window.mljs.Melodi = Melodi
})()