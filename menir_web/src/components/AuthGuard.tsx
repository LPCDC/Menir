import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

/**
 * AuthGuard Higher-Order Component
 * Establishes a render-blocking security boundary.
 * Verifies the presence of the JWT session token before rendering protected routes.
 */
const AuthGuard: React.FC = () => {
    const token = localStorage.getItem('menir_session_token');

    if (!token) {
        // Redirect to login if token is missing, replacing the history stack
        return <Navigate to="/login" replace />;
    }

    // Render the child routes if the token is present
    return <Outlet />;
};

export default AuthGuard;
