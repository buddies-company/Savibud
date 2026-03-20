import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Heading, Button, Card, Modal, Input, Select } from '@soilhat/react-components';
import {
  PlusIcon,
  FlagIcon,
  ArrowTrendingUpIcon,
  TrashIcon,
  CheckIcon,
  ArrowRightIcon,
  MagnifyingGlassIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import * as Icons from '@heroicons/react/24/outline';
import { callApi } from "../services/api";
import { SavingsGoal } from "../utils/constants/types";
import { DynamicHeroIcon } from "../components/DynamicHeroIcon";

const formatCurrency = (val: number) =>
  Number(val).toLocaleString('de-DE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 2
  });

export const SavingsPage = () => {
  const [goals, setGoals] = useState<SavingsGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingGoal, setEditingGoal] = useState<SavingsGoal | null>(null);
  const [iconSearch, setIconSearch] = useState('');
  const [formData, setFormData] = useState<{
    name: string;
    target_amount: number;
    current_amount: number;
    icon: string;
    color: string;
    automation_amount: number | undefined;
    automation_frequency: string | undefined;
    automation_next_run_date: string | undefined;
    automation_is_active: boolean;
  }>({
    name: '',
    target_amount: 0,
    current_amount: 0,
    icon: 'BanknotesIcon',
    color: '#3b82f6',
    automation_amount: undefined,
    automation_frequency: undefined,
    automation_next_run_date: undefined,
    automation_is_active: false
  });

  const fetchGoals = useCallback(async () => {
    try {
      const res = await callApi<SavingsGoal[]>("/savings_goals", "GET");
      setGoals(res.data);
    } catch (error) {
      console.error("Failed to fetch savings goals", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGoals();
  }, [fetchGoals]);

  const handleCreateClick = () => {
    setEditingGoal(null);
    setIconSearch('');
    setFormData({
      name: '',
      target_amount: 0,
      current_amount: 0,
      icon: 'BanknotesIcon',
      color: '#3b82f6',
      automation_amount: undefined,
      automation_frequency: undefined,
      automation_next_run_date: undefined,
      automation_is_active: false
    });
    setShowModal(true);
  };

  const handleEditClick = (goal: SavingsGoal) => {
    setEditingGoal(goal);
    setIconSearch('');
    setFormData({
      name: goal.name,
      target_amount: goal.target_amount || 0,
      current_amount: goal.current_amount || 0,
      icon: goal.icon || 'BanknotesIcon',
      color: goal.color || '#3b82f6',
      automation_amount: goal.automation_amount,
      automation_frequency: goal.automation_frequency,
      automation_next_run_date: goal.automation_next_run_date,
      automation_is_active: goal.automation_is_active || false
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!formData.name) {
      alert("Please fill in the name field");
      return;
    }

    try {
      if (editingGoal) {
        // Update existing goal
        await callApi(`/savings_goals/${editingGoal.id}`, "PUT", undefined, formData);
      } else {
        // Create new goal
        await callApi("/savings_goals", "POST", undefined, formData);
      }
      setShowModal(false);
      fetchGoals();
    } catch (error) {
      console.error("Failed to save goal", error);
    }
  };

  const handleDelete = async (goalId: string) => {
    if (!confirm("Are you sure you want to delete this goal?")) return;
    try {
      await callApi(`/savings_goals/${goalId}`, "DELETE");
      fetchGoals();
    } catch (error) {
      console.error("Failed to delete goal", error);
    }
  };

  const totalSaved = goals.reduce((sum, g) => sum + (Number(g.current_amount) || 0), 0);

  const avgMonthly = goals.reduce((sum, g) => {
    if (!g.automation_is_active || !g.automation_amount) return sum;
    const amount = Number(g.automation_amount) || 0;
    switch (g.automation_frequency) {
      case 'weekly': return sum + (amount * 4.33);
      case 'quarterly': return sum + (amount / 3);
      case 'yearly': return sum + (amount / 12);
      default: return sum + amount;
    }
  }, 0);

  const meta = [
    { key: 'total', value: `${formatCurrency(totalSaved)} Total Saved`, svg: <FlagIcon className="h-4 w-4" /> },
    { key: 'monthly', value: `${formatCurrency(avgMonthly)}/mo pacing`, svg: <ArrowTrendingUpIcon className="h-4 w-4" /> },
  ];

  return (
    <div className="min-h-screen bg-surface-base dark:bg-surface-base-dark transition-colors duration-200">
      <Heading title="Savings Goals" variant="page" meta={meta}>
        <Button size="small" leftIcon={<PlusIcon className="h-4 w-4" />} onClick={handleCreateClick}>
          Create Goal
        </Button>
      </Heading>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin h-8 w-8 border-2 border-primary dark:border-primary-dark border-t-transparent rounded-full" />
          </div>
        ) : goals.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 px-6">
            <div className="text-6xl mb-4">🎯</div>
            <h3 className="text-xl font-bold text-text-primary dark:text-text-primary-dark mb-2">No Savings Goals Yet</h3>
            <p className="text-text-secondary dark:text-text-secondary-dark mb-6">Create your first savings goal to get started</p>
            <Button leftIcon={<PlusIcon className="h-4 w-4" />} onClick={handleCreateClick}>
              Create Your First Goal
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onEdit={() => handleEditClick(goal)}
                onDelete={() => handleDelete(goal.id)}
                onRefresh={fetchGoals}
              />
            ))}
          </div>
        )}
      </main>

      <Modal open={showModal} onClose={() => setShowModal(false)}>
        <h3 className="text-xl font-bold text-text-primary dark:text-text-primary-dark">
          {editingGoal ? 'Edit Goal' : 'Create New Goal'}
        </h3>

        <div className="flex justify-center">
          <div className="w-20 h-20 rounded-[2.5rem] shadow-2xl flex items-center justify-center transition-all duration-300" style={{ backgroundColor: formData.color }}>
            <DynamicHeroIcon iconName={formData.icon} className="h-10 w-10 text-white" />
          </div>
        </div>

        <div className="space-y-4">
          <Input
            label="Goal Name"
            name="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., House Deposit"
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Target Amount (€)"
              name="target_amount"
              type="number"
              value={formData.target_amount}
              onChange={(e) => setFormData({ ...formData, target_amount: Number(e.target.value) })}
              placeholder="0.00"
            />
            <Input
              label="Current Balance (€)"
              name="current_amount"
              type="number"
              value={formData.current_amount}
              onChange={(e) => setFormData({ ...formData, current_amount: Number(e.target.value) })}
              placeholder="0.00"
            />
          </div>

          {/* Icon Picker */}
          <div className="space-y-2">
            <div className="flex items-center justify-between px-1">
              <label className="text-[10px] font-black uppercase text-text-secondary dark:text-text-secondary-dark">Pick an Icon</label>
              {formData.icon !== 'BanknotesIcon' && (
                <button onClick={() => setFormData({ ...formData, icon: 'BanknotesIcon' })} className="text-[10px] text-primary dark:text-primary-dark font-bold flex items-center gap-1">
                  <XMarkIcon className="h-3 w-3" /> Use Default
                </button>
              )}
            </div>
            <div className="p-3 bg-surface-base dark:bg-surface-base-dark rounded-2xl border border-border dark:border-border-dark space-y-3">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-text-secondary dark:text-text-secondary-dark" />
                <input type="text" placeholder="Search icons..." className="w-full bg-transparent border-none focus:ring-0 text-sm pl-9 text-text-primary dark:text-text-primary-dark" value={iconSearch} onChange={(e) => setIconSearch(e.target.value)} />
              </div>
              <div className="grid grid-cols-7 gap-2 max-h-40 overflow-y-auto pr-1">
                {Object.keys(Icons)
                  .filter(name => name.endsWith('Icon'))
                  .filter(name => !iconSearch || name.toLowerCase().includes(iconSearch.toLowerCase()))
                  .slice(0, 28)
                  .map((name) => (
                    <button key={name} onClick={() => setFormData({ ...formData, icon: name })} className={`p-2 rounded-xl transition-all flex items-center justify-center ${formData.icon === name ? 'bg-primary text-white shadow-lg scale-110' : 'hover:bg-surface-panel dark:hover:bg-surface-panel-dark text-text-secondary dark:text-text-secondary-dark'}`}>
                      <DynamicHeroIcon iconName={name} className="h-5 w-5" />
                    </button>
                  ))}
              </div>
            </div>
          </div>

          <div>
            <Input
              label="Color"
              type="color"
              className="h-12"
              value={formData.color}
              onChange={(e) => setFormData({ ...formData, color: e.target.value })}
            />
          </div>

          <div className="pt-4 mt-4 border-t border-border dark:border-border-dark space-y-3">
            <label className="text-[10px] font-black uppercase text-text-secondary dark:text-text-secondary-dark block">Automation (Optional)</label>

            <div className="flex items-center gap-2 p-3 bg-surface-base dark:bg-surface-base-dark rounded-2xl">
              <Input
                label="Enable Auto-Save"
                name="automation_is_active"
                type="checkbox"
                checked={formData.automation_is_active}
                onChange={(e) => setFormData({ ...formData, automation_is_active: e.target.checked })}
              />
            </div>

            {formData.automation_is_active && (
              <>
                <Input
                  label="Auto-Save Amount (€)"
                  name="automation_amount"
                  type="number"
                  value={formData.automation_amount || 0}
                  onChange={(e) => setFormData({ ...formData, automation_amount: Number(e.target.value) })}
                  placeholder="0.00"
                />
                <Select
                  label="Auto-Save Frequency"
                  value={formData.automation_frequency || 'monthly'}
                  onChange={(val) => setFormData({ ...formData, automation_frequency: val as string })}
                  options={[
                    { value: 'monthly', label: 'Monthly' },
                    { value: 'quarterly', label: 'Quarterly (3 months)' },
                    { value: 'yearly', label: 'Yearly' },
                  ]}
                />
                <Input
                  label="Next Run Date"
                  name="automation_next_run_date"
                  type="date"
                  value={formData.automation_next_run_date || ''}
                  onChange={(e) => setFormData({ ...formData, automation_next_run_date: e.target.value })}
                />
              </>
            )}
          </div>
        </div>

        <div className="flex gap-3 pt-4 border-t border-border dark:border-border-dark">
          <Button variant="ghost" color_name="light" onClick={() => setShowModal(false)} className="flex-1">
            Cancel
          </Button>
          <Button
            className="flex-1"
            onClick={handleSave}
            leftIcon={<CheckIcon className="h-4 w-4" />}
          >
            {editingGoal ? 'Update' : 'Create'}
          </Button>
        </div>
      </Modal>
    </div>
  );
};

