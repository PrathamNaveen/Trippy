'use client';

import { KeyboardEvent } from "react";

interface Props {
  value: string;
  onChange: (val: string) => void;
  onSend: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ value, onChange, onSend, disabled, placeholder }: Props) {
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") onSend();
  };

  return (
    <div className="flex p-4 border-t border-gray-700">
      <input
        type="text"
        placeholder={placeholder || "Type your question..."}
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className="flex-1 p-3 rounded-lg bg-gray-800 text-gray-100 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        onClick={onSend}
        className="ml-3 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold transition-colors"
      >
        Send
      </button>
    </div>
  );
}
