import { useCallback, useEffect, useRef, useState } from "react";

const TICK_MS = 1000;

interface Elapsed {
  elapsed: number;
  /** Valeur courante, lisible sans re-render (pour les envois au serveur). */
  getElapsed: () => number;
}

/** Temps passé sur la session : compte seconde par seconde, onglet visible et session ouverte. */
export function useElapsed(initial: number, running: boolean): Elapsed {
  const [elapsed, setElapsed] = useState(initial);
  const ref = useRef(initial);

  useEffect(() => {
    if (!running) return;
    const id = window.setInterval(() => {
      if (document.visibilityState === "hidden") return;
      ref.current += 1;
      setElapsed(ref.current);
    }, TICK_MS);
    return () => window.clearInterval(id);
  }, [running]);

  const getElapsed = useCallback(() => ref.current, []);
  return { elapsed, getElapsed };
}
