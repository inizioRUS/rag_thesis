import { useState } from 'react';
import { Link, useNavigate  } from 'react-router-dom';
import styles from './Login.module.css';

export default function Login() {
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

    const response = await fetch('http://127.0.0.1:8000/login', {
      method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
      body: JSON.stringify({ username, password }),
      credentials: 'include',
    });
    const data = await response.json();

    if (!response.ok) {

      throw new Error(data.detail || 'Ошибка авторизации');
    }
    localStorage.setItem('token', data.token)
    // В случае успеха
    window.location.href = '/';

  } catch (err) {
    setError(err instanceof Error ? err.message : 'Ошибка авторизации');
  } finally {
    setIsLoading(false);
  }
};

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <h1 className={styles.authTitle}>Вход в систему</h1>

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
              placeholder="Введите ваш логин"
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
              {isLoading ? 'Выполняется вход...' : 'Продолжить'}
            </span>
            {!isLoading && <span className={styles.buttonIcon}>→</span>}
          </button>
        </form>

        <div className={styles.authFooter}>
          <p>Нет аккаунта?
          <Link to="/register" className={styles.authLink}>
            Создать аккаунт
          </Link>
          </p>
        </div>
      </div>
    </div>
  );
}