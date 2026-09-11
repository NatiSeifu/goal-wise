import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import pptxgen from "pptxgenjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "..");
const manifestPath = path.join(root, "deck", "slides.json");
const distDir = path.join(root, "dist");
const outputPath = path.join(distDir, "goalwise-final-demo-high-end-v2.pptx");
const deck = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "GoalWise Team";
pptx.company = "GoalWise";
pptx.subject = "Graduate CS final demo";
pptx.title = `${deck.title} - High-End`;
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US"
};
pptx.defineLayout({ name: "LAYOUT_WIDE", width: 13.333, height: 7.5 });
pptx.margin = 0;

const C = {
  night: "101413",
  ink: "18221F",
  ivory: "F6F1E7",
  paper: "FCFAF4",
  cloud: "E8EEE9",
  line: "B9C7BF",
  muted: "68766F",
  green: "0F7A50",
  mint: "8BD8B0",
  blue: "2563A8",
  cyan: "38BDF8",
  amber: "E6A83B",
  coral: "D85F4B",
  white: "FFFFFF"
};

function addNotes(slide, notes) {
  if (notes) slide.addNotes(notes);
}

function addFrame(slide, index, mode = "light") {
  const dark = mode === "dark";
  slide.background = { color: dark ? C.night : C.paper };
  const rail = dark ? C.mint : C.green;
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 7.5,
    fill: { color: dark ? C.night : C.paper },
    line: { color: dark ? C.night : C.paper }
  });
  for (let x = 0.75; x < 12.7; x += 0.55) {
    slide.addShape(pptx.ShapeType.line, {
      x,
      y: 0.65,
      w: 0,
      h: 6.1,
      line: { color: dark ? "1B2421" : "EEF2EE", width: 0.35, transparency: 25 }
    });
  }
  for (let y = 0.85; y < 6.9; y += 0.55) {
    slide.addShape(pptx.ShapeType.line, {
      x: 0.55,
      y,
      w: 12.25,
      h: 0,
      line: { color: dark ? "1B2421" : "EEF2EE", width: 0.35, transparency: 25 }
    });
  }
  slide.addShape(pptx.ShapeType.line, {
    x: 0.52,
    y: 0.47,
    w: 12.3,
    h: 0,
    line: { color: dark ? "32413B" : C.line, width: 0.8 }
  });
  slide.addText("GOALWISE", {
    x: 0.62,
    y: 0.28,
    w: 1.5,
    h: 0.2,
    fontFace: "Aptos",
    fontSize: 9,
    bold: true,
    color: dark ? "8AA297" : C.muted,
    charSpace: 1.2,
    margin: 0
  });
  slide.addText(String(index).padStart(2, "0"), {
    x: 12.24,
    y: 0.28,
    w: 0.58,
    h: 0.18,
    fontFace: "Aptos",
    fontSize: 9,
    bold: true,
    color: dark ? "8AA297" : C.muted,
    align: "right",
    margin: 0
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.52,
    y: 7.02,
    w: 12.3,
    h: 0.04,
    fill: { color: rail },
    line: { color: rail }
  });
}

