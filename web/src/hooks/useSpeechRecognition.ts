import { useCallback, useEffect, useRef, useState } from "react";
import { getLang, SPEECH_LOCALES, translate, type TKey } from "../i18n";

// Types minimaux de l'API Web Speech (absente des types DOM standard).
interface RecognitionAlternative {
  transcript: string;
}
interface RecognitionResult {
  isFinal: boolean;
  0: RecognitionAlternative;
}
interface RecognitionEvent {
  resultIndex: number;
  results: ArrayLike<RecognitionResult>;
}
interface Recognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: RecognitionEvent) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
}
type RecognitionConstructor = new () => Recognition;

const ERROR_MESSAGES: Record<string, TKey> = {
  "not-allowed": "speech.notAllowed",
  "service-not-allowed": "speech.serviceNotAllowed",
  network: "speech.network",
  "audio-capture": "speech.audioCapture",
};
const IGNORED_ERRORS = new Set(["no-speech", "aborted"]);

function getConstructor(): RecognitionConstructor | null {
  const w = window as unknown as {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

interface SpeechState {
  supported: boolean;
  listening: boolean;
  interim: string;
  error: string | null;
  start: () => void;
  stop: () => void;
}

/** Dictée vocale gratuite du navigateur (dans la langue de l'interface) ; `onFinalText` reçoit chaque phrase validée. */
export function useSpeechRecognition(onFinalText: (text: string) => void): SpeechState {
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<Recognition | null>(null);
  const wantedRef = useRef(false);
  const callbackRef = useRef(onFinalText);
  callbackRef.current = onFinalText;
  const supported = getConstructor() !== null;

  const stop = useCallback(() => {
    wantedRef.current = false;
    recognitionRef.current?.stop();
    setInterim("");
  }, []);

  const start = useCallback(() => {
    const Ctor = getConstructor();
    if (!Ctor) return;
    const recognition = new Ctor();
    recognition.lang = SPEECH_LOCALES[getLang()];
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      let pending = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) callbackRef.current(result[0].transcript.trim());
        else pending += result[0].transcript;
      }
      setInterim(pending);
    };
    recognition.onerror = (event) => {
      if (IGNORED_ERRORS.has(event.error)) return;
      wantedRef.current = false;
      const key = ERROR_MESSAGES[event.error];
      setError(key ? translate(key) : translate("speech.generic", { code: event.error }));
    };
    recognition.onend = () => {
      // Chrome coupe la dictée après un silence : on relance tant que l'utilisateur la veut.
      if (wantedRef.current) {
        recognition.start();
        return;
      }
      setListening(false);
      setInterim("");
    };
    recognitionRef.current = recognition;
    wantedRef.current = true;
    setError(null);
    setListening(true);
    recognition.start();
  }, []);

  useEffect(() => () => stop(), [stop]);

  return { supported, listening, interim, error, start, stop };
}
