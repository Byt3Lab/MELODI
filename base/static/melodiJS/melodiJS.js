// Minimal reactive component library (tiny Vue-like)

class MelodiJS {
    constructor(options){
        this.options = options || {}
        this.root = null
        this.components = this.options.components || {}
        // reactive global store (components can access via this.$store)
        this._mountedComponents = []
        this.store = this._makeStore(this.options.store || {})
    }

    mount(target){
        this.root = typeof target === 'string' ? document.querySelector(target) : target
        if (!this.root) throw new Error('Mount target not found')

        // for each registered component, find elements and mount
        const promises = []
        const tags = Object.keys(this.components)
        Object.keys(this.components).forEach(tag => {
            const nodes = Array.from(this.root.querySelectorAll(tag))
            nodes.forEach(node => {
                // skip if already mounted or if inside another custom component (will be mounted by its parent)
                if (node.__melodijs_mounted) return
                if (this._isDescendantOfCustom(node, tags)) return
                const compDef = this.components[tag]
                const comp = new Component(compDef)
                const p = comp.mount(node, this).then(() => { node.__melodijs_mounted = true })
                promises.push(p)
            })
        })

        return Promise.all(promises)
    }

    _isDescendantOfCustom(node, customTags){
        let p = node.parentElement
        while(p){
            const tag = p.tagName && p.tagName.toLowerCase()
            if (tag && customTags.indexOf(tag) !== -1) return true
            p = p.parentElement
        }
        return false
    }

    _makeStore(initial){
        const self = this
        const target = Object.assign({}, initial)
        return new Proxy(target, {
            set(obj, prop, val){
                obj[prop] = val
                // notify mounted components to re-render asynchronously to avoid reentry issues
                Promise.resolve().then(() => {
                    (self._mountedComponents || []).forEach(c => {
                        try { c._render() } catch (e) { /* ignore errors during notify */ }
                    })
                })
                return true
            }
        })
    }
}

class Component {
    constructor(def){
        this.template = def.template || ''
        this.dataFn = def.data || function(){ return {} }
        this.methodsDef = def.methods || {}
        // props can be an array of names or an object with detailed defs
        this.propsDef = def.props || null
        // lifecycle hooks: prefer explicit hooks, fallback to methods (migrated below)
        this.hooks = def.hooks || {}
        this.components = def.components || {}

        this.el = null
        this.app = null
        this.state = null
        this.methods = {}
        this._listeners = []
        this._events = {}
    }

    mount(el, app){
        this.el = el
        this.app = app
        try { console.debug && console.debug('Component.mount start for', el && el.tagName) } catch(e){}

        // capture the light DOM (children) to support <slot>
        // move original children into a detached container so we can re-read on every render
        try {
            this._slotSource = document.createElement('div')
            while (el.firstChild){ this._slotSource.appendChild(el.firstChild) }
        } catch(e){ this._slotSource = document.createElement('div') }

        // obtain props from element attributes
        const props = this._readPropsFromEl(el)

        // (lifecycle hooks should be provided in `hooks` or top-level keys in component def)

        // initialize data and merge props (props override) but only pass declared props
        const initial = this.dataFn.call(props) || {}
        // only include declared props
        const declared = this._gatherDeclaredProps()
        if (declared){
            Object.keys(declared).forEach(key => {
                const def = declared[key]
                if (props.hasOwnProperty(key)){
                    initial[key] = this._coercePropValue(props[key], def)
                } else if (def && def.hasOwnProperty('default')){
                    initial[key] = (typeof def.default === 'function') ? def.default() : def.default
                }
            })
        } else {
            Object.assign(initial, props)
        }

        // attach $store to raw data so methods/state can access it
        initial.$store = app.store

        // create reactive state
        this.state = this._makeReactive(initial)

    // inject references into state for convenience (element, app, root)
    try { this.state.__lastEl = this.el; this.state.__slotSourceEl = this.el; this.state.$app = app; this.state.$root = document } catch(e){}

        // event API helpers available on state
        try {
            const comp = this
            // register event listener on this component
            this.state.$on = function(eventName, handler){
                if (!eventName || typeof handler !== 'function') return
                comp._events[eventName] = comp._events[eventName] || []
                comp._events[eventName].push(handler)
                // return unregister
                return () => {
                    const arr = comp._events[eventName] || []
                    const idx = arr.indexOf(handler)
                    if (idx !== -1) arr.splice(idx, 1)
                }
            }
            // emit event: call local handlers, then bubble up to ancestor components
            this.state.$emit = function(eventName, payload){
                try {
                    const local = comp._events[eventName] || []
                    local.forEach(h => { try { h.call(comp.state, payload) } catch(e){} })
                    // bubble
                    let p = comp.el.parentElement
                    while(p){
                        const parentComp = p.__melodijs_instance
                        if (parentComp){
                            const handlers = parentComp._events[eventName] || []
                            handlers.forEach(h => { try { h.call(parentComp.state, payload) } catch(e){} })
                        }
                        p = p.parentElement
                    }
                } catch(e){}
            }
        } catch(e){}

        // bind methods to state
        try {
            // debug: ensure methodsDef is iterable
            // console.debug('binding methodsDef', Object.keys(this.methodsDef || {}))
            Object.keys(this.methodsDef || {}).forEach(name => {
                this.methods[name] = this.methodsDef[name].bind(this.state)
            })
        } catch (e) {
            console.error('Error binding methods:', e)
        }

    // register component on app so store updates can notify
    app._mountedComponents = app._mountedComponents || []
    app._mountedComponents.push(this)

        // mark instance on element for parent-child lookup
        try { this.el.__melodijs_instance = this } catch(e){}

        // initial render (handle async template resolution)
        return this._render(true)
    }

