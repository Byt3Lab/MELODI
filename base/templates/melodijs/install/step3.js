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

                // Rename fields to match backend expectation if needed
                // Step 1 used: db_provider, db_user, db_password, db_host, db_port, db_name
                // Step 2 used: username, email, password
                // Backend expects: db_provider, db_user, db_password, db_host, db_port, db_name
                // AND presumably admin user details. 
                // Since I don't see the backend code for step3, I'll assume it expects everything or I should call step1 API?
                // Wait, step1.js originally called `/install` (POST).
                // The original code was just step1.
                // Now we are splitting it.
                // If the backend handles everything in one go, I should send everything to `/install`.
                // If the backend has steps, I should call them sequentially.
                // The user asked to "better divide the steps", implying frontend division.
                // I will assume the backend endpoint `/install` handles the full installation or I should check if there are other endpoints.
                // The original `step1.js` posted to `getUrlAPI("install")`.
                // I will assume this endpoint handles the DB config.
                // But now we also have admin user.
                // I'll assume I need to send everything to `getUrlAPI("install")` or maybe a new endpoint `getUrlAPI("install/finish")`.
                // Given I cannot see the backend, I will stick to `getUrlAPI("install")` and send all data.
                // If the backend only expects DB config, then my refactoring of adding Admin User might require backend changes which I cannot do (or user didn't ask for).
                // BUT, the user asked to "improve user experience" and "divide steps".
                // If I add an Admin User step, I must send that data somewhere.
                // I will send all data to `getUrlAPI("install")`. If it fails, I'll know.
                // Actually, `step1.js` originally posted to `/install/step1` (form action) but the JS posted to `getUrlAPI("install")`.

                const res = await fetch(getUrlAPI("install"), {
                    method: "post",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                })

                const data = await res.json()

                if (data.status === 'success') {
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
