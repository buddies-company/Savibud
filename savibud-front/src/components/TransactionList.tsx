import { useMemo, useState } from 'react';
import { Text, Button } from '@soilhat/react-components';
import {
  XMarkIcon,
  ShoppingBagIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';
import { FinancialTransaction } from './FinancialTransaction';
import { Category, Transaction, FilterParams } from '../utils/constants/types';
import { TransactionDetailModal } from './TransactionDetail';

interface TransactionListProps {
  transactions: Transaction[];
  loading: boolean;
  searchLoading: boolean;
  hasMore: boolean;
  savings: any[];
  categories?: Category[];
  onFilterChange: (filters: Partial<FilterParams>) => void;
  onLoadMore: () => void;
  onRefresh?: () => void;
}

export const TransactionList = ({
  transactions,
  loading,
  searchLoading,
  hasMore,
  savings,
  categories,
  onFilterChange,
  onLoadMore,
  onRefresh
}: TransactionListProps) => {
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

  const groupedData = useMemo(() => {
    const groups: Record<string, { items: Transaction[]; total: number }> = {};

    transactions.forEach((tx) => {
      const dateKey = new Date(tx.date).toISOString().split('T')[0];

      if (!groups[dateKey]) {
        groups[dateKey] = { items: [], total: 0 };
      }

      groups[dateKey].items.push(tx);
      groups[dateKey].total += Number(tx.amount);
    });

    return Object.entries(groups).sort((a, b) => b[0].localeCompare(a[0]));
  }, [transactions]);

  if (searchLoading) {
    return <div className="py-20 text-center"><Text>Searching...</Text></div>;
  }

  return (
    <div className="space-y-4">
      {transactions.length === 0 && !loading ? (
        <EmptyState onReset={() => onFilterChange({ q: '', category_id: '', account_id: '', savings_goal_id: '' })} />
      ) : (
        <div className="space-y-8">
          {groupedData.map(([date, { items, total }]) => (
            <section key={date} className="space-y-3">
              <div className="flex justify-between items-center px-1">
                <Text variant="detail" className="font-black uppercase tracking-wider opacity-60">
                  {formatHeaderDate(date)}
                </Text>
                <div className="h-px flex-1 mx-4 bg-border/40 dark:bg-border-dark/20" />
                <Text variant="small" bold className={total >= 0 ? 'text-state-success' : ''}>
                  {total > 0 ? '+' : ''}{total.toLocaleString(undefined, { minimumFractionDigits: 2 })} €
                </Text>
              </div>
              <div className="space-y-2">
                {items.map((tx) => (
                  <FinancialTransaction key={tx.id} tx={tx} onSelect={setSelectedTx} />
                ))}
              </div>
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
                Load more
              </Button>
            </div>
          )}
        </div>
      )}

      <TransactionDetailModal
        tx={selectedTx}
        isOpen={!!selectedTx}
        onClose={() => setSelectedTx(null)}
        onRefresh={onRefresh}
        categories={categories || []}
        savingsGoals={savings}
      />
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