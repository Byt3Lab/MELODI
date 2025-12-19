import { RenderURLTemplate } from '/static/base/melodiJS/render_url_template.js'

const getUrlTemplate = new RenderURLTemplate("base")

export default {
    template: { url: getUrlTemplate("install/step2") },
    data() {
        return {
            username: "",
            email: "",
            password: "",
            password_confirm: "",
            first_name: "",
            last_name: ""
        }
    },
    hooks: {
        beforeMount() {
            // Load data from store if exists
            const user = this.$store.state.admin_user;
            this.username = user.username;
            this.email = user.email;
            this.password = user.password;
            this.password_confirm = user.password;
            this.first_name = user.first_name;
            this.last_name = user.last_name;
        }
    },
    methods: {
        submit(e) {
            e.preventDefault();
            if (!this.username || !this.email || !this.password || !this.first_name || !this.last_name) {
                alert("Tous les champs sont requis.");
                return;
            }

            if (this.password !== this.password_confirm) {
                alert("Les mots de passe ne correspondent pas.");
                return;
            }

            // Save to store
            this.$store.dispatch('updateAdminUser', {
                username: this.username,
                email: this.email,
                password: this.password,
                first_name: this.first_name,
                last_name: this.last_name
            });

            // Navigate to next step
            this.$router.push('/step3');
        }
    }
}
