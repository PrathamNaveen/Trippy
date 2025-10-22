export function sanitizeCollectionName(name: string): string {
  // Replace invalid characters with underscore
  let sanitized = name.replace(/[^a-zA-Z0-9._-]/g, "_");
  // Ensure starts/ends with letter/number
  sanitized = sanitized.replace(/^[^a-zA-Z0-9]+/, "").replace(/[^a-zA-Z0-9]+$/, "");
  if (sanitized.length < 3) sanitized += "_01";
  if (sanitized.length > 512) sanitized = sanitized.slice(0, 512);
  return sanitized;
}

export function isValidCollectionName(name: string): boolean {
  const regex = /^[a-zA-Z0-9]([a-zA-Z0-9._-]{1,510}[a-zA-Z0-9])?$/;
  return regex.test(name);
}