function title(slide, item, index) {
  addFrame(slide, index, "dark");
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.0,
    y: 0,
    w: 13.333,
    h: 7.5,
    fill: { color: C.night },
    line: { color: C.night }
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.68,
    y: 0.78,
    w: 0.16,
    h: 5.75,
    fill: { color: C.green },
    line: { color: C.green }
  });
  slide.addText(item.kicker.toUpperCase(), {
    x: 1.15,
    y: 1.02,
    w: 4.2,
    h: 0.24,
    fontSize: 9,
    bold: true,
    charSpace: 1.4,
    color: C.mint,
    margin: 0
  });
  slide.addText("GoalWise", {
    x: 1.08,
    y: 1.46,
    w: 5.4,
    h: 0.9,
    fontFace: "Aptos Display",
    fontSize: 49,
    bold: true,
    color: C.ivory,
    margin: 0
  });
  slide.addText("weekly planning from explicit assumptions", {
    x: 1.13,
    y: 2.35,
    w: 5.35,
    h: 0.36,
    fontSize: 17,
    color: "B8CEC4",
    margin: 0
  });
  slide.addShape(pptx.ShapeType.arc, {
    x: 7.0,
    y: 1.0,
    w: 4.4,
    h: 4.4,
    adjustPoint: 0.22,
    line: { color: C.mint, width: 2.2, transparency: 8 }
  });
  slide.addShape(pptx.ShapeType.arc, {
    x: 7.55,
    y: 1.55,
    w: 3.3,
    h: 3.3,
    adjustPoint: 0.35,
    line: { color: C.amber, width: 1.5, transparency: 15 }
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 8.43,
    y: 2.36,
    w: 1.65,
    h: 1.65,
    fill: { color: "172C25", transparency: 0 },
    line: { color: C.green, width: 1.3 }
  });
  slide.addText("$", {
    x: 8.43,
    y: 2.62,
    w: 1.65,
    h: 0.56,
    fontSize: 34,
    bold: true,
    color: C.mint,
    align: "center",
    margin: 0
  });
  addMetric(slide, "ONE GOAL", "MVP scope", 6.85, 5.45, C.green, true);
  addMetric(slide, "PACE-v1", "deterministic core", 8.88, 5.45, C.blue, true);
  addMetric(slide, "AI EDGE", "explain only", 10.91, 5.45, C.amber, true);
  slide.addText(item.bullets.join("  /  "), {
    x: 1.15,
    y: 5.5,
    w: 4.85,
    h: 0.62,
    fontSize: 13.5,
    color: "D7E4DD",
    fit: "shrink",
    margin: 0
  });
  addNotes(slide, item.notes);
}

function addMetric(slide, value, label, x, y, color, dark = false) {
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w: 1.78,
    h: 0.82,
    fill: { color: dark ? "17201C" : C.white },
    line: { color: dark ? "304139" : C.line, width: 0.8 }
  });
  slide.addText(value, {
    x: x + 0.12,
    y: y + 0.14,
    w: 1.54,
    h: 0.2,
    fontSize: 12.5,
    bold: true,
    color,
    align: "center",
    margin: 0
  });
  slide.addText(label, {
    x: x + 0.12,
    y: y + 0.45,
    w: 1.54,
    h: 0.17,
    fontSize: 9,
    color: dark ? "9DB3A8" : C.muted,
    align: "center",
    margin: 0
  });
}

function header(slide, item, index, dark = false) {
  addFrame(slide, index, dark ? "dark" : "light");
  slide.addText(item.kicker.toUpperCase(), {
    x: 0.72,
    y: 0.84,
    w: 4.6,
    h: 0.24,
    fontSize: 10,
    bold: true,
    charSpace: 1.1,
    color: dark ? C.mint : C.green,
    margin: 0
  });
  slide.addText(item.title, {
    x: 0.72,
    y: 1.17,
    w: 8.7,
    h: 0.72,
    fontFace: "Aptos Display",
    fontSize: 29,
    bold: true,
    color: dark ? C.ivory : C.ink,
    fit: "shrink",
    margin: 0
  });
  slide.addText(item.subtitle, {
    x: 0.74,
    y: 1.93,
    w: 7.7,
    h: 0.32,
    fontSize: 13,
    color: dark ? "AEBFB6" : C.muted,
    fit: "shrink",
    margin: 0
  });
}

