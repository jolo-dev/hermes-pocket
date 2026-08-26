export function assertExactKeys(
  value: unknown,
  allowedKeys: readonly string[],
  boundaryName: string,
): asserts value is Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`Invalid ${boundaryName}`);
  }
  if (Object.keys(value).some(key => !allowedKeys.includes(key))) {
    throw new Error(`Invalid ${boundaryName}`);
  }
}

export function requireString(value: unknown, boundaryName: string): string {
  if (typeof value !== 'string') {
    throw new Error(`Invalid ${boundaryName}`);
  }
  return value;
}
