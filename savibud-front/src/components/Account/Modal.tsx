import { useState, useEffect } from "react";
import { Modal, Button, Input } from '@soilhat/react-components';
import { CheckIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import * as Icons from '@heroicons/react/24/outline';
import { DynamicHeroIcon } from "../DynamicHeroIcon";
import { callApi } from "../../services/api";
import { ManualAccount } from "../../utils/constants/types";

interface AccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'loan' | 'savings';
  editingAccount: ManualAccount | null;
  onSave: () => void;
}

export const AccountModal = ({ isOpen, onClose, mode, editingAccount, onSave }: AccountModalProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [iconSearch, setIconSearch] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    current_balance: 0,
    initial_amount: 0,
    interest_rate: 3.5,
    duration_months: 360,
    start_date: new Date().toISOString().split('T')[0],
    icon: 'BanknotesIcon',
    color: '#3b82f6',
  });

  useEffect(() => {
    if (editingAccount) {
      setFormData({
        name: editingAccount.name,
        current_balance: editingAccount.current_balance,
        initial_amount: editingAccount.loan_initial_amount || 0,
        interest_rate: editingAccount.loan_interest_rate || 3.5,
        duration_months: editingAccount.loan_duration_months || 360,
        start_date: editingAccount.loan_start_date || new Date().toISOString().split('T')[0],
        icon: editingAccount.icon || (mode === 'loan' ? 'CreditCardIcon' : 'BanknotesIcon'),
        color: editingAccount.color || (mode === 'loan' ? '#ef4444' : '#10b981'),
      });
    } else {
      setFormData({
        name: '',
        current_balance: 0,
        initial_amount: 0,
        interest_rate: 3.5,
        duration_months: 360,
        start_date: new Date().toISOString().split('T')[0],
        icon: mode === 'loan' ? 'CreditCardIcon' : 'BanknotesIcon',
        color: mode === 'loan' ? '#ef4444' : '#10b981',
      });
    }
    setIconSearch('');
  }, [editingAccount, mode, isOpen]);

  const handleSave = async () => {
    if (!formData.name) return alert("Account name is required");
    
    setIsSubmitting(true);
    try {
      const endpoint = mode === 'loan' ? "/accounts/loans" : "/accounts/savings";
      const method = editingAccount ? "PUT" : "POST";
      const url = editingAccount ? `/accounts/${editingAccount.id}` : endpoint;

      const payload = mode === 'loan' ? {
        name: formData.name,
        initial_amount: formData.initial_amount,
        interest_rate: formData.interest_rate,
        duration_months: formData.duration_months,
        start_date: formData.start_date,
        icon: formData.icon,
        color: formData.color,
      } : {
        name: formData.name,
        current_balance: formData.current_balance,
        icon: formData.icon,
        color: formData.color,
      };

      await callApi(url, method, undefined, payload);
      onSave();
      onClose();
    } catch (error) {
      alert("Failed to save account");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose}>
      <div className="p-6 bg-surface-card dark:bg-surface-card-dark rounded-3xl space-y-6 w-full max-w-md">
        <h3 className="text-xl font-bold">
          {editingAccount ? 'Edit Account' : `New ${mode === 'loan' ? 'Loan' : 'Savings'}`}
        </h3>

        <div className="flex justify-center">
          <div className="w-20 h-20 rounded-[2.5rem] shadow-xl flex items-center justify-center transition-all" style={{ backgroundColor: formData.color }}>
            <DynamicHeroIcon iconName={formData.icon} className="h-10 w-10 text-white" />
          </div>
        </div>

        <div className="space-y-4">
          <Input label="Account Name" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} />
          
          {mode === 'loan' ? (
            <>
              <Input label="Initial Amount (€)" type="number" value={formData.initial_amount} onChange={(e) => setFormData({...formData, initial_amount: Number(e.target.value)})} />
              <Input label="Rate (%)" type="number" step="0.01" value={formData.interest_rate} onChange={(e) => setFormData({...formData, interest_rate: Number(e.target.value)})} />
            </>
          ) : (
            <Input label="Current Balance (€)" type="number" value={formData.current_balance} onChange={(e) => setFormData({...formData, current_balance: Number(e.target.value)})} />
          )}

          <div className="space-y-2">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-text-secondary" />
              <input 
                type="text" 
                placeholder="Search icons..." 
                className="w-full bg-surface-base dark:bg-surface-base-dark rounded-xl pl-9 py-2 text-sm border-none focus:ring-1 focus:ring-primary" 
                value={iconSearch} 
                onChange={(e) => setIconSearch(e.target.value)} 
              />
            </div>
            <div className="grid grid-cols-7 gap-2 max-h-32 overflow-y-auto p-1">
              {Object.keys(Icons)
                .filter(name => name.endsWith('Icon') && (!iconSearch || name.toLowerCase().includes(iconSearch.toLowerCase())))
                .slice(0, 21)
                .map((name) => (
                  <button 
                    key={name} 
                    onClick={() => setFormData({...formData, icon: name})} 
                    className={`p-2 rounded-lg flex items-center justify-center transition-all ${formData.icon === name ? 'bg-primary text-white scale-110' : 'hover:bg-surface-panel text-text-secondary'}`}
                  >
                    <DynamicHeroIcon iconName={name} className="h-4 w-4" />
                  </button>
                ))}
            </div>
          </div>

          <Input label="Theme Color" type="color" value={formData.color} onChange={(e) => setFormData({...formData, color: e.target.value})} />
        </div>

        <div className="flex gap-3 pt-4 border-t border-border">
          <Button variant="ghost" className="flex-1" onClick={onClose}>Cancel</Button>
          <Button className="flex-1" onClick={handleSave} isLoading={isSubmitting} leftIcon={<CheckIcon className="h-4 w-4" />}>
            {editingAccount ? 'Update' : 'Create'}
          </Button>
        </div>
      </div>
    </Modal>
  );
};