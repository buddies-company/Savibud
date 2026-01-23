import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./useAuth"

const PrivateRoute = () => {
    const { user } = useAuth();
    if (!user) return <Navigate to="/auth/login" />
    return <Outlet />
}

export default PrivateRoute