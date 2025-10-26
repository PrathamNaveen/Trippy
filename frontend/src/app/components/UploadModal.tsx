'use client';

import { useState, ChangeEvent } from "react";
import { motion } from "framer-motion";
import axios, { AxiosError } from "axios";
import { isValidCollectionName } from "../utils/validation";

interface Props {
  onClose: () => void;
  onUploaded: () => void;
  baseUrl: string;
  sessionId: string;
  onSessionExpired: () => void; // callback to handle session expiration in parent
}

export default function UploadModal({
  onClose,
  onUploaded,
  baseUrl,
  sessionId,
  onSessionExpired,
}: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [collectionName, setCollectionName] = useState<string>("");
  const [status, setStatus] = useState<string>("");

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return setStatus("⚠️ Please select a PDF first.");

    if (!isValidCollectionName(collectionName)) {
      return setStatus(
        "❌ Invalid collection name! Must be 3-512 characters, only letters, numbers, dot, underscore or hyphen, starting & ending with a letter/number."
      );
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("collection_name", collectionName);

    setStatus("⏳ Uploading...");
    try {
      const res = await axios.post(`${baseUrl}/upload_pdf`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          "session_id": sessionId,
        },
      });
      setStatus(`✅ ${res.data.message}`);
      onUploaded();
      setTimeout(onClose, 1000);
    } catch (err: unknown) {
      const axiosErr = err as AxiosError;
      if (axiosErr.response?.status === 401) {
        setStatus("❌ Session expired. Please log in again.");
        onSessionExpired(); // notify parent to show login page
        return;
      }
      console.error(axiosErr);
      setStatus("❌ Error uploading file.");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      className="fixed inset-0 bg-black/50 flex justify-center items-center z-50"
    >
      <motion.div className="bg-gray-900 p-6 rounded-lg w-11/12 max-w-md shadow-xl">
        <h2 className="text-lg font-semibold mb-4 text-gray-100">Upload PDF</h2>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="mb-3 w-full text-gray-100"
        />
        <input
          type="text"
          placeholder="Collection Name"
          value={collectionName}
          onChange={e => setCollectionName(e.target.value)}
          className={`mb-3 w-full p-2 rounded bg-gray-800 text-gray-100 border ${
            collectionName && !isValidCollectionName(collectionName)
              ? "border-red-500"
              : "border-gray-700"
          } focus:outline-none focus:ring-2 focus:ring-blue-500`}
        />
        {status && <div className="text-sm mb-2 text-gray-300">{status}</div>}
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white"
          >
            Upload
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
