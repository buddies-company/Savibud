import { WalletIcon, ShieldCheckIcon, ArrowUpRightIcon, BanknotesIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { Card, Heading, Progress } from '@soilhat/react-components';
import { callApi } from '../services/api';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Category, SavingsGoal, Transaction } from '../utils/constants/types';
import { FinancialTransaction } from '../components/FinancialTransaction';
import { TransactionDetailModal } from '../components/TransactionDetail';
import { DynamicHeroIcon } from '../components/DynamicHeroIcon';

type dashboard_api_response = {
    total_balance: number,
    goals: [],
    recent_activity: Transaction[],
    total_budget: number,
    total_budget_spent: number,
    safe_to_spend: number
}

export const Dashboard = () => {
    const navigate = useNavigate();
    const [totalBalance, setTotalBalance] = useState(0)
    const [safeToSpend, setSafeToSpend] = useState(0)
    const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])
    const [budgetUsed, setBudgetUsed] = useState(0)
    const [totalBudget, setTotalBudget] = useState(0)
    const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

    const [categories, setCategories] = useState<Category[]>([]);
    const [savings, setSavings] = useState<SavingsGoal[]>([]);

    const fetchData = async () => {
        const [catRes] = await Promise.all([
            callApi<Category[]>("/categories", "GET"),
        ]);
        setCategories(catRes.data);
        const [savingsRes] = await Promise.all([
            callApi<SavingsGoal[]>("/savings_goals?limit=5", "GET"),
        ]);
        setSavings(savingsRes.data);
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

    const handleBudgetClick = () => {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        
        const dateFrom = firstDay.toISOString().split('T')[0];
        const dateTo = lastDay.toISOString().split('T')[0];
        
        navigate(`/transactions?date_from=${dateFrom}&date_to=${dateTo}`);
    };

    return (
        <div className="p-6 min-h-screen font-sans">
            <Heading title="Dashboard" />

            {/* --- ROW 1: THE BIG NUMBERS --- */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {/* Total Balance */}
                <Card>
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 rounded-lg"><WalletIcon className="text-primary dark:text-primary-dark h-20" /></div>
                        <span className="text-xs font-medium text-text-secondary dark:text-text-secondary-dark uppercase">Total Balance</span>
                    </div>
                    <h2 className="text-3xl font-bold">{totalBalance.toLocaleString()}€</h2>
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
                <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={handleBudgetClick}>
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 rounded-lg"><DocumentTextIcon className="h-20 text-state-warning dark:text-state-warning-dark" /></div>
                        <span className="text-xs font-medium text-text-secondary dark:text-text-secondary-dark uppercase">Monthly Budget</span>
                    </div>
                    <div className="flex justify-between mb-2">
                        <span className="text-sm font-semibold text-text-secondary dark:text-text-secondary-dark">{budgetUsed.toLocaleString()}% used</span>
                        <span className="text-sm text-text-secondary dark:text-text-secondary-dark">Limit: {totalBudget.toLocaleString()}€</span>
                    </div>
                    <Progress value={budgetUsed} />
                    <p className="mt-4 text-xs text-primary dark:text-primary-dark font-medium">Click to view month transactions →</p>
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
                            <a className="text-primary dark:text-primary-dark text-sm font-medium hover:underline" href='/transactions'>View All</a>
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
                            savingsGoals={savings}
                        />
                    </Card>
                </div>

                {/* Savings Goals (Radial Pulse) */}
                <Card>
                    <h3 className="font-bold  mb-6 flex items-center">
                        <BanknotesIcon className="h-18 mr-2 text-text-secondary dark:text-text-secondary-dark" /> Goals Pulse
                    </h3>
                    <a className="text-primary dark:text-primary-dark text-sm font-medium hover:underline" href='/savings'>View All</a>
                    <div className="space-y-8">
                        {savings.map(goal => {
                            const isNegative = goal.current_amount < 0;
                            const progress = goal.target_amount > 0 ? Math.min(Math.max((goal.current_amount / goal.target_amount) * 100, 0), 100) : 0;
                            const progressColor = isNegative ? 'stroke-state-danger dark:stroke-state-danger-dark' : progress > 75 ? 'stroke-state-success dark:stroke-state-success-dark' : progress > 50 ? 'stroke-primary dark:stroke-primary-dark' : 'stroke-state-warning dark:stroke-state-warning-dark';
                            
                            return (
                                <div key={goal.name} className="flex items-center">
                                    {/* Icon Circle */}
                                    <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-white shadow-sm mr-4 flex-shrink-0" style={{ backgroundColor: goal.color || '#3b82f6' }}>
                                        <DynamicHeroIcon iconName={goal.icon || 'BanknotesIcon'} className="h-6 w-6" />
                                    </div>

                                    {/* SVG Circular Progress */}
                                    {goal.target_amount > 0 && <div className="relative w-16 h-16 mr-4 flex-shrink-0">
                                        <svg className="w-full h-full" viewBox="0 0 36 36">
                                            <path className="text-surface-base dark:text-surface-base-dark stroke-current" strokeWidth="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                            <path className={progressColor + ' stroke-current'} strokeWidth="3" strokeDasharray={`${Math.max(progress, 0)}, 100`} strokeLinecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                        </svg>
                                        <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-text-secondary dark:text-text-secondary-dark">{Math.round(progress)}%</span>
                                    </div>}

                                    <div>
                                        <p className="text-sm font-bold text-text-primary dark:text-text-primary-dark">{goal.name}</p>
                                        <p className={`text-xs ${isNegative ? 'text-state-danger dark:text-state-danger-dark font-semibold' : 'text-text-secondary dark:text-text-secondary-dark'}`}>
                                            €{(goal.current_amount || 0).toLocaleString(undefined, {maximumFractionDigits: 2})} {goal.target_amount > 0 && `of €${goal.target_amount.toLocaleString(undefined, {maximumFractionDigits: 2})}`}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </Card>
            </div>
        </div>
    );
};
