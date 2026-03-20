import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Heading,
  Button,
  Modal,
  Input,
  Card,
  CategoryTree,
  Select
} from '@soilhat/react-components';
import {
  PlusIcon,
  PencilSquareIcon,
  TagIcon,
  BanknotesIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon,
  ArrowRightIcon,
  CalendarDaysIcon,
  TrashIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import * as Icons from '@heroicons/react/24/outline';
import { Category } from '../utils/constants/types';
import { callApi } from '../services/api';
import { DynamicHeroIcon } from '../components/DynamicHeroIcon';
import { RulesManager } from '../components/RulesManager';

export default function BudgetPlanningPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('planning');
  const [modalMode, setModalMode] = useState<'none' | 'category' | 'delete'>('none');
  const [isLoading, setIsLoading] = useState(false);
  const [iconSearch, setIconSearch] = useState('');
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const today = new Date();
    return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
  });

  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [budgetStats, setBudgetStats] = useState<Map<string, { spent: number; remaining: number }>>(new Map());

  // Fetch all base categories
  const fetchData = async () => {
    try {
      const catRes = await callApi<Category[]>("/categories", "GET");
      setCategories(catRes.data || []);
      calculateBudgetStats(catRes.data || []);
    } catch (err) {
      console.error("Failed to fetch categories", err);
    }
  };

  // Fetch actual spending stats for the selected month
  const calculateBudgetStats = async (cats: Category[]) => {
    try {
      const res = await callApi<any[]>(`/categories/stats/budget?month=${selectedMonth}`, "GET");
      const statsArray = res.data || [];
      const statsMap = new Map<string, { spent: number; remaining: number }>();

      cats.forEach(cat => {
        const backendStat = statsArray.find(s => s.category_id === cat.id);
        const spent = backendStat ? backendStat.spent : 0;
        statsMap.set(cat.id, {
          spent,
          remaining: Number(cat.budget_amount || 0) - spent
        });
      });
      setBudgetStats(statsMap);
    } catch (err) {
      console.error("Failed to fetch budget stats", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (categories.length > 0) calculateBudgetStats(categories);
  }, [selectedMonth]);

  // Compute totals and sort categories by active status
  const { totals, categoryStatusMap, incomeCategories, expenseCategories } = useMemo(() => {
    const currentMonthDate = new Date(`${selectedMonth}-01`);
    const statusMap = new Map<string, boolean>();
    const sums = { income: 0, expenses: 0 };

    categories.forEach(c => {
      const start = c.budget_start_date ? new Date(c.budget_start_date) : null;
      const end = c.budget_end_date ? new Date(c.budget_end_date) : null;
      
      const isActive = (!start || currentMonthDate >= new Date(start.getFullYear(), start.getMonth(), 1)) &&
                       (!end || currentMonthDate <= new Date(end.getFullYear(), end.getMonth(), 1));

      statusMap.set(c.id, isActive);
      if (isActive && c.budget_amount) {
        if (c.is_income) sums.income += Number(c.budget_amount);
        else sums.expenses += Number(c.budget_amount);
      }
    });

    const sortFn = (a: Category, b: Category) => {
      const aActive = statusMap.get(a.id) ? 1 : 0;
      const bActive = statusMap.get(b.id) ? 1 : 0;
      if (aActive !== bActive) return bActive - aActive;
      return a.name.localeCompare(b.name);
    };

    return {
      totals: sums,
      categoryStatusMap: statusMap,
      incomeCategories: categories.filter(c => c.is_income).sort(sortFn),
      expenseCategories: categories.filter(c => !c.is_income).sort(sortFn)
    };
  }, [categories, selectedMonth]);

  // Compute Global Performance Metrics
  const globalStats = useMemo(() => {
    let totalSpent = 0;
    let totalBudget = 0;
    
    categories.forEach(c => {
      // We only track expense categories for the burn rate
      if (!c.is_income && categoryStatusMap.get(c.id)) {
        totalBudget += Number(c.budget_amount || 0);
        totalSpent += budgetStats.get(c.id)?.spent || 0;
      }
    });

    const percentUsed = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0;
    const remaining = totalBudget - totalSpent;
    const savingsGoal = totals.income - totals.expenses;

    return { totalSpent, totalBudget, percentUsed, remaining, savingsGoal };
  }, [categories, budgetStats, totals, categoryStatusMap]);

  const handleClose = () => {
    setModalMode('none');
    setSelectedItem(null);
    setIconSearch('');
  };

  const getInheritedIcon = (item: any): string => {
    if (!item) return 'TagIcon';
    if (item.icon) return item.icon;
    if (item.parent_id) {
      const parent = categories.find((c: Category) => c.id === item.parent_id);
      if (parent) return getInheritedIcon(parent);
    }
    return 'TagIcon';
  };

  const filteredIconNames = useMemo(() => {
    const allNames = Object.keys(Icons).filter(name => name.endsWith('Icon'));
    return iconSearch 
      ? allNames.filter(name => name.toLowerCase().includes(iconSearch.toLowerCase())).slice(0, 28)
      : allNames.slice(0, 28);
  }, [iconSearch]);

  const handleSaveCategory = async () => {
    setIsLoading(true);
    const isEdit = !!selectedItem?.id;
    try {
      const payload = {
        ...selectedItem,
        parent_id: selectedItem.parent_id === 'none' ? null : selectedItem.parent_id,
        budget_amount: selectedItem.budget_amount ? Number(selectedItem.budget_amount) : null,
      };
      await callApi(isEdit ? `/categories/${selectedItem.id}` : "/categories", isEdit ? "PUT" : "POST", undefined, payload);
      await fetchData();
      handleClose();
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteCategory = async () => {
    if (!selectedItem?.id) return;
    setIsLoading(true);
    try {
      await callApi(`/categories/${selectedItem.id}`, "DELETE");
      await fetchData();
      handleClose();
    } finally {
      setIsLoading(false);
    }
  };

  // Mobile-first Category Row
  const renderCategoryRow = (item: Category, level: number, { isExpanded, toggle, hasChildren }: any) => {
    const stats = budgetStats.get(item.id);
    const spent = stats?.spent || 0;
    const budget = Number(item.budget_amount || 0);
    const remaining = budget - spent;
    const isActive = categoryStatusMap.get(item.id);
    const isIncome = item.is_income;

    const isOverTarget = remaining < 0;
    const diffColor = isIncome 
      ? (isOverTarget ? 'text-state-success dark:text-state-success-dark' : 'text-state-danger dark:text-state-danger-dark') 
      : (isOverTarget ? 'text-state-danger dark:text-state-danger-dark' : 'text-state-success dark:text-state-success-dark');

    return (
      <div className={`px-4 py-4 border-b border-border/50 dark:border-border-dark/50 hover:bg-surface-base/30 dark:hover:bg-surface-base-dark/30 transition-colors ${!isActive && 'opacity-40 grayscale bg-surface-base/10 dark:bg-surface-base-dark/10'}`}>
        <div className="flex items-start justify-between gap-2" style={{ paddingLeft: `${level * 12}px` }}>
          
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <button onClick={toggle} className={`p-1 rounded shrink-0 hover:bg-surface-panel dark:hover:bg-surface-panel-dark ${!hasChildren && 'invisible'}`}>
              {isExpanded ? <ChevronDownIcon className="h-4 w-4" /> : <ChevronRightIcon className="h-4 w-4" />}
            </button>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm" style={{ backgroundColor: item.color || '#cbd5e1' }}>
              <DynamicHeroIcon iconName={getInheritedIcon(item)} className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col min-w-0">
              <span className={`text-sm font-bold truncate ${!isActive && 'italic'}`}>{item.name}</span>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-[10px] text-text-secondary dark:text-text-secondary-dark font-mono">
                  {isIncome && spent > 0 ? '+' : ''}€{spent.toFixed(0)} / €{budget.toFixed(0)}
                </span>
                {item.is_fixed && <span className="text-[8px] px-1.5 py-0.5 rounded bg-primary/10 text-primary dark:text-primary-dark font-black uppercase tracking-tighter">Fixed</span>}
              </div>
            </div>
          </div>

          <div className="flex flex-col items-end shrink-0 pl-2">
            <span className={`text-sm font-black font-mono ${diffColor}`}>
              €{remaining.toFixed(2)}
            </span>
            <div className="flex gap-1 mt-1">
              <Button onClick={() => { setSelectedItem(item); setModalMode('category'); }} variant='ghost'><PencilSquareIcon className="h-4 w-4" /></Button>
              <Button onClick={() => navigate(`/transactions?category_id=${item.id}`)} variant='ghost'><ArrowRightIcon className="h-4 w-4" /></Button>
              <Button onClick={() => { setSelectedItem(item); setModalMode('delete'); }} variant='ghost' color_name='danger'><TrashIcon className="h-4 w-4" /></Button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-surface-base dark:bg-surface-base-dark text-text-primary dark:text-text-primary-dark">
      <Heading 
        title="Budgeting" 
        variant="page" 
        filters={[
          { key: 'planning', value: 'Overview', active: activeTab === 'planning', props: { onClick: () => setActiveTab('planning') } }, 
          { key: 'rules', value: 'Rules', active: activeTab === 'rules', props: { onClick: () => setActiveTab('rules') } }
        ]}
      >
        <Button size="small" leftIcon={<PlusIcon className="h-4 w-4" />} onClick={() => { setSelectedItem({ name: '', color: '#3b82f6', is_income: false, parent_id: 'none', icon: '', budget_amount: 0, budget_period: 'monthly' }); setModalMode('category'); }}>New</Button>
      </Heading>

      <main className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8 space-y-4 sm:space-y-6">
        {activeTab === 'rules' ? <RulesManager categories={categories} /> : (
          <>
            {/* GLOBAL DASHBOARD */}
            <Card>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <div>
                  <h3 className="text-sm font-black uppercase tracking-widest opacity-70">Global Track</h3>
                  <p className="text-xs text-text-secondary dark:text-text-secondary-dark ">Monthly budget burn rate</p>
                </div>
                <div className="text-right">
                  <span className={`text-2xl font-mono font-black ${globalStats.percentUsed > 100 ? 'text-state-danger dark:text-state-danger-dark' : 'text-primary dark:text-primary-dark'}`}>
                    {globalStats.percentUsed.toFixed(1)}%
                  </span>
                  <span className="text-xs opacity-50 ml-1">used</span>
                </div>
              </div>

              <div className="w-full h-2.5 bg-border/20 dark:bg-border-dark/20 rounded-full overflow-hidden mb-6">
                <div 
                  className={`h-full transition-all duration-700 rounded-full ${
                    globalStats.percentUsed > 100 ? 'bg-state-danger dark:bg-state-danger-dark' : 
                    globalStats.percentUsed > 85 ? 'bg-state-warning dark:bg-state-warning-dark' : 'bg-primary dark:bg-primary-dark'
                  }`}
                  style={{ width: `${Math.min(globalStats.percentUsed, 100)}%` }}
                />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div>
                  <p className="text-[9px] uppercase font-bold opacity-50">Remaining</p>
                  <p className={`text-lg font-mono font-bold ${globalStats.remaining < 0 ? 'text-state-danger dark:text-state-danger-dark' : ''}`}>€{globalStats.remaining.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-[9px] uppercase font-bold opacity-50">Savings Goal</p>
                  <p className="text-lg font-mono font-bold text-state-success">€{globalStats.savingsGoal.toFixed(2)}</p>
                </div>
                <div className="hidden sm:block text-right">
                  <p className="text-[9px] uppercase font-bold opacity-50">Budgeted</p>
                  <p className="text-lg font-mono font-bold">€{globalStats.totalBudget.toFixed(0)}</p>
                </div>
                <div className="hidden sm:block text-right">
                  <p className="text-[9px] uppercase font-bold opacity-50">Actual</p>
                  <p className="text-lg font-mono font-bold">€{globalStats.totalSpent.toFixed(0)}</p>
                </div>
              </div>

              {globalStats.savingsGoal < 0 && (
                <div className="mt-4 p-3 bg-state-danger/10 rounded-lg flex items-center gap-3 text-state-danger text-xs font-bold">
                  <ExclamationTriangleIcon className="h-4 w-4 shrink-0" />
                  Warning: You are planning to spend more than you earn!
                </div>
              )}
            </Card>

            {/* Quick Filter/Totals */}
            <div className="flex sm:grid overflow-x-auto sm:grid-cols-3 gap-3 pb-2 scrollbar-hide">
              <Card className="p-4 min-w-[140px] flex-shrink-0">
                <p className="text-[9px] uppercase font-black tracking-widest mb-1 opacity-60">Month</p>
                <Input type="month" value={selectedMonth} className="h-8 py-0 text-sm" onChange={(e) => setSelectedMonth(e.target.value)} />
              </Card>
              <Card className="p-4 min-w-[140px] flex-shrink-0 border-l-4 border-l-state-success">
                <p className="text-[9px] uppercase font-black tracking-widest opacity-60 text-state-success">Income</p>
                <p className="text-xl font-mono font-bold text-state-success">€{totals.income.toFixed(0)}</p>
              </Card>
              <Card className="p-4 min-w-[140px] flex-shrink-0 border-l-4 border-l-state-danger">
                <p className="text-[9px] uppercase font-black tracking-widest opacity-60 text-state-danger">Expenses</p>
                <p className="text-xl font-mono font-bold text-state-danger">€{totals.expenses.toFixed(0)}</p>
              </Card>
            </div>

            <Card className="overflow-hidden border-none shadow-xl">
              {/* Desktop Only Headers */}
              <div className="hidden sm:grid grid-cols-12 bg-surface-panel dark:bg-surface-panel-dark px-6 py-3 text-[10px] font-black uppercase tracking-widest opacity-60 border-b border-border dark:border-border-dark">
                <div className="col-span-4">Category</div>
                <div className="col-span-2 text-right">Target</div>
                <div className="col-span-2 text-right">Actual</div>
                <div className="col-span-2 text-right">Difference</div>
                <div className="col-span-2 text-right">Actions</div>
              </div>

              {/* Incomes */}
              <div className="bg-state-success/5 border-b border-state-success/10 px-4 py-3 flex justify-between items-center">
                <span className="text-[10px] font-black uppercase text-state-success tracking-tighter">Incomes</span>
                <span className="text-xs font-mono font-bold text-state-success">Total: €{totals.income.toFixed(2)}</span>
              </div>
              <CategoryTree items={incomeCategories} renderItem={renderCategoryRow} />

              {/* Expenses */}
              <div className="bg-state-danger/5 border-y border-state-danger/10 px-4 py-3 mt-4 flex justify-between items-center">
                <span className="text-[10px] font-black uppercase text-state-danger tracking-tighter">Expenses</span>
                <span className="text-xs font-mono font-bold text-state-danger">Total: €{totals.expenses.toFixed(2)}</span>
              </div>
              <CategoryTree items={expenseCategories} renderItem={renderCategoryRow} />
            </Card>
          </>
        )}
      </main>

      {/* MODAL: CATEGORY EDIT/CREATE */}
      <Modal open={modalMode === 'category'} onClose={handleClose}>
        <div className="sticky top-0 bg-surface-panel dark:bg-surface-panel-dark z-20 -mx-6 -mt-6 px-6 py-4 border-b border-border flex justify-between items-center sm:static sm:bg-transparent sm:p-0 sm:border-none">
           <Heading title={selectedItem?.id ? "Edit Category" : "New Category"} />
           <Button variant="ghost" className="sm:hidden" onClick={handleClose}>Done</Button>
        </div>
        
        <div className="space-y-6 mt-6 pb-20 sm:pb-0">
          <Input label="Category Name" value={selectedItem?.name || ''} onChange={(e) => setSelectedItem({ ...selectedItem, name: e.target.value })} leftIcon={<TagIcon className="h-5 w-5" />} />
          <Select label="Parent Category" value={selectedItem?.parent_id || 'none'} onChange={(val) => setSelectedItem({ ...selectedItem, parent_id: val })} options={[{ value: 'none', label: 'None' }, ...categories.filter(c => c.id !== selectedItem?.id).map(c => ({ value: c.id, label: c.name }))]} />
          
          <div className="pt-4 border-t border-border dark:border-border-dark">
            <label className="text-[10px] uppercase tracking-widest mb-4 block opacity-60">Budget Settings</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input label="Amount (€)" type="number" step="0.01" value={selectedItem?.budget_amount || ''} onChange={(e) => setSelectedItem({ ...selectedItem, budget_amount: e.target.value })} leftIcon={<BanknotesIcon className="h-5 w-5" />} />
              <Select label="Frequency" value={selectedItem?.budget_period || 'monthly'} onChange={(val) => setSelectedItem({ ...selectedItem, budget_period: val })} options={[{ value: 'daily', label: 'Daily' }, { value: 'weekly', label: 'Weekly' }, { value: 'monthly', label: 'Monthly' }, { value: 'yearly', label: 'Yearly' }]} />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
              <Input type="date" label="Valid From" value={selectedItem?.budget_start_date || ''} onChange={(e) => setSelectedItem({ ...selectedItem, budget_start_date: e.target.value })} leftIcon={<CalendarDaysIcon className="h-5 w-5" />} />
              <Input type="date" label="Valid Until" value={selectedItem?.budget_end_date || ''} onChange={(e) => setSelectedItem({ ...selectedItem, budget_end_date: e.target.value })} leftIcon={<CalendarDaysIcon className="h-5 w-5" />} />
            </div>
          </div>

          <div className="pt-4 border-t border-border dark:border-border-dark space-y-4">
            <div className="grid grid-cols-2 gap-4 items-end">
              <Input label="Color" type="color" className="h-10 p-1" value={selectedItem?.color || '#3b82f6'} onChange={(e) => setSelectedItem({ ...selectedItem, color: e.target.value })} />
              <div className="flex flex-col gap-2">
                <span className="text-[10px] uppercase opacity-60">Options</span>
                <div className="flex flex-col gap-2">
                  <label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={selectedItem?.is_income || false} onChange={(e) => setSelectedItem({ ...selectedItem, is_income: e.target.checked })} /> Income</label>
                  <label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={selectedItem?.is_fixed || false} onChange={(e) => setSelectedItem({ ...selectedItem, is_fixed: e.target.checked })} /> Fixed Bill</label>
                </div>
              </div>
            </div>
            
            <div className="pt-4">
              <label className="text-[10px] uppercase tracking-widest mb-2 block opacity-60">Icon</label>
              <div className="relative mb-2">
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-text-secondary opacity-50 z-10" />
                <Input type="text" placeholder="Search icons..." value={iconSearch} className="pl-9" onChange={(e) => setIconSearch(e.target.value)} />
              </div>
              <div className="grid grid-cols-4 sm:grid-cols-7 gap-2 max-h-40 overflow-y-auto p-2 bg-surface-base/10 rounded-xl">
                {filteredIconNames.map((name) => (
                  <button key={name} onClick={() => setSelectedItem({ ...selectedItem, icon: name })} className={`p-3 rounded-xl flex items-center justify-center transition-all ${selectedItem?.icon === name ? 'bg-primary text-white shadow-lg' : 'hover:bg-surface-panel opacity-60'}`}><DynamicHeroIcon iconName={name} className="h-5 w-5" /></button>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-surface-base border-t border-border dark:bg-surface-base-dark sm:static sm:bg-transparent sm:border-none sm:p-0 sm:mt-8 flex gap-3 z-30">
          <Button className="flex-1 h-12" onClick={handleSaveCategory} isLoading={isLoading}>Save Changes</Button>
          <Button variant="ghost" className="hidden sm:flex flex-1 h-12" onClick={handleClose}>Cancel</Button>
        </div>
      </Modal>

      {/* MODAL: DELETE CONFIRMATION */}
      <Modal open={modalMode === 'delete'} onClose={handleClose}>
        <div className="flex flex-col items-center text-center py-4">
          <div className="w-16 h-16 bg-state-danger/10 text-state-danger rounded-full flex items-center justify-center mb-6">
            <ExclamationTriangleIcon className="h-10 w-10" />
          </div>
          <Heading title="Delete?" />
          <p className="mt-4 text-sm text-text-secondary px-4 leading-relaxed">
            Delete <span className="font-bold text-text-primary">"{selectedItem?.name}"</span>? 
            This cannot be undone.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 mt-8">
          <Button className="h-12 bg-state-danger border-none" onClick={handleDeleteCategory} isLoading={isLoading}>Delete</Button>
          <Button variant="ghost" className="h-12" onClick={handleClose}>Cancel</Button>
        </div>
      </Modal>
    </div>
  );
}