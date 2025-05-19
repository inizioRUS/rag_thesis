import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from './SettingIndex.module.css';

interface Index {
  id: string;
  name: string;
  description: string;
  milvus_index_name: string;
  is_private: boolean;
}

interface TelegramBot {
  token: string;
  bot_url: string;
}

export default function SettingIndex() {
  const { indexId } = useParams<{ indexId: string }>();
  const navigate = useNavigate();
  const [index, setIndex] = useState<Index | null>(null);
  const [botToken, setBotToken] = useState('');
  const [botUrl, setBotUrl] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/setting_index/${indexId}`);
        setIndex(response.data.index);
        setBotToken(response.data.telegram_bot?.token || '');
        setBotUrl(response.data.telegram_bot?.bot_url || '');
      } catch (err) {
        setError('Ошибка загрузки данных');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [indexId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`http://127.0.0.1:8000/update_index_bot/${indexId}`, {
        bot_token: botToken,
        bot_url: botUrl
      });
      navigate(`http://127.0.0.1:8000/setting_index/${indexId}`);
    } catch (err) {
      setError('Ошибка сохранения настроек');
    }
  };

  if (isLoading) return <div className={styles.loading}>Загрузка...</div>;
  if (!index) return <div className={styles.error}>Индекс не найден</div>;

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Настройки индекса</h1>

      {error && <div className={styles.errorMessage}>{error}</div>}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Название индекса</label>
          <div className={styles.staticValue}>{index.name}</div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Описание</label>
          <div className={styles.staticValue}>{index.description}</div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Milvus Index</label>
          <div className={styles.staticValue}>{index.milvus_index_name}</div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Приватность</label>
          <div className={styles.staticValue}>
            {index.is_private ? '🔒 Приватный' : '🌐 Публичный'}
          </div>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="bot_token" className={styles.label}>
            Telegram Token
          </label>
          <input
            type="text"
            id="bot_token"
            value={botToken}
            onChange={(e) => setBotToken(e.target.value)}
            className={styles.input}
            placeholder="Введите токен от BotFather"
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="bot_url" className={styles.label}>
            Ссылка на бота
          </label>
          <input
            type="text"
            id="bot_url"
            value={botUrl}
            onChange={(e) => setBotUrl(e.target.value)}
            className={styles.input}
            placeholder="Например, https://t.me/your_bot"
          />
        </div>

        <div className={styles.buttonContainer}>
          <button type="submit" className={styles.submitButton}>
            💾 Сохранить
          </button>
        </div>
      </form>
    </div>
  );
}