const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const moduleUrl =
  "https://home-assistant.example/ziggo_modem/ziggo-modem-card.js?v=1.7.0";
const js = fs
  .readFileSync(
    path.join(
      __dirname,
      "../../custom_components/ziggo_modem/www/ziggo-modem-card.js",
    ),
    "utf8",
  )
  .replace("import.meta.url", JSON.stringify(moduleUrl));
class MockElement {
  constructor() {
    let html = "";
    this._content = {
      innerHTML: "",
      querySelectorAll: () => [],
      querySelector: () => null,
    };
    this.shadowRoot = {
      querySelector: (name) =>
        name === "style" && html.includes("<style>") ? {} : null,
      getElementById: () => this._content,
      get innerHTML() {
        return html;
      },
      set innerHTML(v) {
        html = v;
      },
    };
    this.isConnected = true;
  }
  attachShadow() {
    return this.shadowRoot;
  }
}
const registered = {};
const context = vm.createContext({
  HTMLElement: MockElement,
  customElements: {
    get: (k) => registered[k],
    define: (k, v) => (registered[k] = v),
  },
  window: {},
  document: { createElement: () => ({}) },
  URL,
  Date,
  Math,
  Number,
  String,
  Array,
  Object,
  Map,
  Promise,
  JSON,
  CustomEvent: class {},
  console,
});
vm.runInContext(js, context);
const card = new registered["ziggo-modem-card"]();
card.setConfig({ type: "custom:ziggo-modem-card", show_chart: false });
card.hass = {
  locale: { language: "nl" },
  states: {
    sensor_ziggo_dummy: { state: "ignore" },
    "sensor.ziggo_modem_modem_status": {
      entity_id: "sensor.ziggo_modem_modem_status",
      state: "Operational",
    },
    "sensor.ziggo_modem_signaalkwaliteit": {
      entity_id: "sensor.ziggo_modem_signaalkwaliteit",
      state: "Goed",
      attributes: { score: 92 },
    },
    "sensor.ziggo_modem_downstream_snr": {
      entity_id: "sensor.ziggo_modem_downstream_snr",
      state: "39.4",
      attributes: { unit_of_measurement: "dB" },
    },
    "binary_sensor.ziggo_modem_internettoegang": {
      entity_id: "binary_sensor.ziggo_modem_internettoegang",
      state: "on",
      attributes: { device_class: "connectivity" },
    },
    "binary_sensor.ziggo_modem_kabelprobleem": {
      entity_id: "binary_sensor.ziggo_modem_kabelprobleem",
      state: "off",
      attributes: { device_class: "problem" },
    },
  },
};
assert.match(card._content.innerHTML, /92 \/ 100/);
assert.match(card._content.innerHTML, /39\.4/);
assert.match(
  card._content.innerHTML,
  /src="https:\/\/home-assistant\.example\/ziggo_modem\/ziggo-modem-device\.webp"/,
);
assert.match(card._content.innerHTML, /data-action="diagnostics"/);
assert.match(card._content.innerHTML, /Online/);
assert.match(card._content.innerHTML, /Sagemcom · DOCSIS · ha-ziggo-modem/);
const modemStatus = card._hass.states["sensor.ziggo_modem_modem_status"];
modemStatus.attributes = { docsis_version: "4.0" };
card.hass = card._hass;
assert.match(
  card._content.innerHTML,
  /Sagemcom · DOCSIS 4\.0 · ha-ziggo-modem/,
);
modemStatus.state = "unavailable";
card.hass = card._hass;
assert.match(card._content.innerHTML, /Sagemcom · DOCSIS · ha-ziggo-modem/);
assert.doesNotMatch(card._content.innerHTML, /DOCSIS 4\.0/);
assert.match(card._content.innerHTML, /Kabelprobleem/);
assert.doesNotMatch(card._content.innerHTML, /Geen geschiedenis beschikbaar/);
const grid = card.getGridOptions();
assert.equal(grid.max_columns, 12);
assert.equal(grid.min_columns, 4);
assert.equal(
  vm.runInContext("escapeHTML(`<img src=x onerror=alert(1)>`)", context),
  "&lt;img src=x onerror=alert(1)&gt;",
);
const registry = [
  {
    platform: "ziggo_modem",
    device_id: "device-a",
    unique_id: "abc_signal_quality",
    entity_id: "sensor.ziggo_a_quality",
  },
  {
    platform: "ziggo_modem",
    device_id: "device-b",
    unique_id: "def_signal_quality",
    entity_id: "sensor.ziggo_b_quality",
  },
];
const selected = vm.runInContext("selectEntities", context)(
  { device_id: "device-b", entities: { ds_snr: "sensor.manual_snr" } },
  { states: {} },
  registry,
);
assert.equal(selected.signal_quality, "sensor.ziggo_b_quality");
assert.equal(selected.ds_snr, "sensor.manual_snr");
const svg = vm.runInContext("graphMarkup", context)(
  [
    { time: 1, value: 35.5 },
    { time: 2, value: 39.4 },
  ],
  vm.runInContext("NL", context),
);
assert.match(svg, /<svg/);
console.log(
  "OK: Ziggo card mock rendering, registry mapping, HTML escaping, history SVG, Sections sizing",
);
