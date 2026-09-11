import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import pptxgen from "pptxgenjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "..");
const manifestPath = path.join(root, "deck", "slides.json");
const distDir = path.join(root, "dist");
const outputPath = path.join(distDir, "goalwise-final-demo.pptx");

const deck = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "GoalWise Team";
pptx.company = "GoalWise";
pptx.subject = "Graduate CS final demo";
pptx.title = deck.title;
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US"
};
pptx.defineLayout({ name: "LAYOUT_WIDE", width: 13.333, height: 7.5 });
pptx.margin = 0;

const C = {
  ink: "17201C",
  muted: "60706A",
  soft: "F4F7F5",
  line: "CBD8D2",
  green: "1B6B4B",
  mint: "DDEDE5",
  blue: "244C7A",
  amber: "D08B2E",
  red: "A23E3E",
  white: "FFFFFF"
};

function addBackground(slide, index) {
  slide.background = { color: C.soft };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.16,
    fill: { color: index % 3 === 0 ? C.green : index % 3 === 1 ? C.blue : C.amber },
    line: { color: index % 3 === 0 ? C.green : index % 3 === 1 ? C.blue : C.amber }
  });
  slide.addText("GoalWise", {
    x: 0.55,
    y: 0.25,
    w: 2,
    h: 0.22,
    fontFace: "Aptos",
    fontSize: 8,
    bold: true,
    color: C.muted,
    margin: 0
  });
  slide.addText(String(index).padStart(2, "0"), {
    x: 12.12,
    y: 0.22,
    w: 0.7,
    h: 0.25,
    fontFace: "Aptos",
    fontSize: 8,
    color: C.muted,
    align: "right",
    margin: 0
  });
}

function addHeader(slide, item) {
  slide.addText(item.kicker.toUpperCase(), {
    x: 0.75,
    y: 0.72,
    w: 4.5,
    h: 0.26,
    fontFace: "Aptos",
    fontSize: 9,
    bold: true,
    color: C.green,
    charSpace: 0.8,
    margin: 0
  });
  slide.addText(item.title, {
    x: 0.75,
    y: 1.05,
    w: 8.8,
    h: 0.78,
    fontFace: "Aptos Display",
    fontSize: 27,
    bold: true,
    color: C.ink,
    fit: "shrink",
    margin: 0
  });
  slide.addText(item.subtitle, {
    x: 0.77,
    y: 1.86,
    w: 7.8,
    h: 0.36,
    fontFace: "Aptos",
    fontSize: 12,
    color: C.muted,
    fit: "shrink",
    margin: 0
  });
}

function addBulletList(slide, bullets, x, y, w, options = {}) {
  const color = options.color ?? C.ink;
  const accent = options.accent ?? C.green;
  bullets.forEach((bullet, idx) => {
    const top = y + idx * (options.step ?? 0.64);
    slide.addShape(pptx.ShapeType.ellipse, {
      x,
      y: top + 0.09,
      w: 0.13,
      h: 0.13,
      fill: { color: accent },
      line: { color: accent }
    });
    slide.addText(bullet, {
      x: x + 0.28,
      y: top,
      w,
      h: 0.38,
      fontFace: "Aptos",
      fontSize: options.fontSize ?? 13,
      color,
      breakLine: false,
      fit: "shrink",
      margin: 0.01
    });
  });
}

function addFooter(slide) {
  slide.addShape(pptx.ShapeType.line, {
    x: 0.75,
    y: 7.0,
    w: 11.85,
    h: 0,
    line: { color: C.line, width: 0.75 }
  });
  slide.addText("Backend-owned calculations | Immutable snapshots | Explain-only AI boundary", {
    x: 0.75,
    y: 7.1,
    w: 8.5,
    h: 0.22,
    fontFace: "Aptos",
    fontSize: 7.5,
    color: C.muted,
    margin: 0
  });
}

