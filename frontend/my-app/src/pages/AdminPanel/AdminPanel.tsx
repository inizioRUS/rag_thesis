import { useState } from 'react';
import styles from './AdminPanel.module.css';

interface User {
  id: number;
  login: string;
  role: string;
}

export default function AdminPanel() {
  const [users, setUsers] = useState<User[]>([
    { id: 1, login: 'ivan', role: 'admin' },
    { id: 2, login: 'petr', role: 'user' },
    { id: 3, login: 'maria', role: 'moderator' },
  ]);

  const handleRoleChange = (userId: number, newRole: string) => {
    setUsers(users.map(user =>
      user.id === userId ? { ...user, role: newRole } : user
    ));
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Панель администратора</h1>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Логин</th>
              <th>Роль</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.login}</td>
                <td>
                  <select
                    value={user.role}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                    className={styles.select}
                  >
                    <option value="admin">Администратор</option>
                    <option value="moderator">Модератор</option>
                    <option value="user">Пользователь</option>
                  </select>
                </td>
                <td>
                  <button className={styles.button}>
                    Сохранить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}