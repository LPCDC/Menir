import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import AuthGuard from './components/AuthGuard';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import './App.css'; // Standard Vite styling import

const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    // AuthGuard establishes the render-blocking boundary for all child routes
    element: <AuthGuard />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
    ],
  },
]);

const App: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default App;
