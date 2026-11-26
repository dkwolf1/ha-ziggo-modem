const assert = require("node:assert/strict");
const { test } = require("node:test");
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
      querySelectorAll: () => [],
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
card.setConfig({
  type: "custom:ziggo-modem-card",
  layout: "full",
  show_chart: false,
});
assert.equal(card.getGridOptions().columns, "full");
assert.equal(card.getGridOptions().rows, "auto");
assert.match(card._content.innerHTML, /class="shell is-full /);
assert.doesNotMatch(card._content.innerHTML, /class="shell[^"]*has-motion/);
for (const layout of ["auto", "full", "expanded", "compact"]) {
  card.setConfig({ type: "custom:ziggo-modem-card", layout, animations: true });
  assert.match(card._content.innerHTML, /class="shell[^"]*has-motion/);
}
card.setConfig({
  type: "custom:ziggo-modem-card",
  layout: "compact",
  show_chart: false,
});
assert.equal(card.getGridOptions().columns, 6);
assert.equal(card.getGridOptions().rows, 9);
assert.doesNotMatch(card._content.innerHTML, /class="shell is-full /);
const editor = new registered["ziggo-modem-card-editor"]();
editor.setConfig({ layout: "full", language: "nl" });
assert.match(
  editor.shadowRoot.innerHTML,
  /value="full" selected>Volledige breedte/,
);
assert.match(editor.shadowRoot.innerHTML, /data-key="animations" >Animaties tonen/);
editor.setConfig({ layout: "full", language: "en", animations: true });
assert.match(editor.shadowRoot.innerHTML, /value="full" selected>Full width/);
assert.match(editor.shadowRoot.innerHTML, /data-key="animations" checked>Show animations/);
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
const graphMarkup = vm.runInContext("graphMarkup", context);
const samples = [
  { time: 1, value: 35.5 },
  { time: 2, value: 39.4 },
];
const locale = vm.runInContext("NL", context);
const denseHistory = Array.from({ length: 1000 }, (_, i) => ({
  time: i * 60000,
  value: i === 250 ? 33 : 36 + (i % 2),
}));
assert.match(graphMarkup(samples, locale), /class="chart-plot" tabindex="0"/);
const fullChart = graphMarkup(denseHistory, locale, true, true);
const compactChart = graphMarkup(denseHistory, locale, false, false);
const lineSegments = (chart) =>
  chart.match(/class="chart-trace" vector-effect="non-scaling-stroke" d="([^"]+)"/)[1].match(/L/g).length;
assert.ok(lineSegments(fullChart) <= 85);
assert.ok(lineSegments(compactChart) <= 37);
assert.match(fullChart, /class="chart-range" vector-effect="non-scaling-stroke" d="M/);
assert.match(fullChart, /aria-label="SNR 33–37 dB"/);
assert.match(fullChart, /chart-latest is-fresh/);
assert.doesNotMatch(compactChart, /chart-latest is-fresh/);

test("the chart shows only history for the selected sensor and period", async () => {
  const historyCard = new registered["ziggo-modem-card"]();
  const states = {
    "sensor.first_snr": { state: "35" },
    "sensor.second_snr": { state: "40" },
  };
  const response = (values) => [
    values.map((state, i) => ({
      state,
      last_changed: new Date(i * 60000).toISOString(),
    })),
  ];
  const select = (id) => historyCard.setConfig({
    type: "custom:ziggo-modem-card",
    entities: { ds_snr: id },
  });
  const html = () => historyCard._content.innerHTML;
  select("sensor.first_snr");
  historyCard.hass = { states, locale: { language: "en" } };
  historyCard._mounted = true;
  historyCard._hass.callApi = async () => response(["33", "35"]);
  await historyCard._loadHistory();
  assert.match(html(), /SNR 33–35 dB/);

  let finishFirst;
  let finishSecond;
  const pendingFirst = new Promise((resolve) => { finishFirst = resolve; });
  const pendingSecond = new Promise((resolve) => { finishSecond = resolve; });
  historyCard._hass.callApi = (_method, query) =>
    query.includes("sensor.first_snr") ? pendingFirst : pendingSecond;
  historyCard._lastHistoryRequest = 0;
  const firstRefresh = historyCard._loadHistory();
  select("sensor.second_snr");
  assert.doesNotMatch(html(), /SNR 33–35 dB/);
  finishFirst(response(["31", "32"]));
  await firstRefresh;
  assert.doesNotMatch(html(), /SNR 31–32 dB/);
  finishSecond(response(["39", "40"]));
  await new Promise(setImmediate);
  assert.match(html(), /SNR 39–40 dB/);

  historyCard._hass.callApi = async () => response(["36", "40"]);
  historyCard._chartHours = 168;
  historyCard._render();
  assert.doesNotMatch(html(), /SNR 39–40 dB/);
  await new Promise(setImmediate);
  assert.match(html(), /SNR 36–40 dB/);

  historyCard._lastHistoryRequest = 0;
  historyCard._hass.callApi = async () => { throw new Error("Recorder unavailable"); };
  await historyCard._loadHistory();
  assert.match(html(), /SNR 36–40 dB/);
});
console.log(
  "OK: Ziggo card mock rendering, registry mapping, HTML escaping, history SVG, Sections sizing",
);