    _readPropsFromEl(el){
        const props = {}
        Array.from(el.attributes).forEach(attr => {
            // ignore special attributes
            if (/^v-|^@|^:/.test(attr.name)) return
            // only include declared props if propsDef exists
            const name = attr.name
            const declared = this._gatherDeclaredProps()
            if (declared){
                if (declared.hasOwnProperty(name)){
                    props[name] = this._coerceAttrValue(attr.value)
                }
            } else {
                props[name] = this._coerceAttrValue(attr.value)
            }
        })
        return props
    }

    _coerceAttrValue(val){
        // try number and boolean coercion
        if (val === 'true') return true
        if (val === 'false') return false
        if (!isNaN(val) && val.trim() !== '') return Number(val)
        return val
    }

    _gatherDeclaredProps(){
        // returns an object map of propName -> def (if array provided, returns names with undefined defs)
        if (!this.propsDef) return null
        if (Array.isArray(this.propsDef)){
            const out = {}
            this.propsDef.forEach(n => out[n] = {})
            return out
        }
        // assume object
        return this.propsDef
    }

    _coercePropValue(val, def){
        if (!def || !def.type) return val
        const t = def.type
        if (t === Number) return Number(val)
        if (t === Boolean) return (val === '' || val === true || val === 'true')
        if (t === String) return String(val)
        return val
    }

    _makeReactive(obj){
        const self = this
        return new Proxy(obj, {
            set(target, prop, value){
                target[prop] = value
                // re-render component on change (async to avoid reentry)
                Promise.resolve().then(() => { try { self._render() } catch(e){} })
                return true
            }
        })
    }

    _evalExpression(expr, scope){
        // Evaluate arbitrary JS expressions with access to component state and optional scope.
        // Use Function + 'with' to provide convenient access. Errors are swallowed and '' returned.
        try {
            if (!expr || typeof expr !== 'string') return ''
            const expression = expr.trim()
            // build a function that returns the evaluated expression within the state and scope contexts
            const fn = new Function('state', 'scope', 'with(state){ with(scope || {}){ try { return (' + expression + ') } catch(e){ return "" } } }')
            const res = fn(this.state || {}, scope || {})
            return (res === undefined || res === null) ? '' : res
        } catch (e){
            return ''
        }
    }

