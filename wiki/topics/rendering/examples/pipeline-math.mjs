// Teaching calculations only. No GPU, browser, or third-party dependencies.
import { fileURLToPath } from 'node:url';

function requireValue(condition, message) {
  if (!condition) throw new RangeError(message);
}

function vector(value, length) {
  requireValue(Array.isArray(value) && value.length === length
    && value.every(Number.isFinite), `Expected ${length} finite numbers`);
}

function unitValue(value) {
  requireValue(Number.isFinite(value) && value >= 0 && value <= 1,
    'Expected a value in [0, 1]');
}

export function multiplyPoint(matrix, point) {
  vector(matrix, 16);
  vector(point, 4);
  return [0, 1, 2, 3].map(row =>
    point.reduce((sum, value, column) =>
      sum + matrix[column * 4 + row] * value, 0));
}

export function perspective(fovY, aspect, near, far, backend = 'webgl') {
  requireValue([fovY, aspect, near, far].every(Number.isFinite)
    && fovY > 0 && fovY < Math.PI && aspect > 0 && near > 0 && far > near,
  'Expected valid finite perspective parameters');
  requireValue(backend === 'webgl' || backend === 'webgpu',
    'Unknown backend');
  const scale = 1 / Math.tan(fovY / 2);
  const zScale = backend === 'webgl'
    ? -(far + near) / (far - near)
    : -far / (far - near);
  const zOffset = backend === 'webgl'
    ? -2 * far * near / (far - near)
    : -far * near / (far - near);
  return [
    scale / aspect, 0, 0, 0,
    0, scale, 0, 0,
    0, 0, zScale, -1,
    0, 0, zOffset, 0,
  ];
}

export function ndc(clip) {
  vector(clip, 4);
  requireValue(clip[3] !== 0, 'Cannot divide by zero clip w');
  return clip.slice(0, 3).map(value => value / clip[3]);
}

export function perspectiveInterpolate(weights, values, clipW) {
  vector(weights, 3);
  vector(values, 3);
  vector(clipW, 3);
  requireValue(weights.every(value => value >= 0)
    && Math.abs(weights.reduce((a, b) => a + b, 0) - 1) < 1e-10,
  'Expected barycentric weights inside a triangle');
  requireValue(clipW.every(value => value > 0),
    'This teaching example requires positive clip w');
  const inverseW = weights.map((weight, i) => weight / clipW[i]);
  return inverseW.reduce((sum, value, i) => sum + value * values[i], 0)
    / inverseW.reduce((sum, value) => sum + value, 0);
}

export function srgbToLinear(value) {
  unitValue(value);
  return value <= 0.04045
    ? value / 12.92
    : ((value + 0.055) / 1.055) ** 2.4;
}

export function linearToSrgb(value) {
  unitValue(value);
  return value <= 0.0031308
    ? value * 12.92
    : 1.055 * value ** (1 / 2.4) - 0.055;
}

export function textureBytes(width, height, bytesPerTexel = 4, mipmaps = true) {
  requireValue([width, height, bytesPerTexel].every(value =>
    Number.isSafeInteger(value) && value > 0),
  'Expected positive integer texture dimensions and texel size');
  let texels = 0;
  do {
    texels += width * height;
    requireValue(Number.isSafeInteger(texels * bytesPerTexel),
      'Texture estimate exceeds exact integer range');
    if (!mipmaps || (width === 1 && height === 1)) break;
    width = Math.max(1, Math.floor(width / 2));
    height = Math.max(1, Math.floor(height / 2));
  } while (true);
  return texels * bytesPerTexel;
}

export function drawingBufferPixels(width, height, ratio) {
  requireValue([width, height, ratio].every(value =>
    Number.isFinite(value) && value > 0), 'Expected positive finite dimensions');
  // Match the integer sizing strategy in the learning notes, not every browser.
  const w = Math.max(1, Math.round(width * ratio));
  const h = Math.max(1, Math.round(height * ratio));
  requireValue(Number.isSafeInteger(w * h), 'Pixel count exceeds exact range');
  return w * h;
}

export function summary() {
  const gl = perspective(Math.PI / 2, 1, 1, 10);
  const gpu = perspective(Math.PI / 2, 1, 1, 10, 'webgpu');
  return {
    scope: 'CPU teaching math, not shader compilation or GPU measurements',
    ndcDepth: {
      webgl: [-1, -10].map(z => ndc(multiplyPoint(gl, [0, 0, z, 1]))[2]),
      webgpu: [-1, -10].map(z => ndc(multiplyPoint(gpu, [0, 0, z, 1]))[2]),
    },
    interpolation: {
      screenLinear: 0.25,
      perspectiveCorrect: perspectiveInterpolate(
        [0.5, 0.25, 0.25], [0, 1, 0], [1, 2, 4]),
    },
    colors: {
      srgbHalfDecoded: srgbToLinear(0.5),
      linearBlackWhiteMixEncoded: linearToSrgb(0.5),
    },
    theoreticalStorage: {
      rgba8_4096BaseMiB: textureBytes(4096, 4096, 4, false) / 2 ** 20,
      rgba8_4096MipMiB: textureBytes(4096, 4096) / 2 ** 20,
      rgba16f_1080pMiB: textureBytes(1920, 1080, 8, false) / 2 ** 20,
    },
    pixels800x600: {
      dpr1: drawingBufferPixels(800, 600, 1),
      dpr2: drawingBufferPixels(800, 600, 2),
    },
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  console.log(JSON.stringify(summary(), null, 2));
}
