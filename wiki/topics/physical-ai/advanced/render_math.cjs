const fs = require("fs");
const { mathjax } = require("mathjax-full/js/mathjax.js");
const { TeX } = require("mathjax-full/js/input/tex.js");
const { SVG } = require("mathjax-full/js/output/svg.js");
const { liteAdaptor } = require("mathjax-full/js/adaptors/liteAdaptor.js");
const { RegisterHTMLHandler } = require("mathjax-full/js/handlers/html.js");
const { AllPackages } = require("mathjax-full/js/input/tex/AllPackages.js");

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const document = mathjax.document("", {
  InputJax: new TeX({ packages: AllPackages }),
  OutputJax: new SVG({ fontCache: "none" }),
});

const samples = process.argv.includes("--test")
  ? [
      { tex: "\\hat{s}_{t+1}=f(\\hat{s}_t,u_t)", display: false },
      { tex: "\\begin{bmatrix}R&p\\\\0&1\\end{bmatrix}", display: true },
      { tex: "\\Delta q=J^T(JJ^T+\\lambda^2 I)^{-1}e", display: true },
    ]
  : JSON.parse(fs.readFileSync(0, "utf8"));

const result = samples.map(({ tex, display }) => {
  const node = document.convert(tex, {
    display, em: 16, ex: 8, containerWidth: 680,
  });
  const wrapper = adaptor.outerHTML(node);
  if (wrapper.includes('data-mml-node="merror"')) {
    throw new Error(`Invalid TeX: ${tex}`);
  }
  const svg = wrapper.match(/<svg\b[\s\S]*<\/svg>/)[0];
  const width = Number(svg.match(/\bwidth="([0-9.]+)ex"/)[1]);
  const height = Number(svg.match(/\bheight="([0-9.]+)ex"/)[1]);
  const alignMatch = svg.match(/vertical-align:\s*(-?[0-9.]+)ex/);
  return {
    svg, width_ex: width, height_ex: height,
    vertical_ex: alignMatch ? Number(alignMatch[1]) : 0,
  };
});
process.stdout.write(JSON.stringify(result));
