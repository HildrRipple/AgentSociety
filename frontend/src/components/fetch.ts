import { getAccessToken } from "./Auth";

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const token = getAccessToken();
    if (!token) {
        throw new Error("No token found");
    }
    options.headers = { ...options.headers, Authorization: `Bearer ${token}` };
    return fetch(url, options);
}