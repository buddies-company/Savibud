import { useState, useEffect } from 'react';
import { Modal, Input, Select, Button, SearchableCombobox } from '@soilhat/react-components';
import { Transaction, Category, SavingsGoal } from '../utils/constants/types';
import * as Icons from '@heroicons/react/24/outline';
import { CalendarIcon, TagIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';
import { callApi } from '../services/api';

interface Props {
  tx: Partial<Transaction> | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh?: () => void;
  categories: Category[];
  savingsGoals: SavingsGoal[];
}

/** Helper for dynamic icon lookup */
const DynamicHeroIcon = ({ iconName, className }: { iconName: string; className?: string }) => {
  const IconComponent = (Icons as any)[iconName] || QuestionMarkCircleIcon;
  return <IconComponent className={className} />;
};

export const TransactionDetailModal = ({ 
  tx, 
  isOpen, 
  onClose, 
  onRefresh,
  categories,
  savingsGoals
}: Props) => {
  const [formData, setFormData] = useState<Partial<Transaction>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Sync internal state when modal opens or tx changes
  useEffect(() => {
    if (tx) {
      setFormData(tx);
    } else {
      setFormData({
        date: new Date(),
        amount: 0,
        label: '',
        category_id: undefined,
        savings_goal_id: undefined
      });
    }
  }, [tx, isOpen]);

  if (!tx && isOpen === false) return null;

  const isVirtual = !formData.account_id;
  const selectedCategory = categories.find(c => c.id === formData.category_id);
  const catColor = selectedCategory?.color || '#9ca3af';
    const isEdit = !!formData.id;

  const handleSave = async () => {
    setIsSubmitting(true);
    const url = isEdit ? `/transactions/${formData.id}` : "/transactions";
    const method = isEdit ? "PUT" : "POST";

    try {
      await callApi(url, method, undefined, formData);
      if (onRefresh) onRefresh();
      onClose();
    } catch (error) {
      console.error("Save failed", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose}>
      <div className="p-6 bg-surface-card dark:bg-surface-card-dark rounded-3xl space-y-6">
        <header className="flex justify-between items-center">
            <h3 className="text-xl font-bold text-text-primary dark:text-text-primary-dark">
                {isEdit ? 'Edit Transaction' : 'New Virtual Transaction'}
            </h3>
            {isVirtual && (
                <span className="px-3 py-1 bg-primary/10 dark:bg-primary-dark/90 text-primary dark:text-primary-dark text-[10px] font-black uppercase rounded-full">
                    Virtual
                </span>
            )}
        </header>

        {/* Amount Section */}
        <div className="text-center py-8 bg-surface-base dark:bg-surface-base-dark rounded-[2.5rem] border border-border/50 dark:border-border-dark/50 shadow-inner relative overflow-hidden">
          <div className="absolute top-4 left-4">
             <div 
                className="w-12 h-12 rounded-2xl flex items-center justify-center text-white shadow-lg transition-transform"
                style={{ backgroundColor: catColor }}
             >
                <DynamicHeroIcon iconName={selectedCategory?.icon || 'TagIcon'} className="h-6 w-6" />
             </div>
          </div>
          
          <p className="text-text-secondary dark:text-text-secondary-dark text-[10px] uppercase font-black tracking-widest mb-1">
            Transaction Value
          </p>
          <div className="flex items-center justify-center gap-2">
             <input 
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({...formData, amount: Number(e.target.value)})}
                className={`bg-transparent text-4xl font-black text-center outline-none w-1/2 ${Number(formData.amount) > 0 ? 'text-state-success dark:text-state-success-dark' : ''}`}
             />
             <span className="text-2xl font-black opacity-30">€</span>
          </div>
        </div>

        {/* Form Fields */}
        <div className="space-y-4">
          <Input 
            label="Description" 
            value={formData.label || ''} 
            onChange={(e) => setFormData({...formData, label: e.target.value})}
            placeholder="Merchant or reference..."
            leftIcon={<TagIcon className="h-5 w-5" />}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input 
                label="Date" 
                type="date"
                value={formData.date?.toString().split('T')[0]} 
                onChange={(e) => setFormData({...formData, date: new Date(e.target.value)})}
                leftIcon={<CalendarIcon className="h-5 w-5" />}
            />
            <SearchableCombobox 
                label="Category"
                value={formData.category_id}
                options={categories.map(c => ({ value: c.id, label: c.name, description: c.is_income ? 'Income' : 'Expense' }))}
                onChange={(val) => setFormData({...formData, category_id: val as string})}
            />
          </div>

          <div className="pt-2 border-t border-border dark:border-border-dark">
             <Select 
                label="Link to Savings Goal"
                placeholder="Optional: Select a goal"
                value={formData.savings_goal_id || 'none'}
                onChange={(val) => setFormData({...formData, savings_goal_id: val === 'none' ? undefined : (val as string)})}
                options={[
                    { value: 'none', label: 'No Savings Goal' },
                    ...savingsGoals.map(g => ({ value: g.id, label: g.name }))
                ]}
                className="bg-primary/5 dark:bg-primary-dark/5 p-1 rounded-xl"
             />
             <p className="mt-2 text-[10px] text-text-secondary dark:text-text-secondary-dark italic px-2">
                Linking to a goal will move this amount to the "Virtual Account" history.
             </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex gap-3 pt-4 border-t border-border dark:border-border-dark">
          <Button variant="ghost" color_name="light" onClick={onClose} className="flex-1">
            Discard
          </Button>
          <Button 
            className="flex-1 shadow-xl shadow-primary/20" 
            onClick={handleSave}
            isLoading={isSubmitting}
            leftIcon={isEdit ? <Icons.ArrowPathIcon className="h-4 w-4" /> : <Icons.CheckIcon className="h-4 w-4" />}
          >
            {isEdit ? 'Update' : 'Create'}
          </Button>
        </div>
      </div>
    </Modal>
  );
};