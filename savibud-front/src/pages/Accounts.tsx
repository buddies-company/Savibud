import { useEffect, useState, useMemo } from 'react';
import {
  Heading,
  Button,
  Card,
} from '@soilhat/react-components';
import {
  PlusIcon,
  ArrowTopRightOnSquareIcon,
  CreditCardIcon,
  WalletIcon,
  BuildingLibraryIcon,
  InformationCircleIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';
import { Account } from '../utils/constants/types';
import { callApi } from '../services/api';

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAccounts = async () => {
    setIsLoading(true);
    try {
      const res = await callApi<Account[]>("/accounts", "GET");
      setAccounts(res.data);
    } catch (error) {
      console.error("Failed to fetch accounts", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const totalBalance = useMemo(() => {
    return accounts.reduce((acc, curr) => acc + Number(curr.balance), 0);
  }, [accounts]);

  const handleConnectBank = () => {
    callApi<{url:string}>("/powens/connect").then(async (data) => {
      globalThis.location.href = data.data.url; // Redirect to Powens WebView
    });
  };

  return (
    <div className="min-h-screen bg-surface-base dark:bg-surface-base-dark transition-colors duration-200">
      <Heading
        title="My Accounts"
        variant="page"
      >
        <Button 
          onClick={handleConnectBank}
          leftIcon={<PlusIcon className="h-4 w-4" />}
          className="shadow-lg shadow-primary/20"
        >
          Connect Bank
        </Button>
      </Heading>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* --- GLOBAL NET WORTH SUMMARY --- */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-primary dark:bg-primary-dark border-none rounded-[2.5rem] p-6 shadow-2xl overflow-hidden relative group">
            <div className="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl group-hover:scale-125 transition-transform duration-700" />
            <div className="relative z-10">
              <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-80">Total Net Worth</p>
              <h2 className="text-4xl font-black mt-2">
                {totalBalance.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}€
              </h2>
              <div className="mt-4 flex items-center gap-2">
                <span className="px-2 py-0.5 bg-white/20 rounded-md text-[10px] font-bold">
                  {accounts.length} ACTIVE CONNECTIONS
                </span>
              </div>
            </div>
          </Card>

          {/* Optional: Add small stats cards here like "Monthly Change" or "Savings Ratio" */}
        </div>

        {/* --- ACCOUNTS LIST --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoading ? (
            // Simple Skeleton State
            [1, 2, 3].map(i => (
              <div key={i} className="h-48 bg-surface-card dark:bg-surface-card-dark rounded-3xl animate-pulse" />
            ))
          ) : accounts.length > 0 ? (
            accounts.map((acc) => (
              <Card 
                key={acc.id} 
                className="rounded-3xl hover:shadow-xl transition-all duration-300 border-border/50 dark:border-border-dark/50 group cursor-pointer"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-2xl bg-surface-base dark:bg-surface-base-dark flex items-center justify-center text-primary shadow-inner">
                        {acc.type === 'card' ? <CreditCardIcon className="h-6 w-6" /> : <BuildingLibraryIcon className="h-6 w-6" />}
                      </div>
                      <div>
                        <h3 className="font-bold text-text-primary dark:text-text-primary-dark truncate max-w-[150px]">
                          {acc.label}
                        </h3>
                        <p className="text-[10px] text-text-secondary dark:text-text-secondary-dark uppercase font-black tracking-widest opacity-60">
                          {acc.bank_name || 'Bank Account'}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <p className="text-[10px] font-black text-text-secondary dark:text-text-secondary-dark uppercase tracking-widest">Available Balance</p>
                    <div className="flex items-baseline gap-1">
                      <span className={`text-2xl font-black ${Number(acc.balance) < 0 ? 'text-state-danger' : 'text-text-primary dark:text-text-primary-dark'}`}>
                        {Number(acc.balance).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}
                      </span>
                      <span className="text-sm font-bold opacity-30 text-text-primary dark:text-text-primary-dark">€</span>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-border/50 dark:border-border-dark/50 flex justify-between items-center">
                    <div className="flex items-center gap-1.5">
                       <div className="w-1.5 h-1.5 rounded-full bg-state-success animate-pulse" />
                       <span className="text-[9px] font-black text-text-secondary uppercase">Synced via Powens</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            /* --- EMPTY STATE --- */
            <div className="col-span-full py-20 flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-20 h-20 bg-surface-base dark:bg-surface-base-dark rounded-[2.5rem] flex items-center justify-center">
                <WalletIcon className="h-10 w-10 text-text-secondary opacity-20" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-text-primary dark:text-text-primary-dark">No accounts linked</h3>
                <p className="text-sm text-text-secondary max-w-xs mx-auto">
                  Connect your bank to automatically sync your transactions and manage your budget.
                </p>
              </div>
              <Button onClick={handleConnectBank} variant="ghost" color_name="light">
                Get Started
              </Button>
            </div>
          )}
        </div>

        {/* --- INFORMATION NOTICE --- */}
        <div className="bg-surface-card dark:bg-surface-card-dark border border-border dark:border-border-dark p-4 rounded-2xl flex gap-4 items-start">
          <InformationCircleIcon className="h-6 w-6 text-primary shrink-0" />
          <p className="text-xs text-text-secondary dark:text-text-secondary-dark leading-relaxed">
            Your bank data is securely synchronized through Powens. We do not store your banking credentials. 
            Balances are typically updated every 6 to 24 hours depending on your bank's API.
          </p>
        </div>
      </main>
    </div>
  );
}