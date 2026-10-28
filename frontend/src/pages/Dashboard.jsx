import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import AdminDashboardView from "./AdminDashboardView";
import UserDashboardView from "./UserDashboardView";

export default function Dashboard() {
    const { user } = useContext(AuthContext);

    if (!user) {
        return null;
    }

    if (user.role === "admin") {
        return <AdminDashboardView />;
    }

    return <UserDashboardView />;
}
