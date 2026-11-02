import { convertToExcalidrawElements, ROUNDNESS } from "@excalidraw/excalidraw";
import type { ExcalidrawElementSkeleton } from "@excalidraw/excalidraw/data/transform";
import type { NonDeletedExcalidrawElement } from "@excalidraw/excalidraw/element/types";
import type { LibraryItem } from "@excalidraw/excalidraw/types";

/** Formes prêtes à l'emploi du panneau Bibliothèque (le cylindre n'existe pas parmi les outils). */

interface Marking {
  groupIds: string[];
  customData: { component: string };
}

type Point = [number, number];

const mark = (group: string, component: string): Marking => ({
  groupIds: [group],
  customData: { component },
});

const ellipse = (x: number, y: number, width: number, height: number, m: Marking) =>
  ({ type: "ellipse", x, y, width, height, ...m }) satisfies ExcalidrawElementSkeleton;

const rectangle = (x: number, y: number, width: number, height: number, m: Marking) =>
  ({ type: "rectangle", x, y, width, height, ...m }) satisfies ExcalidrawElementSkeleton;

const line = (x: number, y: number, points: Point[], m: Marking, curved = false) =>
  ({
    type: "line",
    x,
    y,
    points,
    ...(curved ? { roundness: { type: ROUNDNESS.PROPORTIONAL_RADIUS } } : {}),
    ...m,
  }) satisfies ExcalidrawElementSkeleton;

const label = (text: string, x: number, y: number, m: Marking) =>
  ({ type: "text", text, x, y, ...m }) satisfies ExcalidrawElementSkeleton;

const CYLINDER_WIDTH = 100;
const CYLINDER_CAP = 30;
const CYLINDER_BODY = 70;

function database(): ExcalidrawElementSkeleton[] {
  const m = mark("lib-database", "database");
  const half = CYLINDER_CAP / 2;
  return [
    ellipse(0, 0, CYLINDER_WIDTH, CYLINDER_CAP, m),
    line(0, half, [[0, 0], [0, CYLINDER_BODY]], m),
    line(CYLINDER_WIDTH, half, [[0, 0], [0, CYLINDER_BODY]], m),
    line(0, half + CYLINDER_BODY, [[0, 0], [CYLINDER_WIDTH / 2, CYLINDER_CAP], [CYLINDER_WIDTH, 0]], m, true),
    label("DB", 38, 45, m),
  ];
}

function queue(): ExcalidrawElementSkeleton[] {
  const m = mark("lib-queue", "queue");
  const dividers = [35, 70, 105].map((x) => line(x, 0, [[0, 0], [0, 40]], m));
  return [rectangle(0, 0, 140, 40, m), ...dividers, label("Queue", 48, 50, m)];
}

function externalService(): ExcalidrawElementSkeleton[] {
  const m = mark("lib-cloud", "cloud");
  return [{ ...ellipse(0, 0, 150, 80, m), strokeStyle: "dashed" }, label("Service externe", 20, 32, m)];
}

function user(): ExcalidrawElementSkeleton[] {
  const m = mark("lib-user", "user");
  return [
    ellipse(15, 0, 30, 30, m),
    line(30, 30, [[0, 0], [0, 45]], m),
    line(8, 45, [[0, 0], [44, 0]], m),
    line(30, 75, [[0, 0], [-20, 30]], m),
    line(30, 75, [[0, 0], [20, 30]], m),
    label("Utilisateur", -8, 112, m),
  ];
}

const SHAPES: { id: string; name: string; build: () => ExcalidrawElementSkeleton[] }[] = [
  { id: "lib-database", name: "Base de données (cylindre)", build: database },
  { id: "lib-queue", name: "File / queue", build: queue },
  { id: "lib-cloud", name: "Service externe", build: externalService },
  { id: "lib-user", name: "Utilisateur", build: user },
];

/** Éléments de la bibliothèque préchargée dans Excalidraw. */
export function buildLibraryItems(): LibraryItem[] {
  const created = Date.now();
  return SHAPES.map((shape) => ({
    id: shape.id,
    name: shape.name,
    status: "unpublished",
    created,
    elements: convertToExcalidrawElements(shape.build()) as NonDeletedExcalidrawElement[],
  }));
}
