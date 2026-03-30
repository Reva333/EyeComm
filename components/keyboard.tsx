"use client"
import KeyButton from "./key-button"

interface KeyboardProps {
  onKeyPress: (key: string) => void
}

const KEYBOARD_LAYOUT = [
  ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
  ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
  ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Backspace"],
  ["Z", "X", "C", "V", "B", "N", "M", ".", ",", "?"],
  ["Space", "Enter", "Clear"],
]

export default function Keyboard({ onKeyPress }: KeyboardProps) {
  return (
    <div className="flex-1 bg-background p-2 flex flex-col justify-center gap-2 overflow-hidden">
      {KEYBOARD_LAYOUT.map((row, rowIndex) => (
        <div key={rowIndex} className="flex gap-2 justify-center flex-1">
          {row.map((key) => (
            <KeyButton
              key={key}
              label={key}
              dataKey={key}
              onPress={() => onKeyPress(key)}
              isWide={key === "Space" || key === "Enter" || key === "Clear"}
            />
          ))}
        </div>
      ))}
    </div>
  )
}