function addPill(slide, label, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.42,
    rectRadius: 0.06,
    fill: { color },
    line: { color },
  });
  slide.addText(label, {
    x: x + 0.1,
    y: y + 0.11,
    w: w - 0.2,
    h: 0.16,
    fontFace: "Aptos",
    fontSize: 8,
    bold: true,
    color: C.white,
    align: "center",
    margin: 0
  });
}

function addNotes(slide, notes) {
  if (notes) slide.addNotes(notes);
}

function titleSlide(item, index) {
  const slide = pptx.addSlide();
  slide.background = { color: "EEF5F0" };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 5.1,
    h: 7.5,
    fill: { color: C.green },
    line: { color: C.green }
  });
  slide.addText(item.kicker.toUpperCase(), {
    x: 0.72,
    y: 0.68,
    w: 3.4,
    h: 0.28,
    fontSize: 9,
    bold: true,
    color: "BBDCCB",
    charSpace: 0.9,
    margin: 0
  });
  slide.addText(item.title, {
    x: 0.7,
    y: 1.3,
    w: 4,
    h: 0.9,
    fontFace: "Aptos Display",
    fontSize: 42,
    bold: true,
    color: C.white,
    margin: 0
  });
  slide.addText(item.subtitle, {
    x: 0.75,
    y: 2.28,
    w: 3.55,
    h: 0.56,
    fontFace: "Aptos",
    fontSize: 14,
    color: "E6F2EC",
    fit: "shrink",
    margin: 0
  });
  slide.addShape(pptx.ShapeType.arc, {
    x: 5.95,
    y: 0.78,
    w: 5.9,
    h: 5.9,
    adjustPoint: 0.25,
    line: { color: C.line, width: 2 }
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 8.13,
    y: 2.36,
    w: 1.55,
    h: 1.55,
    fill: { color: C.mint },
    line: { color: C.green, width: 1.2 }
  });
  slide.addText("$", {
    x: 8.13,
    y: 2.63,
    w: 1.55,
    h: 0.5,
    fontFace: "Aptos Display",
    fontSize: 30,
    bold: true,
    color: C.green,
    align: "center",
    margin: 0
  });
  addBulletList(slide, item.bullets, 6.35, 4.75, 5.5, { fontSize: 14, step: 0.72 });
  slide.addText(String(index).padStart(2, "0"), {
    x: 11.9,
    y: 6.88,
    w: 0.65,
    h: 0.22,
    fontSize: 8,
    color: C.muted,
    align: "right",
    margin: 0
  });
  addNotes(slide, item.notes);
}

function scopeSlide(item, index) {
  const slide = pptx.addSlide();
  addBackground(slide, index);
  addHeader(slide, item);
  const cards = [
    ["Current", ["One active goal", "Manual assumptions", "Backend results"], C.green],
    ["Accepted edge", ["Planning CSV import", "Preview then confirm", "Normalized inputs"], C.blue],
    ["Deferred", ["Bank sync", "Raw transactions", "Multi-goal support"], C.amber]
  ];
  cards.forEach(([title, lines, color], idx) => {
    const x = 0.85 + idx * 4.15;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 2.85,
      w: 3.55,
      h: 2.55,
      rectRadius: 0.07,
      fill: { color: C.white },
      line: { color: C.line, width: 1 }
    });
    addPill(slide, title, x + 0.27, 3.1, 1.45, color);
    addBulletList(slide, lines, x + 0.32, 3.85, 2.75, { fontSize: 11.5, step: 0.48, accent: color });
  });
  addFooter(slide);
  addNotes(slide, item.notes);
}

