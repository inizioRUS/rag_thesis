import { useEffect,useState } from "react";
import { Link } from "react-router-dom";
import IndexCard from './components/IndexCard';
import { useNavigate } from 'react-router-dom'; // 👈 добавить

interface Index {
  id: string;
  name: string;
  description: string;
  rating:number
  averageRating: number
  countRating: number
}

interface User {
  username: string;
}
interface ApiIndicesResponse {
  indices: Array<Omit<Index, 'averageRating'>>;
}
export default function HomePage() {

  const [user, setUser] = useState<User | null>(null);
  const [indices, setIndices] = useState<Index[]>([]);
  const [page, setPage] = useState(0);
  const navigate = useNavigate(); // 👈 добавить
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
    .then((data: ApiIndicesResponse) => { // Явно указываем тип ответа
      const indicesWithRating = data.indices.map(index => ({
        ...index,
        rating: Math.floor(Math.random() * 5) + 1,
        averageRating: Math.floor(Math.random() * 5) + 1, // общий рейтинг
        countRating: Math.floor(Math.random() * 100) + 1 // общий рейтинг
      }));
      if (indicesWithRating.length === 0) return;
      setIndices(prev => [...prev, ...indicesWithRating]);
      setPage(page);
    });
}
 const handleLogout = async (e:any) => {
    e.preventDefault();  // чтобы не было перехода по ссылке по умолчанию
    await fetch("http://127.0.0.1:8000/logout");  // вызов сервера (можно убрать, если сервер не требует)
    localStorage.removeItem("token");  // очистка токена
    setUser(null);
  };
  return (
    <div className="container">
      <h1 className="header">Добро пожаловать в IndexHub</h1>

      <div className="auth-section">
        {user ? (
          <>
            <a href="/home" className="button secondary">Личный кабинет</a>
            <a href="/make_index" className="button primary">Создать индекс</a>
                <a href="/logout" className="button danger" onClick={handleLogout}>
      Выйти
    </a>
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
            <IndexCard key={index.id} index={index} />
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