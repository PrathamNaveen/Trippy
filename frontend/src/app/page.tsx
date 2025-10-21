'use client';

import { useState, KeyboardEvent } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/query', {
        question: input,
      });

      const aiMessage: Message = {
        role: 'assistant',
        content: res.data.answer || res.data.error || 'No answer.',
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Error contacting backend',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-100">
      <div className="flex-1 p-4 overflow-y-auto space-y-3 flex flex-col">
        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`p-3 rounded-xl max-w-xl break-words ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 self-end text-white'
                  : 'bg-gradient-to-r from-purple-700 to-purple-800 self-start text-white'
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

      <div className="flex p-4 border-t border-gray-700">
        <input
          type="text"
          placeholder="Ask about your Italy trip..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 p-3 rounded-lg bg-gray-800 text-gray-100 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={sendMessage}
          className="ml-3 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
