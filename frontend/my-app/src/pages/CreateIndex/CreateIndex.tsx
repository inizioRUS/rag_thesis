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
    if (!selectedFile) return;

    if (llmType === 'api' && !apiToken) {
      setUploadStatus('Токен обязателен для внешнего API');
      return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);
    formData.append('milvus_index_name', milvusIndexName);
    formData.append('is_private', String(isPrivate));
    formData.append('file', selectedFile);
    formData.append('type_llm', llmType);
    formData.append('token_llm', apiToken);
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
  <label htmlFor="file-upload" className={styles.label}>
    Загрузите архив с текстом (zip)
  </label>

  <div
    className={`${styles.dropzone} ${isDragging ? styles.dragging : ''}`}
    onDragOver={(e) => {
      e.preventDefault();
      setIsDragging(true);
    }}
    onDragLeave={() => setIsDragging(false)}
    onDrop={(e) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) {
        handleFile(file);
      }
    }}
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
      onChange={(e) => {
        const file = e.target.files?.[0];
        if (file) {
          handleFile(file);
        }
      }}
      accept=".zip"
      className={styles.fileInput}
      style={{ display: 'none' }}
    />
  </div>
</div>

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