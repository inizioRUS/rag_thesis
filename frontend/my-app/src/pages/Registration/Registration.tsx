import { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './Registration.module.css';

export default function Registration() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError('');
  setIsLoading(true);

  try {
    if (!username || !password) {
      throw new Error('Заполните все поля');
    }

    const response = await fetch('http://127.0.0.1:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'Ошибка регистрации');
    }

    // В случае успеха
    window.location.href = '/'; // или /main, если надо

  } catch (err) {
    setError(err instanceof Error ? err.message : 'Ошибка регистрации');
  } finally {
    setIsLoading(false);
  }
};

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <h1 className={styles.authTitle}>Создать аккаунт</h1>

        {error && (
          <div className={styles.errorMessage}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.authForm}>
          <div className={styles.formGroup}>
            <label className={styles.inputLabel}>Имя пользователя</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={styles.formInput}
              placeholder="Придумайте логин"
              disabled={isLoading}
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.inputLabel}>Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.formInput}
              placeholder="••••••••"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className={styles.primaryButton}
            disabled={isLoading}
          >
            <span className={styles.buttonText}>
              {isLoading ? 'Создание аккаунта...' : 'Зарегистрироваться'}
            </span>
            {!isLoading && <span className={styles.buttonIcon}>→</span>}
          </button>
        </form>

        <div className={styles.authFooter}>
          <p>Уже есть аккаунт?
          <Link to="/login" className={styles.authLink}>
            Войти в систему
          </Link>
          </p>
        </div>
      </div>
    </div>
  );
}