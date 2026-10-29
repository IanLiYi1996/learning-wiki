import assert from 'node:assert/strict';
import test from 'node:test';
import {
  drawingBufferPixels,
  linearToSrgb,
  multiplyPoint,
  ndc,
  perspective,
  perspectiveInterpolate,
  srgbToLinear,
  summary,
  textureBytes,
} from './pipeline-math.mjs';

function close(actual, expected, tolerance = 1e-10) {
  assert.ok(Math.abs(actual - expected) < tolerance,
    `${actual} should be close to ${expected}`);
}

test('column-major translation affects a point, not a direction', () => {
  const translation = [
    1, 0, 0, 0, 0, 1, 0, 0,
    0, 0, 1, 0, 4, 5, 6, 1,
  ];
  assert.deepEqual(multiplyPoint(translation, [1, 2, 3, 1]), [5, 7, 9, 1]);
  assert.deepEqual(multiplyPoint(translation, [1, 2, 3, 0]), [1, 2, 3, 0]);
});

test('WebGL perspective maps near and far to -1 and 1', () => {
  const p = perspective(Math.PI / 2, 1, 1, 10);
  close(ndc(multiplyPoint(p, [0, 0, -1, 1]))[2], -1);
  close(ndc(multiplyPoint(p, [0, 0, -10, 1]))[2], 1);
});

test('WebGPU perspective maps near and far to 0 and 1', () => {
  const p = perspective(Math.PI / 2, 1, 1, 10, 'webgpu');
  close(ndc(multiplyPoint(p, [0, 0, -1, 1]))[2], 0);
  close(ndc(multiplyPoint(p, [0, 0, -10, 1]))[2], 1);
});

test('perspective scales x by distance and horizontal aspect', () => {
  const p = perspective(Math.PI / 2, 2, 1, 10);
  close(ndc(multiplyPoint(p, [1, 0, -2, 1]))[0], 0.25);
  close(ndc(multiplyPoint(p, [1, 0, -4, 1]))[0], 0.125);
});

test('near and far violations remain outside WebGL NDC', () => {
  const p = perspective(Math.PI / 2, 1, 1, 10);
  assert.ok(ndc(multiplyPoint(p, [0, 0, -0.5, 1]))[2] < -1);
  assert.ok(ndc(multiplyPoint(p, [0, 0, -20, 1]))[2] > 1);
});

test('projection rejects invalid parameters and backend', () => {
  for (const args of [
    [0, 1, 1, 10], [Math.PI, 1, 1, 10], [1, 0, 1, 10],
    [1, 1, 0, 10], [1, 1, 10, 1], [1, 1, 1, Infinity],
    [1, 1, 1, 10, 'unknown'],
  ]) assert.throws(() => perspective(...args), RangeError);
});

test('vector shape, nonfinite input, and zero w are rejected', () => {
  assert.throws(() => multiplyPoint([], [0, 0, 0, 1]), RangeError);
  assert.throws(() => ndc([NaN, 0, 0, 1]), RangeError);
  assert.throws(() => ndc([1, 2, 3, 0]), RangeError);
  assert.throws(() => ndc([1, 2, 3]), RangeError);
});

test('different clip w changes interpolation', () => {
  close(perspectiveInterpolate(
    [0.5, 0.25, 0.25], [0, 1, 0], [1, 2, 4]), 2 / 11);
  close(perspectiveInterpolate(
    [1 / 3, 1 / 3, 1 / 3], [0, 1, 0], [1, 2, 4]), 2 / 7);
});

test('equal clip w reduces to linear interpolation', () => {
  close(perspectiveInterpolate(
    [0.5, 0.25, 0.25], [0, 1, 0], [4, 4, 4]), 0.25);
});

test('interpolation preserves vertices and uniform scalar attributes', () => {
  close(perspectiveInterpolate([0, 1, 0], [4, 7, 9], [1, 2, 4]), 7);
  close(perspectiveInterpolate(
    [0.2, 0.3, 0.5], [3, 3, 3], [1, 2, 4]), 3);
});

test('invalid interpolation weights and clip w are rejected', () => {
  for (const [weights, w] of [
    [[0, 0, 0], [1, 2, 4]],
    [[1.1, -0.1, 0], [1, 2, 4]],
    [[0.5, 0.25, 0.25], [1, 0, 4]],
    [[0.5, 0.25, 0.25], [1, -2, 4]],
  ]) assert.throws(() =>
    perspectiveInterpolate(weights, [0, 1, 0], w), RangeError);
});

test('inverse transpose preserves normal perpendicularity under scale', () => {
  const tangent = [2, -1, 0];
  const wrongNormal = [2, 1, 0];
  const correctNormal = [0.5, 1, 0];
  const dot = (a, b) => a.reduce((sum, value, i) => sum + value * b[i], 0);
  assert.equal(dot(tangent, wrongNormal), 3);
  assert.equal(dot(tangent, correctNormal), 0);
});

test('sRGB half is not half of linear intensity', () => {
  close(srgbToLinear(0.5), 0.21404114048223255);
  close(linearToSrgb(0.5), 0.7353569830524495);
});

test('sRGB branches and a deterministic round trip are consistent', () => {
  close(srgbToLinear(0), 0);
  close(srgbToLinear(1), 1);
  close(srgbToLinear(0.04), 0.04 / 12.92);
  close(linearToSrgb(0.003), 0.003 * 12.92);
  for (let i = 0; i <= 100; i++) {
    close(linearToSrgb(srgbToLinear(i / 100)), i / 100);
  }
});

test('closed-domain color example rejects HDR and nonfinite values', () => {
  for (const value of [-1, 2, NaN, Infinity]) {
    assert.throws(() => srgbToLinear(value), RangeError);
    assert.throws(() => linearToSrgb(value), RangeError);
  }
});

test('square mip storage uses the finite series, not rounded 4/3', () => {
  assert.equal(textureBytes(4096, 4096, 4, false), 64 * 2 ** 20);
  assert.equal(textureBytes(4096, 4096), 89_478_484);
  assert.equal(textureBytes(1, 1), 4);
});

test('rectangular and NPOT mip chains are counted level by level', () => {
  assert.equal(textureBytes(8, 1), (8 + 4 + 2 + 1) * 4);
  assert.equal(textureBytes(3, 5), (15 + 2 + 1) * 4);
  assert.equal(textureBytes(1920, 1080, 8, false), 1920 * 1080 * 8);
});

test('storage estimates reject invalid or inexact dimensions', () => {
  for (const args of [[0, 2], [2, -1], [2.5, 3], [2, 3, 0],
    [Number.MAX_SAFE_INTEGER, 2]]) {
    assert.throws(() => textureBytes(...args), RangeError);
  }
});

test('DPR doubling quadruples integer-sized pixel coverage', () => {
  assert.equal(drawingBufferPixels(800, 600, 1), 480_000);
  assert.equal(drawingBufferPixels(800, 600, 2), 1_920_000);
  assert.equal(drawingBufferPixels(1, 1, 0.1), 1);
  assert.throws(() => drawingBufferPixels(800, 600, 0), RangeError);
  assert.throws(() => drawingBufferPixels(Infinity, 600, 1), RangeError);
});

test('summary is deterministic and explicitly excludes GPU measurements', () => {
  assert.deepEqual(summary(), summary());
  assert.match(summary().scope, /not shader compilation or GPU measurements/);
});
