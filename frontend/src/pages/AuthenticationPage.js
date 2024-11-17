/* frontend/src/pages/AuthenticationPage.js */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AuthenticationPage.css';

const AuthenticationPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLogin) {
      try {
        const response = await axios.post('http://localhost:5000/api/auth/login', {
          username,
          password,
        });
        navigate('/dashboard');
      } catch (error) {
        setErrorMessage('Giriş bilgileri hatalı.');
      }
    } else {
      try {
        const response = await axios.post('http://localhost:5000/api/auth/register', {
          username,
          email,
          password,
        });
        setIsLogin(true);
      } catch (error) {
        setErrorMessage('Kayıt işlemi başarısız.');
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="logo-container">
        <img className="logo" src="logo.png" alt="Logo" />
        <h2>Uygulama Adı</h2>
      </div>
      <div className="form-container">
        <h2>{isLogin ? 'Giriş Yap' : 'Kayıt Ol'}</h2>
        {errorMessage && <div className="error-message">{errorMessage}</div>}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input
              type="text"
              placeholder="Kullanıcı Adı"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          {!isLogin && (
            <div className="input-group">
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          )}
          <div className="input-group">
            <input
              type="password"
              placeholder="Şifre"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="button-group">
            <button type="submit" className={isLogin ? 'login' : 'create-account'}>
              {isLogin ? 'Giriş Yap' : 'Kayıt Ol'}
            </button>
          </div>
        </form>
        <div className="auth-toggle">
          <p>
            {isLogin ? 'Hesabınız yok mu? ' : 'Zaten hesabınız var mı? '}
            <span onClick={() => setIsLogin(!isLogin)}>
              {isLogin ? 'Kayıt Ol' : 'Giriş Yap'}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthenticationPage;
