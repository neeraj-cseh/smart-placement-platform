import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";

const dashboardRoutes = [
  "/",
  "/login",
  "/signup",
  "/learning-path",
  "/practice",
  "/mock-tests",
  "/code-editor",
  "/ai-interview",
  "/analytics",
  "/companies",
  "/profile",
  "/admin",
];

function App() {
  return (
    <Router>
      <Routes>
        {dashboardRoutes.map((path) => (
          <Route key={path} path={path} element={<Layout />} />
        ))}
      </Routes>
    </Router>
  );
}

export default App;
