import { useEffect, useRef } from "react";
import { callApi } from "../../services/api";

export const Callback = () => {
    const hasCalledApi = useRef(false);

    useEffect(() => {
        const urlParams = new URLSearchParams(globalThis.location.search);
        const code = urlParams.get('code');
        const userId = urlParams.get('state');

        if (code && !hasCalledApi.current) {
            hasCalledApi.current = true;

            callApi("/powens/exchange_token", "POST", undefined, { code, user_id: userId })
                .then(() => {
                    globalThis.location.href = "/";
                })
                .catch((err) => {
                    console.error("Exchange failed:", err);
                });
        }
        else {
            globalThis.location.href = "/";
        }
    }, []);
    return (
        <div>
            <h1>Connecting your bank...</h1>
        </div>
    );
}