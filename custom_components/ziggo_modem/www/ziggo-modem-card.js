/* Ziggo Modem Neon Card · v1.1.0 · MPL-2.0 · zero third-party dependencies */
// SPDX-License-Identifier: MPL-2.0
const CARD_TYPE = "ziggo-modem-card";
const CARD_IMAGE_URL = new URL("./ziggo-modem-device.webp", import.meta.url)
  .href;
const ALL_KEYS = [
  "status",
  "uptime",
  "signal_quality",
  "ds_snr",
  "ds_power",
  "us_power",
  "ds_rate",
  "us_rate",
  "internet_access",
  "cable_issue",
  "internet_outage",
  "line_stability",
  "api_status",
  "last_successful_update",
  "us_t3",
  "connection_interruptions",
  "failed_updates",
  "ds_uncorrected_ofdm",
];
const DEFAULT_METRICS = [
  "ds_snr",
  "ds_power",
  "us_power",
  "ds_rate",
  "us_rate",
];
const OPTIONAL_METRICS = [
  "us_t3",
  "connection_interruptions",
  "failed_updates",
  "ds_uncorrected_ofdm",
  "line_stability",
  "api_status",
];
const METRIC_ICONS = {
  ds_snr: "〰",
  ds_power: "↓",
  us_power: "↑",
  ds_rate: "⇣",
  us_rate: "⇡",
  us_t3: "⚡",
  connection_interruptions: "↯",
  failed_updates: "↻",
  ds_uncorrected_ofdm: "✳",
  line_stability: "◈",
  api_status: "◎",
};
const NL = {
  title: "Ziggo Modem",
  status: "Status",
  uptime: "Uptime",
  signal_quality: "Signaalkwaliteit",
  ds_snr: "Downstream SNR",
  ds_power: "Downstream power",
  us_power: "Upstream power",
  ds_rate: "Downloadprofiel",
  us_rate: "Uploadprofiel",
  internet_access: "Internettoegang",
  cable_issue: "Kabelprobleem",
  internet_outage: "Internetstoring",
  line_stability: "Lijnstabiliteit",
  api_status: "API-status",
  last_successful_update: "Laatste update",
  us_t3: "T3-time-outs",
  connection_interruptions: "Onderbrekingen",
  failed_updates: "Mislukte updates",
  ds_uncorrected_ofdm: "OFDM-fouten",
  good: "Goed",
  moderate: "Matig",
  bad: "Slecht",
  online: "Online",
  offline: "Offline",
  yes: "Ja",
  no: "Nee",
  unavailable: "Niet beschikbaar",
  diagnostics: "Diagnostiek",
  close: "Sluiten",
  history: "Downstream SNR",
  quality_context:
    "Je modem kan online zijn terwijl de metingen op de kabellijn een lagere signaalscore opleveren.",
  quality_reason_unavailable:
    "De integratie geeft geen reden voor deze score door.",
  history_unavailable: "Geen geschiedenis beschikbaar (Recorder vereist)",
  no_data:
    "Geen Ziggo-entiteiten gevonden. Kies een apparaat in de kaarteditor of vul entities in.",
  editor_title: "Ziggo Neon · kaartinstellingen",
  title_label: "Titel",
  device: "Modem/apparaat",
  autodetect: "Automatisch detecteren",
  layout: "Weergave",
  auto: "Automatisch",
  compact: "Compact",
  expanded: "Uitgebreid",
  full: "Volledige breedte",
  language: "Taal",
  detect: "Automatisch",
  modem: "Modemafbeelding tonen",
  chart: "SNR-grafiek tonen",
  glow: "Lichteffecten gebruiken",
  animations: "Animaties tonen",
  history_period: "Grafiekperiode",
  metrics: "Tegels op de kaart",
  entities: "Geavanceerd: entiteiten handmatig koppelen",
  help: "Sla wijzigingen op met de dashboardeditor.",
  updated: "Bijgewerkt",
  day: "24 uur",
  week: "7 dagen",
  waiting: "Sensoren laden…",
};
const EN = {
  title: "Ziggo Modem",
  status: "Status",
  uptime: "Uptime",
  signal_quality: "Signal quality",
  ds_snr: "Downstream SNR",
  ds_power: "Downstream power",
  us_power: "Upstream power",
  ds_rate: "Download profile",
  us_rate: "Upload profile",
  internet_access: "Internet access",
  cable_issue: "Cable issue",
  internet_outage: "Internet outage",
  line_stability: "Line stability",
  api_status: "API status",
  last_successful_update: "Last update",
  us_t3: "T3 timeouts",
  connection_interruptions: "Interruptions",
  failed_updates: "Failed updates",
  ds_uncorrected_ofdm: "OFDM errors",
  good: "Good",
  moderate: "Moderate",
  bad: "Bad",
  online: "Online",
  offline: "Offline",
  yes: "Yes",
  no: "No",
  unavailable: "Unavailable",
  diagnostics: "Diagnostics",
  close: "Close",
  history: "Downstream SNR",
  quality_context:
    "Your modem can be online while readings on the cable line result in a lower signal score.",
  quality_reason_unavailable:
    "The integration did not provide a reason for this score.",
  history_unavailable: "No history available (Recorder required)",
  no_data:
    "No Ziggo entities found. Select a device or configure entities in the card editor.",
  editor_title: "Ziggo Neon · card settings",
  title_label: "Title",
  device: "Modem/device",
  autodetect: "Auto detect",
  layout: "Layout",
  auto: "Automatic",
  compact: "Compact",
  expanded: "Expanded",
  full: "Full width",
  language: "Language",
  detect: "Automatic",
  modem: "Show modem illustration",
  chart: "Show SNR chart",
  glow: "Enable glow effects",
  animations: "Show animations",
  history_period: "Chart period",
  metrics: "Tiles on the card",
  entities: "Advanced: map entity IDs",
  help: "Save changes using the dashboard editor.",
  updated: "Updated",
  day: "24 hours",
  week: "7 days",
  waiting: "Loading sensors…",
};
const CSS = `
:host { display:block; height:100%; min-width:0; color:var(--primary-text-color,#f6f7fb); }
ha-card { box-sizing:border-box; display:block; height:100%; min-height:0; width:100%; overflow:hidden; container-type:inline-size; color:var(--primary-text-color,#f6f7fb); border-radius:25px; border:1px solid rgba(255,255,255,.15); background:linear-gradient(154deg,#1a1b24 0%,#0a101d 48%,#10111a 100%); box-shadow:0 16px 45px rgba(0,0,0,.20); }
.shell { box-sizing:border-box; min-height:100%; padding:18px; display:flex; flex-direction:column; gap:13px; position:relative; isolation:isolate; }
.shell::before { content:""; pointer-events:none; position:absolute; inset:0; z-index:-1; opacity:.85; background:radial-gradient(ellipse at 8% 35%,rgba(255,115,0,.24),transparent 44%),radial-gradient(ellipse at 96% 5%,rgba(255,128,0,.13),transparent 50%); }
.glow { position:absolute; inset:0; pointer-events:none; z-index:-1; border-radius:25px; box-shadow:inset 0 0 0 1px rgba(255,135,35,.30),inset 0 0 32px rgba(255,123,8,.08); }
.head { display:flex; justify-content:space-between; align-items:center; gap:9px; min-width:0; }
.identity { display:flex; align-items:center; gap:12px; min-width:0; }
.brand { flex:none; display:grid; place-items:center; width:42px; height:42px; background:linear-gradient(135deg,#ffae31,#ff6200); border-radius:13px; font-weight:900; color:#16121a; font-size:26px; box-shadow:0 6px 22px rgba(255,115,0,.24); }
.heading { min-width:0; } .title { font-size:23px; font-weight:760; letter-spacing:-.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.subtitle { color:#b7afaf; font-size:12px; letter-spacing:.2px; }
.hero { display:grid; grid-template-columns:minmax(85px,1fr) minmax(130px,1.25fr) minmax(135px,1fr); gap:12px; align-items:center; }
.hardware { position:relative; height:208px; display:flex; justify-content:center; align-items:flex-end; overflow:visible; }
.hardware::before { content:""; position:absolute; bottom:12px; width:140%; height:52%; border-radius:50%; background:#ff6b00; opacity:.24; filter:blur(34px); }
.hardware img { height:100%; max-width:100%; object-fit:contain; filter:drop-shadow(0 15px 12px rgba(0,0,0,.7)); }
.gauge-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; min-width:0; }
.gauge { --ring:#4cda74; width:min(100%,202px); aspect-ratio:1; position:relative; display:grid; place-items:center; border-radius:50%; box-shadow:0 0 0 1px rgba(255,255,255,.13),0 0 24px rgba(44,241,95,.09); }
.gauge::before { content:""; position:absolute; inset:13px; border-radius:50%; background:radial-gradient(circle at 35% 15%,#252830,#090d14 69%); box-shadow:inset 0 0 0 1px rgba(255,255,255,.06); }
.gauge-ring { position:absolute; inset:0; width:100%; height:100%; fill:none; stroke-width:7; transform:rotate(135deg); }
.gauge-track { stroke:rgba(149,162,173,.2); } .gauge-progress { stroke:var(--ring); }
.gauge-inner { position:relative; display:flex; align-items:center; justify-content:center; flex-direction:column; text-align:center; }
.gauge-overline { font-size:11px; color:#c6ccca; } .gauge-status { font-size:clamp(18px,5cqi,30px); font-weight:800; line-height:1.15; margin:5px 0; }
.gauge-score { color:#d8e6e3; font-size:12px; font-variant-numeric:tabular-nums; }
.status-stack { display:flex; flex-direction:column; gap:7px; min-width:0; }
.status-item { display:flex; align-items:center; justify-content:space-between; gap:6px; border:1px solid rgba(255,255,255,.12); background:rgba(7,11,20,.5); border-radius:11px; padding:9px 10px; font-size:12px; }
.status-label { color:#c8c9d0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.status-value { font-weight:750; white-space:nowrap; font-size:13px; overflow:hidden; text-overflow:ellipsis; }
.good { color:#5af383; } .warn { color:#ffbf62; } .bad { color:#ff6c73; } .muted { color:#a3aab7; }
.metrics { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:8px; }
.metric { grid-column:span 2; padding:10px 11px; border-radius:13px; border:1px solid rgba(255,255,255,.13); background:linear-gradient(145deg,rgba(255,255,255,.078),rgba(0,0,0,.11)); overflow:hidden; min-width:0; }
.metric.wide { grid-column:span 3; }
.metric-title { font-size:11px; line-height:1.3; color:#bec3cb; display:flex; gap:6px; align-items:center; }
.metric-icon { font-weight:900; color:#ffa044; font-size:17px; line-height:1; }
.metric-value { margin-top:5px; font-size:clamp(16px,2.9cqi,22px); line-height:1.2; font-weight:740; font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }
.metric-unit { font-size:12px; font-weight:500; color:#c7cfdb; white-space:nowrap; }
.chart { border-radius:15px; padding:11px 12px 9px; background:rgba(0,0,0,.31); border:1px solid rgba(255,255,255,.12); }
.chart-head { display:flex; align-items:flex-start; gap:8px; justify-content:space-between; margin-bottom:14px; }
.chart-title { display:block; color:#c6cdd6; font-size:12px; font-weight:600; }
.chart-current { display:block; margin-top:3px; font-size:22px; font-variant-numeric:tabular-nums; line-height:1.2; }
.chart-current small { color:#b8c6ce; font-size:12px; font-weight:500; }
.chart-select { font:inherit; font-size:11px; color:inherit; color-scheme:dark; background:#182229; border:1px solid #454750; border-radius:8px; padding:4px 6px; }
.chart-grid { display:grid; grid-template-columns:max-content minmax(0,1fr); gap:6px 9px; }
.chart-axis { color:#aab5c2; font-size:10px; font-variant-numeric:tabular-nums; }
.chart-y { display:flex; flex-direction:column; justify-content:space-between; text-align:right; line-height:1; margin-block:-5px; }
.chart-x { grid-column:2; display:flex; justify-content:space-between; gap:6px; white-space:nowrap; }
.chart-plot { position:relative; min-width:0; height:104px; outline-offset:4px; }
.chart-svg { width:100%; height:100%; display:block; overflow:visible; pointer-events:none; }
.chart-guide,.chart-range,.chart-trace { fill:none; }
.chart-guide { stroke:rgba(190,204,222,.15); }
.chart-range { stroke:#80cfb0; stroke-opacity:.42; }
.chart-trace { stroke:#71dfb0; stroke-width:1.25; stroke-linecap:round; stroke-linejoin:round; }
.chart-latest { position:absolute; width:6px; height:6px; border-radius:50%; background:#a7f6cf; transform:translate(-50%,-50%); pointer-events:none; }
.chart-latest.is-fresh { animation:ziggoSamplePop .95s ease-out; }
.chart-latest.is-fresh::after { content:""; position:absolute; inset:-1px; border:2px solid #a7f6cf; border-radius:inherit; animation:ziggoPulse .95s ease-out both; }
@keyframes ziggoSamplePop { 35% { box-shadow:0 0 12px 4px #8cebbb; } }
@keyframes ziggoPulse { from { opacity:1; transform:scale(1); } to { opacity:0; transform:scale(4.2); } }
.chart-tooltip { position:absolute; z-index:1; top:0; bottom:0; border-left:1px solid rgba(221,240,233,.45); pointer-events:none; }
.chart-tooltip output { position:absolute; top:0; left:6px; padding:5px 7px; border-radius:6px; background:#18262c; color:#e8f7f0; border:1px solid #51696b; font-size:11px; white-space:nowrap; }
.chart-tooltip.is-right output { left:auto; right:6px; }
.chart-empty { display:grid; place-items:center; color:#a4acb8; font-size:12px; height:90px; text-align:center; }
.footer { margin-top:auto; display:flex; align-items:center; justify-content:space-between; gap:12px; padding-top:2px; }
.footer-left { display:flex; align-items:center; gap:8px; min-width:0; font-size:11px; color:#b8bbca; }
.dot { display:inline-block; height:8px; width:8px; background:#52db73; border-radius:50%; box-shadow:0 0 8px rgba(69,250,106,.4); flex:none; } .dot.bad { background:#ff656e;box-shadow:0 0 8px rgba(255,101,110,.4); } .dot.muted { background:#8b919e;box-shadow:none; } .dot.warn { background:#ffb044;box-shadow:0 0 8px rgba(255,176,68,.4); }
.has-motion .dot.good { position:relative; }
.has-motion .dot.good::after { content:""; position:absolute; inset:0; border:1px solid #79f69c; border-radius:inherit; animation:ziggoOnlinePulse 3s ease-out infinite; }
.shell.has-motion:not(.no-effects)::after { content:""; position:absolute; inset:0 14px auto; height:3px; pointer-events:none; border-radius:6px; background:linear-gradient(90deg,transparent,#ff9d3c 42%,#ffe1a6 50%,#ff9d3c 58%,transparent) 150% 0 / 45% 100% no-repeat; filter:drop-shadow(0 0 5px #f88e31); animation:ziggoEdgeSweep 5s ease-in-out infinite; }
@keyframes ziggoOnlinePulse { 0% { opacity:.95; transform:scale(1); } 50%,100% { opacity:0; transform:scale(3); } }
@keyframes ziggoEdgeSweep { 0% { background-position:-85% 0; opacity:0; } 13%,55% { opacity:1; } 70%,100% { background-position:185% 0; opacity:0; } }
.small-button { font:inherit; color:#f1f0f4; padding:8px 11px; border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.09); border-radius:11px; cursor:pointer; font-size:12px; white-space:nowrap; }
.small-button:hover,.small-button:focus-visible { background:rgba(255,136,0,.25); }
.alert { border:1px solid rgba(249,185,78,.25); color:#ffcb80; background:rgba(255,130,13,.09); border-radius:9px; padding:11px; font-size:12px; }
.diagnostics-dialog { box-sizing:border-box; width:min(440px,calc(100% - 32px)); max-height:calc(100% - 32px); padding:18px; color:#f6f7fb; background:#181b24; border:1px solid rgba(255,255,255,.2); border-radius:18px; }
.diagnostics-dialog::backdrop { background:rgba(0,0,0,.6); }
.diagnostics-header { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px; }
.diagnostics-header h2 { margin:0; font-size:18px; }
.quality-details { margin-bottom:12px; overflow-wrap:anywhere; }
.quality-details h3 { margin:0 0 6px; font-size:15px; }
.quality-details p { margin:0 0 6px; font-size:13px; }
.quality-details [data-quality-context] { color:#bec3cb; }
.details { display:grid; grid-template-columns:repeat(auto-fit,minmax(min(132px,100%),1fr)); gap:7px; }
.details .metric { grid-column:auto; }
.shell.no-modem .hero { grid-template-columns:minmax(140px,1fr) minmax(160px,1fr); }
.shell.no-effects .glow,.shell.no-effects .hardware::before { display:none; }
@media(prefers-reduced-motion:reduce) {
  .chart-latest.is-fresh { animation:none; }
  .chart-latest.is-fresh::after,.has-motion .dot.good::after,.shell.has-motion:not(.no-effects)::after { display:none; }
}
@container (max-width:620px) { .shell.no-modem .hero {grid-template-columns:1fr;} .shell { padding:13px; gap:10px; } .title { font-size:19px; } .hero { grid-template-columns:120px 1fr; } .hardware { height:150px; } .gauge { width:158px; } .status-stack { grid-column:1/-1; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); } .metric { grid-column:span 3; } .metric.wide { grid-column:span 3; } .gauge-status { font-size:22px; } .details { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@container (max-width:380px) { .hero { grid-template-columns:1fr 1fr; gap:5px; } .hardware { height:125px; } .gauge { width:min(100%,137px); } .gauge::before { inset:9px; } .status-stack { grid-template-columns:1fr 1fr; } .status-item { padding:8px; } .status-value { font-size:11px; } .status-label { font-size:10px; } .brand { height:35px; width:35px; font-size:22px; } .metric-value { font-size:16px; } .chart-plot { height:88px; } .footer-left { font-size:10px; } }
.shell.is-compact .hero { grid-template-columns:78px 1fr; } .shell.is-compact .hardware { height:120px; } .shell.is-compact .gauge { width:130px; } .shell.is-compact .gauge::before { inset:9px; } .shell.is-compact .status-stack { grid-column:1/-1; display:grid; grid-template-columns:1fr 1fr; } .shell.is-compact .metric { grid-column:span 3; } .shell.is-compact .gauge-status { font-size:20px; }
@container (min-width:760px) {
  .shell.is-full { padding:20px; gap:16px; }
  .is-full .hero { grid-template-columns:120px 180px minmax(0,1fr); gap:20px; }
  .shell.is-full.no-modem .hero { grid-template-columns:180px minmax(0,1fr); }
  .is-full .hardware { height:150px; }
  .is-full .gauge { width:min(100%,166px); }
  .is-full .status-stack { display:grid; width:100%; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }
  .is-full .status-item { flex-direction:column; align-items:flex-start; padding:10px 13px; }
  .is-full .status-value { font-size:16px; max-width:100%; }
  .is-full .metrics { grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); }
  .is-full .metrics > .metric { grid-column:auto; }
  .is-full .chart { padding:14px 16px 12px; }
  .is-full .chart-title { font-size:14px; }
  .is-full .chart-axis { font-size:11px; }
  .is-full .chart-plot { height:clamp(138px,15cqi,190px); }
  .is-full .chart-empty { height:clamp(150px,20cqi,240px); }
}
`;
const EDITOR_CSS = `
:host { display:block; color:var(--primary-text-color); } .form { display:grid; gap:13px; padding:9px 0; } h3 { margin:0; font-size:18px; } label { display:grid; gap:5px; font-size:13px; } input,select { box-sizing:border-box; font:inherit; color:var(--primary-text-color); background:var(--card-background-color); border:1px solid var(--divider-color,#a2a2a2); border-radius:8px; min-height:38px; padding:7px; width:100%; } select option { background:var(--card-background-color); } .check { display:flex; gap:9px; align-items:center; } .check input { width:18px; min-height:unset; height:18px; } .options { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px; } details { padding:9px; border:1px solid var(--divider-color); border-radius:8px; } summary { cursor:pointer; } .tip { opacity:.65; font-size:12px; } .pairs { display:grid; gap:7px; margin-top:12px; }`;
const ENTITY_SUFFIXES = {
  status: ["modem_status", "status"],
  uptime: ["uptime"],
  signal_quality: ["signaalkwaliteit", "signal_quality"],
  ds_snr: ["downstream_snr"],
  ds_power: ["downstream_power"],
  us_power: ["upstream_power"],
  ds_rate: ["download_profiel", "download_profile"],
  us_rate: ["upload_profiel", "upload_profile"],
  internet_access: ["internettoegang", "internet_access"],
  cable_issue: ["kabelprobleem", "cable_issue"],
  internet_outage: ["internet_storing", "internet_outage"],
  line_stability: ["lijnstabiliteit", "line_stability"],
  api_status: ["api_status"],
  last_successful_update: [
    "laatste_succesvolle_update",
    "last_successful_update",
  ],
  us_t3: ["upstream_t3_timeouts", "upstream_t3"],
  connection_interruptions: [
    "verbindingsonderbrekingen",
    "connection_interruptions",
  ],
  failed_updates: ["mislukte_updates", "failed_updates"],
  ds_uncorrected_ofdm: ["ds_errors_ofdm"],
};
let registryPromise;
async function getRegistry(hass) {
  if (!registryPromise) {
    registryPromise = hass
      .callWS({ type: "config/entity_registry/list" })
      .catch((error) => {
        registryPromise = undefined;
        throw error;
      });
  }
  return registryPromise;
}
function escapeHTML(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
}
function localeFor(config, hass) {
  return config?.language === "en" ||
    (config?.language !== "nl" &&
      String(hass?.locale?.language || "nl").startsWith("en"))
    ? EN
    : NL;
}
function isAvailable(state) {
  return (
    state &&
    !["unknown", "unavailable", "none", ""].includes(
      String(state.state).toLowerCase(),
    )
  );
}
function numberOrNull(value) {
  if (value === undefined || value === null || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}
function displayValue(state) {
  return isAvailable(state) ? String(state.state) : "—";
}
function scoreStatus(score) {
  if (score === null) return "muted";
  return score >= 80 ? "good" : score >= 50 ? "warn" : "bad";
}
function statusClass(value) {
  if (value === null || value === undefined || value === "—") return "muted";
  const v = String(value).trim().toLowerCase();
  if (
    [
      "online",
      "connected",
      "operational",
      "up",
      "goed",
      "good",
      "stable",
      "stabiel",
      "ok",
      "yes",
      "ja",
      "true",
      "on",
    ].includes(v)
  )
    return "good";
  if (
    [
      "offline",
      "disconnected",
      "down",
      "bad",
      "slecht",
      "failed",
      "error",
      "false",
      "no",
      "nee",
      "off",
    ].includes(v)
  )
    return "bad";
  return "warn";
}
function friendlyState(state, kind, lang) {
  if (!isAvailable(state)) return "—";
  if (
    state.attributes?.device_class &&
    state.entity_id.startsWith("binary_sensor.")
  ) {
    const on = state.state === "on";
    return (kind === "internet_access" ? on : !on)
      ? kind === "internet_access"
        ? lang.yes
        : lang.no
      : kind === "internet_access"
        ? lang.no
        : lang.yes;
  }
  return String(state.state);
}
function binaryClass(state, kind) {
  if (!isAvailable(state)) return "muted";
  const on = state.state === "on";
  return (kind === "internet_access" ? on : !on) ? "good" : "bad";
}
function timeDisplay(state, lang) {
  if (!isAvailable(state)) return "—";
  const date = new Date(state.state);
  if (Number.isNaN(date.getTime())) return displayValue(state);
  return date.toLocaleTimeString(lang === NL ? "nl-NL" : "en-GB", {
    hour: "2-digit",
    minute: "2-digit",
  });
}
function selectEntities(config, hass, registry) {
  const mappings = {};
  const entries = (Array.isArray(registry) ? registry : []).filter(
    (e) => e.platform === "ziggo_modem" && e.entity_id,
  );
  const devices = new Map();
  for (const entry of entries) {
    const group =
      entry.device_id ||
      String(entry.unique_id || "")
        .split("_")
        .slice(0, -1)
        .join("_") ||
      "default";
    if (!devices.has(group)) devices.set(group, []);
    devices.get(group).push(entry);
  }
  const deviceId =
    config.device_id && devices.has(config.device_id)
      ? config.device_id
      : devices.keys().next().value;
  const deviceEntries = devices.get(deviceId) || [];
  const allowFallback = !entries.length;
  for (const key of ALL_KEYS) {
    const record = deviceEntries.find((e) =>
      String(e.unique_id || "").endsWith(`_${key}`),
    );
    if (record) mappings[key] = record.entity_id;
    if (!mappings[key] && allowFallback) {
      const domain =
        key.includes("access") ||
        key.includes("issue") ||
        key === "internet_outage"
          ? "binary_sensor"
          : "sensor";
      const candidates = Object.keys(hass.states || {}).filter(
        (id) =>
          id.startsWith(`${domain}.`) &&
          (id.includes("ziggo") || id.includes("sagemcom")),
      );
      for (const suffix of ENTITY_SUFFIXES[key] || [key]) {
        const match = candidates.find((id) => id.endsWith(`_${suffix}`));
        if (match) {
          mappings[key] = match;
          break;
        }
      }
    }
  }
  for (const [key, entityId] of Object.entries(config.entities || {})) {
    if (
      ALL_KEYS.includes(key) &&
      typeof entityId === "string" &&
      entityId.trim()
    )
      mappings[key] = entityId.trim();
  }
  return mappings;
}
function historyLanguage(locale) {
  return locale === NL ? "nl-NL" : "en-GB";
}

function graphMarkup(samples, locale, full, animateLatest) {
  if (samples.length < 2)
    return `<div class="chart-empty">${escapeHTML(locale.history_unavailable)}</div>`;
  const first = samples[0];
  const latest = samples[samples.length - 1];
  const duration = latest.time - first.time || 1;
  const limit = full ? 84 : 36;
  const buckets = new Map();
  let min = Infinity;
  let max = -Infinity;
  for (const { time, value } of samples) {
    min = Math.min(min, value);
    max = Math.max(max, value);
    const index = Math.min(limit - 1, Math.floor((time - first.time) / duration * limit));
    const bucket = buckets.get(index) || {
      count: 0, offset: 0, sum: 0, min: value, max: value,
    };
    bucket.count++;
    bucket.offset += time - first.time;
    bucket.sum += value;
    bucket.min = Math.min(bucket.min, value);
    bucket.max = Math.max(bucket.max, value);
    buckets.set(index, bucket);
  }
  const padding = Math.max(0.5, (max - min) * 0.16);
  const low = Math.floor((min - padding) * 2) / 2;
  const high = Math.ceil((max + padding) * 2) / 2;
  const x = (time) => ((time - first.time) / duration * 700).toFixed(1);
  const y = (value) => ((high - value) / (high - low) * 100).toFixed(1);
  const trend = Array.from(buckets.values(), (b) => ({
    time: first.time + b.offset / b.count,
    value: b.sum / b.count,
  }));
  const path = [first, ...trend, latest]
    .map((p, i) => `${i ? "L" : "M"}${x(p.time)},${y(p.value)}`)
    .join(" ");
  const extrema = [];
  for (const [index, bucket] of Array.from(buckets.values()).entries()) {
    const { time, value: average } = trend[index];
    const lowPoint = average - bucket.min >= 0.9 ? bucket.min : average;
    const highPoint = bucket.max - average >= 0.9 ? bucket.max : average;
    if (lowPoint !== highPoint) {
      extrema.push(`M${x(time)},${y(lowPoint)}V${y(highPoint)}`);
    }
  }
  const language = historyLanguage(locale);
  const number = new Intl.NumberFormat(language, { maximumFractionDigits: 2 });
  const dateOptions = { day: "2-digit", month: "short" };
  const timeOptions = { hour: "2-digit", minute: "2-digit" };
  const start = new Date(first.time);
  const end = new Date(latest.time);
  const dateTimeOptions = { ...dateOptions, ...timeOptions };
  const endOptions = start.toDateString() === end.toDateString() ? timeOptions : dateTimeOptions;
  return `<div class="chart-grid">
    <div class="chart-axis chart-y" aria-hidden="true"><span>${number.format(high)}</span><span>${number.format((low + high) / 2)}</span><span>${number.format(low)}</span></div>
    <div class="chart-plot" tabindex="0" role="group" aria-label="SNR ${number.format(min)}–${number.format(max)} dB">
      <svg class="chart-svg" viewBox="0 0 700 100" preserveAspectRatio="none" aria-hidden="true">
        <path class="chart-guide" vector-effect="non-scaling-stroke" d="M0,0H700 M0,50H700 M0,100H700"/>
        <path d="${path} L${x(latest.time)},100 L0,100 Z" fill="#71dfb0" fill-opacity=".045"/>
        <path class="chart-range" vector-effect="non-scaling-stroke" d="${extrema.join(" ")}"/>
        <path class="chart-trace" vector-effect="non-scaling-stroke" d="${path}"/>
      </svg>
      <span class="chart-latest${animateLatest ? " is-fresh" : ""}" style="left:${Number(x(latest.time)) / 7}%;top:${y(latest.value)}%" aria-hidden="true"></span>
      <div class="chart-tooltip" hidden><output></output></div>
    </div>
    <div class="chart-axis chart-x" aria-hidden="true"><span>${escapeHTML(start.toLocaleString(language, dateTimeOptions))}</span><span>${escapeHTML(end.toLocaleString(language, endOptions))}</span></div>
  </div>`;
}

function bindChart(plot, samples, locale) {
  const tooltip = plot.querySelector(".chart-tooltip");
  const output = tooltip.querySelector("output");
  const start = samples[0].time;
  const duration = samples[samples.length - 1].time - start || 1;
  const date = new Intl.DateTimeFormat(historyLanguage(locale), { dateStyle: "short", timeStyle: "short" });
  const number = new Intl.NumberFormat(historyLanguage(locale), { maximumFractionDigits: 6 });
  let index = samples.length - 1;
  const show = (next) => {
    index = next;
    const sample = samples[index];
    const position = (sample.time - start) / duration * 100;
    tooltip.style.left = `${position}%`;
    tooltip.classList.toggle("is-right", position > 50);
    const label = `${number.format(sample.value)} dB · ${date.format(sample.time)}`;
    if (output.textContent !== label) output.textContent = label;
    tooltip.hidden = false;
  };
  const pick = (event) => {
    const bounds = plot.getBoundingClientRect();
    const target = start + (event.clientX - bounds.left) / bounds.width * duration;
    let left = 0;
    let right = samples.length - 1;
    while (left < right) {
      const middle = Math.floor((left + right) / 2);
      if (samples[middle].time < target) left = middle + 1;
      else right = middle;
    }
    if (left > 0 && target - samples[left - 1].time < samples[left].time - target) left--;
    show(left);
  };
  plot.addEventListener("pointermove", (event) => {
    if (event.pointerType === "mouse") pick(event);
  });
  plot.addEventListener("click", pick);
  plot.addEventListener("pointerleave", (event) => {
    if (event.pointerType === "mouse") tooltip.hidden = true;
  });
  plot.addEventListener("blur", () => { tooltip.hidden = true; });
  plot.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      tooltip.hidden = true;
    } else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      const next = tooltip.hidden ? index : index + (event.key === "ArrowLeft" ? -1 : 1);
      show(Math.max(0, Math.min(samples.length - 1, next)));
    }
  });
}

class ZiggoModemCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._registry = [];
    this._history = { key: "", samples: [] };
    this._chartHours = 24;
    this._lastHistoryRequest = 0;
    this._historyRequestKey = "";
    this._lastSignature = "";
    this._mounted = false;
    this._registryLoaded = false;
  }
  static getStubConfig() {
    return {
      type: `custom:${CARD_TYPE}`,
      title: "Ziggo Modem",
      layout: "auto",
      show_modem: true,
      show_chart: true,
      glow: true,
      animations: false,
      metrics: [...DEFAULT_METRICS],
    };
  }
  static getConfigElement() {
    return document.createElement("ziggo-modem-card-editor");
  }
  setConfig(config) {
    if (!config || config.type !== `custom:${CARD_TYPE}`)
      throw new Error(`Expected type: custom:${CARD_TYPE}`);
    const metrics = Array.isArray(config.metrics)
      ? config.metrics.filter(
          (x) => DEFAULT_METRICS.includes(x) || OPTIONAL_METRICS.includes(x),
        )
      : DEFAULT_METRICS;
    this._config = { ...ZiggoModemCard.getStubConfig(), ...config, metrics };
    this._lastSignature = "";
    this._render();
    this._loadRegistry();
  }
  set hass(hass) {
    this._hass = hass;
    this._loadRegistry();
    this._render();
    this._loadHistory();
  }
  getCardSize() {
    return this._config?.layout === "compact" ? 8 : 12;
  }
  getGridOptions() {
    if (this._config?.layout === "full") {
      return { columns: "full", rows: "auto", min_columns: 4 };
    }
    return {
      columns: this._config?.layout === "compact" ? 6 : 12,
      rows: this._config?.layout === "compact" ? 9 : 12,
      min_columns: 4,
      max_columns: 12,
      min_rows: 6,
      max_rows: 18,
    };
  }
  connectedCallback() {
    this._mounted = true;
    this._loadRegistry();
    this._loadHistory();
  }
  disconnectedCallback() {
    this._mounted = false;
  }
  async _loadRegistry() {
    if (
      this._registryLoaded ||
      this._loadingRegistry ||
      !this._hass ||
      !this._config ||
      !this._mounted
    )
      return;
    this._loadingRegistry = true;
    try {
      const list = await getRegistry(this._hass);
      if (!this._mounted) return;
      this._registry = list;
      this._registryLoaded = true;
      this._lastSignature = "";
      this._render();
      this._loadHistory();
    } catch {
      this._registry = [];
      this._registryLoaded = true;
      this._render();
    } finally {
      this._loadingRegistry = false;
    }
  }
  _resolve() {
    return selectEntities(
      this._config,
      this._hass || { states: {} },
      this._registry,
    );
  }
  async _loadHistory() {
    if (
      !this._mounted ||
      !this._config?.show_chart ||
      !this._hass?.callApi ||
      this._inHistory
    )
      return;
    const id = this._resolve().ds_snr;
    if (!id) return;
    const hours = this._chartHours;
    const key = `${id}:${hours}`;
    if (
      key === this._historyRequestKey &&
      Date.now() - this._lastHistoryRequest < 300000
    )
      return;
    const previousLatest = key === this._history.key
      ? this._history.samples.at(-1)?.time
      : undefined;
    this._historyRequestKey = key;
    this._lastHistoryRequest = Date.now();
    this._inHistory = true;
    const now = new Date(),
      start = new Date(now.getTime() - hours * 3600000);
    const query = `history/period/${encodeURIComponent(start.toISOString())}?filter_entity_id=${encodeURIComponent(id)}&end_time=${encodeURIComponent(now.toISOString())}&minimal_response=1&no_attributes=1`;
    const isCurrent = () =>
      this._mounted &&
      this._config.show_chart &&
      hours === this._chartHours &&
      id === this._resolve().ds_snr;
    try {
      const result = await this._hass.callApi("GET", query);
      if (!isCurrent()) return;
      const list = Array.isArray(result?.[0]) ? result[0] : [];
      const samples = list
        .map((s) => ({
          time: new Date(s?.last_changed || s?.last_updated).getTime(),
          value: numberOrNull(s?.state),
        }))
        .filter((s) => s.value !== null && Number.isFinite(s.time))
        .sort((a, b) => a.time - b.time);
      this._history = { key, samples };
      this._freshHistory =
        previousLatest !== undefined && samples.at(-1)?.time > previousLatest;
    } catch {
      // Keep the last successful series when Recorder is temporarily unavailable.
    } finally {
      this._inHistory = false;
      if (!isCurrent()) this._historyRequestKey = "";
      this._lastSignature = "";
      this._render();
    }
  }
  _state(key) {
    const id = this._resolve()[key];
    return id ? this._hass.states[id] : undefined;
  }
  _metric(key, locale) {
    const state = this._state(key),
      value = displayValue(state),
      unit = state?.attributes?.unit_of_measurement || "";
    const width = ["ds_rate", "us_rate"].includes(key) ? " wide" : "";
    return `<div class="metric${width}" title="${escapeHTML(state?.entity_id || locale.unavailable)}"><div class="metric-title"><span class="metric-icon" aria-hidden="true">${METRIC_ICONS[key] || "•"}</span>${escapeHTML(locale[key] || key)}</div><div class="metric-value">${escapeHTML(value)}${value !== "—" && unit ? ` <span class="metric-unit">${escapeHTML(unit)}</span>` : ""}</div></div>`;
  }
  _statusItem(key, value, tone, locale) {
    return `<div class="status-item"><span class="status-label">${escapeHTML(locale[key] || key)}</span><span class="status-value ${tone}">${escapeHTML(value)}</span></div>`;
  }
  _render() {
    if (!this._hass || !this._config || !this.isConnected) return;
    const m = this._resolve(),
      locale = localeFor(this._config, this._hass);
    const history = this._history.key === `${m.ds_snr}:${this._chartHours}`
      ? this._history.samples
      : [];
    const statusState = this._hass.states[m.status];
    const reportedDocsis = statusState?.attributes?.docsis_version;
    const docsisVersion =
      isAvailable(statusState) &&
      typeof reportedDocsis === "string" &&
      /^[0-9]+(?:\.[0-9]+)*$/.test(reportedDocsis)
        ? reportedDocsis
        : "";
    const quality = this._hass.states[m.signal_quality];
    const reasonAttribute =
      quality?.attributes?.reden ?? quality?.attributes?.reason;
    const qualityReason =
      typeof reasonAttribute === "string" ? reasonAttribute.trim() : "";
    const score = numberOrNull(quality?.attributes?.score);
    const showQualityDetails =
      isAvailable(quality) && (score !== null || Boolean(qualityReason));
    const selected = Object.values(m).map((id) => [
      id,
      this._hass.states[id]?.state,
      this._hass.states[id]?.last_updated,
      this._hass.states[id]?.attributes?.score,
    ]);
    const signature = JSON.stringify([
      this._config,
      locale.diagnostics,
      selected,
      qualityReason,
      docsisVersion,
      this._chartHours,
      history.length,
      this._lastHistoryRequest,
    ]);
    if (signature === this._lastSignature) return;
    this._lastSignature = signature;
    if (!this.shadowRoot.querySelector("style")) {
      this.shadowRoot.innerHTML = `<style>${CSS}</style><div id="content"></div>
        <dialog class="diagnostics-dialog" aria-labelledby="diagnostics-title">
          <form method="dialog" class="diagnostics-header">
            <h2 id="diagnostics-title"></h2>
            <button class="small-button" type="submit" autofocus></button>
          </form>
          <section class="quality-details" hidden>
            <h3></h3>
            <p data-quality-reason></p>
            <p data-quality-context></p>
          </section>
          <div class="details"></div>
        </dialog>`;
      this.shadowRoot.querySelector("dialog")?.addEventListener("close", () => {
        this.shadowRoot.querySelector('[data-action="diagnostics"]')?.focus();
      });
    }
    const content = this.shadowRoot.getElementById("content");
    const scoreClamped =
      score === null ? null : Math.min(100, Math.max(0, score));
    const visibleScore = scoreClamped === null ? 0 : scoreClamped * 0.75;
    const previousScore = this._gaugeEntity === m.signal_quality
      ? this._gaugeScore
      : undefined;
    this._gaugeScore = visibleScore;
    this._gaugeEntity = m.signal_quality;
    const animate =
      this._config.animations === true &&
      !window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const freshHistory = this._freshHistory;
    this._freshHistory = false;
    const tone = scoreStatus(scoreClamped),
      ring =
        tone === "bad" ? "#ff656e" : tone === "warn" ? "#ffb044" : "#59e77c";
    const qualValue = displayValue(quality);
    const rawStatus = displayValue(statusState);
    const healthy = ["operational", "online", "up", "connected"].includes(
      rawStatus.toLowerCase(),
    );
    const statusValue = healthy
      ? locale.online
      : ["down", "offline", "disconnected"].includes(rawStatus.toLowerCase())
        ? locale.offline
        : rawStatus;
    const internet = this._state("internet_access"),
      cable = this._state("cable_issue");
    const healthTone =
      (isAvailable(internet) && internet.state === "off") ||
      (isAvailable(cable) && cable.state === "on")
        ? "bad"
        : statusClass(statusValue);
    const timestamp = this._state("last_successful_update");
    const snrState = this._hass.states[m.ds_snr];
    const snr = isAvailable(snrState) ? numberOrNull(snrState.state) : null;
    const snrDisplay = snr === null
      ? "—"
      : new Intl.NumberFormat(historyLanguage(locale), {
          maximumFractionDigits: 2,
        }).format(snr);
    const metrics = (this._config.metrics || []).filter((key) => m[key]);
    const diagnostics = OPTIONAL_METRICS.filter((key) => m[key]);
    const hasDiagnostics = showQualityDetails || diagnostics.length > 0;
    const dialog = this.shadowRoot.querySelector("dialog");
    if (dialog) {
      dialog.querySelector("h2").textContent = locale.diagnostics;
      dialog.querySelector("button").textContent = locale.close;
      const qualityDetails = dialog.querySelector(".quality-details");
      qualityDetails.hidden = !showQualityDetails;
      qualityDetails.querySelector("h3").textContent = locale.signal_quality;
      qualityDetails.querySelector("[data-quality-reason]").textContent =
        qualityReason || locale.quality_reason_unavailable;
      qualityDetails.querySelector("[data-quality-context]").textContent =
        locale.quality_context;
      dialog.querySelector(".details").innerHTML = diagnostics
        .map((key) => this._metric(key, locale))
        .join("");
      if (dialog.open && !hasDiagnostics) dialog.close();
    }
    const hasData = Boolean(m.status || m.signal_quality || m.ds_snr);
    const full = this._config.layout === "full";
    const layoutClass = full
      ? "is-full"
      : this._config.layout === "compact"
        ? "is-compact"
        : "";
    const focusedChartControl = this.shadowRoot.activeElement?.matches(".chart-plot, .chart-select")
      ? this.shadowRoot.activeElement.className
      : "";
    content.innerHTML = `<ha-card><div class="shell ${this._config.show_modem ? "" : "no-modem "}${layoutClass} ${this._config.glow ? "" : "no-effects "}${this._config.animations === true ? "has-motion" : ""}">
      <div class="glow"></div>
      <header class="head"><div class="identity"><span class="brand" aria-hidden="true">Z</span><div class="heading"><div class="title">${escapeHTML(this._config.title || locale.title)}</div><div class="subtitle">Sagemcom · DOCSIS${docsisVersion ? ` ${escapeHTML(docsisVersion)}` : ""} · ha-ziggo-modem</div></div></div></header>
      ${
        hasData
          ? `<section class="hero">
        ${this._config.show_modem ? `<div class="hardware"><img src="${escapeHTML(CARD_IMAGE_URL)}" alt="Ziggo modem" loading="lazy"></div>` : ""}
        <div class="gauge-wrap"><div class="gauge" style="--ring:${ring};">
          <svg class="gauge-ring" viewBox="0 0 100 100" aria-hidden="true">
            <circle class="gauge-track" cx="50" cy="50" r="46" pathLength="100" stroke-dasharray="75 25"/>
            <circle class="gauge-progress" cx="50" cy="50" r="46" pathLength="100" stroke-dasharray="${visibleScore} 100"/>
          </svg>
          <div class="gauge-inner"><span class="gauge-overline">${escapeHTML(locale.signal_quality)}</span><span class="gauge-status ${tone}">${escapeHTML(qualValue)}</span><span class="gauge-score">${scoreClamped === null ? "—" : scoreClamped + " / 100"}</span></div></div></div>
        <div class="status-stack">
          ${this._statusItem("status", statusValue, statusClass(statusValue), locale)}
          ${this._statusItem("uptime", displayValue(this._state("uptime")), "", locale)}
          ${this._statusItem("internet_access", friendlyState(internet, "internet_access", locale), binaryClass(internet, "internet_access"), locale)}
          ${this._statusItem("cable_issue", friendlyState(cable, "cable_issue", locale), binaryClass(cable, "cable_issue"), locale)}
        </div>
      </section>
      ${metrics.length ? `<section class="metrics" aria-label="DOCSIS">${metrics.map((key) => this._metric(key, locale)).join("")}</section>` : ""}
      ${this._config.show_chart ? `<section class="chart"><div class="chart-head"><div><span class="chart-title">${escapeHTML(locale.history)}</span><strong class="chart-current">${snrDisplay}${snr === null ? "" : " <small>dB</small>"}</strong></div><select class="chart-select" data-action="period" aria-label="${escapeHTML(locale.history_period)}"><option value="24" ${this._chartHours === 24 ? "selected" : ""}>${escapeHTML(locale.day)}</option><option value="168" ${this._chartHours === 168 ? "selected" : ""}>${escapeHTML(locale.week)}</option></select></div>${graphMarkup(history, locale, full, animate && freshHistory)}</section>` : ""}`
          : `<p class="alert">${escapeHTML(locale.no_data)}</p>`
      }
      <footer class="footer"><span class="footer-left"><span class="dot ${healthTone}" aria-hidden="true"></span>${escapeHTML(locale.updated)} · ${escapeHTML(timeDisplay(timestamp, locale))}</span>${hasDiagnostics ? `<button class="small-button" type="button" data-action="diagnostics" aria-haspopup="dialog">${escapeHTML(locale.diagnostics)}</button>` : ""}</footer>
    </div></ha-card>`;
    if (animate && previousScore !== undefined && previousScore !== visibleScore) {
      content.querySelector(".gauge-progress")?.animate(
        { strokeDasharray: [`${previousScore} 100`, `${visibleScore} 100`] },
        { duration: 850, easing: "cubic-bezier(.2,.65,.3,1)" },
      );
    }
    const plot = content.querySelector(".chart-plot");
    if (plot) bindChart(plot, history, locale);
    if (focusedChartControl) content.querySelector(`.${focusedChartControl}`)?.focus({ preventScroll: true });
    content
      .querySelector('[data-action="diagnostics"]')
      ?.addEventListener("click", () => dialog.showModal());
    content
      .querySelector('[data-action="period"]')
      ?.addEventListener("change", (e) => {
        this._chartHours = Number(e.target.value);
        this._lastSignature = "";
        this._render();
        this._loadHistory();
      });
    this._loadHistory();
  }
}

class ZiggoModemCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._registry = [];
  }
  setConfig(config) {
    this._config = { ...ZiggoModemCard.getStubConfig(), ...config };
    this._render();
  }
  set hass(hass) {
    this._hass = hass;
    if (!this._requested) {
      this._requested = true;
      getRegistry(hass)
        .then((entries) => {
          this._registry = entries;
          this._render();
        })
        .catch(() => {});
    }
  }
  _change(patch) {
    this._config = { ...this._config, ...patch };
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: this._config },
        bubbles: true,
        composed: true,
      }),
    );
    this._render();
  }
  _render() {
    if (!this._config) return;
    const locale = localeFor(this._config, this._hass);
    const devices = new Map();
    for (const e of this._registry) {
      if (
        e.platform === "ziggo_modem" &&
        e.device_id &&
        !devices.has(e.device_id)
      )
        devices.set(e.device_id, e.entity_id);
    }
    const fields = this._config.metrics || DEFAULT_METRICS;
    this.shadowRoot.innerHTML = `<style>${EDITOR_CSS}</style><div class="form"><h3>${escapeHTML(locale.editor_title)}</h3>
      <label>${escapeHTML(locale.title_label)}<input data-key="title" value="${escapeHTML(this._config.title || "")}"></label>
      <label>${escapeHTML(locale.device)}<select data-key="device_id"><option value="">${escapeHTML(locale.autodetect)}</option>${Array.from(
        devices,
      )
        .map(
          ([id, name]) =>
            `<option value="${escapeHTML(id)}" ${this._config.device_id === id ? "selected" : ""}>${escapeHTML(name)}</option>`,
        )
        .join("")}</select></label>
      <label>${escapeHTML(locale.layout)}<select data-key="layout">${["auto", "compact", "expanded", "full"].map((k) => `<option value="${k}" ${this._config.layout === k ? "selected" : ""}>${escapeHTML(locale[k])}</option>`).join("")}</select></label>
      <label>${escapeHTML(locale.language)}<select data-key="language"><option value="auto">${escapeHTML(locale.detect)}</option><option value="nl" ${this._config.language === "nl" ? "selected" : ""}>Nederlands</option><option value="en" ${this._config.language === "en" ? "selected" : ""}>English</option></select></label>
      ${[
        ["show_modem", "modem"],
        ["show_chart", "chart"],
        ["glow", "glow"],
        ["animations", "animations"],
      ]
        .map(
          ([k, label]) =>
            `<label class="check"><input type="checkbox" data-key="${k}" ${this._config[k] ? "checked" : ""}>${escapeHTML(locale[label])}</label>`,
        )
        .join("")}
      <strong>${escapeHTML(locale.metrics)}</strong><div class="options">${[...DEFAULT_METRICS, ...OPTIONAL_METRICS].map((key) => `<label class="check"><input type="checkbox" data-metric="${key}" ${fields.includes(key) ? "checked" : ""}>${escapeHTML(locale[key] || key)}</label>`).join("")}</div>
      <details><summary>${escapeHTML(locale.entities)}</summary><div class="pairs">${ALL_KEYS.map((key) => `<label>${escapeHTML(locale[key] || key)}<input data-entity="${key}" value="${escapeHTML(this._config.entities?.[key] || "")}" placeholder="sensor.ziggo_modem_..."></label>`).join("")}</div></details>
      <span class="tip">${escapeHTML(locale.help)}</span></div>`;
    this.shadowRoot.querySelectorAll("[data-key]").forEach((el) =>
      el.addEventListener("change", () => {
        const key = el.dataset.key;
        this._change({ [key]: el.type === "checkbox" ? el.checked : el.value });
      }),
    );
    this.shadowRoot.querySelectorAll("[data-metric]").forEach((el) =>
      el.addEventListener("change", () => {
        const keys = [...DEFAULT_METRICS, ...OPTIONAL_METRICS].filter(
          (key) =>
            this.shadowRoot.querySelector(`[data-metric="${key}"]`)?.checked,
        );
        this._change({ metrics: keys });
      }),
    );
    this.shadowRoot.querySelectorAll("[data-entity]").forEach((el) =>
      el.addEventListener("change", () => {
        const entities = { ...(this._config.entities || {}) };
        if (el.value.trim()) entities[el.dataset.entity] = el.value.trim();
        else delete entities[el.dataset.entity];
        this._change({ entities });
      }),
    );
  }
}
if (!customElements.get(CARD_TYPE))
  customElements.define(CARD_TYPE, ZiggoModemCard);
if (!customElements.get("ziggo-modem-card-editor"))
  customElements.define("ziggo-modem-card-editor", ZiggoModemCardEditor);
window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === CARD_TYPE))
  window.customCards.push({
    type: CARD_TYPE,
    name: "Ziggo Modem · Neon",
    description:
      "Responsive, cinematic DOCSIS dashboard for Ziggo Sagemcom modems",
    preview: true,
  });
