import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { callApi } from "../services/api";
import { Transaction, FilterParams, BankAccount, SavingsGoal, Category } from "../utils/constants/types";
import { TransactionList } from "../components/TransactionList";
import { Button, Input, Select } from "@soilhat/react-components";
import { XMarkIcon } from "@heroicons/react/24/outline";

export const TransactionPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);

  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [savings, setSavings] = useState<SavingsGoal[]>([]);

  const [filters, setFilters] = useState<FilterParams>({
    q: searchParams.get('q') || '',
    category_id: searchParams.get('category_id') || '',
    account_id: searchParams.get('account_id') || '',
    savings_goal_id: searchParams.get('savings_goal_id') || '',
    date_from: searchParams.get('date_from') || '',
    date_to: searchParams.get('date_to') || '',
    uncategorized_only: searchParams.get('uncategorized_only') === 'true',
  });

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [accRes, budRes, savRes] = await Promise.all([
          callApi<BankAccount[]>("/accounts", "GET"),
          callApi<Category[]>("/categories", "GET"),
          callApi<SavingsGoal[]>("/savings_goals", "GET"),
        ]);
        setAccounts(accRes.data || []);
        setCategories(budRes.data || []);
        setSavings(savRes.data || []);
      } catch (error) {
        console.error("Failed to fetch filter options", error);
      }
    };
    fetchOptions();
  }, []);

  const fetchTransactions = useCallback(async (isNewFilter: boolean, pageToFetch: number) => {
    if (isNewFilter) setSearchLoading(true);
    else setLoading(true);

    const cleanFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, value]) => value !== '')
    );

    try {
      const response = await callApi<Transaction[]>(
        "/transactions", 
        "GET", 
        undefined, 
        undefined,
        { 
          ...cleanFilters, 
          page: pageToFetch, 
          limit: 20 
        }
      );

      const newData = response.data || [];
      setTransactions(prev => isNewFilter ? newData : [...prev, ...newData]);
      setHasMore(newData.length === 20);
    } catch (error) {
      console.error("Failed to fetch transactions", error);
    } finally {
      setSearchLoading(false);
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    setPage(1);
    fetchTransactions(true, 1);

    const newParams = new URLSearchParams();
    Object.entries(filters).forEach(([key, val]) => {
      if (val) newParams.set(key, String(val));
    });
    setSearchParams(newParams);
  }, [filters, fetchTransactions, setSearchParams]);

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchTransactions(false, nextPage);
  };

  const handleRefresh = () => {
    setPage(1);
    fetchTransactions(true, 1);
  };

  const handleClearFilters = () => {
    setFilters({ q: '', category_id: '', account_id: '', savings_goal_id: '', date_from: '', date_to: '', uncategorized_only: false });
  };

  const getOptions = (data: any[], labelKey: string, allLabel: string) => [
    { value: "", label: allLabel },
    ...data.map(item => ({ 
      value: item.id, 
      label: labelKey.includes('.') ? item.category?.name : item[labelKey] 
    }))
  ];

  // Get today's date and 90 days ago for default date range
  const getTodayString = () => new Date().toISOString().split('T')[0];
  const get90DaysAgoString = () => {
    const date = new Date();
    date.setDate(date.getDate() - 90);
    return date.toISOString().split('T')[0];
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <div className="mb-6 space-y-4 p-4 bg-surface-card dark:bg-surface-card-dark rounded-2xl border border-border">
        <div className="flex items-center justify-between">
          <h3 className="font-bold">Filters</h3>
          {Object.values(filters).some(v => v) && (
            <Button size="small" variant="ghost" onClick={handleClearFilters} leftIcon={<XMarkIcon className="h-4 w-4" />}>
              Clear
            </Button>
          )}
        </div>

        <Input
          placeholder="Search transactions..."
          value={filters.q || ''}
          onChange={(e) => setFilters(prev => ({ ...prev, q: e.target.value }))}
        />

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Select
            label="Account"
            value={filters.account_id || ''}
            onChange={(val) => setFilters(prev => ({ ...prev, account_id: String(val) }))}
            options={getOptions(accounts, 'name', 'All Accounts')}
          />

          <Select
            label="Category"
            value={filters.category_id || ''}
            onChange={(val) => setFilters(prev => ({ ...prev, category_id: String(val) }))}
            options={getOptions(categories, 'name', 'All Categories')}
          />

          <Select
            label="Savings Goal"
            value={filters.savings_goal_id || ''}
            onChange={(val) => setFilters(prev => ({ ...prev, savings_goal_id: String(val) }))}
            options={getOptions(savings, 'name', 'All Savings Goals')}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="From Date"
              type="date"
              value={filters.date_from || get90DaysAgoString()} 
              onChange={(e) => setFilters(prev => ({ ...prev, date_from: e.target.value }))}
            />
            <Input
              label="To Date"
              type="date"
              value={filters.date_to || getTodayString()} 
              onChange={(e) => setFilters(prev => ({ ...prev, date_to: e.target.value }))}
            />
        </div>

        <Input
          type="checkbox"
          label="Show only uncategorized"
          checked={filters.uncategorized_only || false}
          onChange={(e) => setFilters(prev => ({ ...prev, uncategorized_only: e.target.checked }))}
        />
      </div>

      <TransactionList
        transactions={transactions}
        loading={loading}
        searchLoading={searchLoading}
        hasMore={hasMore}
        onLoadMore={handleLoadMore}
        savings={savings}
        categories={categories}
        onFilterChange={(newFilters) => setFilters(prev => ({ ...prev, ...newFilters }))}
        onRefresh={handleRefresh}
      />
    </div>
  );
};