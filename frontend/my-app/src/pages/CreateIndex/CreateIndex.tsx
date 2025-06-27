import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import styles from './CreateIndex.module.css';
import { useNavigate } from 'react-router-dom'; // 👈 добавить

export default function CreateIndex() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [milvusIndexName, setMilvusIndexName] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [llmType, setLlmType] = useState<'local' | 'api'>('local');
  const [apiToken, setApiToken] = useState('');
  const [uploadType, setUploadType] = useState<'file' | 'url'>('file'); // 👈 Новое состояние
  const [url, setUrl] = useState(''); // 👈 Новое состояние для URL
  const [chunkSize, setChunkSize] = useState<number>(512); // 👈 Добавлено
  const [overlap, setOverlap] = useState<number>(64);        // 👈 Добавлено

  const navigate = useNavigate(); // 👈 добавить

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
    const handleFile = (file: File) => {
      setSelectedFile(file);
    };
  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files[0]) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isNaN(chunkSize) || chunkSize <= 256 ) {
      setUploadStatus('Размер чанка должен быть положительным числом');
      return;
    }
    if (isNaN(overlap) || overlap < 10) {
      setUploadStatus('Перекрытие не может быть отрицательным');
      return;
    }
    if (uploadType === 'file' && !selectedFile) {
      setUploadStatus('Пожалуйста, выберите файл');
      return;
    }

    if (uploadType === 'url' && !url) {
      setUploadStatus('Пожалуйста, введите ссылку');
      return;
    }

    if (llmType === 'api' && !apiToken) {
      setUploadStatus('Токен обязателен для внешнего API');
      return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);
    formData.append('milvus_index_name', milvusIndexName);
    formData.append('is_private', String(isPrivate));
    formData.append('type_llm', llmType);
    formData.append('token_llm', apiToken);
     formData.append('chunk_size', String(chunkSize)); // 👈 Добавлено
    formData.append('overlap', String(overlap));     // 👈 Добавлено
    if (uploadType === 'file' && selectedFile) {
      formData.append('file', selectedFile);
    } else if (uploadType === 'url' && url) {
      formData.append('url', url);
    }
    const token = localStorage.getItem('token');
    try {
      setUploadStatus('Отправка архива...');
      console.log(formData)
      const response = await axios.post('http://127.0.0.1:8000/make_index/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        },
      });

      if (response.data.task_id) {
        pollStatus(response.data.task_id);
      }
    } catch (error) {
      const err = error as any;
      setUploadStatus(`Ошибка: ${err.response?.data?.detail || 'Ошибка загрузки'}`);
    }
  };

  const pollStatus = (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`http://localhost:8001/status/${taskId}`);
        setUploadStatus(`Статус: ${response.data.status}`);

        if (response.data.status === 'готово') {
          clearInterval(interval);
          setUploadStatus(prev => prev + ' ✅ Индекс успешно создан!');
        }
      } catch (error) {
        clearInterval(interval);
        setUploadStatus('Ошибка проверки статуса');
      }
    }, 3000);

    return () => clearInterval(interval);
  };

  return (
    <div className={styles.container}>
        <button onClick={() => navigate(-1)} className={styles.backButton}>
        ← Назад
      </button>
      <h1 className={styles.title}>Создание индекса</h1>

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Название индекса</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={styles.input}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Описание</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={styles.textarea}
            required
          />
        </div>

         <div className={styles.formGroup}>
          <label className={styles.label}>Тип загрузки</label>
          <div className={styles.radioGroup}>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                value="file"
                checked={uploadType === 'file'}
                onChange={() => setUploadType('file')}
              />
              Файл
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                value="url"
                checked={uploadType === 'url'}
                onChange={() => setUploadType('url')}
              />
              Ссылка
            </label>
          </div>
        </div>

        {uploadType === 'file' && (
          <div className={styles.formGroup}>
            <label htmlFor="file-upload" className={styles.label}>
              Загрузите архив с текстом (zip)
            </label>
            <div
              className={`${styles.dropzone} ${isDragging ? styles.dragging : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  fileInputRef.current?.click();
                }
              }}
              aria-label="Зона загрузки файла"
            >
              <p className={styles.dropzoneText}>
                {selectedFile
                  ? `Выбран файл: ${selectedFile.name}`
                  : 'Перетащите .zip файл сюда или нажмите для выбора'}
              </p>
              <input
                id="file-upload"
                type="file"
                ref={fileInputRef}
                onChange={handleFileInput}
                accept=".zip"
                className={styles.fileInput}
                style={{ display: 'none' }}
              />
            </div>
          </div>
        )}

        {uploadType === 'url' && (
          <div className={styles.formGroup}>
            <label className={styles.label}>Ссылка на сайт</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className={styles.input}
              placeholder="https://example.com/archive"
              required
            />
          </div>
        )}

        <div className={styles.formGroup}>
          <label className={styles.label}>Название индекса в Milvus</label>
          <input
            type="text"
            value={milvusIndexName}
            onChange={(e) => setMilvusIndexName(e.target.value)}
            className={styles.input}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>Размер чанка (chunk size)</label>
          <input
            type="number"
            value={chunkSize}
            onChange={(e) => setChunkSize(Number(e.target.value))}
            className={styles.input}
            min="1"
            required
          />
          <p className={styles.hint}>Рекомендуемое значение: 256-512 символов</p>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Перекрытие (overlap)</label>
          <input
            type="number"
            value={overlap}
            onChange={(e) => setOverlap(Number(e.target.value))}
            className={styles.input}
            min="0"
            required
          />
          <p className={styles.hint}>Рекомендуется 10-20% от размера чанка</p>
        </div>
        <div className={styles.checkboxGroup}>
          <input
            type="checkbox"
            id="is_private"
            checked={isPrivate}
            onChange={(e) => setIsPrivate(e.target.checked)}
            className={styles.checkbox}
          />
          <label htmlFor="is_private" className={styles.checkboxLabel}>
            Приватный индекс?
          </label>
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>Тип LLM</label>
          <select
            value={llmType}
            onChange={(e) => setLlmType(e.target.value as 'local' | 'api')}
            className={styles.select}
          >
            <option value="local">Локальная модель</option>
            <option value="api">Внешний API</option>
          </select>
        </div>

        {llmType === 'api' && (
          <div className={styles.formGroup}>
            <label className={styles.label}>API Токен</label>
            <input
              type="password"
              value={apiToken}
              onChange={(e) => setApiToken(e.target.value)}
              className={styles.input}
              placeholder="Введите ваш API токен"
            />
          </div>
        )}
        <button type="submit" className={styles.submitButton}>
          Создать индекс
        </button>
      </form>

      {uploadStatus && (
        <div className={styles.statusBlock}>
          <h2 className={styles.statusTitle}>Статус загрузки:</h2>
          <p className={styles.statusText}>{uploadStatus}</p>
        </div>
      )}
    </div>
  );
}