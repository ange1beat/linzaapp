/**
 * Converts snake_case keys to camelCase recursively.
 * Used to transform backend (Python/snake_case) responses
 * to frontend (TypeScript/camelCase) format.
 */
function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
}

export function snakeToCamel<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((item) => snakeToCamel(item)) as T;
  }
  if (obj !== null && typeof obj === "object" && !(obj instanceof Date)) {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
      result[toCamelCase(key)] = snakeToCamel(value);
    }
    return result as T;
  }
  return obj as T;
}

export function camelToSnake<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((item) => camelToSnake(item)) as T;
  }
  if (obj !== null && typeof obj === "object" && !(obj instanceof Date)) {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
      result[toSnakeCase(key)] = camelToSnake(value);
    }
    return result as T;
  }
  return obj as T;
}
