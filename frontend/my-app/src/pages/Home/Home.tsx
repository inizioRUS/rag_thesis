import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './Home.module.css';

interface Index {
  id: string;
  name: string;
  description: string;
}

export default function Home() {
  const [indices, setIndices] = useState<Index[]>([]);
  const [favorites, setFavorites] = useState<Index[]>([]);
  const [showFavorites, setShowFavorites] = useState(false);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const loadIndices = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/indices?page=${page}&per_page=12`);
        const data = await response.json();
        setIndices(data.indices);
      } catch (error) {
        console.error('Error loading indices:', error);
      }
    };
    loadIndices();
  }, [page]);

  const toggleFavorites = () => setShowFavorites(!showFavorites);

  const addToFavorites = (index: Index) => {
    if (!favorites.some(fav => fav.id === index.id)) {
      setFavorites([...favorites, index]);
    }
  };

  return (
    <div className={styles.container}>
      {/* Боковая панель избранного */}
      <div className={`${styles.sidePanel} ${showFavorites ? styles.active : ''}`}>
        <div className={styles.sidePanelHeader}>
          <h3>Избранное</h3>
          <button onClick={toggleFavorites} className={styles.closeButton}>×</button>
        </div>
        <div className={styles.favoritesList}>
          {favorites.map(index => (
            <div key={index.id} className={styles.favoriteItem}>
              <h4>{index.name}</h4>
              <p>{index.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Основной контент */}
      <div className={styles.mainContent}>
        {/* Шапка */}
        <div className={styles.header}>
          <Link to="/" className={styles.homeButton}>🏠</Link>
          <button onClick={toggleFavorites} className={styles.favoritesButton}>
            ★ Избранное ({favorites.length})
          </button>
        </div>

        {/* Навигация */}
        <nav className={styles.navBar}>
          <Link to="/main" className={styles.navLink}>Главная</Link>
          <Link to="/make_index" className={`${styles.navLink} ${styles.primary}`}>Создать индекс</Link>
          <Link to="/logout" className={`${styles.navLink} ${styles.danger}`}>Выйти</Link>
        </nav>

        {/* Список индексов */}
        <h2 className={styles.sectionTitle}>Ваши индексы</h2>

        {indices.length > 0 ? (
          <div className={styles.grid}>
            {indices.map(index => (
              <div key={index.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <h3>{index.name}</h3>
                  <button
                    onClick={() => addToFavorites(index)}
                    className={styles.favoriteButton}
                    aria-label="Добавить в избранное"
                  >
                    ★
                  </button>
                </div>
                <p className={styles.cardDescription}>{index.description}</p>

                <div className={styles.cardActions}>
                  <Link to={`/index/${index.id}`} className={`${styles.button} ${styles.chat}`}>
                    💬 Чат
                  </Link>
                  <Link to={`/setting_index/${index.id}`} className={`${styles.button} ${styles.settings}`}>
                    ⚙️ Настройки
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className={styles.emptyState}>У вас пока нет индексов</p>
        )}
      </div>
    </div>
  );
}