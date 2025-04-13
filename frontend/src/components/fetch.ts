import { getAccessToken } from "./Auth";

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const token = getAccessToken();
    if (!token) {
        throw new Error("No token found, please login");
    }
    options.headers = { ...options.headers, Authorization: `Bearer ${token}` };
    return fetch(url, options);
}

export const fetchCustom = async (url: string, options: RequestInit = {}) => {
    return fetchWithAuth(url, options);
};
