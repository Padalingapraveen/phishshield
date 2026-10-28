import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useLocation } from "react-router-dom";

export default function Layout({ children }) {
    const location = useLocation();
    
    // Map paths to page titles
    const getPageTitle = () => {
        if (location.pathname === "/") return "Dashboard Overview";
        if (location.pathname === "/scan") return "Email Analysis";
        return "Dashboard";
    };

    return (
        <div className="soc-layout">
            <Sidebar />
            <div className="soc-main">
                <Topbar pageTitle={getPageTitle()} />
                <main className="soc-content">
                    {children}
                </main>
            </div>
        </div>
    );
}
