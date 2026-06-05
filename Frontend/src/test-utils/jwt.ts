/** Construit un faux JWT (header.payload.signature) pour les tests unitaires. */
export function buildTestJwt(payload: Record<string, unknown>): string {
  const encode = (value: object) =>
    btoa(JSON.stringify(value))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '')

  return `header.${encode(payload)}.signature`
}
