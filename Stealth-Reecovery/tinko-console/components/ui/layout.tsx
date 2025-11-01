import * as React from "react"
import { cn } from "@/lib/utils"

interface PageHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  actions?: React.ReactNode
}

function PageHeader({ className, children, actions, ...props }: PageHeaderProps) {
  return (
    <div className={cn("flex items-start justify-between gap-space-4 mb-space-6", className)} {...props}>
      <div className="space-y-space-2 flex-1">{children}</div>
      {actions && <div className="flex items-center gap-space-2">{actions}</div>}
    </div>
  )
}

function PageTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h1
      className={cn("text-3xl font-bold tracking-tighter text-foreground", className)}
      {...props}
    />
  )
}

function PageDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn("text-base text-muted-foreground leading-normal", className)}
      {...props}
    />
  )
}

function Section({ className, ...props }: React.HTMLAttributes<HTMLElement>) {
  return (
    <section
      className={cn("space-y-space-4", className)}
      {...props}
    />
  )
}

function SectionHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("space-y-space-1 mb-space-4", className)} {...props} />
  )
}

function SectionTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2
      className={cn("text-xl font-semibold tracking-tighter text-foreground", className)}
      {...props}
    />
  )
}

function SectionDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn("text-sm text-muted-foreground leading-normal", className)}
      {...props}
    />
  )
}

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg" | "xl" | "2xl" | "full"
}

function Container({ className, size = "xl", ...props }: ContainerProps) {
  return (
    <div
      className={cn(
        "mx-auto w-full",
        "px-space-4 sm:px-space-6 lg:px-space-8",
        size === "sm" && "max-w-2xl",
        size === "md" && "max-w-4xl",
        size === "lg" && "max-w-6xl",
        size === "xl" && "max-w-7xl",
        size === "2xl" && "max-w-screen-2xl",
        size === "full" && "max-w-full",
        className
      )}
      {...props}
    />
  )
}

export {
  PageHeader,
  PageTitle,
  PageDescription,
  Section,
  SectionHeader,
  SectionTitle,
  SectionDescription,
  Container,
}
