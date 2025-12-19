import { RenderURLTemplate } from '/static/base/melodiJS/render_url_template.js'

const getUrlTemplate = new RenderURLTemplate("base")

export default {
    template: { url: getUrlTemplate("install/finish") },
    data() {
        return {}
    },
    mounted() {
        // Clear session storage as installation is complete
        sessionStorage.removeItem('melodi_install_state');
    }
}
