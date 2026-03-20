import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heading, Button, Card } from '@soilhat/react-components';
import {
  PlusIcon, CreditCardIcon, WalletIcon, BuildingLibraryIcon,
  ArrowRightIcon, PencilSquareIcon, ArrowPathIcon
} from '@heroicons/react/24/outline';
import { UnifiedAccount, BankAccount, ManualAccount } from '../utils/constants/types';
import { callApi } from '../services/api';

export default function AccountsPage() {
  const navigate = useNavigate();
  const [accounts, setAccounts] = useState<UnifiedAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState<string | null>(null);

  const fetchAccounts = async () => {
    setIsLoading(true);
    try {
      const res = await callApi<UnifiedAccount[]>("/accounts", "GET");
      setAccounts(res.data);
    } catch (error) {
      console.error("Failed to fetch accounts", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSync = async (accountId?: string) => {
    const syncId = accountId || 'global';
    setIsSyncing(syncId);
    try {
      const endpoint = accountId ? `/accounts/${accountId}/sync` : "/accounts/sync";
      await callApi(endpoint, "POST");
      await fetchAccounts(); // Refresh data after sync
    } catch (error) {
      console.error("Sync failed", error);
    } finally {
      setIsSyncing(null);
    }
  };

  useEffect(() => { fetchAccounts(); }, []);

  const categorized = useMemo(() => {
    const data = {
      banks: {} as Record<string, { total: number; list: BankAccount[] }>,
      manual: [] as ManualAccount[],
      loans: [] as ManualAccount[],
      totalNetWorth: 0
    };

    accounts.forEach(acc => {
      // Handle balance mapping: 'balance' for Bank, 'current_balance' for Manual
      const balance = 'balance' in acc ? Number(acc.balance) : Number(acc.current_balance);
      data.totalNetWorth += balance;

      if ('bank_name' in acc) {
        // It's a Bank Account
        const bank = acc.bank_name || 'Other';
        if (!data.banks[bank]) data.banks[bank] = { total: 0, list: [] };
        data.banks[bank].list.push(acc);
        data.banks[bank].total += balance;
      } else {
        // It's a Manual Account
        if (acc.account_type === 'loan') {
          data.loans.push(acc);
        } else {
          data.manual.push(acc);
        }
      }
    });

    return data;
  }, [accounts]);

  const handleConnectBank = () => {
    callApi<{ url: string }>("/powens/connect").then(async (data) => {
      globalThis.location.href = data.data.url;
    });
  };

  return (
    <div className="min-h-screen bg-surface-base dark:bg-surface-base-dark">
      <Heading title="Portfolio" variant="page">
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => navigate('/accounts/manual/new')} leftIcon={<PlusIcon className="h-4 w-4" />}>
            Add Manual
          </Button>
          <Button
            variant="ghost"
            onClick={() => handleSync()}
            isLoading={isSyncing === 'global'}
            leftIcon={<ArrowPathIcon className={`h-4 w-4 ${isSyncing === 'global' ? 'animate-spin' : ''}`} />}
          >
            Sync All
          </Button>
          <Button onClick={handleConnectBank} leftIcon={<BuildingLibraryIcon className="h-4 w-4" />}>
            Connect Bank
          </Button>
        </div>
      </Heading>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-12">
        {/* 1. Net Worth Header */}
        <Card className="bg-primary p-8 text-white rounded-[2.5rem]">
          <p className="text-[10px] font-black uppercase tracking-widest opacity-70">Total Net Worth</p>
          <h2 className="text-5xl font-black mt-2">
            {categorized.totalNetWorth.toLocaleString('fr-FR')}€
          </h2>
        </Card>

        {isLoading ? (
          <p>Loading accounts...</p>
        ) : (
          <>
            {/* 2. Bank Sections */}
            {Object.entries(categorized.banks).map(([name, group]) => (
              <div key={name} className="space-y-4">
                <div className="flex justify-between items-end px-4 border-b border-border/50 pb-2">
                  <h3 className="text-xl font-black uppercase italic">{name}</h3>
                  <span className="font-bold text-primary">{group.total.toLocaleString()}€</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {group.list.map(acc => (
                    <AccountCard key={acc.id} account={acc} type="bank" isSyncing={isSyncing} handleSync={handleSync} />
                  ))}
                </div>
              </div>
            ))}

            {/* 3. Manual Assets */}
            {categorized.manual.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-sm font-black text-text-secondary uppercase tracking-[0.3em] px-4">Manual Assets</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {categorized.manual.map(acc => (
                    <AccountCard key={acc.id} account={acc} type="manual" />
                  ))}
                </div>
              </div>
            )}

            {/* 4. Liabilities (Loans) */}
            {categorized.loans.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-sm font-black text-state-danger uppercase tracking-[0.3em] px-4">Liabilities</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {categorized.loans.map(acc => (
                    <AccountCard key={acc.id} account={acc} type="loan" />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

// --- Dynamic Card Component ---
function AccountCard({ account, type, isSyncing, handleSync}: { account: UnifiedAccount, type: 'bank' | 'manual' | 'loan', isSyncing?: string | null, handleSync?: (id: string) => void }) {
  const navigate = useNavigate();
  // Safe balance access based on type
  const balance = 'balance' in account ? account.balance : account.current_balance;

  return (
    <Card className="rounded-[2rem] p-6 hover:shadow-lg transition-all group">
      <div className="flex justify-between mb-4">
        <div className={`p-3 rounded-xl ${type === 'loan' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}>
          {type === 'bank' ? <BuildingLibraryIcon className="h-6 w-6" /> :
            type === 'loan' ? <CreditCardIcon className="h-6 w-6" /> : <WalletIcon className="h-6 w-6" />}
        </div>
        {type === 'bank' && <button
          onClick={(e) => { e.stopPropagation(); handleSync && handleSync(account.id); }}
          disabled={isSyncing !== null}
          className="p-2 hover:bg-surface-base dark:hover:bg-surface-base-dark rounded-xl transition-colors text-text-secondary"
        >
          <ArrowPathIcon className={`h-4 w-4 ${isSyncing === account.id ? 'animate-spin text-primary' : ''}`} />
        </button>}
        <button onClick={() => navigate(`/accounts/${type}/edit/${account.id}`)} className="opacity-0 group-hover:opacity-100 transition-opacity">
          <PencilSquareIcon className="h-5 w-5 text-text-secondary" />
        </button>
      </div>

      <p className="text-[10px] font-black text-text-secondary uppercase truncate">{account.name}</p>
      <p className={`text-2xl font-black mt-1 ${balance < 0 ? 'text-state-danger' : ''}`}>
        {Number(balance).toLocaleString('fr-FR')}€
      </p>

      <Button
        variant="ghost"
        className="w-full justify-between mt-4 px-0 hover:bg-transparent group-hover:text-primary"
        rightIcon={<ArrowRightIcon className="h-4 w-4" />}
        onClick={() => navigate(`/transactions?account_id=${account.id}`)}
      >
        View Details
      </Button>
    </Card>
  );
}