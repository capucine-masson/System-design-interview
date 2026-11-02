import { useCallback, useEffect, useMemo, useRef } from "react";

interface Autosave<T> {
  /** Planifie la sauvegarde de la dernière valeur (anti-rebond + délai maximal). */
  schedule: (value: T) => void;
  /** Sauvegarde immédiatement ce qui est en attente (changement de page, fermeture). */
  flush: () => void;
}

/**
 * Sauvegarde automatique : attend `debounceMs` sans changement, mais jamais plus de `maxWaitMs`
 * depuis la première modification non enregistrée.
 */
export function useAutosave<T>(
  save: (value: T) => void,
  debounceMs: number,
  maxWaitMs: number,
): Autosave<T> {
  const pending = useRef<{ value: T } | null>(null);
  const debounceTimer = useRef<number | null>(null);
  const maxTimer = useRef<number | null>(null);
  const saveRef = useRef(save);
  saveRef.current = save;

  const clearTimers = useCallback(() => {
    if (debounceTimer.current !== null) window.clearTimeout(debounceTimer.current);
    if (maxTimer.current !== null) window.clearTimeout(maxTimer.current);
    debounceTimer.current = null;
    maxTimer.current = null;
  }, []);

  const flush = useCallback(() => {
    clearTimers();
    const current = pending.current;
    pending.current = null;
    if (current) saveRef.current(current.value);
  }, [clearTimers]);

  const schedule = useCallback(
    (value: T) => {
      pending.current = { value };
      if (debounceTimer.current !== null) window.clearTimeout(debounceTimer.current);
      debounceTimer.current = window.setTimeout(flush, debounceMs);
      if (maxTimer.current === null) maxTimer.current = window.setTimeout(flush, maxWaitMs);
    },
    [debounceMs, maxWaitMs, flush],
  );

  useEffect(() => clearTimers, [clearTimers]);

  return useMemo(() => ({ schedule, flush }), [schedule, flush]);
}
