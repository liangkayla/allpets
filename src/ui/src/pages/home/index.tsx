import React, { useState, useRef, useEffect } from "react";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
};

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      role: "assistant",
      text: "Hi there! I'm AllPets - your personal AI assistant for all things pets! Feel free to ask a question about pet care or upload a pet you're curious about :)",
    },
  ]);

  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  // file upload
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  const pushMessage = (role: "user" | "assistant", text: string) => {
    setMessages((prev) => [
      ...prev,
      { id: String(Date.now()) + Math.random(), role, text },
    ]);
  };

  // text generation
  const sendText = async () => {
    const prompt = input.trim();
    if (!prompt) return;

    setError(null);
    setSending(true);

    pushMessage("user", prompt);
    setInput("");

    // placeholder text while model is generating
    const placeholderId = "temp-" + Date.now();
    setMessages((prev) => [...prev, { id: placeholderId, role: "assistant", text: "Thinking, please wait :)" }]);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        const j = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(j.detail || res.statusText);
      }

      const json = await res.json();
      const reply = json.response ?? "";

      // replace placeholder text with model output
      setMessages((prev) =>
        prev.map((m) =>
          m.id === placeholderId ? { ...m, text: reply } : m
        )
      );
    } catch (e: any) {
      setMessages((prev) => prev.filter((m) => m.id !== placeholderId));
      pushMessage("assistant", `Error: ${e?.message ?? String(e)}`);
    } finally {
      setSending(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendText();
    }
  };

  // image upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(e.target.files?.[0] ?? null);
    setError(null);
  };

  const uploadImage = async () => {
    if (!selectedFile) {
      setError("Please choose an image first.");
      return;
    }

    setError(null);

    // user message
    pushMessage("user", `Selected Pet Image: ${selectedFile.name}`);

    // placeholder text while model is classifying
    const placeholderId = "img-" + Date.now();
    pushMessage("assistant", "Classifying pet...");

    try {
      const form = new FormData();
      form.append("file", selectedFile);

      const res = await fetch("/api/classify", {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const j = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(j.detail || res.statusText);
      }

      const json = await res.json();
      const predicted = json.response ?? "Unknown";

      // replace placeholder text
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          text: `Predicted: ${predicted}.`,
        };
        return updated;
      });

      // Reset file selection
      setSelectedFile(null);
      if (fileRef.current) fileRef.current.value = "";

      const carePrompt = `Provide a concise care summary for a pet ${predicted}.`

      const carePlaceholderId = "care-" + Date.now();
      setMessages((prev) => [...prev, { id: carePlaceholderId, role: "assistant", text: "Generating care summary..." }]);

      // call /api/generate
      const genRes = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: carePrompt }),
      });

      if (!genRes.ok) {
        const j = await genRes.json().catch(() => ({ detail: genRes.statusText }));
        throw new Error(j.detail || genRes.statusText);
      }

      const genJson = await genRes.json();
      let careText = genJson.response ?? "No care info available.";

      // sanitize/trim the result a bit
      careText = careText.toString().trim();

      // replace the care placeholder with the generated summary
      setMessages((prev) => prev.map((m) => (m.id === carePlaceholderId ? { ...m, text: careText } : m)));

    } catch (err: any) {
      setMessages((prev) => prev.filter((m) => m.text !== "Classifying image..." && m.text !== "Generating care summary..."));
      pushMessage("assistant", `Error: ${err?.message ?? String(err)}`);
      setError(String(err?.message ?? err));
    }
  };

  return (
    <div style={styles.container}>
      {/* Chat history */}
      <div style={styles.messages}>
        {messages.map((m) => (
          <div
            key={m.id}
            style={m.role === "user" ? styles.userMsg : styles.assistantMsg}
          >
            {m.text}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Image input + upload button */}
      <div style={styles.imageBar}>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
        />
        <button onClick={uploadImage} disabled={!selectedFile}>
          Upload Image
        </button>
      </div>

      {/* Text input */}
      <div style={styles.inputBar}>
        <textarea
          placeholder="Type a message here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          style={styles.textarea}
          disabled={sending}
        />
        <button onClick={() => void sendText()} disabled={!input.trim() || sending}>
          Send
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}
    </div>
  );
};

/* ------- Minimal styles -------- */
const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: 800,
    margin: "24px auto",
    border: "1px solid #ddd",
    borderRadius: 8,
    overflow: "hidden",
    fontFamily: "system-ui",
  },
  messages: {
    height: 400,
    overflowY: "auto",
    padding: 12,
    display: "flex",
    flexDirection: "column",
    gap: 12,
    background: "#fff",
  },
  userMsg: {
    alignSelf: "flex-end",
    background: "#dbeafe",
    padding: 10,
    borderRadius: 8,
    maxWidth: "70%",
  },
  assistantMsg: {
    alignSelf: "flex-start",
    background: "#f3f4f6",
    padding: 10,
    borderRadius: 8,
    maxWidth: "70%",
  },
  imageBar: {
    display: "flex",
    gap: 8,
    padding: 12,
    borderTop: "1px solid #eee",
    alignItems: "center",
  },
  inputBar: {
    display: "flex",
    gap: 8,
    padding: 12,
    borderTop: "1px solid #eee",
    background: "#f9fafb",
  },
  textarea: {
    flex: 1,
    minHeight: 50,
    maxHeight: 140,
    resize: "vertical",
    padding: 8,
    borderRadius: 6,
    border: "1px solid #ccc",
  },
  error: {
    padding: 10,
    background: "#ffeaea",
    color: "#b91c1c",
    borderTop: "1px solid #fcc",
  },
};

export default Chat;
