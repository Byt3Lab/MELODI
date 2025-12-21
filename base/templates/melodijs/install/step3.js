import { RenderURLTemplate } from '/static/base/melodiJS/render_url_template.js'
import { RenderURLAPI } from '/static/base/melodiJS/render_url_api.js'

const getUrlTemplate = new RenderURLTemplate("base")
const getUrlAPI = new RenderURLAPI("base")

export default {
    template: { url: getUrlTemplate("install/step3") },
    data() {
        return {
            loading: false,
            error: null
        }
    },
    computed: {
        db_config() {
            return this.$store.state.db_config;
        },
        admin_user() {
            return this.$store.state.admin_user;
        }
    },
    methods: {
        async finish() {
            this.loading = true;
            this.error = null;

            try {
                // Combine data
                const payload = {
                    "db_config": this.db_config,
                    "admin_user": this.admin_user
                };

                const res = await fetch(getUrlAPI("install"), {
                    method: "post",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                })

                const data = await res.json()

                if (data.status_code === 200) {
                    this.$store.dispatch('setInstallationStatus', 'success');
                    // Redirect to finish page
                    this.$router.push('/finish');
                } else {
                    this.error = data.message || "Une erreur est survenue lors de l'installation.";
                }
            } catch (e) {
                console.error(e);
                this.error = "Erreur de communication avec le serveur.";
            } finally {
                this.loading = false;
            }
        }
    }
}
