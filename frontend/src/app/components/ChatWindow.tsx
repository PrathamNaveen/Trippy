'use client';

import { motion, AnimatePresence } from "framer-motion";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  messages: Message[];
  loading: boolean;
}

export default function ChatWindow({ messages, loading }: Props) {
  return (
    <div className="flex-1 p-4 overflow-y-auto space-y-3 flex flex-col">
      <AnimatePresence>
        {messages.map((msg, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`p-3 rounded-xl max-w-xl break-words ${
              msg.role === "user"
                ? "bg-gradient-to-r from-blue-500 to-blue-600 self-end text-white"
                : "bg-gradient-to-r from-purple-700 to-purple-800 self-start text-white"
            }`}
          >
            {msg.content}
          </motion.div>
        ))}
      </AnimatePresence>

      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="self-start text-gray-300 italic animate-pulse"
        >
          AI is thinking...
        </motion.div>
      )}
    </div>
  );
}
