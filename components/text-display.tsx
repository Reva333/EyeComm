"use client"

interface TextDisplayProps {
  text: string
}

export default function TextDisplay({ text }: TextDisplayProps) {
  return (
    <div className="bg-primary border-b-2 border-accent p-6 flex flex-col gap-3 pr-80">
      <div className="bg-background rounded-lg p-6 min-h-20 max-h-28 overflow-y-auto border-2 border-secondary">
        <p className="text-lg text-foreground whitespace-pre-wrap break-words font-medium">
          {text || <span className="text-muted-foreground italic">Text will appear here...</span>}
        </p>
      </div>
    </div>
  )
}
