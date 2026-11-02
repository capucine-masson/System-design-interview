import { vi } from "vitest";

/** Faux Excalidraw pour jsdom : capture les props reçues et permet de simuler des modifications. */

export interface CapturedProps {
  initialData?: { elements?: unknown[]; appState?: Record<string, unknown>; libraryItems?: unknown[] };
  onChange?: (elements: unknown[], appState: { viewBackgroundColor: string }) => void;
  excalidrawAPI?: (api: unknown) => void;
  theme?: string;
  langCode?: string;
  viewModeEnabled?: boolean;
  UIOptions?: { tools?: { image?: boolean } };
}

export const excalidraw = {
  props: null as CapturedProps | null,
  updateScene: vi.fn(),
};

export const excalidrawModule = {
  Excalidraw: (props: CapturedProps) => {
    excalidraw.props = props;
    props.excalidrawAPI?.({ updateScene: excalidraw.updateScene });
    return <div data-testid="excalidraw" />;
  },
  convertToExcalidrawElements: (skeleton: unknown[]) => skeleton,
  restoreElements: (elements: unknown[]) => elements,
  ROUNDNESS: { PROPORTIONAL_RADIUS: 2 },
  CaptureUpdateAction: { IMMEDIATELY: "IMMEDIATELY" },
};
