import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import styles from './CreateIndex.module.css';

export default function CreateIndex() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [milvusIndexName, setMilvusIndexName] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
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

    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);
    formData.append('milvus_index_name', milvusIndexName);
    formData.append('is_private', String(isPrivate));
    formData.append('file', selectedFile);

    try {
      setUploadStatus('Отправка архива...');

      const response = await axios.post('/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.task_id) {
        pollStatus(response.data.task_id);
      }
    } catch (error) {
      setUploadStatus(`Ошибка: ${error.response?.data?.detail || 'Ошибка загрузки'}`);
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
          <label className={styles.label}>Загрузите архив с текстом (zip)</label>
          <div
            className={`${styles.dropzone} ${isDragging ? styles.dragging : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <p className={styles.dropzoneText}>
              {selectedFile
                ? `Выбран файл: ${selectedFile.name}`
                : 'Перетащите файл сюда или нажмите для выбора'}
            </p>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileInput}
              accept=".zip"
              className={styles.fileInput}
              required
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