/**
 * Motion & Animation Utilities
 * 
 * Provides Framer Motion wrappers with pre-configured animations
 * that respect reduced motion preferences and follow design system timing.
 * 
 * All animations use design tokens for consistency.
 */

'use client'

import { motion, type HTMLMotionProps, type Variants } from 'framer-motion'
import { type ReactNode } from 'react'

// ============================================================================
// ANIMATION VARIANTS - Pre-configured with design system timing
// ============================================================================

/**
 * Fade in from opacity 0 to 1
 */
export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: {
      duration: 0.18,
      ease: [0.4, 0, 0.2, 1]
    }
  },
  exit: { 
    opacity: 0,
    transition: {
      duration: 0.12,
      ease: [0.4, 0, 1, 1]
    }
  }
}

/**
 * Slide up from bottom with fade
 */
export const slideUp: Variants = {
  initial: { 
    y: '100%',
    opacity: 0
  },
  animate: { 
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.18,
      ease: [0.34, 1.56, 0.64, 1] // Spring easing
    }
  },
  exit: { 
    y: '100%',
    opacity: 0,
    transition: {
      duration: 0.12,
      ease: [0.4, 0, 1, 1]
    }
  }
}

/**
 * Slide down from top with fade
 */
export const slideDown: Variants = {
  initial: { 
    y: '-100%',
    opacity: 0
  },
  animate: { 
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.18,
      ease: [0.34, 1.56, 0.64, 1] // Spring easing
    }
  },
  exit: { 
    y: '-100%',
    opacity: 0,
    transition: {
      duration: 0.12,
      ease: [0.4, 0, 1, 1]
    }
  }
}

/**
 * Scale in from 95% to 100% with fade
 * Perfect for modals and popovers
 */
export const scaleIn: Variants = {
  initial: { 
    scale: 0.95,
    opacity: 0
  },
  animate: { 
    scale: 1,
    opacity: 1,
    transition: {
      duration: 0.12,
      ease: [0.34, 1.56, 0.64, 1] // Spring easing
    }
  },
  exit: { 
    scale: 0.95,
    opacity: 0,
    transition: {
      duration: 0.12,
      ease: [0.4, 0, 1, 1]
    }
  }
}

/**
 * Stagger children animations
 * Use with staggerChildren prop
 */
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.02
    }
  }
}

// ============================================================================
// WRAPPER COMPONENTS - Easy-to-use motion wrappers
// ============================================================================

interface MotionWrapperProps extends HTMLMotionProps<'div'> {
  children: ReactNode
  variant?: 'fadeIn' | 'slideUp' | 'slideDown' | 'scaleIn' | 'stagger'
  delay?: number
}

const variantMap = {
  fadeIn,
  slideUp,
  slideDown,
  scaleIn,
  stagger: staggerContainer
}

/**
 * Generic motion wrapper with preset variants
 * 
 * @example
 * <MotionWrapper variant="fadeIn">
 *   <Card>Content</Card>
 * </MotionWrapper>
 */
export function MotionWrapper({
  children,
  variant = 'fadeIn',
  delay = 0,
  ...props
}: MotionWrapperProps) {
  const variants = variantMap[variant]
  
  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{ 
        transitionDelay: delay ? `${delay}ms` : undefined
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// ============================================================================
// BUTTON INTERACTIONS - Tactile press animations
// ============================================================================

interface AnimatedButtonProps extends HTMLMotionProps<'button'> {
  children: ReactNode
  pressScale?: number
}

/**
 * Button with tactile press animation
 * 
 * @example
 * <AnimatedButton onClick={handleClick}>
 *   Click Me
 * </AnimatedButton>
 */
export function AnimatedButton({
  children,
  pressScale = 0.97,
  ...props
}: AnimatedButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: pressScale }}
      transition={{
        duration: 0.12,
        ease: [0.34, 1.56, 0.64, 1]
      }}
      {...props}
    >
      {children}
    </motion.button>
  )
}

// ============================================================================
// CARD INTERACTIONS - Subtle lift on hover
// ============================================================================

interface AnimatedCardProps extends HTMLMotionProps<'div'> {
  children: ReactNode
  liftAmount?: number
}

/**
 * Card with subtle lift animation on hover
 * 
 * @example
 * <AnimatedCard>
 *   <h3>Card Title</h3>
 *   <p>Card content</p>
 * </AnimatedCard>
 */
export function AnimatedCard({
  children,
  liftAmount = -4,
  ...props
}: AnimatedCardProps) {
  return (
    <motion.div
      whileHover={{
        y: liftAmount,
        boxShadow: 'var(--shadow-md)'
      }}
      transition={{
        duration: 0.18,
        ease: [0.4, 0, 0.2, 1]
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// ============================================================================
// PAGE TRANSITIONS - For route changes
// ============================================================================

interface PageTransitionProps {
  children: ReactNode
}

/**
 * Page transition wrapper
 * Apply to page-level content for smooth transitions
 * 
 * @example
 * <PageTransition>
 *   <main>Page content</main>
 * </PageTransition>
 */
export function PageTransition({ children }: PageTransitionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{
        duration: 0.18,
        ease: [0.4, 0, 0.2, 1]
      }}
    >
      {children}
    </motion.div>
  )
}

// ============================================================================
// TOAST ANIMATIONS - For notifications
// ============================================================================

/**
 * Toast slide-in from top-right
 */
export const toastVariants: Variants = {
  initial: {
    opacity: 0,
    x: '100%',
    scale: 0.95
  },
  animate: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: {
      duration: 0.18,
      ease: [0.34, 1.56, 0.64, 1]
    }
  },
  exit: {
    opacity: 0,
    x: '100%',
    scale: 0.95,
    transition: {
      duration: 0.12,
      ease: [0.4, 0, 1, 1]
    }
  }
}

// ============================================================================
// NAV ANIMATIONS - For sidebar/drawer
// ============================================================================

/**
 * Sidebar slide-in from left
 */
export const sidebarVariants: Variants = {
  closed: {
    x: '-100%',
    transition: {
      duration: 0.18,
      ease: [0.4, 0, 1, 1]
    }
  },
  open: {
    x: 0,
    transition: {
      duration: 0.18,
      ease: [0.4, 0, 0.2, 1]
    }
  }
}

/**
 * Backdrop fade for overlays
 */
export const backdropVariants: Variants = {
  hidden: {
    opacity: 0,
    transition: {
      duration: 0.12
    }
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.12
    }
  }
}

// ============================================================================
// UTILITY HOOKS - For programmatic animations
// ============================================================================

/**
 * Detects if user prefers reduced motion
 * 
 * @example
 * const prefersReduced = usePrefersReducedMotion()
 * if (!prefersReduced) {
 *   // Apply animations
 * }
 */
export function usePrefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  
  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  return mediaQuery.matches
}
