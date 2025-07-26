import React, { useState, useEffect } from "react";
import { BrowserRouter, Route, Routes, Navigate, useNavigate } from "react-router-dom";

const api = (endpoint, opt) =>
  fetch(process.env.REACT_APP_API_URL + endpoint, {
    ...opt,
    headers: {
      "Content-Type": "application/json",
      ...(opt?.headers || {}),
      ...(localStorage.getItem("token")
        ? { Authorization: `Bearer ${localStorage.getItem("token")}` }
        : {}),
    },
  }).then((r) => r.json());

function Login({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const nav = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    const res = await api("/token", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    if (res.access_token) {
      localStorage.setItem("token", res.access_token);
      setUser({ username, role: res.role });
      nav("/");
    } else {
      alert("Login failed");
    }
  };

  return (
    <div className="container">
      <form onSubmit={handleLogin} className="mx-auto mt-5" style={{ maxWidth: 320 }}>
        <h3>Login</h3>
        <input required className="form-control my-2" value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" />
        <input required className="form-control my-2" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
        <button className="btn btn-primary w-100 mt-2" type="submit">Login</button>
      </form>
    </div>
  );
}

function Dashboard({ user }) {
  return (
    <div className="container">
      <h2 className="mt-3">Welcome, {user.username}!</h2>
      <div>Role: {user.role}</div>
      <nav className="nav mt-3">
        <a className="nav-link" href="/products">Products</a>
        <a className="nav-link" href="/sales">Sales</a>
        <a className="nav-link" href="/billing">Billing</a>
        {user.role==="admin" && <a className="nav-link" href="/export">Marketplace Export</a>}
      </nav>
    </div>
  );
}

// You'd create ProductList, AddProduct, SalesPage, BillingPage, ExportPage components here (similar pattern).

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (localStorage.getItem("token"))
      api("/me").then((u) => setUser(u.user ? { username: u.user, role: u.role } : null));
  }, []);

  if (!user) return (
    <BrowserRouter>
      <Routes>
        <Route path="*" element={<Login setUser={setUser} />} />
      </Routes>
    </BrowserRouter>
  );

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard user={user} />} />
        {/* Add
            <Route path="/products" element={<ProductList ... />} />
            <Route path="/sales" element={<SalesPage ... />} /> etc.
        */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;