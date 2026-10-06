/**
 * FullscreenBlocker — Full-screen overlay that blocks the test UI when the student
 * exits fullscreen mode during a proctored session.
 *
 * Renders a modal urging the student to re-enter fullscreen.
 * Parent pages trigger this via the `exitBlocked` state from `useFullscreen`.
 */
import { Maximize2, ShieldAlert } from 'lucide-react';

interface FullscreenBlockerProps {
  onReenter: () => void;
  warningNumber?: number;
}

export default function FullscreenBlocker({ onReenter, warningNumber = 1 }: FullscreenBlockerProps) {
  return (
    <div
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-black/95 backdrop-blur-xl"
      style={{ userSelect: 'none' }}
    >
      {/* Animated shield */}
      <div className="relative mb-8">
        <div className="w-28 h-28 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center animate-pulse">
          <div className="w-20 h-20 rounded-full bg-red-500/20 border border-red-500/50 flex items-center justify-center">
            <ShieldAlert size={40} className="text-red-400" />
          </div>
        </div>
        {/* Warning badge */}
        <div className="absolute -top-1 -right-1 w-8 h-8 rounded-full bg-red-600 border-2 border-background flex items-center justify-center text-xs font-bold text-white">
          {warningNumber}
        </div>
      </div>

      <h1 className="text-2xl font-bold text-white mb-3 font-display tracking-tight">
        Fullscreen Required
      </h1>
      <p className="text-muted-foreground text-sm text-center max-w-sm mb-2 leading-relaxed">
        You exited fullscreen mode. This violation has been logged and reported to your trainer.
      </p>
      <p className="text-red-400 text-xs font-semibold mb-8 text-center">
        Your test session is paused until you return to fullscreen.
      </p>

      {/* Proctoring violation count */}
      <div className="mb-8 px-4 py-2 rounded-full bg-red-500/10 border border-red-500/30 text-red-300 text-xs font-semibold">
        Violation #{warningNumber} recorded in audit trail
      </div>

      <button
        onClick={onReenter}
        className="px-6 py-2.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-bold text-xs flex items-center gap-2 shadow-subtle transition-colors"
      >
        <Maximize2 size={16} />
        Return to Fullscreen
      </button>

      <p className="mt-6 text-muted-foreground/50 text-xs text-center">
        Multiple violations may result in automatic test termination.
      </p>
    </div>
  );
}