function scope(slide, item, index) {
  header(slide, item, index);
  const columns = [
    ["CURRENT", "What the demo can defend", ["one active savings goal", "manual assumptions", "safe-to-spend + status"], C.green],
    ["EDGE", "Accepted but controlled", ["CSV preview + confirmation", "optional AI explanation", "snapshot-scoped summaries"], C.blue],
    ["DEFERRED", "Named honestly", ["bank sync", "raw transaction import", "multi-goal planning"], C.coral]
  ];
  columns.forEach(([label, titleText, lines, color], i) => {
    const x = 0.82 + i * 4.12;
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y: 2.82,
      w: 3.55,
      h: 2.92,
      fill: { color: i === 0 ? "F5FBF7" : i === 1 ? "F4F8FC" : "FFF8F5" },
      line: { color, width: 1.0 }
    });
    slide.addText(label, {
      x: x + 0.22,
      y: 3.08,
      w: 1.4,
      h: 0.2,
      fontSize: 9.5,
      bold: true,
      charSpace: 1.1,
      color,
      margin: 0
    });
    slide.addText(titleText, {
      x: x + 0.22,
      y: 3.43,
      w: 2.9,
      h: 0.28,
      fontSize: 14,
      bold: true,
      color: C.ink,
      margin: 0
    });
    addLines(slide, lines, x + 0.24, 4.1, 2.8, color);
  });
  addNotes(slide, item.notes);
}

function addLines(slide, lines, x, y, w, color = C.green, dark = false, step = 0.42) {
  lines.forEach((text, i) => {
    slide.addShape(pptx.ShapeType.line, {
      x,
      y: y + i * step + 0.12,
      w: 0.17,
      h: 0,
      line: { color, width: 1.2 }
    });
    slide.addText(text, {
      x: x + 0.28,
      y: y + i * step,
      w,
      h: 0.3,
      fontSize: 12,
      color: dark ? C.ivory : C.ink,
      fit: "shrink",
      margin: 0
    });
  });
}

function architecture(slide, item, index) {
  header(slide, item, index, true);
  const nodes = [
    ["Browser", "React renders", 0.8, 3.05, C.cyan],
    ["API", "FastAPI /api/v1", 3.18, 3.05, C.mint],
    ["Services", "ownership + normalize", 5.55, 3.05, C.amber],
    ["pace-v1", "pure calculation", 7.92, 3.05, C.green],
    ["Snapshots", "immutable audit", 10.3, 3.05, C.cyan]
  ];
  nodes.forEach(([name, sub, x, y, color], i) => {
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w: 1.72,
      h: 1.06,
      fill: { color: "17201C" },
      line: { color, width: 1.1 }
    });
    slide.addText(name, {
      x: x + 0.12,
      y: y + 0.22,
      w: 1.48,
      h: 0.2,
      fontSize: 12.5,
      bold: true,
      color,
      align: "center",
      margin: 0
    });
    slide.addText(sub, {
      x: x + 0.12,
      y: y + 0.56,
      w: 1.48,
      h: 0.2,
      fontSize: 9.5,
      color: "AEBFB6",
      align: "center",
      fit: "shrink",
      margin: 0
    });
    if (i < nodes.length - 1) {
      slide.addShape(pptx.ShapeType.line, {
        x: x + 1.72,
        y: y + 0.53,
        w: 0.66,
        h: 0,
        line: { color: "6C8377", width: 1.1, endArrowType: "triangle" }
      });
    }
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.86,
    y: 5.25,
    w: 11.35,
    h: 0.62,
    fill: { color: "17201C" },
    line: { color: "31443B" }
  });
  slide.addText("Frontend formats and visualizes; the backend owns official financial outputs.", {
    x: 1.12,
    y: 5.45,
    w: 10.82,
    h: 0.18,
    fontSize: 13.5,
    bold: true,
    color: C.ivory,
    align: "center",
    margin: 0
  });
  addNotes(slide, item.notes);
}

function decision(slide, item, index) {
  header(slide, item, index);
  const parsed = item.bullets.map((b) => {
    const [label, ...rest] = b.split(":");
    return [label, rest.join(":").trim()];
  });
  const colors = [C.green, C.blue, C.amber, C.coral, C.green];
  parsed.forEach(([label, body], i) => {
    const x = i < 2 ? 0.82 + i * 5.95 : 0.82 + (i - 2) * 3.98;
    const y = i < 2 ? 2.76 : 5.05;
    const w = i < 2 ? 5.35 : 3.45;
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w,
      h: i < 2 ? 1.4 : 1.15,
      fill: { color: i === 0 ? "F3FBF7" : C.white },
      line: { color: colors[i], width: i === 0 ? 1.4 : 0.8 }
    });
    slide.addText(label.toUpperCase(), {
      x: x + 0.2,
      y: y + 0.18,
      w: 1.6,
      h: 0.18,
      fontSize: 9,
      bold: true,
      charSpace: 1,
      color: colors[i],
      margin: 0
    });
    slide.addText(body, {
      x: x + 0.22,
      y: y + 0.52,
      w: w - 0.45,
      h: i < 2 ? 0.52 : 0.48,
      fontSize: i < 2 ? 13.5 : 11.2,
      bold: i === 0,
      color: C.ink,
      fit: "shrink",
      margin: 0
    });
  });
  addNotes(slide, item.notes);
}

