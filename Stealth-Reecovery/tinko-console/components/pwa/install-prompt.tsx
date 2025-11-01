"use client";

import { useState, useEffect } from "react";
import { X, Download, Smartphone } from "lucide-react";

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: "accepted" | "dismissed";
    platform: string;
  }>;
  prompt(): Promise<void>;
}

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if app is already installed
    const isInStandaloneMode = () =>
      window.matchMedia("(display-mode: standalone)").matches ||
      (window.navigator as { standalone?: boolean }).standalone ||
      document.referrer.includes("android-app://");

    setIsStandalone(isInStandaloneMode());

    // Detect iOS
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as { MSStream?: unknown }).MSStream;
    setIsIOS(iOS);

    // Check if user has dismissed the prompt before
    const dismissed = localStorage.getItem("pwa-install-dismissed");
    const dismissedDate = dismissed ? new Date(dismissed) : null;
    const daysSinceDismissed = dismissedDate
      ? (Date.now() - dismissedDate.getTime()) / (1000 * 60 * 60 * 24)
      : 999;

    // Show prompt if:
    // 1. Not in standalone mode
    // 2. Either iOS or has deferredPrompt
    // 3. Not dismissed in last 7 days
    if (!isInStandaloneMode() && daysSinceDismissed > 7) {
      if (iOS) {
        // Show iOS prompt after 30 seconds
        const timer = setTimeout(() => setShowPrompt(true), 30000);
        return () => clearTimeout(timer);
      }
    }

    // Listen for beforeinstallprompt event
    const handler = (e: Event) => {
      e.preventDefault();
      const installEvent = e as BeforeInstallPromptEvent;
      setDeferredPrompt(installEvent);
      
      // Show prompt after 30 seconds of interaction
      const timer = setTimeout(() => {
        if (daysSinceDismissed > 7) {
          setShowPrompt(true);
        }
      }, 30000);
      
      return () => clearTimeout(timer);
    };

    window.addEventListener("beforeinstallprompt", handler);

    return () => {
      window.removeEventListener("beforeinstallprompt", handler);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    try {
      await deferredPrompt.prompt();
      const choiceResult = await deferredPrompt.userChoice;

      if (choiceResult.outcome === "accepted") {
        console.log("User accepted the install prompt");
      } else {
        console.log("User dismissed the install prompt");
      }

      setDeferredPrompt(null);
      setShowPrompt(false);
    } catch (error) {
      console.error("Error showing install prompt:", error);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem("pwa-install-dismissed", new Date().toISOString());
  };

  // Don't show if already installed
  if (isStandalone) return null;

  // Don't show if user closed it
  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:bottom-4 sm:left-4 sm:right-auto sm:max-w-md animate-slide-up">
      <div className="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-strong">
        <button
          onClick={handleDismiss}
          className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
          aria-label="Dismiss install prompt"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-start gap-4">
          <div className="rounded-xl bg-primary-100 p-3">
            {isIOS ? (
              <Smartphone className="h-6 w-6 text-primary-600" />
            ) : (
              <Download className="h-6 w-6 text-primary-600" />
            )}
          </div>

          <div className="flex-1">
            <h3 className="text-lg font-semibold text-slate-900 mb-1">
              Install Tinko Recovery
            </h3>
            <p className="text-sm text-slate-600 mb-4">
              {isIOS
                ? "Add to your home screen for quick access and offline support."
                : "Install our app for a faster experience with offline support."}
            </p>

            {isIOS ? (
              <div className="space-y-2 rounded-lg bg-blue-50 border border-blue-200 p-3">
                <p className="text-xs font-medium text-blue-900">How to install on iOS:</p>
                <ol className="text-xs text-blue-700 space-y-1 ml-4 list-decimal">
                  <li>Tap the Share button in Safari</li>
                  <li>Scroll down and tap &quot;Add to Home Screen&quot;</li>
                  <li>Tap &quot;Add&quot; in the top right corner</li>
                </ol>
              </div>
            ) : (
              <button
                onClick={handleInstall}
                className="btn-primary w-full py-2.5 text-sm"
              >
                Install Now
              </button>
            )}

            {!isIOS && (
              <button
                onClick={handleDismiss}
                className="mt-2 w-full text-center text-xs text-slate-500 hover:text-slate-700 transition-colors"
              >
                Maybe later
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
