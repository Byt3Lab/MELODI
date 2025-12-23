import { RenderURLTemplate } from '/static/base/melodiJS/render_url_template.js'

const getUrlTemplate = new RenderURLTemplate("base")

export default {
    template: { url: getUrlTemplate("install/step1") },
    data() {
        return {
            db_provider: "postgresql",
            db_user: "",
            db_password: "",
            db_password_confirm: "",
            db_host: "localhost",
            db_port: "5432",
            db_name: "",
            loading_btn: false
        }
    },
    hooks: {
        beforeMount() {
            // Load data from store if exists
            const config = this.$store.state.db_config;

            this.db_provider = config.provider || "postgresql";
            this.db_user = config.user;
            this.db_password = config.password;
            this.db_password_confirm = config.password; // Pre-fill confirm if loaded
            this.db_host = config.host || "localhost";
            this.db_port = config.port || "5432";
            this.db_name = config.name;
        }
    },
    watch: {

    },
    methods: {
        submit(e) {
            e.preventDefault();
            if (!this.db_name) {
                alert("Le nom de la base de données est requis.");
                return;
            }

            if (!this.db_host || !this.db_user || !this.db_port || !this.db_password) {
                alert("Veuillez remplir tous les champs de connexion (Hôte, Port, Utilisateur, Mot de passe).");
                return;
            }
            if (this.db_password !== this.db_password_confirm) {
                alert("Les mots de passe de la base de données ne correspondent pas.");
                return;
            }

            // Save to store
            this.$store.dispatch('updateDBConfig', {
                provider: this.db_provider,
                host: this.db_host,
                port: this.db_port,
                user: this.db_user,
                password: this.db_password,
                name: this.db_name
            });

            // Navigate to next step
            this.$router.push('/step2');
        }
    }
}