function security(slide, item, index) {
  header(slide, item, index);
  const controls = [
    ["Session", "HTTP-only cookie; only a hashed opaque token is stored server-side", C.green],
    ["CSRF", "Unsafe authenticated methods require a CSRF token", C.blue],
    ["Ownership", "Private cross-user resource access returns 404", C.coral],
    ["Hosting", "Railway uses secure cookies, allowlisted origins, and PostgreSQL", C.amber]
  ];
  controls.forEach(([titleText, body, color], i) => {
    const x = 0.9 + (i % 2) * 5.95;
    const y = 2.72 + Math.floor(i / 2) * 1.55;
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w: 5.35,
      h: 1.05,
      fill: { color: C.white },
      line: { color, width: 1.2 }
    });
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w: 0.14,
      h: 1.05,
      fill: { color },
      line: { color }
    });
    slide.addText(titleText, {
      x: x + 0.34,
      y: y + 0.2,
      w: 1.35,
      h: 0.24,
      fontSize: 13,
      bold: true,
      color,
      margin: 0
    });
    slide.addText(body, {
      x: x + 1.78,
      y: y + 0.2,
      w: 3.2,
      h: 0.46,
      fontSize: 12.2,
      color: C.ink,
      fit: "shrink",
      margin: 0
    });
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 1.05,
    y: 5.95,
    w: 11.1,
    h: 0.52,
    fill: { color: C.ink },
    line: { color: C.ink }
  });
  slide.addText("Demo failure case: unauthorized or cross-user access fails without exposing another user's financial data.", {
    x: 1.25,
    y: 6.12,
    w: 10.7,
    h: 0.16,
    fontSize: 12.2,
    bold: true,
    color: C.ivory,
    align: "center",
    fit: "shrink",
    margin: 0
  });
  addNotes(slide, item.notes);
}

function pipeline(slide, item, index) {
  header(slide, item, index, true);
  const steps = [
    ["COMMITTED", "snapshot", C.green],
    ["MINIMIZED", "aggregate payload", C.cyan],
    ["GENERATED", "explanation prose", C.amber],
    ["VALIDATED", "schema + snapshot", C.mint],
    ["RENDERED", "backend numbers", C.blue]
  ];
  steps.forEach(([top, bottom, color], i) => {
    const x = 0.72 + i * 2.48;
    slide.addShape(pptx.ShapeType.hexagon, {
      x,
      y: 3.0,
      w: 1.72,
      h: 1.28,
      fill: { color: "17201C" },
      line: { color, width: 1.15 }
    });
    slide.addText(top, {
      x: x + 0.17,
      y: 3.34,
      w: 1.38,
      h: 0.16,
      fontSize: 8.8,
      bold: true,
      charSpace: 0.8,
      color,
      align: "center",
      margin: 0
    });
    slide.addText(bottom, {
      x: x + 0.17,
      y: 3.62,
      w: 1.38,
      h: 0.17,
      fontSize: 9,
      color: "C7D8CF",
      align: "center",
      fit: "shrink",
      margin: 0
    });
    if (i < steps.length - 1) {
      slide.addShape(pptx.ShapeType.line, {
        x: x + 1.75,
        y: 3.64,
        w: 0.74,
        h: 0,
        line: { color: "6C8377", width: 1, endArrowType: "triangle" }
      });
    }
  });
  slide.addText("Runtime AI is allowed to explain a committed calculation. It is not allowed to become the calculator.", {
    x: 1.15,
    y: 5.32,
    w: 10.9,
    h: 0.42,
    fontSize: 16,
    bold: true,
    color: C.ivory,
    align: "center",
    fit: "shrink",
    margin: 0
  });
  addNotes(slide, item.notes);
}

