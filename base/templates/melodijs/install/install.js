import { createApp } from '/static/base/melodiJS/melodijs.js'
import { MelodiRouter } from '/static/base/melodiJS/router.js'
import { MelodiStore } from '/static/base/melodiJS/store.js'
import { MelodiUI } from '/static/base/melodiUI/melodi.ui.js'
import Step1 from '/static_templates_melodijs/base/install/step1.js'
import Step2 from '/static_templates_melodijs/base/install/step2.js'
import Step3 from '/static_templates_melodijs/base/install/step3.js'
import Finish from '/static_templates_melodijs/base/install/finish.js'

// 2. Initialize Store
function saveState(state) {
    const db_config = state.db_config
    const admin_user = state.admin_user
    const installation_status = state.installation_status
    sessionStorage.setItem('melodi_install_state', JSON.stringify({ db_config, admin_user, installation_status }))
}

function loadState() {
    const state = sessionStorage.getItem('melodi_install_state')
    return state ? JSON.parse(state) : null
}

const store = new MelodiStore({
    state() {
        const stateSave = loadState()

        return {
            db_config: {
                provider: stateSave?.db_config?.provider || 'postgresql',
                host: stateSave?.db_config?.host || 'localhost',
                port: stateSave?.db_config?.port || '5432',
                user: stateSave?.db_config?.user || '',
                password: stateSave?.db_config?.password || '',
                name: stateSave?.db_config?.name || ''
            },
            admin_user: {
                username: stateSave?.admin_user?.username || '',
                email: stateSave?.admin_user?.email || '',
                password: stateSave?.admin_user?.password || '',
                first_name: stateSave?.admin_user?.first_name || '',
                last_name: stateSave?.admin_user?.last_name || ''
            },
            installation_status: stateSave?.installation_status || ''
        }
    },
    actions: {
        updateDBConfig(config) {
            this.state.db_config = config
            saveState(this.state)
        },
        updateAdminUser(user) {
            this.state.admin_user = user
            saveState(this.state)
        },
        setInstallationStatus(status) {
            this.state.installation_status = status
            saveState(this.state)
        }
    }
})

// 3. Initialize Router
const routes = [
    { path: '/', component: Step1, transition: 'fade' },
    { path: '/step2', component: Step2, transition: 'fade' },
    { path: '/step3', component: Step3, transition: 'fade' },
    { path: '/finish', component: Finish, transition: 'fade' },
    { path: '/:pathMatch(.*)*', component: Step1, transition: 'fade' }
]

const router = new MelodiRouter({
    routes
})

// 4. Create App
const app = createApp({
    template: `
        <div class="melodi-install-app">
            <router-view></router-view>
        </div>
    `
})

app.use(store)
app.use(router)
app.use(MelodiUI)

app.mount("#app")