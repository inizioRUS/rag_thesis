import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage/HomePage";
import ChatPage from './pages/ChatPage/ChatPage';
import Login from './pages/Login/Login';
import Registration from './pages/Registration/Registration';
import SettingIndex from './pages/SettingIndex/SettingIndex';
import CreateIndex from './pages/CreateIndex/CreateIndex';
import Home from './pages/Home/Home';
import AdminPanel from './pages/AdminPanel/AdminPanel';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/index/:id" element={<ChatPage />} />
        <Route path="/setting_index/:id" element={<SettingIndex />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Registration />} />
        <Route path="/make_index" element={<CreateIndex />} />
        <Route path="/home" element={<Home />} />
        <Route path="/admin" element={<AdminPanel />} />
        {/* 404 fallback можно добавить позже */}
      </Routes>
    </Router>
  );
}