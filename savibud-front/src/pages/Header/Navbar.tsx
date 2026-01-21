import { Navbar, Button } from "@soilhat/react-components";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { 
  HomeIcon, 
  BanknotesIcon, 
  ChartPieIcon, 
  ArrowsRightLeftIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  BuildingLibraryIcon // New Icon for Accounts
} from '@heroicons/react/24/outline';
import React from "react";

// 1. Updated Nav Items
const navItems = [
  { 
    label: "Dashboard", 
    icon: <HomeIcon className="size-5" />, 
    element: <NavLink to="/" className={({ isActive }) => isActive ? "text-primary dark:text-primary-dark" : ""}>Dashboard</NavLink> 
  },
  { 
    label: "Accounts", // Added Accounts here
    icon: <BuildingLibraryIcon className="size-5" />, 
    element: <NavLink to="/accounts" className={({ isActive }) => isActive ? "text-primary dark:text-primary-dark" : ""}>Accounts</NavLink> 
  },
  { 
    label: "Transactions", 
    icon: <ArrowsRightLeftIcon className="size-5" />, 
    element: <NavLink to="/transactions" className={({ isActive }) => isActive ? "text-primary dark:text-primary-dark" : ""}>Transactions</NavLink> 
  },
  { 
    label: "Budgets", 
    icon: <ChartPieIcon className="size-5" />, 
    element: <NavLink to="/budgets" className={({ isActive }) => isActive ? "text-primary dark:text-primary-dark" : ""}>Budgets</NavLink> 
  },
  { 
    label: "Savings", 
    icon: <BanknotesIcon className="size-5" />, 
    element: <NavLink to="/savings" className={({ isActive }) => isActive ? "text-primary dark:text-primary-dark" : ""}>Savings</NavLink> 
  },
];

export const NavbarComponent = () => {
    const navigate = useNavigate();
  return (
    <Navbar 
      layout="sidebar"
      brandName="Savibud" 
      logoURl="/assets/pal.png"
      links={navItems}
      actions={
        <div className="space-y-2 w-full">
            {/* Optional: Quick access to Profile in actions area */}
            <Button 
              variant="ghost" 
              className="w-full justify-start gap-3 text-text-secondary dark:text-text-secondary-dark"
              onClick={() => navigate("/profile")}
            >
              <UserCircleIcon className="size-5" />
              Settings
            </Button>
            <Button 
              variant="ghost" 
              className="w-full justify-start gap-3 text-state-danger opacity-70 hover:opacity-100"
              onClick={() => navigate("/auth/login")}
            >
              <ArrowRightOnRectangleIcon className="size-5" />
              Logout
            </Button>
        </div>
      }
      mobileNav={<SavibudMobileNav />}
    >
      <Outlet />
    </Navbar>
  );
};

// 2. Updated Custom Mobile Navigation
const SavibudMobileNav = () => {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 h-16 border-t border-border dark:border-border-dark bg-surface-panel/90 dark:bg-surface-panel-dark/90 backdrop-blur-xl px-2 flex items-center justify-around">
      <MobileTab to="/" icon={<HomeIcon />} label="Home" />
      <MobileTab to="/accounts" icon={<BuildingLibraryIcon />} label="Banks" /> {/* Added to mobile */}
      <MobileTab to="/transactions" icon={<ArrowsRightLeftIcon />} label="Activity" />
      <MobileTab to="/savings" icon={<BanknotesIcon />} label="Savings" />
      <MobileTab to="/budgets" icon={<ChartPieIcon />} label="Budget" />
    </nav>
  );
};

const MobileTab = ({ to, icon, label }: { to: string; icon: React.ReactElement; label: string }) => (
  <NavLink 
    to={to} 
    className={({ isActive }) => `
      flex flex-col items-center gap-1 transition-all duration-300 min-w-[60px]
      ${isActive ? 'text-primary dark:text-primary-dark scale-110' : 'text-text-secondary dark:text-text-secondary-dark'}
    `}
  >
    {React.cloneElement(icon, { className: "size-5" })}
    <span className="text-[9px] font-black uppercase tracking-tighter">{label}</span>
  </NavLink>
);