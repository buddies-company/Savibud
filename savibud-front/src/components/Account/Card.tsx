import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Button, Modal, Input } from '@soilhat/react-components';
import { TrashIcon, ArrowRightIcon, CheckIcon } from '@heroicons/react/24/outline';
import { DynamicHeroIcon } from "../DynamicHeroIcon";
import { callApi } from "../../services/api";
import { ManualAccount, UnifiedAccount } from "../../utils/constants/types"; // Use the Unified type

interface AccountCardProps {
  // Use the union type to handle both bank and manual data
  account: UnifiedAccount; 
  onEdit: () => void;
  onDelete: () => void;
  onRefresh: () => void;
}

export const AccountCard = ({ account, onEdit, onDelete, onRefresh }: AccountCardProps) => {
  const navigate = useNavigate();

  const getBalance = (acc: UnifiedAccount): number => {
    if (acc.type === 'manual') {
      return acc.current_balance;
    }
    return acc.balance;
  };
  const displayBalance = getBalance(account);
  
  const [showSnapshot, setShowSnapshot] = useState(false);
  const [snapshotBalance, setSnapshotBalance] = useState(displayBalance);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRecordSnapshot = async () => {
    setIsSubmitting(true);
    try {
      await callApi(`/accounts/${account.id}/snapshot`, "POST", undefined, { balance: snapshotBalance });
      setShowSnapshot(false);
      onRefresh();
    } catch (error) {
      alert("Failed to record snapshot");
    } finally {
      setIsSubmitting(false);
    }
  };

  const isLoan = account.account_type === "loan";
  const isManual = account.type === "manual";

  return (
    <>
      <Card>
        <div className="flex justify-between items-start mb-4">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center text-white" style={{ backgroundColor: account.color || '#3b82f6' }}>
            <DynamicHeroIcon iconName={account.icon || 'BanknotesIcon'} className="h-5 w-5" />
          </div>
          <div className="flex gap-1">
            {/* Show edit only for manual accounts */}
            {isManual && (
              <button onClick={onEdit} className="p-1 hover:bg-surface-panel rounded-md transition-colors">
                <DynamicHeroIcon iconName="PencilSquareIcon" className="h-4 w-4 text-text-secondary" />
              </button>
            )}
            <button onClick={onDelete} className="p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors">
              <TrashIcon className="h-4 w-4 text-state-danger" />
            </button>
          </div>
        </div>

        <h3 className="text-lg font-bold truncate">{account.name}</h3>
        
        {/* --- 2. Use displayBalance here --- */}
        <p className={`text-sm mb-4 font-mono font-bold ${displayBalance < 0 ? 'text-state-danger' : 'text-text-secondary'}`}>
          €{displayBalance.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}
        </p>

        {isLoan && (account as ManualAccount).loan_monthly_payment && (
          <div className="p-3 bg-primary/5 rounded-2xl mb-4 border border-primary/10">
            <div className="text-xs font-bold text-primary">Monthly: €{(account as ManualAccount).loan_monthly_payment?.toLocaleString()}</div>
            <div className="text-[10px] text-text-secondary">{(account as ManualAccount).loan_interest_rate}% rate</div>
          </div>
        )}

        <div className="flex gap-2">
          {/* Only manual savings accounts get snapshots */}
          {isManual && !isLoan && (
            <Button className="flex-1" size="small" onClick={() => setShowSnapshot(true)}>Snapshot</Button>
          )}
          <Button 
            variant="ghost" 
            className="flex-1" 
            size="small" 
            rightIcon={<ArrowRightIcon className="h-4 w-4" />} 
            onClick={() => navigate(`/accounts/${account.id}/history`)}
          >
            History
          </Button>
        </div>
      </Card>

      <Modal open={showSnapshot} onClose={() => setShowSnapshot(false)}>
        <div className="p-6 bg-surface-card dark:bg-surface-card-dark rounded-3xl space-y-6 w-80">
          <h3 className="text-lg font-bold">New Balance for {account.name}</h3>
          <Input 
            type="number" 
            value={snapshotBalance} 
            onChange={(e) => setSnapshotBalance(Number(e.target.value))} 
          />
          <div className="flex gap-3">
            <Button variant="ghost" className="flex-1" onClick={() => setShowSnapshot(false)}>Cancel</Button>
            <Button className="flex-1" onClick={handleRecordSnapshot} isLoading={isSubmitting} leftIcon={<CheckIcon className="h-4 w-4" />}>Record</Button>
          </div>
        </div>
      </Modal>
    </>
  );
};