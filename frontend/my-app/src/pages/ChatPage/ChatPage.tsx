import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import styles from './ChatPage.module.css';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  sources?: string[];
  downloadLink?: string;
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
  llm_type?: string;
  token?: string;
}

const API_BASE_URL = 'http://127.0.0.1:8000';

export default function ChatPage() {
  const { id: indexId } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [index, setIndex] = useState<Index | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [generateDocument, setGenerateDocument] = useState(false);
  const [documentPrompt, setDocumentPrompt] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Загрузка индекса и списка чатов
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [indexRes, chatsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/index/${indexId}`),
          fetch(`${API_BASE_URL}/api/chats?index_id=${indexId}`)
        ]);

        const indexData = await indexRes.json();
        const chatsData = await chatsRes.json();

        setIndex(indexData);
        setChats(chatsData.chats);
        // Автовыбор последнего чата
        if (chatsData.length > 0) {
          setSelectedChatId(chatsData[chatsData.length - 1].id);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [indexId]);

  // Загрузка сообщений выбранного чата
  useEffect(() => {
    const loadChatMessages = async () => {
      if (!selectedChatId) {
        setMessages([]);
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/chats/${selectedChatId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
        const chat: Chat = await response.json();
        setMessages(chat.messages);
      } catch (error) {
        console.error('Error loading chat:', error);
      }
    };

    loadChatMessages();
  }, [selectedChatId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => scrollToBottom(), [messages]);
  const token = localStorage.getItem('token');
  // Создание нового чата
  const handleCreateNewChat = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          index_id: indexId,
          title: `Новый чат ${new Date().toLocaleTimeString()}`,
        })
      });

      const newChat: Chat = await response.json();
      setChats(prev => [...prev, newChat]);
      setSelectedChatId(newChat.id);
      setMessages([]);
      setInputMessage('');
      setDocumentPrompt('');
    } catch (error) {
      console.error('Error creating chat:', error);
    }
  };

  // Отправка сообщения
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedChatId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    // Обновляем локальное состояние и сервер
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    await saveChatMessages(selectedChatId, newMessages);

    setInputMessage('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const endpoint = generateDocument ? 'get_ml_document' : 'get_ml_response';
      const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
         'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          message: inputMessage,
          document_prompt: generateDocument ? documentPrompt : undefined,
          index_id: indexId,
          chat_id: selectedChatId
        })
      });

      const data = await response.json();
      const botMessage: Message = {
        id: Date.now().toString(),
        content: data.reply,
        sender: 'bot',
        timestamp: new Date(),
        sources: data.sources,
        downloadLink: data.download_link
      };

      // Обновляем сервер с новым сообщением бота
      const updatedMessages = [...newMessages, botMessage];
      setMessages(updatedMessages);
      await saveChatMessages(selectedChatId, updatedMessages);

      setDocumentPrompt('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Сохранение сообщений чата на сервере
  const saveChatMessages = async (chatId: string, messages: Message[]) => {
    try {
      await fetch(`${API_BASE_URL}/api/chats/${chatId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
          },
        body: JSON.stringify({ messages })
      });
    } catch (error) {
      console.error('Error saving chat:', error);
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
            onClick={handleCreateNewChat}
          >
            + Новый чат
          </button>
        </div>

        <div className={styles.chatList}>
          {Array.isArray(chats) && chats.map(chat => (
            <div
              key={chat.id}
              className={`${styles.chatItem} ${
                selectedChatId === chat.id ? styles.active : ''
              }`}
              onClick={() => setSelectedChatId(chat.id)}
            >
              {chat.title}
            </div>
          ))}
        </div>
      </div>

      {/* Основная область */}
      <div className={styles.main}>
        <header className={styles.header}>
          <button onClick={() => navigate(-1)} className={styles.backButton}>
            ← Назад
          </button>
          <div className={styles.headerTitle}>
            <h1>{index.name}</h1>
          </div>
        </header>

        <div className={styles.chatWindow}>
          {messages.map((message) => (
            <div key={message.id} className={`${styles.message} ${message.sender === 'user' ? styles.user : styles.bot}`}>
              <div className={styles.messageContent}>
                <ReactMarkdown>{message.content}</ReactMarkdown>
                {message.downloadLink && (
                  <div className={styles.downloadSection}>
                    <a
                      href={message.downloadLink}
                      download
                      className={styles.downloadButton}
                    >
                      Скачать документ
                    </a>
                  </div>
                )}
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
          <div className={styles.documentOptions}>
            <label className={styles.documentToggle}>
              <input
                type="checkbox"
                checked={generateDocument}
                onChange={(e) => setGenerateDocument(e.target.checked)}
              />
              Генерация документа
            </label>
            {generateDocument && (
              <textarea
                value={documentPrompt}
                onChange={(e) => setDocumentPrompt(e.target.value)}
                placeholder="Введите дополнительные инструкции для документа..."
                className={styles.documentTextarea}
              />
            )}
          </div>

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
              disabled={isLoading || !selectedChatId}
            >
              {isLoading ? '✧' : '➤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}