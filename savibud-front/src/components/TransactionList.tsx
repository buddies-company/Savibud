import { useMemo, useState, useEffect } from 'react';
import { Text, Input, Button, Pill } from '@soilhat/react-components';
import { 
  MagnifyingGlassIcon, 
  XMarkIcon,
  ShoppingBagIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';
import { FinancialTransaction } from './FinancialTransaction';
import { Category, Transaction } from '../utils/constants/types';
import { TransactionDetailModal } from './TransactionDetail';
import { callApi } from '../services/api';

interface TransactionListProps {
  transactions: Transaction[];
  loading: boolean;
  hasMore: boolean;
  filters: { q: string, category_id: string };
  onFilterChange: (filters: unknown) => void;
  onLoadMore: () => void;
}

export const TransactionList = ({ 
  transactions, 
  loading, 
  hasMore, 
  filters, 
  onFilterChange,
  onLoadMore 
}: TransactionListProps) => {

  // Debounce search input to avoid API spam
  const [localSearch, setLocalSearch] = useState(filters.q);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
      
        const fetchData = async () => {
          const [catRes] = await Promise.all([
            callApi<Category[]>("/categories", "GET"),
          ]);
          setCategories(catRes.data);
        };

  useEffect(() => {
    fetchData();
    }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      onFilterChange({ q: localSearch });
    }, 400);
    return () => clearTimeout(timer);
  }, [localSearch, onFilterChange]);

  // Grouping Logic (Still needed for the UI display)
  const groupedData = useMemo(() => {
    const groups: Record<string, { items: Transaction[]; total: number }> = {};
    transactions.forEach((tx) => {
      const dateKey = tx.date instanceof Date 
        ? tx.date.toISOString().split('T')[0] 
        : String(tx.date).split('T')[0];
      
      if (!groups[dateKey]) groups[dateKey] = { items: [], total: 0 };
      groups[dateKey].items.push(tx);
      groups[dateKey].total += Number(tx.amount);
    });
    return Object.entries(groups).sort((a, b) => b[0].localeCompare(a[0]));
  }, [transactions]);

  return (
    <div className="space-y-4">
      <div className="sticky top-0 z-20 bg-surface-base/90 dark:bg-surface-base-dark/90 backdrop-blur-md pt-2 pb-4 space-y-3">
        <Input
          placeholder="Search activity..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          leftIcon={<MagnifyingGlassIcon className="h-5 w-5" />}
          rightIcon={loading ? <div className="animate-spin h-4 w-4 border-2 border-primary dark:border-primary-dark border-t-transparent rounded-full" /> : null}
          variant="soft"
        />

        <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar -mx-4 px-4 sm:mx-0 sm:px-0">
          <Pill 
            label="All" 
            active={!filters.category_id} 
            onClick={() => onFilterChange({ category_id: '' })} 
          />
          {categories.map((cat) => (
            <Pill 
              key={cat.id}
              label={cat.name}
              active={filters.category_id === cat.id}
              onClick={() => onFilterChange({ category_id: cat })}
            />
          ))}
        </div>
      </div>

      {transactions.length === 0 && !loading ? (
        <EmptyState onReset={() => { setLocalSearch(''); onFilterChange({ q: '', category_id: '' }); }} />
      ) : (
        <div className="space-y-8">
          {groupedData.map(([date, { items, total }]) => (
            <section key={date} className="space-y-3">
              <div className="flex justify-between items-center px-1">
                <Text variant="detail" className="font-black">
                  {formatHeaderDate(date)}
                </Text>
                <div className="h-px flex-1 mx-4 bg-border/40 dark:bg-border-dark/20" />
                <Text variant="small" bold className={total >= 0 ? 'text-state-success dark:text-state-success-dark' : ''}>
                  {total > 0 ? '+' : ''}{total.toLocaleString()} €
                </Text>
              </div>
              <div className="space-y-2">
                {items.map((tx) => <FinancialTransaction key={tx.id} tx={tx} onSelect={setSelectedTx} />)}
              </div>
              <TransactionDetailModal 
                    tx={selectedTx} 
                    isOpen={!!selectedTx} 
                    onClose={() => setSelectedTx(null)} 
                    categories={categories}
                    savingsGoals={[]}
                />
            </section>
          ))}

          {hasMore && (
            <div className="pt-4 pb-8 flex justify-center">
              <Button 
                variant="ghost" 
                onClick={onLoadMore} 
                isLoading={loading}
                leftIcon={<ChevronDownIcon className="h-4 w-4" />}
              >
                Load older transactions
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};


const EmptyState = ({ onReset }: { onReset: () => void }) => (
  <div className="flex flex-col items-center justify-center py-24 px-6">
    <div className="relative mb-6">
      <div className="absolute inset-0 bg-primary/10 dark:bg-primary-dark/90 blur-3xl rounded-full" />
      <div className="relative bg-surface-panel dark:bg-surface-panel-dark p-6 rounded-3xl border border-border dark:border-border-dark shadow-xl">
         <ShoppingBagIcon className="h-12 w-12 text-text-secondary/40 dark:text-text-secondary-dark/60" />
         <XMarkIcon className="h-6 w-6 text-state-danger dark:text-state-danger-dark absolute -top-1 -right-1 bg-surface-base dark:bg-surface-base-dark rounded-full border border-border dark:border-border-dark" />
      </div>
    </div>
    <Text variant="h3" className="mb-2">No Transactions Found</Text>
    <Text variant="small" className="text-text-secondary dark:text-text-secondary-dark text-center">Try adjusting your filters.</Text>
    <Button variant="ghost" className="mt-6" onClick={onReset}>Reset filters</Button>
  </div>
);

const formatHeaderDate = (dateStr: string) => {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return "Today";
  if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
  return date.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });
};