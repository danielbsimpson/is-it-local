/**
 * Lightweight local logging. Writes structured events to the browser console.
 * No third-party analytics or monitoring is used in the PoC (REQ-008).
 */

export type LogProps = Record<string, unknown>;

export function logEvent(name: string, props: LogProps = {}): void {
  // eslint-disable-next-line no-console
  console.info(`[is-it-local] ${name}`, props);
}

export function logError(error: unknown, props: LogProps = {}): void {
  // eslint-disable-next-line no-console
  console.error("[is-it-local] error", { error, ...props });
}