function verification(slide, item, index) {
  header(slide, item, index);
  const bars = [
    ["pace golden", 92, C.green],
    ["API + auth", 84, C.blue],
    ["migration smoke", 72, C.amber],
    ["frontend checks", 78, C.coral]
  ];
  bars.forEach(([label, pct, color], i) => {
    const y = 2.82 + i * 0.72;
    slide.addText(label, {
      x: 1.0,
      y,
      w: 1.55,
      h: 0.2,
      fontSize: 12,
      bold: true,
      color: C.ink,
      margin: 0
    });
    slide.addShape(pptx.ShapeType.rect, {
      x: 2.85,
      y: y + 0.03,
      w: 7.5,
      h: 0.18,
      fill: { color: C.cloud },
      line: { color: C.cloud }
    });
    slide.addShape(pptx.ShapeType.rect, {
      x: 2.85,
      y: y + 0.03,
      w: 7.5 * pct / 100,
      h: 0.18,
      fill: { color },
      line: { color }
    });
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 10.8,
    y: 2.82,
    w: 1.5,
    h: 3.05,
    fill: { color: C.ink },
    line: { color: C.ink }
  });
  slide.addText("Known gap", {
    x: 11.0,
    y: 3.15,
    w: 1.1,
    h: 0.2,
    fontSize: 10.5,
    bold: true,
    color: C.amber,
    align: "center",
    margin: 0
  });
  slide.addText("Tests prove contracts, not production load.", {
    x: 10.98,
    y: 3.72,
    w: 1.15,
    h: 1.0,
    fontSize: 12.5,
    bold: true,
    color: C.ivory,
    align: "center",
    fit: "shrink",
    margin: 0
  });
  addNotes(slide, item.notes);
}

function demo(slide, item, index) {
  header(slide, item, index, true);
  const items = [
    ["01", "Value path", "Load plan and read weekly safe-to-spend", C.green],
    ["02", "Failure path", "Invalid or unauthorized access fails safely", C.amber],
    ["03", "Evidence path", "Show snapshot and test/deploy proof", C.cyan]
  ];
  items.forEach(([num, titleText, body, color], i) => {
    const x = 1.05 + i * 4.05;
    slide.addText(num, {
      x,
      y: 2.9,
      w: 0.82,
      h: 0.35,
      fontSize: 20,
      bold: true,
      color,
      margin: 0
    });
    slide.addShape(pptx.ShapeType.line, {
      x,
      y: 3.42,
      w: 2.9,
      h: 0,
      line: { color, width: 1.6 }
    });
    slide.addText(titleText, {
      x,
      y: 3.68,
      w: 2.9,
      h: 0.28,
      fontSize: 15,
      bold: true,
      color: C.ivory,
      margin: 0
    });
    slide.addText(body, {
      x,
      y: 4.14,
      w: 2.8,
      h: 0.44,
      fontSize: 12,
      color: "BFD1C8",
      fit: "shrink",
      margin: 0
    });
  });
  slide.addText("Deck stops here. Product proof starts in the browser.", {
    x: 1.08,
    y: 5.82,
    w: 10.9,
    h: 0.35,
    fontSize: 19,
    bold: true,
    color: C.mint,
    align: "center",
    margin: 0
  });
  addNotes(slide, item.notes);
}

const renderers = {
  title,
  scope,
  architecture,
  decision,
  security,
  pipeline,
  verification,
  demo
};

deck.slides.forEach((item, idx) => {
  const slide = pptx.addSlide();
  const renderer = renderers[item.kind] ?? scope;
  renderer(slide, item, idx + 1);
});

fs.mkdirSync(distDir, { recursive: true });
await pptx.writeFile({ fileName: outputPath });
console.log(`Wrote ${path.relative(process.cwd(), outputPath)}`);
