import { useEffect, useState, useCallback } from "react";
import { callApi } from "../services/api";
import { Transaction } from "../utils/constants/types";
import { TransactionList } from "../components/TransactionList";

export const TransactionPage = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  // Current filter state
  const [filters, setFilters] = useState({
    q: new URLSearchParams(globalThis.location.search).get('q') || '',
    category_id: new URLSearchParams(globalThis.location.search).get('category_id') || '',
    account_id: new URLSearchParams(globalThis.location.search).get('account_id') || ''
  });

  const fetchTransactions = useCallback(async (isNewFilter = false) => {
    setLoading(true);
    const currentPage = isNewFilter ? 1 : page;
    
    try {
      const response = await callApi<Transaction[]>("/transactions","GET", undefined, {
        params: { 
          ...filters, 
          page: currentPage,
          limit: 20 
        }
      });

      const newData = response.data;
      
      setTransactions(prev => isNewFilter ? newData : [...prev, ...newData]);
      setHasMore(newData.length === 20); // If we got a full page, there might be more
      if (!isNewFilter) setPage(p => p + 1);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  // Refetch when filters change
  useEffect(() => {
    setPage(1);
    fetchTransactions(true);
  }, [filters.q, filters.category_id, filters.account_id]);

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <TransactionList 
        transactions={transactions} 
        loading={loading}
        hasMore={hasMore}
        filters={filters}
        onFilterChange={(newFilters) => setFilters(prev => ({ ...prev, ...newFilters }))}
        onLoadMore={() => fetchTransactions(false)}
      />
    </div>
  );
};