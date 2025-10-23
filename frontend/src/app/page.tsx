'use client';

import { useState, useEffect } from "react";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";

import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import CollectionSelector from "./components/CollectionSelector";
import UploadModal from "./components/UploadModal";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [collections, setCollections] = useState<string[]>([]);
  const [activeCollection, setActiveCollection] = useState("");
  const [showUpload, setShowUpload] = useState(false);

  const baseUrl = "http://localhost:8000";
  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      const res = await axios.get(`${baseUrl}/list_collections`);
      setCollections(res.data.collections || []);
    } catch (err) {
      console.error(err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !activeCollection) return;
    const userMessage: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${baseUrl}/query`, {
        question: input,
        collection_name: activeCollection,
      });
      const aiMessage: Message = {
        role: "assistant",
        content: res.data.answer || res.data.error || "No answer",
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Error contacting backend" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-100">
      {/* Top bar: selector + upload */}
      <div className="p-4 border-b border-gray-700 flex flex-col sm:flex-row items-center gap-3">
        <CollectionSelector
          collections={collections}
          active={activeCollection}
          onSelect={setActiveCollection}
        />
        <button
          onClick={() => setShowUpload(true)}
          className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold"
        >
          Upload PDF
        </button>
        <button
          onClick={fetchCollections}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold"
        >
          Refresh
        </button>
      </div>

      <ChatWindow messages={messages} loading={loading} />
      <ChatInput
        value={input}
        onChange={setInput}
        onSend={sendMessage}
        disabled={!activeCollection}
        placeholder={activeCollection ? `Ask about ${activeCollection}...` : "Select a collection first..."}
      />

      <AnimatePresence>
        {showUpload && (
          <UploadModal
            onClose={() => setShowUpload(false)}
            onUploaded={fetchCollections}
            baseUrl={baseUrl}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
