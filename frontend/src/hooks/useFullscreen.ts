/**
 * useFullscreen — Mandatory fullscreen enforcement hook for proctored sessions.
 *
 * Enters fullscreen on mount, monitors for exit, and exposes the current state
 * and a re-enter handler so the calling page can show a blocking overlay.
 */
import { useState, useEffect, useCallback, useRef } from 'react';

export interface UseFullscreenOptions {
  /** Callback fired each time fullscreen is exited (for logging proctoring events). */
  onExit?: () => void;
  /** Set to false to disable enforcement (e.g., in dev/non-proctored contexts). */
  enabled?: boolean;
}

export interface UseFullscreenReturn {
  isFullscreen: boolean;
  enterFullscreen: () => Promise<void>;
  exitBlocked: boolean; // true while user is outside fullscreen mid-session
}

export function useFullscreen({
  onExit,
  enabled = true,
}: UseFullscreenOptions = {}): UseFullscreenReturn {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [exitBlocked, setExitBlocked] = useState(false);
  const mountedRef = useRef(false);

  const enterFullscreen = useCallback(async () => {
    if (!document.fullscreenEnabled) return;
    try {
      await document.documentElement.requestFullscreen({ navigationUI: 'hide' });
      setIsFullscreen(true);
      setExitBlocked(false);
    } catch (err) {
      console.warn('[useFullscreen] Could not enter fullscreen:', err);
    }
  }, []);

  // Listen for browser fullscreen change events
  useEffect(() => {
    if (!enabled) return;

    const handleChange = () => {
      const inFullscreen = !!document.fullscreenElement;
      setIsFullscreen(inFullscreen);

      if (!inFullscreen && mountedRef.current) {
        // User exited fullscreen during an active session
        setExitBlocked(true);
        onExit?.();
      }
    };

    document.addEventListener('fullscreenchange', handleChange);
    document.addEventListener('webkitfullscreenchange', handleChange); // Safari

    return () => {
      document.removeEventListener('fullscreenchange', handleChange);
      document.removeEventListener('webkitfullscreenchange', handleChange);
    };
  }, [enabled, onExit]);

  // Auto-enter fullscreen on mount (after a brief tick so DOM is ready)
  useEffect(() => {
    if (!enabled) return;
    mountedRef.current = false; // Don't fire onExit during initial entry

    const timer = setTimeout(async () => {
      await enterFullscreen();
      mountedRef.current = true; // Start monitoring after initial entry
    }, 400);

    return () => {
      clearTimeout(timer);
      // Exit fullscreen gracefully when the proctored component unmounts
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      }
      mountedRef.current = false;
    };
  }, [enabled, enterFullscreen]);

  return { isFullscreen, enterFullscreen, exitBlocked };
}
