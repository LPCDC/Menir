import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';

const Login: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMsg, setErrorMsg] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrorMsg('');
        setIsLoading(true);

        try {
            // Execute the STRICTLY TYPED POST request to the authentication endpoint
            // This is mapped exactly to the OpenAPI 3.1.0 Contract definition.
            const { data, error, response } = await client.POST("/auth/token", {
                body: {
                    username,
                    password,
                },
            });

            if (response.status === 200 && data?.token) {
                // Galvanic Isolation boundary successfully unlocked
                localStorage.setItem("menir_session_token", data.token);

                // Redirect to Dashboard (Protected UI Boundary)
                navigate("/", { replace: true });
            } else {
                // Fallback for 401 or bad request
                setErrorMsg('Autenticação falhou. Credenciais forjadas ou inválidas.');
            }
        } catch (err) {
            setErrorMsg('Erro de Conexão. O Backend Synapse está inativo?');
            console.error("Login Interface Error:", err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ padding: '3rem', maxWidth: '400px', margin: '0 auto', textAlign: 'center', fontFamily: 'sans-serif' }}>
            <h2>Menir Enterprise</h2>
            <p style={{ color: '#555', marginBottom: '2rem' }}>Acesso Zero-Trust</p>

            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <input
                    type="text"
                    placeholder="Enterprise ID (ex: beco, santos)"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    style={{ padding: '0.8rem', border: '1px solid #ccc', borderRadius: '4px' }}
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={{ padding: '0.8rem', border: '1px solid #ccc', borderRadius: '4px' }}
                />

                {errorMsg && (
                    <div style={{ color: 'red', fontSize: '0.9rem', padding: '0.5rem', border: '1px solid red', borderRadius: '4px' }}>
                        {errorMsg}
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isLoading}
                    style={{
                        padding: '1rem',
                        background: isLoading ? '#999' : '#000',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: isLoading ? 'not-allowed' : 'pointer',
                        fontWeight: 'bold'
                    }}
                >
                    {isLoading ? 'Autenticando...' : 'Entrar no Sistema'}
                </button>
            </form>
        </div>
    );
};

export default Login;
