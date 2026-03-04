import createClient from "openapi-fetch";
import type { paths } from "./schema";

// 1. Initialize strictly typed client wrapping the Menir OpenApi Schema
const client = createClient<paths>({
    baseUrl: "http://localhost:8000",
});

// 2. Galvanic Isolation Middleware
// Enforces the "menir_session_token" Bearer JWT on every outbound call
client.use({
    onRequest({ request }) {
        const token = localStorage.getItem("menir_session_token");
        if (token) {
            request.headers.set("Authorization", `Bearer ${token}`);
        }
        return request;
    },

    onResponse({ response }) {
        // 3. Security Boundary: If the tenant context was forged or token expired,
        // the backend returns 401 or 403. Kill the session immediately.
        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem("menir_session_token");
            // Hard refresh to trigger the UI Guard fallback (e.g. redirect to Login/Auth block)
            window.location.reload();
        }
        return response;
    },
});

export default client;
