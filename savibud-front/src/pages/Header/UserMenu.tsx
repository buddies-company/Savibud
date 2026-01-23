import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { User } from '../../utils/constants/types';
import { NavLink } from 'react-router-dom';

type UserMenuProps = {
  user?: User | null;
  onLogout: () => void;
};

export default function UserMenu({ user, onLogout }: Readonly<UserMenuProps>) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  const { t } = useTranslation('translation', { keyPrefix: 'pages.user' });

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      const target = e.target as Node | null;
      if (ref.current && target && !ref.current.contains(target)) setOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const avatarUrl =
    user?.avatar && user.avatar.trim().length > 0
      ? user.avatar
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.username ?? 'User')}`;

  return (
    <div className="relative text-gray-800 dark:text-gray-100" ref={ref}>
      <button
        className="flex items-center gap-2 rounded-full px-2 py-1 hover:bg-gray-100 dark:hover:bg-gray-800 focus-ring"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <img src={avatarUrl} alt="Avatar" className="h-8 w-8 rounded-full" />
        <span className="hidden sm:inline text-sm text-gray-800 dark:text-gray-100">
          {user?.username ?? 'User'}
        </span>
        <svg className="h-4 w-4 text-gray-600 dark:text-gray-300" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path
            fillRule="evenodd"
            d="M5.23 7.21a.75.75 0 011.06.02L10 11.17l3.71-3.94a.75.75 0 011.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-56 rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg p-1"
        >
          <NavLink to="/settings" className="block rounded px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
            Paramètres
          </NavLink>
          <button
            onClick={onLogout}
            role="menuitem"
            className="w-full text-left rounded px-3 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            {t("logout")}
          </button>
        </div>
      )}
    </div>
  );
}