function architectureSlide(item, index) {
  const slide = pptx.addSlide();
  addBackground(slide, index);
  addHeader(slide, item);
  const y = 3.0;
  const boxes = [
    ["React + Vite", "renders backend values", 0.75, C.blue],
    ["FastAPI", "auth, validation, ownership", 3.25, C.green],
    ["pace-v1", "deterministic engine", 5.75, C.amber],
    ["Snapshots", "immutable history", 8.25, C.green],
    ["Dashboard", "read model JSON", 10.75, C.blue]
  ];
  boxes.forEach(([title, sub, x, color], idx) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w: 1.9,
      h: 1.18,
      rectRadius: 0.06,
      fill: { color: C.white },
      line: { color, width: 1.4 }
    });
    slide.addText(title, {
      x: x + 0.15,
      y: y + 0.23,
      w: 1.6,
      h: 0.22,
      fontSize: 11,
      bold: true,
      color,
      align: "center",
      margin: 0
    });
    slide.addText(sub, {
      x: x + 0.16,
      y: y + 0.55,
      w: 1.58,
      h: 0.34,
      fontSize: 8.5,
      color: C.muted,
      align: "center",
      fit: "shrink",
      margin: 0
    });
    if (idx < boxes.length - 1) {
      slide.addShape(pptx.ShapeType.line, {
        x: x + 1.9,
        y: y + 0.59,
        w: 0.6,
        h: 0,
        line: { color: C.muted, width: 1.1, beginArrowType: "none", endArrowType: "triangle" }
      });
    }
  });
  addBulletList(slide, item.bullets, 1.05, 5.25, 10.8, { fontSize: 11.2, step: 0.35, accent: C.green });
  addFooter(slide);
  addNotes(slide, item.notes);
}

function decisionSlide(item, index) {
  const slide = pptx.addSlide();
  addBackground(slide, index);
  addHeader(slide, item);
  const labels = ["Claim", "Evidence", "Alternative", "Risk", "Mitigation"];
  item.bullets.forEach((bullet, idx) => {
    const x = idx < 3 ? 0.85 + idx * 4.15 : 2.9 + (idx - 3) * 4.15;
    const y = idx < 3 ? 2.65 : 5.0;
    const color = idx === 0 ? C.green : idx === 1 ? C.blue : idx === 2 ? C.amber : idx === 3 ? C.red : C.green;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w: 3.55,
      h: 1.42,
      rectRadius: 0.06,
      fill: { color: C.white },
      line: { color: C.line, width: 1 }
    });
    addPill(slide, labels[idx], x + 0.2, y + 0.22, 1.08, color);
    slide.addText(bullet.replace(/^[^:]+:\s*/, ""), {
      x: x + 0.26,
      y: y + 0.78,
      w: 3.02,
      h: 0.36,
      fontSize: 10.2,
      color: C.ink,
      fit: "shrink",
      margin: 0
    });
  });
  addFooter(slide);
  addNotes(slide, item.notes);
}

function pipelineSlide(item, index) {
  const slide = pptx.addSlide();
  addBackground(slide, index);
  addHeader(slide, item);
  const steps = [
    ["Snapshot", "committed aggregate fields", C.green],
    ["AI digest", "bounded prose only", C.blue],
    ["Validation", "schema + snapshot match", C.amber],
    ["UI", "renders backend numbers", C.green]
  ];
  steps.forEach(([title, sub, color], idx) => {
    const x = 1.0 + idx * 3.05;
    slide.addShape(pptx.ShapeType.chevron, {
      x,
      y: 3.0,
      w: 2.35,
      h: 1.1,
      fill: { color },
      line: { color }
    });
    slide.addText(title, {
      x: x + 0.1,
      y: 3.25,
      w: 1.75,
      h: 0.2,
      fontSize: 12,
      bold: true,
      color: C.white,
      align: "center",
      margin: 0
    });
    slide.addText(sub, {
      x: x + 0.1,
      y: 3.55,
      w: 1.75,
      h: 0.24,
      fontSize: 8,
      color: C.white,
      align: "center",
      fit: "shrink",
      margin: 0
    });
  });
  addBulletList(slide, item.bullets, 1.25, 5.05, 10.5, { fontSize: 12, step: 0.42, accent: C.green });
  addFooter(slide);
  addNotes(slide, item.notes);
}

