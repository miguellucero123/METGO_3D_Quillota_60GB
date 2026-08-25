/** Cache de hub/mis-faenas para el router (sin ciclo import router↔auth). */

/** @type {{ at: number, catalogo_completo: boolean, slugs: Set<string> } | null} */
let hubCache = null

export function getHubCache() {
  return hubCache
}

export function setHubCache(value) {
  hubCache = value
}

export function invalidateHubCache() {
  hubCache = null
}
