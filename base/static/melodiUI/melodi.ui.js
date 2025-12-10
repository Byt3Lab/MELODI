const MelodiUI = {
    install: function (app, options) {
        // --- m-btn ---
        app.components['m-btn'] = {
            props: {
                variant: { type: String, default: 'primary' }, // primary, secondary, success, danger, warning, info, light, dark
                size: { type: String, default: 'md' }, // sm, md, lg
                block: { type: Boolean, default: false },
                disabled: { type: Boolean, default: false },
                type: { type: String, default: 'button' },
                outline: { type: Boolean, default: false }
            },
            template: `
                <button 
                    :class="['m-btn', 'm-btn-' + variant, 'm-btn-' + size, block ? 'm-btn-block' : '', outline ? 'm-btn-outline-' + variant : '']"
                    :disabled="disabled"
                    :type="type"
                    @click="$emit('click', $event)"
                >
                    <slot></slot>
                </button>
            `
        };

        // --- m-input ---
        app.components['m-input'] = {
            props: {
                modelValue: { type: String, default: '' },
                label: { type: String, default: '' },
                type: { type: String, default: 'text' },
                placeholder: { type: String, default: '' },
                id: { type: String, default: '' },
                error: { type: String, default: '' },
                disabled: { type: Boolean, default: false }
            },
            template: `
                <div class="m-form-group">
                    <label v-if="label" :for="id" class="m-form-label">{{ label }}</label>
                    <input 
                        :id="id"
                        :type="type" 
                        :value="modelValue" 
                        :placeholder="placeholder"
                        :disabled="disabled"
                        :class="['m-form-control', error ? 'is-invalid' : '']"
                        @input="$emit('update:modelValue', $event.target.value)"
                        @change="$emit('change', $event.target.value)"
                        @focus="$emit('focus', $event)"
                        @blur="$emit('blur', $event)"
                    />
                    <div v-if="error" class="m-invalid-feedback">{{ error }}</div>
                </div>
            `
        };

        // --- m-card ---
        app.components['m-card'] = {
            props: {
                title: { type: String, default: '' },
                subtitle: { type: String, default: '' },
                imgTop: { type: String, default: '' }
            },
            template: `
                <div class="m-card">
                    <img v-if="imgTop" :src="imgTop" class="m-card-img-top" alt="Card image">
                    <div v-if="$slots.header || title" class="m-card-header">
                        <slot name="header">
                            <h5 v-if="title" class="m-card-title">{{ title }}</h5>
                            <h6 v-if="subtitle" class="m-card-subtitle">{{ subtitle }}</h6>
                        </slot>
                    </div>
                    <div class="m-card-body">
                        <slot></slot>
                    </div>
                    <div v-if="$slots.footer" class="m-card-footer">
                        <slot name="footer"></slot>
                    </div>
                </div>
            `
        };

        // --- m-modal ---
        app.components['m-modal'] = {
            props: {
                modelValue: { type: Boolean, default: false }, // v-model for visibility
                title: { type: String, default: '' },
                size: { type: String, default: 'md' } // sm, md, lg, xl
            },
            methods: {
                close() {
                    this.$emit('update:modelValue', false);
                    this.$emit('close');
                },
                backdropClick(e) {
                    if (e.target === e.currentTarget) {
                        this.close();
                    }
                }
            },
            template: `
                <div v-if="modelValue" class="m-modal-backdrop" @click="backdropClick">
                    <div :class="['m-modal', 'm-modal-' + size]" role="dialog">
                        <div class="m-modal-content">
                            <div class="m-modal-header">
                                <slot name="header">
                                    <h5 class="m-modal-title">{{ title }}</h5>
                                    <button type="button" class="m-btn-close" @click="close">&times;</button>
                                </slot>
                            </div>
                            <div class="m-modal-body">
                                <slot></slot>
                            </div>
                            <div v-if="$slots.footer" class="m-modal-footer">
                                <slot name="footer">
                                    <button type="button" class="m-btn m-btn-secondary" @click="close">Close</button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            `
        };

        // --- m-navbar ---
        app.components['m-navbar'] = {
            props: {
                brand: { type: String, default: 'Melodi' },
                brandUrl: { type: String, default: '#' },
                variant: { type: String, default: 'light' }, // light, dark
                fixed: { type: String, default: '' } // top, bottom
            },
            data() {
                return {
                    collapsed: true
                };
            },
            methods: {
                toggle() {
                    this.collapsed = !this.collapsed;
                }
            },
            template: `
                <nav :class="['m-navbar', 'm-navbar-' + variant, fixed ? 'm-navbar-fixed-' + fixed : '']">
                    <div class="m-container">
                        <a :href="brandUrl" class="m-navbar-brand">{{ brand }}</a>
                        <button class="m-navbar-toggler" type="button" @click="toggle">
                            <span class="m-navbar-toggler-icon"></span>
                        </button>
                        <div :class="['m-navbar-collapse', collapsed ? 'collapsed' : '']">
                            <slot></slot>
                        </div>
                    </div>
                </nav>
            `
        };

        // --- m-alert ---
        app.components['m-alert'] = {
            props: {
                variant: { type: String, default: 'info' }, // primary, secondary, success, danger, warning, info, light, dark
                dismissible: { type: Boolean, default: false },
                modelValue: { type: Boolean, default: true }
            },
            methods: {
                close() {
                    this.$emit('update:modelValue', false);
                    this.$emit('close');
                }
            },
            template: `
                <div v-if="modelValue" :class="['m-alert', 'm-alert-' + variant, dismissible ? 'm-alert-dismissible' : '']" role="alert">
                    <slot></slot>
                    <button v-if="dismissible" type="button" class="m-btn-close" @click="close">&times;</button>
                </div>
            `
        };
    }
};

export { MelodiUI };