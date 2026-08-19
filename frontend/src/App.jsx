import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import ScanEmail from "./pages/ScanEmail";
import Navbar from "./components/Navbar";

export default function App() {

    return (
        <BrowserRouter>

            <Navbar />

            <Routes>

                <Route
                    path="/"
                    element={<Dashboard />}
                />

                <Route
                    path="/scan"
                    element={<ScanEmail />}
                />

            </Routes>

        </BrowserRouter>
    );
}