import { useToast } from "@soilhat/react-components";
import { saveDataToCache, getCachedData } from "./idb";

// Global flag to prevent multiple concurrent token refresh attempts
let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

export const getApiUrl = (url: string) => {
    const isDemo = localStorage.getItem("demo")
    const api = isDemo ? "/demo" : "/api";
    const postfix = isDemo ? ".json" : "";
    return `${api}${url}${postfix}`
}

const refreshAccessToken = async (): Promise<boolean> => {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(getApiUrl("/token/refresh"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (response.ok) {
            const data = await response.json();
            if (data.access_token) {
                localStorage.setItem("token", data.access_token);
                return true;
            }
        }
    } catch (err) {
        console.debug('Failed to refresh token', err);
    }
    return false;
};

// API response wrapper
export type ApiResponse<T = unknown> = { data: T; offline: boolean };

// Track in-flight GET requests to avoid duplicate network calls (useful during
// React Strict Mode double-mount in development and for rapidly re-rendered components).
const inFlightRequests: Map<string, Promise<ApiResponse<unknown>>> = new Map();

export const callApi = async <T = unknown>(
    url: string,
    method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" = "GET",
    save_name?: string | undefined,
    data?: BodyInit | null | undefined | object,
    params?: Record<string, string | number | boolean | null | undefined>
): Promise<ApiResponse<T>> => {
    const offline = !navigator.onLine
    if (offline && save_name) {
        serveCachedData(save_name);
    }

    let body: BodyInit | undefined = undefined;
    const headers: Record<string, string> = {
        "Authorization": `Bearer ${localStorage.getItem("token")}`,
        "Access-Control-Allow-Origin": "*",
    };

    if (method !== "GET" && data !== undefined && data !== null) {
        if (data instanceof FormData) {
            body = data;
            // Do not set Content-Type for FormData
        } else if (typeof data === "string") {
            body = data;
            headers["Content-Type"] = "application/json";
        } else {
            body = JSON.stringify(data);
            headers["Content-Type"] = "application/json";
        }
    }

    // Build URL with query parameters
    let finalUrl = getApiUrl(url);
    if (params && Object.keys(params).length > 0) {
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                queryParams.append(key, String(value));
            }
        });
        finalUrl += `?${queryParams.toString()}`;
    }

    // Deduplicate GET requests by returning the existing in-flight Promise when present.
    if (method === 'GET') {
        const key = finalUrl;
        if (inFlightRequests.has(key)) {
            return inFlightRequests.get(key) as Promise<ApiResponse<T>>;
        }

        const promise: Promise<ApiResponse<T>> = fetch(finalUrl, { method, headers, body })
            .then(async (response) => {
                if (!response.ok) {
                    if (response.status === 401 || response.status === 403) {
                        // Try to refresh token
                        if (!isRefreshing) {
                            isRefreshing = true;
                            refreshPromise = refreshAccessToken();
                        }
                        const refreshed = await refreshPromise;
                        isRefreshing = false;
                        refreshPromise = null;

                        if (refreshed) {
                            // Retry the request with new token
                            const newHeaders = {
                                ...headers,
                                "Authorization": `Bearer ${localStorage.getItem("token")}`,
                            };
                            const retryResponse = await fetch(finalUrl, { method, headers: newHeaders, body });
                            if (retryResponse.ok) {
                                const json = (await retryResponse.json()) as T;
                                if (save_name) await saveDataToCache(json, save_name);
                                return { data: json, offline };
                            }
                        }
                        // If refresh failed or retry failed, logout
                        localStorage.clear();
                        globalThis.location.href = "/auth/login";
                        throw new Error("Session expired");
                    }
                    throw new Error(response.statusText);
                }
                const json = (await response.json()) as T;
                if (save_name) await saveDataToCache(json, save_name);
                return { data: json, offline };
            }).catch(async (err) => {
                if (err.message === "Failed to fetch") {
                    if (save_name) return serveCachedData<T>(save_name);
                }
                throw err;
            }).finally(() => {
                inFlightRequests.delete(key);
            });

        // store as loose ApiResponse<unknown> in the map for deduping
        inFlightRequests.set(key, promise as Promise<ApiResponse<unknown>>);
        return promise;
    }

    // Non-GET requests: proceed normally (no dedupe)
    return await fetch(finalUrl, {
        method: method,
        headers: headers,
        body: body,
    }).then(async (response) => {
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                // Try to refresh token
                if (!isRefreshing) {
                    isRefreshing = true;
                    refreshPromise = refreshAccessToken();
                }
                const refreshed = await refreshPromise;
                isRefreshing = false;
                refreshPromise = null;

                if (refreshed) {
                    // Retry the request with new token
                    const newHeaders = {
                        ...headers,
                        "Authorization": `Bearer ${localStorage.getItem("token")}`,
                    };
                    const retryResponse = await fetch(finalUrl, { method, headers: newHeaders, body });
                    if (retryResponse.ok) {
                        const json = (await retryResponse.json()) as T;
                        if (save_name) await saveDataToCache(json, save_name);
                        return { data: json, offline };
                    }
                }
                // If refresh failed or retry failed, logout
                localStorage.clear();
                globalThis.location.href = "/auth/login";
                throw new Error("Session expired");
            }
            throw new Error(response.statusText);
        }
        const json = (await response.json()) as T;
        if (save_name) await saveDataToCache(json, save_name);
        return { data: json, offline };
    }).catch(async (err) => {
        if (err.message === "Failed to fetch") {
            if (save_name) {
                return serveCachedData<T>(save_name);
            }
        }
        throw err;
    });
}

const serveCachedData = async <T = unknown>(save_name: string): Promise<ApiResponse<T>> => {
    const { error, info } = useToast();
    const cached = await getCachedData(save_name);
    if (cached) info("You are offline. Serving cached data.");
    else error("You are offline and no cached data is available.");
    return { data: cached as T, offline: true };
}