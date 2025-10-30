// mini framework pour rendre l'application reative

(function () {
    if (!window.mljs) {
        console.log("mljs is not defined")
        return
    }

    class Melodi{
        constructor(options) {
            this.el = document.querySelector(options.el)
            this.content = this.el.innerHTML
            this.data = options.data
            this.init()
        }

        init() {
            // // Crée un proxy réactif
            // this.data = new Proxy(this.data, {
            //     set: (target, key, value) => {
            //         target[key] = value
            //         this.update()
            //         return true
            //     }
            // })

            this.update()
        }

        update() {
            // Recherche les {{ ... }} dans le HTML
            const content = this.content
            this.el.innerHTML = content.replace(
                /\[\[(.+?)\]\]/g,
                (match, key) => {
                    key = key.trim()
                    return this.data[key] || ''
                }
            )
        }
    }

    window.mljs.Melodi = Melodi
})()