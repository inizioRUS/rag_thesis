import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import styles from './ChatPage.module.css';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  sources?: string[];
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
}

interface Index {
  id: string;
  name: string;
  description: string;
}

export default function ChatPage() {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [index, setIndex] = useState<Index | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [selectedChat, setSelectedChat] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Загрузка данных
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [indexRes, chatsRes] = await Promise.all([
          fetch(`http://127.0.0.1:8000/api/index/${id}`),
          fetch(`/api/chats?index_id=${id}`)
        ]);

        setIndex(await indexRes.json());
        setChats(await chatsRes.json());
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [id]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => scrollToBottom(), [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/get_ml_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          index_id: id
        })
      });

      const data = await response.json();
      const botMessage: Message = {
        id: Date.now().toString(),
        content: data.reply,
        sender: 'bot',
        timestamp: new Date(),
        sources: data.sources
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const templates = [
    "Объясни простыми словами",
    "Сформулируй основные тезисы",
    "Приведи примеры использования",
    "Сравни с аналогичными концепциями"
  ];

  if (!index) return <div className={styles.loading}>Загрузка...</div>;

  return (
    <div className={styles.container}>
      {/* Боковая панель */}
      <div className={styles.sidebar}>
        <div className={styles.newChat}>
          <button
            className={styles.newChatButton}
            onClick={() => setSelectedChat(null)}
          >
            + Новый чат
          </button>
        </div>

        <div className={styles.chatList}>
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`${styles.chatItem} ${
                selectedChat === chat.id ? styles.active : ''
              }`}
              onClick={() => setSelectedChat(chat.id)}
            >
              {chat.title}
            </div>
          ))}
        </div>
      </div>

      {/* Основная область */}
      <div className={styles.main}>
        <header className={styles.header}>
          <h1>{index.name}</h1>
          <p>{index.description}</p>
        </header>

        <div className={styles.chatWindow}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`${styles.message} ${
                message.sender === 'user' ? styles.user : styles.bot
              }`}
            >
              <div className={styles.messageContent}>
                {message.content}
                {message.sources && (
                  <div className={styles.sources}>
                    <span>Источники:</span>
                    {message.sources.map((source, idx) => (
                      <a
                        key={idx}
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.sourceLink}
                      >
                        Файл {idx + 1}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputArea}>
          <div className={styles.templates}>
            {templates.map((template) => (
              <button
                key={template}
                className={styles.templateButton}
                onClick={() => setInputMessage(template)}
              >
                {template}
              </button>
            ))}
          </div>

          <div className={styles.inputContainer}>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Напишите сообщение..."
              className={styles.input}
              disabled={isLoading}
            />
            <button
              className={styles.sendButton}
              onClick={handleSendMessage}
              disabled={isLoading}
            >
              {isLoading ? '✧' : '➤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}