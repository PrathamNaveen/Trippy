'use client'

import { useState, useEffect } from "react";
import axios, { AxiosError } from "axios";
import { AnimatePresence } from "framer-motion";

import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import CollectionSelector from "./components/CollectionSelector";
import UploadModal from "./components/UploadModal";
import AuthPage from "./components/Auth";

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
  const [sessionId, setSessionId] = useState<string | null>(null);

  const baseUrl = "http://localhost:8000";

  // Check if user is already logged in
  useEffect(() => {
    const storedSession = localStorage.getItem("session_id");
    if (storedSession) setSessionId(storedSession);
  }, []);

  // Fetch collections whenever sessionId changes
  useEffect(() => {
    if (sessionId) fetchCollections();
  }, [sessionId]);

  // Helper to handle 401 (session expired)
  const handleSessionExpired = () => {
    localStorage.removeItem("session_id");
    setSessionId(null);
    alert("Session expired. Please log in again.");
    return <AuthPage onLogin={handleLogin} />;
  };
  
  // Fetch collections
  const fetchCollections = async () => {
    if (!sessionId) return;
    try {
      const res = await axios.get(`${baseUrl}/list_collections`, {
        headers: { "session_id": sessionId },
      });
      setCollections(res.data.collections || []);
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        handleSessionExpired();
      } else {
        console.error(err);
      }
    }
  };

  // Send message to backend
  const sendMessage = async () => {
    if (!input.trim() || !activeCollection || !sessionId) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(
        `${baseUrl}/query`,
        { question: input, collection_name: activeCollection },
        { headers: { "session_id": sessionId } }
      );

      const aiMessage: Message = {
        role: "assistant",
        content: res.data.answer || res.data.error || "No answer",
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        handleSessionExpired();
      } else {
        console.error(err);
        setMessages(prev => [
          ...prev,
          { role: "assistant", content: "Error contacting backend" },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle login from AuthPage
  const handleLogin = (newSessionId: string) => {
    setSessionId(newSessionId);
    localStorage.setItem("session_id", newSessionId);
  };

  // Not logged in → show AuthPage
  if (!sessionId) return <AuthPage onLogin={handleLogin} />;

  // Logged in → show chat UI
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
        placeholder={
          activeCollection
            ? `Ask about ${activeCollection}...`
            : "Select a collection first..."
        }
      />

      <AnimatePresence>
        {showUpload && (
          <UploadModal
            onClose={() => setShowUpload(false)}
            onUploaded={fetchCollections}
            baseUrl={baseUrl}
            sessionId={sessionId}
            onSessionExpired={handleSessionExpired}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
