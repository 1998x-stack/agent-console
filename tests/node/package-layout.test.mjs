import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';

const root = new URL('../../', import.meta.url);
const read = (path) => readFileSync(new URL(path, root), 'utf8');

test('root package requires a pinned pnpm package manager', () => {
  const pkg = JSON.parse(read('package.json'));
  assert.equal(pkg.private, true);
  assert.match(pkg.packageManager, /^pnpm@\d+\.\d+\.\d+$/);
});

test('distinct Web UI and Pi worker packages', () => {
  const web = JSON.parse(read('apps/web/package.json'));
  const pi = JSON.parse(read('services/pi-worker/package.json'));
  assert.notEqual(web.name, pi.name);
  assert.equal(web.private, true);
  assert.equal(pi.private, true);
});

test('lockfile is committed before dependency installation', () => {
  assert.ok(existsSync(new URL('pnpm-lock.yaml', root)));
});
