import * as React from "react"
import { cn } from "@/lib/utils"
import { Label } from "./label"

type FormFieldContextValue = {
  id: string
  error?: boolean
  errorMessage?: string
}

const FormFieldContext = React.createContext<FormFieldContextValue | undefined>(undefined)

function useFormFieldContext() {
  const context = React.useContext(FormFieldContext)
  if (!context) {
    throw new Error("FormField components must be used within FormField")
  }
  return context
}

interface FormFieldProps {
  children: React.ReactNode
  error?: boolean
  errorMessage?: string
  className?: string
}

function FormField({ children, error, errorMessage, className }: FormFieldProps) {
  const id = React.useId()
  
  return (
    <FormFieldContext.Provider value={{ id, error, errorMessage }}>
      <div className={cn("space-y-space-2", className)}>
        {children}
      </div>
    </FormFieldContext.Provider>
  )
}

interface FormLabelProps extends React.ComponentPropsWithoutRef<typeof Label> {
  required?: boolean
}

function FormLabel({ children, required, ...props }: FormLabelProps) {
  const { id } = useFormFieldContext()
  
  return (
    <Label htmlFor={id} {...props}>
      {children}
      {required && <span className="text-destructive ml-1" aria-label="required">*</span>}
    </Label>
  )
}

interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
}

function FormInput({ error: errorProp, ...props }: FormInputProps) {
  const { id, error: contextError, errorMessage } = useFormFieldContext()
  const error = errorProp ?? contextError
  
  return (
    <input
      id={id}
      aria-invalid={error}
      aria-describedby={error && errorMessage ? `${id}-error` : undefined}
      className={cn(
        "flex h-10 w-full rounded-lg border bg-card px-space-4 py-space-2 text-sm shadow-xs transition-all duration-base ease-spring",
        "placeholder:text-muted-foreground",
        "focus:outline-none focus:outline-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-muted",
        "dark:bg-card dark:text-foreground",
        !error && "border-input focus:border-primary focus:ring-2 focus:ring-primary/20",
        error && "border-destructive focus:border-destructive focus:ring-2 focus:ring-destructive/20"
      )}
      {...props}
    />
  )
}

interface FormTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean
  autoResize?: boolean
}

function FormTextarea({ error: errorProp, autoResize, onChange, ...props }: FormTextareaProps) {
  const { id, error: contextError, errorMessage } = useFormFieldContext()
  const error = errorProp ?? contextError
  const textareaRef = React.useRef<HTMLTextAreaElement | null>(null)

  const resizeTextarea = React.useCallback(() => {
    const textarea = textareaRef.current
    if (textarea && autoResize) {
      textarea.style.height = "auto"
      textarea.style.height = `${textarea.scrollHeight}px`
    }
  }, [autoResize])

  React.useEffect(() => {
    if (autoResize) {
      resizeTextarea()
    }
  }, [autoResize, resizeTextarea])

  const handleChange = React.useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      if (autoResize) {
        resizeTextarea()
      }
      onChange?.(e)
    },
    [autoResize, onChange, resizeTextarea]
  )
  
  return (
    <textarea
      id={id}
      ref={textareaRef}
      aria-invalid={error}
      aria-describedby={error && errorMessage ? `${id}-error` : undefined}
      onChange={handleChange}
      className={cn(
        "flex min-h-[80px] w-full rounded-lg border bg-card px-space-4 py-space-3 text-sm shadow-xs transition-all duration-base ease-spring resize-y",
        "placeholder:text-muted-foreground",
        "focus:outline-none focus:outline-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-muted disabled:resize-none",
        "dark:bg-card dark:text-foreground",
        !error && "border-input focus:border-primary focus:ring-2 focus:ring-primary/20",
        error && "border-destructive focus:border-destructive focus:ring-2 focus:ring-destructive/20",
        autoResize && "resize-none overflow-hidden"
      )}
      {...props}
    />
  )
}

function FormDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn("text-xs text-muted-foreground", className)}
      {...props}
    />
  )
}

function FormError() {
  const { id, error, errorMessage } = useFormFieldContext()
  
  if (!error || !errorMessage) return null
  
  return (
    <p
      id={`${id}-error`}
      className="text-xs text-destructive font-medium"
      role="alert"
    >
      {errorMessage}
    </p>
  )
}

export { FormField, FormLabel, FormInput, FormTextarea, FormDescription, FormError }
