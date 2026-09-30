import { useState } from "react";
import {
  Send,
  Sparkles,
  Bot,
  User,
  Plus,
  Menu,
} from "lucide-react";
import { motion } from "framer-motion";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const [sessionId] = useState(
    () => `session_${Date.now()}`
  );

  const sendMessage = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setQuestion("");
    setLoading(true);

    const userMessage = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
      {
        role: "assistant",
        content: "",
      },
    ]);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: sessionId,
            question: trimmedQuestion,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }

      const data = await response.json();

      setMessages((prev) => {
        const updated = [...prev];

        const lastMessage =
          updated[updated.length - 1];

        if (
          lastMessage &&
          lastMessage.role === "assistant"
        ) {
          updated[updated.length - 1] = {
            ...lastMessage,
            content: data.answer,
          };
        }

        return updated;
      });
    } catch (error) {
      console.error(error);

      setMessages((prev) => {
        const updated = [...prev];

        const lastMessage =
          updated[updated.length - 1];

        if (
          lastMessage &&
          lastMessage.role === "assistant"
        ) {
          updated[updated.length - 1] = {
            ...lastMessage,
            content:
              "Sorry, something went wrong while connecting to SYNTRA.",
          };
        }

        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const newChat = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white flex">

      {/* Sidebar */}

      <aside className="hidden md:flex w-64 border-r border-white/10 bg-[#080808] flex-col">

        <div className="p-5">
          <div className="flex items-center gap-3">

            <div className="w-10 h-10 rounded-xl bg-[#39ff88]/10 border border-[#39ff88]/30 flex items-center justify-center">

              <Sparkles
                size={20}
                className="text-[#39ff88]"
              />

            </div>

            <div>

              <h1 className="font-semibold text-lg">
                SYNTRA
              </h1>

              <p className="text-xs text-gray-500">
                AI Assistant
              </p>

            </div>

          </div>
        </div>

        <div className="px-4">

          <button
            onClick={newChat}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border border-white/10 hover:border-[#39ff88]/40 hover:bg-[#39ff88]/5 transition"
          >

            <Plus size={18} />

            <span className="text-sm">
              New Chat
            </span>

          </button>

        </div>

        <div className="mt-auto p-4 border-t border-white/10">

          <div className="text-xs text-gray-500">
            Adaptive & Context-Aware
          </div>

          <div className="text-xs text-gray-600 mt-1">
            SYNTRA v0.1.0
          </div>

        </div>

      </aside>

      {/* Main */}

      <main className="flex-1 flex flex-col min-h-screen">

        {/* Header */}

        <header className="h-16 border-b border-white/10 flex items-center px-5 md:px-8">

          <button className="md:hidden mr-3">
            <Menu size={22} />
          </button>

          <div>

            <h2 className="font-medium">
              SYNTRA
            </h2>

            <p className="text-xs text-gray-500">
              Intelligent Question Answering
            </p>

          </div>

          <div className="ml-auto flex items-center gap-2">

            <span className="w-2 h-2 rounded-full bg-[#39ff88] shadow-[0_0_8px_#39ff88]" />

            <span className="text-xs text-gray-400">
              Online
            </span>

          </div>

        </header>

        {/* Messages */}

        <section className="flex-1 overflow-y-auto px-4 md:px-12 py-8">

          {messages.length === 0 ? (

            <div className="h-full flex items-center justify-center">

              <motion.div
                initial={{
                  opacity: 0,
                  y: 15,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                className="text-center max-w-xl"
              >

                <div className="mx-auto w-16 h-16 rounded-2xl bg-[#39ff88]/10 border border-[#39ff88]/30 flex items-center justify-center mb-6">

                  <Sparkles
                    size={30}
                    className="text-[#39ff88]"
                  />

                </div>

                <h2 className="text-3xl md:text-4xl font-semibold mb-3">
                  How can I help you?
                </h2>

                <p className="text-gray-500 text-sm md:text-base">
                  Ask SYNTRA anything and get
                  intelligent, context-aware answers.
                </p>

              </motion.div>

            </div>

          ) : (

            <div className="max-w-4xl mx-auto space-y-7">

              {messages.map(
                (message, index) => (

                  <motion.div
                    key={index}
                    initial={{
                      opacity: 0,
                      y: 8,
                    }}
                    animate={{
                      opacity: 1,
                      y: 0,
                    }}
                    className={`flex gap-4 ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >

                    {message.role === "assistant" && (

                      <div className="w-9 h-9 shrink-0 rounded-xl bg-[#39ff88]/10 border border-[#39ff88]/20 flex items-center justify-center">

                        <Bot
                          size={18}
                          className="text-[#39ff88]"
                        />

                      </div>

                    )}

                    <div
                      className={`max-w-[80%] rounded-2xl px-5 py-3 whitespace-pre-wrap leading-7 text-sm md:text-base ${
                        message.role === "user"
                          ? "bg-[#39ff88] text-black"
                          : "bg-white/[0.04] border border-white/10 text-gray-200"
                      }`}
                    >

                      {message.content ||
                        (loading &&
                        message.role === "assistant"
                          ? "Thinking..."
                          : "")}

                    </div>

                    {message.role === "user" && (

                      <div className="w-9 h-9 shrink-0 rounded-xl bg-white/10 flex items-center justify-center">

                        <User size={18} />

                      </div>

                    )}

                  </motion.div>

                )
              )}

            </div>

          )}

        </section>

        {/* Input */}

        <div className="border-t border-white/10 p-4 md:p-6">

          <div className="max-w-4xl mx-auto">

            <div className="relative flex items-end bg-[#0b0b0b] border border-white/10 rounded-2xl focus-within:border-[#39ff88]/40 transition">

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Message SYNTRA..."
                rows={1}
                disabled={loading}
                className="flex-1 resize-none bg-transparent outline-none px-5 py-4 text-sm md:text-base placeholder:text-gray-600 disabled:opacity-50"
              />

              <button
                onClick={sendMessage}
                disabled={
                  loading ||
                  !question.trim()
                }
                className="m-2 w-10 h-10 rounded-xl bg-[#39ff88] text-black flex items-center justify-center hover:brightness-110 disabled:opacity-30 disabled:hover:brightness-100 transition"
              >

                <Send size={18} />

              </button>

            </div>

            <p className="text-center text-xs text-gray-600 mt-3">
              SYNTRA can make mistakes. Verify
              important information.
            </p>

          </div>

        </div>

      </main>

    </div>
  );
}

export default App;