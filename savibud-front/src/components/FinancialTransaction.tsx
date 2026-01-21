import { Transaction } from '../utils/constants/types';
import * as Icons from '@heroicons/react/24/outline';
import { QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

/**
 * Helper to render HeroIcons from a string
 */
const DynamicHeroIcon = ({ iconName, className }: { iconName: string; className?: string }) => {
  const IconComponent = (Icons as any)[iconName] || QuestionMarkCircleIcon;
  return <IconComponent className={className} />;
};

export const FinancialTransaction = ({ 
  tx, 
  onSelect,
  onRefresh // Callback to tell parent to reload data after an update
}: { 
  tx: Transaction; 
  onSelect: (tx: Transaction) => void;
  onRefresh?: () => void;
}) => {
  if (!tx) return null;

  const { label, amount, date, category } = tx;
  const isPositive = Number(amount) > 0;

  /**
   * Resolve Visuals: 
   * If category exists, use its color/icon.
   * Else, use "Uncategorized" defaults.
   */
  const categoryColor = category?.color || '#9ca3af'; // Gray-400 fallback
  const categoryIcon = category?.icon || 'QuestionMarkCircleIcon';

  return (
    <button
      onClick={() => onSelect(tx)}
      className="w-full flex items-center cursor-pointer justify-between p-3 hover:bg-surface-base/80 dark:hover:bg-surface-base-dark/20 rounded-2xl transition-all text-left group border border-transparent hover:border-border dark:hover:border-border-dark"
    >
      <div className="flex items-center min-w-0">
        {/* Category Icon Box */}
        <div 
          className="w-11 h-11 shrink-0 rounded-2xl flex items-center justify-center mr-4 shadow-sm transition-transform group-hover:scale-105"
          style={{ 
            backgroundColor: category ? `${categoryColor}20` : '#f3f4f6', // 20% opacity background
            color: categoryColor 
          }}
        >
           <DynamicHeroIcon 
             iconName={categoryIcon} 
             className="w-6 h-6" 
           />
        </div>

        <div className="min-w-0">
          <p className="font-bold text-sm text-text-primary dark:text-text-primary-dark truncate pr-2">
            {label}
          </p>
          <div className="flex items-center gap-2 mt-0.5">
            <p className="text-text-secondary dark:text-text-secondary-dark text-[10px] font-medium uppercase tracking-wider">
              {new Date(date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}
            </p>
            {category && (
              <>
                <span className="text-text-secondary/30 text-[10px]">•</span>
                <span 
                  className="text-[10px] font-black uppercase tracking-tighter"
                  style={{ color: categoryColor }}
                >
                  {category.name}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-col items-end gap-1">
        <span className={`font-mono font-bold whitespace-nowrap text-sm ${
          isPositive 
            ? 'text-state-success dark:text-state-success-dark' 
            : 'text-text-primary dark:text-text-primary-dark'
        }`}>
          {isPositive ? '+' : ''}{Number(amount).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}€
        </span>
        {/* Visual cue for savings goals link if applicable */}
        {tx.savings_goal_id && (
          <div className="flex items-center gap-1 text-[9px] text-primary dark:text-primary-dark font-bold uppercase tracking-widest">
            <Icons.SparklesIcon className="h-2.5 w-2.5" /> Saved
          </div>
        )}
      </div>
    </button>
  );
};