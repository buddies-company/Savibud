import { WalletIcon, ShieldCheckIcon, ArrowUpRightIcon, BanknotesIcon, DocumentTextIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import { Card, Progress } from '@soilhat/react-components';
import { callApi } from '../services/api';
import { useEffect, useState } from 'react';
import { Category, Transaction } from '../utils/constants/types';
import { FinancialTransaction } from '../components/FinancialTransaction';
import { TransactionDetailModal } from '../components/TransactionDetail';

type dashboard_api_response = {
    total_balance: number,
    goals: [],
    recent_activity: Transaction[],
    total_budget: number,
    total_budget_spent: number,
    safe_to_spend: number
}

export const Dashboard = () => {
    const [totalBalance, setTotalBalance] = useState(0)
    const [safeToSpend, setSafeToSpend] = useState(0)
    const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])
    const [budgetUsed, setBudgetUsed] = useState(0)
    const [totalBudget, setTotalBudget] = useState(0)
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
        callApi<dashboard_api_response>('/dashboard/summary').then(data => {
            const resp = data.data
            setTotalBalance(resp.total_balance)
            setSafeToSpend(resp.safe_to_spend)
            setRecentTransactions(resp.recent_activity)
            setTotalBudget(resp.total_budget)
            setBudgetUsed((resp.total_budget_spent * 100 / resp.total_budget) || 0)
        });
    }, []);

    const stats = {
        goals: [
            { name: 'New Car', progress: 75, color: 'text-blue-500' },
            { name: 'Emergency', progress: 40, color: 'text-green-500' },
            { name: 'Vacation', progress: 90, color: 'text-purple-500' },
        ]
    };

    return (
        <div className="p-6 min-h-screen font-sans">
            <header className="mb-8">
                <h1 className="text-2xl font-bold">Financial Command Center</h1>
                <p className="text-sm">Welcome back! Here is your health check for December.</p>
            </header>

            {/* --- ROW 1: THE BIG NUMBERS --- */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {/* Total Balance */}
                <Card>
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 rounded-lg"><WalletIcon className="text-primary dark:text-primary-dark h-20" /></div>
                        <span className="text-xs font-medium text-text-secondary dark:text-text-secondary-dark uppercase">Total Balance</span>
                    </div>
                    <h2 className="text-3xl font-bold">{totalBalance.toLocaleString()}€</h2>
                    <div className="mt-4 flex items-center text-sm">
                        <ArrowTrendingUpIcon className="mr-1 h-16" /> <span>+2.4% from last month</span>
                    </div>
                </Card>

                {/* Safe to Spend */}
                <Card>
                    <div className="flex items-center justify-between">
                        <div className="p-2 rounded-lg"><ShieldCheckIcon className="h-20 text-state-success dark:text-state-success-dark" /></div>
                        <span className="text-xs font-medium text-text-secondary dark:text-text-secondary-dark uppercase">Safe to Spend</span>
                    </div>
                    <h2 className="text-3xl font-bold">{safeToSpend.toLocaleString()}€</h2>
                    <p className="mt-4 text-text-secondary dark:text-text-secondary-dark text-xs">After bills & savings commitments</p>
                </Card>

                {/* Budget Progress */}
                <Card>
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 rounded-lg"><DocumentTextIcon className="h-20 text-state-warning dark:text-state-warning-dark" /></div>
                        <span className="text-xs font-medium text-text-secondary dark:text-text-secondary-dark uppercase">Monthly Budget</span>
                    </div>
                    <div className="flex justify-between mb-2">
                        <span className="text-sm font-semibold text-text-secondary dark:text-text-secondary-dark">{budgetUsed}% used</span>
                        <span className="text-sm text-text-secondary dark:text-text-secondary-dark">Limit: {totalBudget}€</span>
                    </div>
                    <Progress value={budgetUsed} />
                </Card>
            </div>

            {/* --- ROW 2: ACTIVITY & GOALS --- */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Recent Activity (Table Mini) */}
                <div className="lg:col-span-2">
                    <Card>
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="font-bold  flex items-center">
                                <ArrowUpRightIcon className="h-18 mr-2 text-text-secondary dark:text-text-secondary-dark" /> Recent Activity
                            </h3>
                            <button className="text-primary dark:text-primary-dark text-sm font-medium hover:underline">View All</button>
                        </div>
                        <div className="space-y-4">
                            {recentTransactions.map(tx => (
                                <FinancialTransaction tx={tx} key={tx.id} onSelect={setSelectedTx} />
                            ))}
                        </div>
                        <TransactionDetailModal
                            tx={selectedTx}
                            categories={categories}
                            isOpen={!!selectedTx}
                            onClose={() => setSelectedTx(null)}
                    savingsGoals={[]}
                        />
                    </Card>
                </div>

                {/* Savings Goals (Radial Pulse) */}
                <Card>
                    <h3 className="font-bold  mb-6 flex items-center">
                        <BanknotesIcon className="h-18 mr-2 text-text-secondary dark:text-text-secondary-dark" /> Goals Pulse
                    </h3>
                    <div className="space-y-8">
                        {stats.goals.map(goal => (
                            <div key={goal.name} className="flex items-center">
                                {/* Simple SVG Circular Progress */}
                                <div className="relative w-16 h-16 mr-4">
                                    <svg className="w-full h-full" viewBox="0 0 36 36">
                                        <path className="text-surface-base dark:text-surface-base-dark stroke-current" strokeWidth="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                        <path className={`${goal.color} stroke-current`} strokeWidth="3" strokeDasharray={`${goal.progress}, 100`} strokeLinecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                    </svg>
                                    <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-text-secondary dark:text-text-secondary-dark">{goal.progress}%</span>
                                </div>
                                <div>
                                    <p className="text-sm font-bold ">{goal.name}</p>
                                    <p className="text-xs text-text-secondary dark:text-text-secondary-dark">Scheduled sync active</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
};