const GoalCard = ({ goal, onEdit, onDelete, onRefresh }: any) => {
  const navigate = useNavigate();
  const [showContribute, setShowContribute] = useState(false);
  const [contributionAmount, setContributionAmount] = useState(0);
  const [contributionDate, setContributionDate] = useState(new Date().toISOString().split('T')[0]);
  const [isContributing, setIsContributing] = useState(false);

  const progress = Math.min(Math.max((goal.current_amount / goal.target_amount) * 100, 0), 100);
  const remaining = Math.max(goal.target_amount - goal.current_amount, 0);
  const isNegative = goal.current_amount < 0;
  const color = isNegative ? 'bg-state-danger dark:bg-state-danger-dark' : progress > 75 ? 'bg-state-success dark:bg-state-success-dark' : progress > 50 ? 'bg-primary dark:bg-primary-dark' : 'bg-state-warning dark:bg-state-warning-dark';

  const handleContribute = async () => {
    if (contributionAmount <= 0) {
      alert("Please enter a valid amount");
      return;
    }
    setIsContributing(true);
    try {
      await callApi(`/savings_goals/${goal.id}/contribute`, "POST", undefined, { 
        amount: contributionAmount,
        date: contributionDate
      });
      setShowContribute(false);
      setContributionAmount(0);
      setContributionDate(new Date().toISOString().split('T')[0]);
      onRefresh();
    } catch (error) {
      console.error("Failed to contribute", error);
    } finally {
      setIsContributing(false);
    }
  };

  return (
    <>
      <Card>
        <div className="flex justify-between items-start mb-4">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center text-white shadow-sm" style={{ backgroundColor: goal.color || '#3b82f6' }}>
            <DynamicHeroIcon iconName={goal.icon || 'BanknotesIcon'} className="h-5 w-5" />
          </div>
          <div className="flex gap-1">
            <Button variant="ghost" color_name="light" size="small" onClick={onEdit} className="p-1">
              <Icons.PencilSquareIcon className="h-4 w-4" />
            </Button>
            <Button variant="ghost" color_name="light" size="small" onClick={onDelete} className="p-1">
              <TrashIcon className="h-4 w-4 text-state-danger dark:text-state-danger-dark" />
            </Button>
          </div>
        </div>

        <h3 className="text-lg font-bold text-text-primary dark:text-text-primary-dark mb-1">{goal.name}</h3>
        <p className={`text-sm mb-6 font-semibold font-mono ${isNegative ? 'text-state-danger dark:text-state-danger-dark' : 'text-text-secondary dark:text-text-secondary-dark'}`}>
          {formatCurrency(goal.current_amount || 0)}
          {goal.target_amount > 0 && ` of ${formatCurrency(goal.target_amount)}`}
        </p>

        {goal.target_amount > 0 && (
          <>
            <div className="relative w-full h-3 bg-surface-base dark:bg-surface-base-dark rounded-full overflow-hidden mb-4">
              <div className={`absolute top-0 left-0 h-full ${color} transition-all duration-500`} style={{ width: `${progress}%` }} />
            </div>
            <div className="flex items-center justify-between text-xs font-semibold text-text-secondary dark:text-text-secondary-dark mb-4">
              <span>{Math.round(progress)}% Complete</span>
              <div>{formatCurrency(remaining)} to go</div>
            </div>
          </>
        )}

        {goal.automation_is_active && (
          <div className="p-3 mb-4 bg-primary/10 dark:bg-primary-dark/10 border border-primary/20 dark:border-primary-dark/20 rounded-2xl">
            <div className="text-xs font-semibold text-primary dark:text-primary-dark mb-1">
              Auto-Save: {formatCurrency(goal.automation_amount || 0)}/{goal.automation_frequency}
            </div>
            {goal.automation_next_run_date && (
              <div className="text-[10px] text-text-secondary dark:text-text-secondary-dark">
                Next run: {new Date(goal.automation_next_run_date).toLocaleDateString()}
              </div>
            )}
          </div>
        )}

        <div className="flex gap-2">
          <Button className="flex-1" onClick={() => setShowContribute(true)} leftIcon={<PlusIcon className="h-4 w-4" />}>
            Add Savings
          </Button>
          <Button variant="ghost" className="flex-1" rightIcon={<ArrowRightIcon className="h-4 w-4" />} onClick={() => navigate(`/transactions?savings_goal_id=${goal.id}`)}>
            View
          </Button>
        </div>
      </Card>

      <Modal open={showContribute} onClose={() => setShowContribute(false)}>
        <div className="p-6 bg-surface-card dark:bg-surface-card-dark rounded-3xl space-y-6 w-80">
          <h3 className="text-lg font-bold text-text-primary dark:text-text-primary-dark">Contribute to {goal.name}</h3>
          <Input name="Amount (€)" type="number" value={contributionAmount} onChange={(e) => setContributionAmount(Number(e.target.value))} placeholder="0.00" step="0.01" />
          <Input name="Date" type="date" value={contributionDate} onChange={(e) => setContributionDate(e.target.value)} />
          <div className="flex gap-3">
            <Button variant="ghost" color_name="light" onClick={() => setShowContribute(false)} className="flex-1">Cancel</Button>
            <Button className="flex-1" onClick={handleContribute} isLoading={isContributing} leftIcon={<CheckIcon className="h-4 w-4" />}>Contribute</Button>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default SavingsPage;