class OpenClashConfigCard extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
    this._pendingOption = null;
    this._pendingMode = null;
    this._pendingMaster = null;
    this._pendingAction = null;
  }

  static getConfigElement() {
    return document.createElement("openclash-config-card-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:openclash-config-card",
      entity: "",
      title: "OpenClash Manager",
      show_dropdown: false,
      show_master_switch: true,
      show_operation_mode: true,
      show_status: true,
      show_version: false,
      show_buttons: true,
    };
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Invalid configuration");
    }

    this._config = {
      title: "OpenClash",
      show_dropdown: false,
      show_master_switch: true,
      show_operation_mode: true,
      show_status: true,
      show_version: false,
      show_buttons: true,
      ...config,
    };

    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.update();
  }

  get hass() {
    return this._hass;
  }

  connectedCallback() {
    this.render();
    this.update();
  }

  getCardSize() {
    return 6;
  }

  render() {
    if (!this._config) return;

    this.innerHTML = `
      <ha-card class="openclash-card">
        <div class="oc-header">
          <button class="oc-icon-button" type="button" title="More info">
            <ha-icon icon="mdi:router-wireless"></ha-icon>
          </button>
          <div class="oc-title-wrap">
            <div class="oc-title"></div>
            <div class="oc-version" style="display:none"></div>
          </div>
          <div class="oc-header-actions">
            <ha-switch class="oc-master-switch" style="display:none"></ha-switch>
            <button class="oc-refresh" type="button" title="Refresh">
              <ha-icon icon="mdi:refresh"></ha-icon>
            </button>
          </div>
        </div>

        <div class="oc-status-bar" style="display:none">
          <div class="oc-status-indicator">
            <span class="oc-status-dot"></span>
            <span class="oc-status-text"></span>
          </div>
          <div class="oc-mode-badge" style="display:none"></div>
        </div>

        <div class="oc-current">
          <div class="oc-current-label">Active config</div>
          <div class="oc-current-value"></div>
        </div>

        <div class="oc-mode-select-wrap" style="display:none">
           <ha-select class="oc-mode-select" naturalMenuWidth fixedMenuPosition label="Operation Mode"></ha-select>
        </div>

        <div class="oc-dropdown-wrap" style="display:none">
          <ha-select class="oc-select" naturalMenuWidth fixedMenuPosition label="Switch Config"></ha-select>
        </div>

        <div class="oc-options"></div>
        
        <div class="oc-actions" style="display:none">
          <button class="oc-btn-action" data-action="restart" title="Restart OpenClash">
            <ha-icon icon="mdi:restart"></ha-icon>
            <span>Restart</span>
          </button>
          <button class="oc-btn-action" data-action="update_subscriptions" title="Update Subscriptions">
            <ha-icon icon="mdi:update"></ha-icon>
            <span>Update Subs</span>
          </button>
          <button class="oc-btn-action" data-action="update_cores" title="Update Cores">
            <ha-icon icon="mdi:cpu-64-bit"></ha-icon>
            <span>Cores</span>
          </button>
        </div>

        <div class="oc-empty">No configs found</div>
      </ha-card>
      <style>
        :host { display: block; }
        .openclash-card {
          overflow: hidden;
          padding-bottom: 8px;
        }
        .oc-header {
          display: flex;
          align-items: center;
          padding: 16px 16px 8px;
          gap: 12px;
        }
        .oc-title-wrap { flex: 1; min-width: 0; }
        .oc-title {
          font-size: 18px;
          font-weight: 600;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .oc-version {
          font-size: 11px;
          color: var(--secondary-text-color);
          margin-top: -2px;
        }
        .oc-header-actions {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .oc-icon-button, .oc-refresh {
          width: 38px;
          height: 38px;
          border-radius: 50%;
          border: none;
          background: var(--secondary-background-color);
          color: var(--primary-text-color);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
        }
        .oc-status-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 16px 12px;
        }
        .oc-status-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          font-weight: 500;
        }
        .oc-status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--disabled-text-color);
        }
        .oc-status-dot.on { background: #4caf50; box-shadow: 0 0 4px #4caf50; }
        .oc-status-dot.off { background: #f44336; }
        
        .oc-mode-badge {
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          padding: 2px 8px;
          border-radius: 10px;
          background: var(--primary-color);
          color: var(--text-primary-color, white);
        }

        .oc-current {
          margin: 0 16px 12px;
          padding: 12px;
          border-radius: 12px;
          background: var(--secondary-background-color);
          border: 1px solid var(--divider-color);
        }
        .oc-current-label { font-size: 11px; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.5px; }
        .oc-current-value { font-size: 16px; font-weight: 600; margin-top: 2px; }

        .oc-mode-select-wrap, .oc-dropdown-wrap { padding: 0 16px 12px; }
        ha-select { width: 100%; }

        .oc-options {
          display: grid;
          gap: 8px;
          padding: 0 16px 8px;
        }
        .oc-option {
          display: flex;
          align-items: center;
          padding: 10px 12px;
          border-radius: 10px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          cursor: pointer;
          transition: all 0.2s;
          gap: 12px;
          text-align: left;
          width: 100%;
        }
        .oc-option:hover { background: var(--secondary-background-color); }
        .oc-option.active {
          border-color: var(--primary-color);
          background: color-mix(in srgb, var(--primary-color) 10%, var(--card-background-color));
        }
        .oc-option-name { flex: 1; font-weight: 500; font-size: 14px; }
        .oc-option ha-icon { color: var(--secondary-text-color); --mdc-icon-size: 20px; }
        .oc-option.active ha-icon { color: var(--primary-color); }

        .oc-actions {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 8px;
          padding: 8px 16px 8px;
          border-top: 1px solid var(--divider-color);
          margin-top: 8px;
        }
        .oc-btn-action {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 4px;
          padding: 8px 4px;
          border-radius: 8px;
          border: none;
          background: transparent;
          color: var(--primary-text-color);
          cursor: pointer;
          font-size: 10px;
          font-weight: 500;
        }
        .oc-btn-action:hover { background: var(--secondary-background-color); }
        .oc-btn-action ha-icon { --mdc-icon-size: 20px; color: var(--secondary-text-color); }
        
        .oc-empty { display: none; padding: 16px; text-align: center; color: var(--secondary-text-color); }
        .oc-empty.visible { display: block; }
      </style>
    `;

    this.querySelector(".oc-icon-button")?.addEventListener("click", () => this._showMoreInfo());
    this.querySelector(".oc-refresh")?.addEventListener("click", () => this._refreshEntity());
    this.querySelector(".oc-master-switch")?.addEventListener("change", (e) => this._toggleMaster(e));
    this.querySelector(".oc-mode-select")?.addEventListener("selected", (e) => this._selectMode(e.target.value));
    this.querySelector(".oc-select")?.addEventListener("selected", (e) => this._selectOption(e.target.value));
    
    this.querySelectorAll(".oc-btn-action").forEach(btn => {
        btn.addEventListener("click", () => this._runAction(btn.dataset.action));
    });
  }

  update() {
    if (!this._hass || !this.isConnected) return;

    const mainEntity = this._getEntity();
    if (!mainEntity) return;

    const related = this._getRelatedEntities(mainEntity.entity_id);
    
    // Title & Version
    this.querySelector(".oc-title").textContent = this._config.title || mainEntity.attributes.friendly_name || "OpenClash";
    const versionEl = this.querySelector(".oc-version");
    if (this._config.show_version && related.version) {
        versionEl.textContent = `v${related.version.state}`;
        versionEl.style.display = "block";
    } else {
        versionEl.style.display = "none";
    }

    // Master Switch
    const masterEl = this.querySelector(".oc-master-switch");
    if (this._config.show_master_switch && related.master) {
        masterEl.checked = related.master.state === "on";
        masterEl.disabled = this._pendingMaster !== null;
        masterEl.style.display = "block";
    } else {
        masterEl.style.display = "none";
    }

    // Status Bar
    const statusBar = this.querySelector(".oc-status-bar");
    if (this._config.show_status && related.status) {
        statusBar.style.display = "flex";
        const dot = this.querySelector(".oc-status-dot");
        const text = this.querySelector(".oc-status-text");
        const isRunning = related.status.state === "on";
        dot.className = `oc-status-dot ${isRunning ? "on" : "off"}`;
        text.textContent = isRunning ? "Running" : "Stopped";
        
        const badge = this.querySelector(".oc-mode-badge");
        if (related.mode) {
            badge.textContent = related.mode.state;
            badge.style.display = "block";
        } else {
            badge.style.display = "none";
        }
    } else {
        statusBar.style.display = "none";
    }

    // Active Config
    this.querySelector(".oc-current-value").textContent = mainEntity.state || "Not selected";

    // Mode Select
    const modeWrap = this.querySelector(".oc-mode-select-wrap");
    if (this._config.show_operation_mode && related.mode) {
        modeWrap.style.display = "block";
        this._updateModeSelect(related.mode);
    } else {
        modeWrap.style.display = "none";
    }

    // Config Select
    const options = mainEntity.attributes.options || [];
    const selectWrap = this.querySelector(".oc-dropdown-wrap");
    if (this._config.show_dropdown && options.length > 0) {
        selectWrap.style.display = "block";
        this._updateConfigSelect(options, mainEntity.state);
    } else {
        selectWrap.style.display = "none";
    }

    // Config Buttons
    if (!this._config.show_dropdown) {
        this._updateOptions(options, mainEntity.state);
    } else {
        this.querySelector(".oc-options").innerHTML = "";
    }

    // Actions
    const actionsWrap = this.querySelector(".oc-actions");
    if (this._config.show_buttons) {
        actionsWrap.style.display = "grid";
        this.querySelectorAll(".oc-btn-action").forEach(btn => {
            const action = btn.dataset.action;
            btn.disabled = !related[action] || this._pendingAction === action;
        });
    } else {
        actionsWrap.style.display = "none";
    }

    this.querySelector(".oc-empty").classList.toggle("visible", options.length === 0);
  }

  _getRelatedEntities(mainId) {
    const states = this._hass.states;
    const base = mainId.replace("select.", "").replace("_config", "");
    
    // Attempt to find siblings by domain and suffix
    const findBySuffix = (domain, suffix) => {
        const potential = `${domain}.${base}_${suffix}`;
        return states[potential] || null;
    };

    return {
        master: findBySuffix("switch", "enable"),
        mode: findBySuffix("select", "operation_mode"),
        status: findBySuffix("binary_sensor", "status"),
        version: findBySuffix("sensor", "version"),
        restart: findBySuffix("button", "restart"),
        update_subscriptions: findBySuffix("button", "update_subscriptions"),
        update_cores: findBySuffix("button", "update_cores"),
    };
  }

  _updateModeSelect(modeEntity) {
    const select = this.querySelector(".oc-mode-select");
    if (!select) return;
    const options = modeEntity.attributes.options || ["rule", "global", "direct"];
    if (select.innerHTML === "" || select.options_count !== options.length) {
        select.innerHTML = "";
        for (const opt of options) {
            const item = document.createElement("mwc-list-item");
            item.value = opt;
            item.textContent = opt.toUpperCase();
            select.appendChild(item);
        }
        select.options_count = options.length;
    }
    select.value = this._pendingMode || modeEntity.state;
    select.disabled = this._pendingMode !== null;
  }

  _updateConfigSelect(options, current) {
    const select = this.querySelector(".oc-select");
    if (!select) return;
    if (select.innerHTML === "" || select.options_count !== options.length) {
        select.innerHTML = "";
        for (const opt of options) {
            const item = document.createElement("mwc-list-item");
            item.value = opt;
            item.textContent = opt;
            select.appendChild(item);
        }
        select.options_count = options.length;
    }
    select.value = this._pendingOption || current;
    select.disabled = this._pendingOption !== null;
  }

  _updateOptions(options, current) {
    const container = this.querySelector(".oc-options");
    if (!container) return;
    container.innerHTML = "";
    for (const option of options) {
      const active = option === current;
      const pending = option === this._pendingOption;
      const button = document.createElement("button");
      button.type = "button";
      button.className = `oc-option${active ? " active" : ""}`;
      button.disabled = this._pendingOption !== null;
      button.innerHTML = `
        <ha-icon icon="${active ? "mdi:check-circle" : "mdi:file-document-outline"}"></ha-icon>
        <div class="oc-option-name">${option}</div>
        ${active ? '<ha-icon icon="mdi:chevron-right" style="opacity:0.5"></ha-icon>' : ""}
      `;
      button.addEventListener("click", () => this._selectOption(option));
      container.appendChild(button);
    }
  }

  async _toggleMaster(ev) {
    const mainEntity = this._getEntity();
    const related = this._getRelatedEntities(mainEntity.entity_id);
    if (!related.master) return;
    
    const turnOn = ev.target.checked;
    this._pendingMaster = turnOn;
    this.update();
    try {
        await this._hass.callService("switch", turnOn ? "turn_on" : "turn_off", {
            entity_id: related.master.entity_id
        });
    } finally {
        this._pendingMaster = null;
        this.update();
    }
  }

  async _selectMode(mode) {
    const mainEntity = this._getEntity();
    const related = this._getRelatedEntities(mainEntity.entity_id);
    if (!related.mode || mode === related.mode.state || this._pendingMode) return;

    this._pendingMode = mode;
    this.update();
    try {
        await this._hass.callService("select", "select_option", {
            entity_id: related.mode.entity_id,
            option: mode
        });
    } finally {
        this._pendingMode = null;
        this.update();
    }
  }

  async _selectOption(option) {
    const entity = this._getEntity();
    if (!entity || option === entity.state || this._pendingOption) return;

    this._pendingOption = option;
    this.update();
    try {
      await this._hass.callService("select", "select_option", {
        entity_id: entity.entity_id,
        option,
      });
    } finally {
      this._pendingOption = null;
      this.update();
    }
  }

  async _runAction(action) {
    const mainEntity = this._getEntity();
    const related = this._getRelatedEntities(mainEntity.entity_id);
    const entity = related[action];
    if (!entity || this._pendingAction) return;

    this._pendingAction = action;
    this.update();
    try {
        await this._hass.callService("button", "press", {
            entity_id: entity.entity_id
        });
    } finally {
        this._pendingAction = null;
        this.update();
    }
  }

  async _refreshEntity() {
    const entity = this._getEntity();
    if (!entity) return;
    await this._hass.callService("homeassistant", "update_entity", { entity_id: entity.entity_id });
  }

  _showMoreInfo() {
    this.dispatchEvent(new CustomEvent("hass-more-info", {
        bubbles: true, composed: true, detail: { entityId: this._getEntityId() }
    }));
  }

  _getEntityId() {
    if (this._config.entity && this._hass.states[this._config.entity]) return this._config.entity;
    const matches = Object.entries(this._hass.states)
      .filter(([id, state]) => id.startsWith("select.") && (id.includes("openclash") || (state.attributes.friendly_name || "").toLowerCase().includes("openclash")))
      .map(([id]) => id);
    return matches[0] || null;
  }

  _getEntity() {
    const id = this._getEntityId();
    return id ? this._hass.states[id] : null;
  }
}

class OpenClashConfigCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._hass && this.querySelector(".entity")) {
        const entities = Object.keys(this._hass.states).filter(id => id.startsWith("select.")).sort();
        const select = this.querySelector(".entity");
        if (select.innerHTML === "") {
            for (const ent of entities) {
                const opt = document.createElement("option");
                opt.value = ent;
                opt.textContent = ent;
                select.appendChild(opt);
            }
            select.value = this._config.entity || "";
        }
    }
  }

  render() {
    this.innerHTML = `
      <div class="card-config">
        <ha-select label="Main Entity (Config Select)" class="entity" .value="${this._config.entity || ""}">
        </ha-select>
        <ha-textfield label="Title" class="title" value="${this._config.title || "OpenClash"}"></ha-textfield>
        
        <div class="switches">
            <ha-formfield label="Show Dropdown for Configs">
              <ha-switch class="show_dropdown" ${this._config.show_dropdown !== false ? "checked" : ""}></ha-switch>
            </ha-formfield>
            <ha-formfield label="Show Master Switch">
              <ha-switch class="show_master_switch" ${this._config.show_master_switch !== false ? "checked" : ""}></ha-switch>
            </ha-formfield>
            <ha-formfield label="Show Operation Mode">
              <ha-switch class="show_operation_mode" ${this._config.show_operation_mode !== false ? "checked" : ""}></ha-switch>
            </ha-formfield>
            <ha-formfield label="Show Status Information">
              <ha-switch class="show_status" ${this._config.show_status !== false ? "checked" : ""}></ha-switch>
            </ha-formfield>
            <ha-formfield label="Show Version">
              <ha-switch class="show_version" ${this._config.show_version ? "checked" : ""}></ha-switch>
            </ha-formfield>
            <ha-formfield label="Show Action Buttons">
              <ha-switch class="show_buttons" ${this._config.show_buttons !== false ? "checked" : ""}></ha-switch>
            </ha-formfield>
        </div>
      </div>
      <style>
        .card-config { display: grid; gap: 16px; padding: 8px 0; }
        .switches { display: grid; gap: 8px; }
        ha-formfield { display: flex; justify-content: space-between; align-items: center; }
        ha-select, ha-textfield { width: 100%; }
      </style>
    `;

    this.querySelectorAll("ha-switch").forEach(sw => {
        sw.addEventListener("change", (e) => {
            this._valueChanged({ [sw.className]: e.target.checked });
        });
    });

    this.querySelector(".entity")?.addEventListener("selected", (e) => {
      this._valueChanged({ entity: e.target.value });
    });
    
    this.querySelector(".title")?.addEventListener("change", (e) => {
      this._valueChanged({ title: e.target.value });
    });
  }

  _valueChanged(changed) {
    const config = { ...this._config, ...changed };
    this.dispatchEvent(new CustomEvent("config-changed", {
      bubbles: true, composed: true, detail: { config }
    }));
  }
}

if (!customElements.get("openclash-config-card")) {
  customElements.define("openclash-config-card", OpenClashConfigCard);
}

if (!customElements.get("openclash-config-card-editor")) {
  customElements.define("openclash-config-card-editor", OpenClashConfigCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "openclash-config-card")) {
  window.customCards.push({
    type: "openclash-config-card",
    name: "OpenClash Manager Card",
    description: "Manage OpenClash configs, modes, and service status from a single card.",
  });
}