    // Process structural directives: v-for, v-if / v-else-if / v-else, v-show
    _processDirectives(tpl){
        const root = document.createElement('div')
        root.innerHTML = tpl

        const processChildren = (parent, scope) => {
            const outFrag = document.createDocumentFragment()
            const children = Array.from(parent.childNodes)
            for (let i = 0; i < children.length; i++){
                const child = children[i]
                if (child.nodeType === 1){ // element
                    // handle v-if chain
                    if (child.hasAttribute('v-if')){
                        // evaluate chain from i onwards
                        let picked = null
                        let j = i
                        while(j < children.length){
                            const sib = children[j]
                            // skip whitespace text nodes between v-if/v-else chain
                            if (sib.nodeType === 3 && (!sib.nodeValue || /^\s*$/.test(sib.nodeValue))){ j++; continue }
                            if (sib.nodeType !== 1) break
                            if (sib.hasAttribute('v-if') || sib.hasAttribute('v-else-if') || sib.hasAttribute('v-else')){
                                const expr = sib.getAttribute('v-if') || sib.getAttribute('v-else-if')
                                let take = false
                                if (expr){
                                    const val = this._evalExpression(expr, scope)
                                    take = !!val
                                } else if (sib.hasAttribute('v-else')){
                                    take = true
                                }
                                if (take && picked == null){ picked = sib }
                                j++
                                continue
                            }
                            break
                        }
                        if (picked){
                            // process picked element (clone without the v-if/else attrs)
                            const clone = picked.cloneNode(true)
                            clone.removeAttribute('v-if'); clone.removeAttribute('v-else-if'); clone.removeAttribute('v-else')
                            const processed = processNode(clone, scope)
                            processed.forEach(n => outFrag.appendChild(n))
                        } else {
                            // nothing matches, no node appended
                        }
                        // skip processed siblings
                        i = j-1
                        continue
                    }
                    // general processing (handles v-for inside)
                    const nodes = processNode(child, scope)
                    nodes.forEach(n => outFrag.appendChild(n))
                } else if (child.nodeType === 3){ // text node -> interpolate
                    const txt = child.nodeValue
                    const replaced = txt.replace(/\{\{\s*([^}]+)\s*\}\}/g, (m, expr) => {
                        const val = this._evalExpression(expr, scope)
                        return (val == null) ? '' : String(val)
                    })
                    outFrag.appendChild(document.createTextNode(replaced))
                } else {
                    // other nodes
                    outFrag.appendChild(child.cloneNode(true))
                }
            }
            return outFrag.childNodes ? Array.from(outFrag.childNodes) : [outFrag]
        }

        const processNode = (node, scope) => {
            // if node has v-for
            if (node.hasAttribute && node.hasAttribute('v-for')){
                const expr = node.getAttribute('v-for').trim()
                // support: "item in items" or "(item, index) in items"
                const inMatch = expr.match(/^\s*(?:\(([^,]+)\s*,\s*([^\)]+)\)|([^\s]+))\s+in\s+(.+)$/)
                if (!inMatch) return []
                let itemName, indexName, listExpr
                if (inMatch[1]){ itemName = inMatch[1].trim(); indexName = inMatch[2].trim(); listExpr = inMatch[4].trim() }
                else { itemName = inMatch[3].trim(); listExpr = inMatch[4].trim() }
                const list = this._evalExpression(listExpr, scope)
                const out = []
                // support arrays and objects (dictionary) iteration
                if (Array.isArray(list)){
                    for (let idx = 0; idx < list.length; idx++){
                        const item = list[idx]
                        const newScope = Object.assign({}, scope || {})
                        newScope[itemName] = item
                        if (indexName) newScope[indexName] = idx
                        const clone = node.cloneNode(true)
                        clone.removeAttribute('v-for')
                        // process clone's children recursively
                        const processed = processChildren(clone, newScope)
                        // wrap processed into a container element to return nodes
                        const container = document.createElement('div')
                        processed.forEach(n => container.appendChild(n))
                        Array.from(container.childNodes).forEach(n => out.push(n))
                    }
                } else if (list && typeof list === 'object'){
                    const keys = Object.keys(list)
                    for (let k = 0; k < keys.length; k++){
                        const key = keys[k]
                        const item = list[key]
                        const newScope = Object.assign({}, scope || {})
                        newScope[itemName] = item
                        if (indexName) newScope[indexName] = key
                        const clone = node.cloneNode(true)
                        clone.removeAttribute('v-for')
                        const processed = processChildren(clone, newScope)
                        const container = document.createElement('div')
                        processed.forEach(n => container.appendChild(n))
                        Array.from(container.childNodes).forEach(n => out.push(n))
                    }
                }
                return out
            }

