"use client";

import en from "@/locales/en";
import ta from "@/locales/ta";
import hi from "@/locales/hi";

type Dict = typeof en;

const dictionaries: Record<string, Dict> = {
  en,
  ta: ta as any,
  hi: hi as any,
};

export function useI18n() {
  // Minimal client-side locale selection; defaults to 'en'
  let locale = "en";
  if (typeof window !== "undefined") {
    locale = (localStorage.getItem("locale") || "en").toLowerCase();
  }
  const dict = dictionaries[locale] || en;
  const t = (path: string): string => {
    const parts = path.split(".");
    let cur: any = dict;
    for (const p of parts) {
      cur = cur?.[p];
      if (cur === undefined) return path; // fallback to key
    }
    return typeof cur === "string" ? cur : path;
  };
  return { t, locale };
}
