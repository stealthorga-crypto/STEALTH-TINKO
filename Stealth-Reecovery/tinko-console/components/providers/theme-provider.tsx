/**
 * Theme Provider Component
 * 
 * Wraps the app with next-themes ThemeProvider.
 * Handles system preference detection and theme persistence.
 */

"use client"

import { ThemeProvider as NextThemesProvider } from 'next-themes'
import { type ReactNode } from 'react'

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange={false}
      storageKey="tinko-theme"
    >
      {children}
    </NextThemesProvider>
  )
}

// Re-export useTheme from next-themes for convenience
export { useTheme } from 'next-themes'
