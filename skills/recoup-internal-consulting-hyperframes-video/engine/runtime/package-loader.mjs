import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import dependencies from './dependencies.cjs';
const manifest = JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf8'));

export function hyperframesPackageSpec(name) {
  const version = manifest.dependencies[name];
  if (!version || !/^\d+\.\d+\.\d+(?:-[\w.-]+)?$/.test(version)) {
    throw new Error(`No pinned dependency declared for ${name}`);
  }
  return `${name}@${version}`;
}
export async function importPackagesOrBootstrap(names, options = {}) {
  // Retain the callers' interface; setup is explicit and never runs an npm install during a render.
  const modules = {};
  for (const name of names) {
    modules[name] = await import(pathToFileURL(dependencies.resolvePackage(name)).href);
  }
  return modules;
}
