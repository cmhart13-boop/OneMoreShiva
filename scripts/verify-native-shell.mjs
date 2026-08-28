import fs from "node:fs";

const required = [
  "app/layout.js",
  "app/page.js",
  "app/ShivaApp.js",
  "app/globals.css",
  "app/api/players/route.js",
  "app/api/coach/route.js",
  "app/api/espn/route.js",
  "vercel.json"
];

for (const file of required) {
  if (!fs.existsSync(file)) throw new Error(`Missing native app file: ${file}`);
}

const active = required
  .filter((file) => file.endsWith(".js") || file.endsWith(".css"))
  .map((file) => fs.readFileSync(file, "utf8"))
  .join("\n");

for (const forbidden of [
  "streamlit",
  "stAppViewContainer",
  "data-testid=\"st",
  "type=\"radio\"",
  "role=\"radio\""
]) {
  if (active.toLowerCase().includes(forbidden.toLowerCase())) {
    throw new Error(`Forbidden legacy UI token survived: ${forbidden}`);
  }
}

const css = fs.readFileSync("app/globals.css", "utf8");
for (const token of [".splash", ".kickoff-clock", ".pill.active", ".bottom-nav", ".coach-hero"]) {
  if (!css.includes(token)) throw new Error(`Missing UI contract: ${token}`);
}

const layout = fs.readFileSync("app/layout.js", "utf8");
for (const token of [
  "background: \"#071019\"",
  "apple-mobile-web-app-status-bar-style",
  ".brand-subtitle{font-size:14px!important",
  "@media(max-width:620px){.brand-subtitle{font-size:13.5px!important"
]) {
  if (!layout.includes(token)) throw new Error(`Missing first-paint/header contract: ${token}`);
}

const app = fs.readFileSync("app/ShivaApp.js", "utf8");
for (const token of [
  "Start Mock Draft",
  "Trade Analyzer",
  "Fantasy Football Intelligence",
  "Start/Sit",
  "Waivers",
  "Trades",
  "Lineup",
  "Watch",
  "Analysts",
  "League"
]) {
  if (!app.includes(token)) throw new Error(`Missing product contract: ${token}`);
}

if (/●|•|type=["']radio["']|role=["']radio["']/i.test(app)) {
  throw new Error("Dot/radio selection indicator survived in native app.");
}

console.log("Native Shiva shell verification passed.");
