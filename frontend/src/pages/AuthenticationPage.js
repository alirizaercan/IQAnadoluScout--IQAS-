/* frontend/src/pages/AuthenticationPage.js */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/AuthenticationPage.css';
import logoImage from '../assets/images/IQAS_auth.png';
import userIcon from '../assets/images/user_icon.png';

const AuthenticationPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    firstname: '',
    lastname: '',
    email: '',
    role: '',
    club: '',
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLogin) {
      try {
        const response = await axios.post('http://localhost:5000/api/auth/login', {
          username: formData.username,
          password: formData.password,
        });
        if (response.data.message === 'Login successful') {
          navigate('/dashboard');
        } else {
          alert('Login failed');
        }
      } catch (error) {
        alert('Login error');
      }
    } else {
      try {
        const response = await axios.post('http://localhost:5000/api/auth/register', formData);
        if (response.data.message === 'Registration successful') {
          setIsLogin(true);
        } else {
          alert('Registration failed');
        }
      } catch (error) {
        alert('Registration error');
      }
    }
  };

  return (
    <div className="auth-page">
      <div className="logo-section">
        <img src={logoImage} alt="IQAnadoluScout Logo" className="logo" />
      </div>
      <div className={`form-section ${isLogin ? 'login' : 'create-account'}`}>
        <div className="avatar-container">
          <div className="logo-overlay"></div>
          <img src={userIcon} alt="Avatar" className="avatar" />
          <h2>{isLogin ? 'Sign In' : 'Sign Up'}</h2>
        </div>
        <form onSubmit={handleSubmit}>
          {/* Create Account inputs */}
          {!isLogin && (
            <>
              <div className="input-group">
                <input
                  type="text"
                  id="firstname"
                  name="firstname"
                  value={formData.firstname}
                  onChange={handleChange}
                  placeholder="First Name"
                  required
                />
                <input
                  type="text"
                  id="lastname"
                  name="lastname"
                  value={formData.lastname}
                  onChange={handleChange}
                  placeholder="Last Name"
                  required
                />
              </div>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Email"
                required
              />
              <div className="input-group">
                <input
                  type="text"
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  placeholder="Role"
                  required
                />
                <input
                  type="text"
                  id="club"
                  name="club"
                  value={formData.club}
                  onChange={handleChange}
                  placeholder="Club"
                  required
                />
              </div>
            </>
          )}
          
          {/* Username and Password labels (visible only in Login) */}
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Username"
            required
          />
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Password"
            required
          />
          
          <div className="button-container">
            <button
              type="button"
              className="switch-button"
              onClick={() => setIsLogin(!isLogin)}
            >
              {isLogin ? 'Create Account' : 'Back to Login'}
            </button>
            <button type="submit" className="submit-button">
              {isLogin ? 'Log In' : 'Sign Up'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthenticationPage;
