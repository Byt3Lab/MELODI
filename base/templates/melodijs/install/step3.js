import { RenderURLTemplate } from '/static/base/melodiJS/render_url_template.js'
import { RenderURLAPI } from '/static/base/melodiJS/render_url_api.js'

const getUrlTemplate = new RenderURLTemplate("base")
const getUrlAPI = new RenderURLAPI("base")

export default {
    template: { url: getUrlTemplate("install/step3") },
    data() {
        return {
            loading: false,
            error: null,
            distribution: 'cloud',
            lang: 'fr',
            currency: 'XAF',
            time_zone: 'UTC',
            prefix_table: 'ml_'
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
    hooks: {
        beforeMount() {
            const app_cfg = this.$store.state.app_config || {}
            this.distribution = app_cfg.type_distribution || 'cloud'
            this.lang = app_cfg.lang || 'fr'
            this.currency = app_cfg.currency || 'XAF'
            this.time_zone = app_cfg.time_zone || 'UTC'
            this.prefix_table = app_cfg.prefix_table || 'ml_'
        }
    },
    methods: {
        async finish() {
            this.loading = true;
            this.error = null;

            try {
                // Update store with app settings
                this.$store.dispatch('updateAppConfig', {
                    type_distribution: this.distribution,
                    lang: this.lang,
                    currency: this.currency,
                    time_zone: this.time_zone,
                    prefix_table: this.prefix_table
                })

                // Combine data
                const payload = {
                    "db_config": this.db_config,
                    "admin_user": this.admin_user,
                    "app_config": this.$store.state.app_config
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