function verificationSlide(item, index) {
  const slide = pptx.addSlide();
  addBackground(slide, index);
  addHeader(slide, item);
  const groups = [
    ["Calculation", "golden scenarios", C.green],
    ["Privacy", "cross-user tests", C.blue],
    ["Persistence", "migration smoke", C.amber],
    ["Frontend", "lint + build + capture", C.green]
  ];
  groups.forEach(([title, sub, color], idx) => {
    const x = 0.95 + idx * 3.0;
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y: 2.75,
      w: 2.35,
      h: 1.75,
      fill: { color: C.white },
      line: { color: C.line }
    });
    slide.addText(title, {
      x: x + 0.18,
      y: 3.05,
      w: 1.95,
      h: 0.24,
      fontSize: 12,
      bold: true,
      color,
      align: "center",
      margin: 0
    });
    slide.addText(sub, {
      x: x + 0.18,
      y: 3.5,
      w: 1.95,
      h: 0.28,
      fontSize: 9.2,
      color: C.muted,
      align: "center",
      fit: "shrink",
      margin: 0
    });
  });
  addBulletList(slide, item.bullets, 1.1, 5.25, 10.8, { fontSize: 10.8, step: 0.34, accent: C.green });
  addFooter(slide);
  addNotes(slide, item.notes);
}

function demoSlide(item, index) {
  const slide = pptx.addSlide();
  addBackground(slide, index);
  addHeader(slide, item);
  const steps = [
    ["1", "Value path", "View weekly safe-to-spend"],
    ["2", "Failure path", "Invalid or unauthorized access fails"],
    ["3", "Evidence path", "Show snapshot, checks, or deployment proof"]
  ];
  steps.forEach(([num, title, sub], idx) => {
    const x = 1.05 + idx * 4.05;
    slide.addShape(pptx.ShapeType.ellipse, {
      x,
      y: 3.05,
      w: 0.78,
      h: 0.78,
      fill: { color: idx === 0 ? C.green : idx === 1 ? C.amber : C.blue },
      line: { color: idx === 0 ? C.green : idx === 1 ? C.amber : C.blue }
    });
    slide.addText(num, {
      x,
      y: 3.22,
      w: 0.78,
      h: 0.22,
      fontSize: 16,
      bold: true,
      color: C.white,
      align: "center",
      margin: 0
    });
    slide.addText(title, {
      x: x + 0.98,
      y: 3.05,
      w: 2.25,
      h: 0.28,
      fontSize: 15,
      bold: true,
      color: C.ink,
      margin: 0
    });
    slide.addText(sub, {
      x: x + 0.98,
      y: 3.45,
      w: 2.32,
      h: 0.42,
      fontSize: 10.2,
      color: C.muted,
      fit: "shrink",
      margin: 0
    });
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.25,
    y: 5.3,
    w: 10.8,
    h: 0.72,
    rectRadius: 0.05,
    fill: { color: C.ink },
    line: { color: C.ink }
  });
  slide.addText("Switch to the live GoalWise app, then use terminal evidence only after the product path is clear.", {
    x: 1.55,
    y: 5.53,
    w: 10.2,
    h: 0.2,
    fontSize: 11,
    bold: true,
    color: C.white,
    align: "center",
    margin: 0
  });
  addFooter(slide);
  addNotes(slide, item.notes);
}

const renderers = {
  title: titleSlide,
  scope: scopeSlide,
  architecture: architectureSlide,
  decision: decisionSlide,
  pipeline: pipelineSlide,
  verification: verificationSlide,
  demo: demoSlide
};

deck.slides.forEach((item, idx) => {
  const renderer = renderers[item.kind] ?? scopeSlide;
  renderer(item, idx + 1);
});

fs.mkdirSync(distDir, { recursive: true });
await pptx.writeFile({ fileName: outputPath });
console.log(`Wrote ${path.relative(process.cwd(), outputPath)}`);
