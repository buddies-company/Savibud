import { Navbar, Button } from "@soilhat/react-components";
import { Outlet, useNavigate } from "react-router-dom";
import { 
  HomeIcon, 
  BanknotesIcon, 
  ChartPieIcon, 
  ArrowsRightLeftIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  BuildingLibraryIcon,
} from '@heroicons/react/24/outline';

const navItems = [
  { 
    label: "Dashboard", 
    icon: <HomeIcon className="size-5" />, 
    to:"/",
  },
  { 
    label: "Accounts", 
    icon: <BuildingLibraryIcon className="size-5" />, 
    to:"/accounts",
  },
  { 
    label: "Transactions", 
    icon: <ArrowsRightLeftIcon className="size-5" />, 
    to:"/transactions",
  },
  { 
    label: "Budgets", 
    icon: <ChartPieIcon className="size-5" />, 
    to:"/budgets",
  },
  { 
    label: "Savings", 
    icon: <BanknotesIcon className="size-5" />, 
    to:"/savings",
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
    >
      <Outlet />
    </Navbar>
  );
};
