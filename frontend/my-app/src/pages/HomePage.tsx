import { useEffect,useState } from "react";
import { Link } from "react-router-dom";


interface Index {
  id: string;
  name: string;
  description: string;
}

interface User {
  username: string;
}

export default function HomePage() {

  const [user, setUser] = useState<User | null>(null);
  const [indices, setIndices] = useState<Index[]>([]);
  const [page, setPage] = useState(0);

useEffect(() => {
  const token = localStorage.getItem('token');



    fetch("http://127.0.0.1:8000/user", {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(async response => response.json())
    .then(data => setUser(data.username));

    loadMoreIndices(1);
  }, []);

  function loadMoreIndices(page: number) {
    fetch(`http://127.0.0.1:8000/api/indices?page=${page}&per_page=12`)
        .then(res => res.json())
        .then(data => {
        if (data.indices.length === 0) return;
        setIndices(prev => [...prev, ...data.indices]);
        setPage(page);
      });

  }

  return (
    <div className="container">
      <h1 className="header">Добро пожаловать в IndexHub</h1>

      <div className="auth-section">
        {user ? (
          <>
            <a href="/home" className="button secondary">Личный кабинет</a>
            <a href="/make_index" className="button primary">Создать индекс</a>
            <a href="/logout" className="button danger">Выйти</a>
          </>
        ) : (
          <>
            <a href="/login" className="button primary">Войти</a>
            <a href="/register" className="button accent">Зарегистрироваться</a>
          </>
        )}
      </div>

      <h2 className="section-title">Публичные индексы</h2>
      <div className="grid">
        {indices.map(index => (
          <div key={index.id} className="card">
            <h3 className="card-title">{index.name}</h3>
            <p className="card-description">{index.description}</p>
            <a href={`/index/${index.id}`} className="card-link">Перейти в чат</a>
          </div>
        ))}
      </div>

      <div className="load-more">
        <button
          className="button primary"
          onClick={() => loadMoreIndices(page + 1)}
        >
          Загрузить больше
        </button>
      </div>
    </div>
  );
}