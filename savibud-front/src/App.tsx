import { Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { NavbarComponent } from "./pages/Header/Navbar";
import AuthLayout, { Login, Register } from './pages/auth';
import AuthProvider from "./components/routing/AuthProvider";
import PrivateRoute from "./components/routing/PrivateRoute";
import { Callback } from "./pages/powens/Callback";
import SavingsPage from "./pages/Saving";
import BudgetPage from "./pages/Budget";
import { TransactionPage } from "./pages/Transactions";
import AccountsPage from "./pages/Accounts";

const App = () => {
  return (
    <Suspense fallback="loading">
      <BrowserRouter>
        <Routes>
          <Route element={<AuthProvider />}>
            <Route path="auth" element={<AuthLayout />}>
              <Route path="login" element={<Login />} />
              <Route path="register" element={<Register />} />
            </Route>
            <Route element={<PrivateRoute />}>
              <Route element={<NavbarComponent />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/savings" element={<SavingsPage />} />
                <Route path="/budgets" element={<BudgetPage />} />
                <Route path="/transactions" element={<TransactionPage />}/>
                <Route path="/accounts" element={<AccountsPage />} />
                <Route path="/powens/callback" element={<Callback />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </Suspense>
  );
};
export default App;