            // support v-pre: when present, return element as-is without processing children or interpolation
            if (node.hasAttribute && node.hasAttribute('v-pre')){
                const raw = node.cloneNode(true)
                raw.removeAttribute('v-pre')
                return [raw]
            }

            // no v-for: clone and process children, apply v-show attribute if present
            const el = node.cloneNode(false)
            // handle v-show
            if (el.hasAttribute && el.hasAttribute('v-show')){
                const showExpr = el.getAttribute('v-show')
                const show = !!this._evalExpression(showExpr, scope)
                // set inline style
                const prev = el.getAttribute('style') || ''
                el.setAttribute('style', prev + ';display:' + (show ? '' : 'none') )
                el.removeAttribute('v-show')
            }
            // process child nodes
            const childProcessed = processChildren(node, scope)
            childProcessed.forEach(n => el.appendChild(n))
            return [el]
        }

        const resultNodes = processChildren(root, null)
        // build HTML
        const wrap = document.createElement('div')
        resultNodes.forEach(n => wrap.appendChild(n))
        return wrap.innerHTML
    }

    async _render(isInitial){
        // resolve template: string, or from element id (template tag), or from URL
        let tpl = this.template
        if (!tpl){
            tpl = this.el.innerHTML
        } else if (typeof tpl === 'object'){
            // { el: '#tplId' } or { url: '...' }
            if (tpl.el){
                const node = document.querySelector(tpl.el)
                tpl = node ? node.innerHTML : ''
            } else if (tpl.url){
                try {
                    const resp = await fetch(tpl.url)
                    tpl = await resp.text()
                } catch (e){
                    tpl = ''
                }
            }
        }

        // use template string now
        tpl = tpl || ''

        // process <slot> placeholders first so slot content can contain directives
        if (this._slotSource && tpl.indexOf('<slot') !== -1){
            const slotSource = document.createElement('div')
            slotSource.innerHTML = this._slotSource.innerHTML || ''

            const tplNode = document.createElement('div')
            tplNode.innerHTML = tpl

            const slotEls = Array.from(tplNode.querySelectorAll('slot'))
            slotEls.forEach(slotEl => {
                const name = slotEl.getAttribute('name')
                let inserted = false
                if (name){
                    const nodes = Array.from(slotSource.querySelectorAll('[slot="' + name + '"]'))
                    if (nodes.length){
                        nodes.forEach(n => slotEl.parentNode.insertBefore(n.cloneNode(true), slotEl))
                        inserted = true
                    }
                } else {
                    const nodes = Array.from(slotSource.childNodes).filter(n => {
                        return !(n.nodeType === 1 && n.hasAttribute && n.hasAttribute('slot'))
                    })
                    if (nodes.length){
                        nodes.forEach(n => slotEl.parentNode.insertBefore(n.cloneNode(true), slotEl))
                        inserted = true
                    }
                }

                if (!inserted){
                    const fallback = slotEl.innerHTML && slotEl.innerHTML.trim()
                    if (fallback){
                        const frag = document.createElement('div')
                        frag.innerHTML = slotEl.innerHTML
                        Array.from(frag.childNodes).forEach(n => slotEl.parentNode.insertBefore(n.cloneNode(true), slotEl))
                    }
                }

                slotEl.parentNode.removeChild(slotEl)
            })

            tpl = tplNode.innerHTML
        }

        // process structural directives (v-for, v-if/else, v-show) and perform scoped interpolation
        try {
            tpl = this._processDirectives(tpl)
        } catch (e) { /* fail-safe: ignore directive errors */ }

        // convert event shorthand @click, @input to data-on-* attributes
        tpl = tpl.replace(/@([a-zA-Z0-9_:-]+)\s*=\s*"([^"]+)"/g, (m, ev, handler) => {
            return `data-on-${ev}="${handler}"`
        })

        // convert v-model to data-model
        tpl = tpl.replace(/v-model\s*=\s*"([^"]+)"/g, (m, prop) => `data-model="${prop}"`)

        // call beforeMount once for initial render, or beforeUpdate for updates
        try {
            if (isInitial && typeof this.hooks.beforeMount === 'function') this.hooks.beforeMount.call(this.state)
            if (!isInitial && typeof this.hooks.beforeUpdate === 'function') this.hooks.beforeUpdate.call(this.state)
        } catch (e){ /* ignore */ }

        // set HTML
        this.el.innerHTML = tpl

        // bind events
        this._bindEvents()

        // bind v-models
        this._bindModels()

    // mount nested components (avoid remounting already mounted elements)
    await this._mountNestedComponents()

        // call mounted/updated hooks
        try {
            if (isInitial && typeof this.hooks.mounted === 'function') this.hooks.mounted.call(this.state)
            if (!isInitial && typeof this.hooks.updated === 'function') this.hooks.updated.call(this.state)
        } catch (e){ /* ignore */ }

        return true
    }

    _escape(v){
        if (v == null) return ''
        return String(v)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
    }

    _bindEvents(){
        const el = this.el
        // find elements with attributes starting with data-on-
        const all = el.querySelectorAll('[data-on-click], [data-on-input], [data-on-change], [data-on-submit]')
        all.forEach(node => {
            Array.from(node.attributes).forEach(attr => {
                if (!attr.name.startsWith('data-on-')) return
                const ev = attr.name.slice('data-on-'.length)
                const handler = attr.value.trim()
                if (!handler) return
                const fn = this.methods[handler]
                if (typeof fn === 'function'){
                    const bound = (e) => { fn(e) }
                    node.addEventListener(ev, bound)
                    this._listeners.push({ node, ev, fn: bound })
                }
            })
        })
    }

    _bindModels(){
        const el = this.el
        const nodes = el.querySelectorAll('[data-model]')
        nodes.forEach(node => {
            const prop = node.getAttribute('data-model').trim()
            if (!prop) return

            // set initial value from state
            if (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA' || node.tagName === 'SELECT'){
                if (node.type === 'checkbox'){
                    node.checked = !!this.state[prop]
                } else {
                    node.value = this.state[prop] == null ? '' : this.state[prop]
                }

                // update state when input changes
                const bound = (e) => {
                    const val = node.type === 'checkbox' ? node.checked : node.value
                    this.state[prop] = val
                }
                node.addEventListener('input', bound)
                this._listeners.push({ node, ev: 'input', fn: bound })
            } else {
                // non-input elements: ensure innerText matches
                node.innerText = this.state[prop] == null ? '' : this.state[prop]
            }
        })
    }

    unmount(){
        // call unmounted hook
        try { if (typeof this.hooks.unmounted === 'function') this.hooks.unmounted.call(this.state) } catch(e){}

        // remove event listeners
        this._listeners.forEach(l => {
            try { l.node.removeEventListener(l.ev, l.fn) } catch(e){}
        })
        this._listeners = []

        // remove from app mounted list
        try {
            if (this.app && Array.isArray(this.app._mountedComponents)){
                const idx = this.app._mountedComponents.indexOf(this)
                if (idx !== -1) this.app._mountedComponents.splice(idx, 1)
            }
        } catch(e){}

        // unmark DOM
        try { if (this.el) { this.el.__melodijs_mounted = false; this.el.innerHTML = '' } } catch(e){}
    }

    async _mountNestedComponents(){
        if (!this.app || !this.app.components) return
        const tags = Object.keys(this.app.components)
        for (const tag of tags){
            const nodes = Array.from(this.el.querySelectorAll(tag))
            for (const node of nodes){
                if (node.__melodijs_mounted) continue
                // avoid mounting nodes that are nested inside other custom elements already mounted
                let parent = node.parentElement
                let skip = false
                while(parent){
                    const t = parent.tagName && parent.tagName.toLowerCase()
                    if (t && tags.indexOf(t) !== -1 && parent !== this.el){ skip = true; break }
                    parent = parent.parentElement
                }
                if (skip) continue
                const compDef = this.app.components[tag]
                const comp = new Component(compDef)
                try {
                    await comp.mount(node, this.app)
                    node.__melodijs_mounted = true
                } catch(e){ /* ignore child mount errors */ }
            }
        }
    }
}

// small helper to create app (Vue-like)
function createApp(options){
    return new MelodiJS(options)
}

export { createApp }
