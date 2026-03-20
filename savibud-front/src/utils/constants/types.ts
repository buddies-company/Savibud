export type User = {
  username: string;
  avatar?: string | null;
};

export type LoginData = {
  username: string;
  password: string;
};

export type FilterParams = {
  q?: string;
  category_id?: string;
  account_id?: string;
  savings_goal_id?: string;
  date_from?: string; // ISO format: YYYY-MM-DD
  date_to?: string;   // ISO format: YYYY-MM-DD
  uncategorized_only?: boolean;
  page?: number;
  limit?: number;
};

// Shared properties
interface BaseAccount {
  id: string;
  name: string;
  currency: string;
  is_active: boolean;
  icon?: string;
  color: string;
}

// Specifically for Powens accounts
export interface BankAccount extends BaseAccount {
  type: 'bank'; // Discriminator
  bank_name: string;
  balance: number;
  account_type: string;
  last_sync: string | null;
}

// Specifically for Manual accounts (Savings or Loans)
export interface ManualAccount extends BaseAccount {
  type: 'manual'; // Discriminator
  account_type: 'loan' | 'savings';
  current_balance: number;
  loan_initial_amount?: number;
  loan_interest_rate?: number;
  loan_duration_months?: number;
  loan_start_date?: string;
  loan_monthly_payment?: number;
}

// Unified type for the UI
export type UnifiedAccount = BankAccount | ManualAccount;

export type SnapshotAccount = {
  id: string;
  account_id?: string;  // For Powens accounts
  manual_account_id?: string;  // For manual accounts
  user_id: string;
  balance: number;
  snapshot_date: string;
  recorded_at: string;
}

export type Transaction = {
  account_id?: string;
  amount: number
  category_id?: string
  date: Date
  id: number
  internal_link_id?: number | null
  is_deleted: boolean
  is_internal: boolean
  label: string
  powens_transaction_id: string
  savings_goal_id: string
  category: Category
  saving_goal: SavingsGoal
}

export type Category = {
  id: string;
  name: string;
  parent_id: string | null;
  color: string;
  icon: string | null;
  is_income: boolean;
  budget_amount?: number;
  budget_period?: string;
  budget_start_date?: Date;
  budget_end_date?: Date;
  is_fixed?: boolean;
}

export type SavingsGoal = {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  icon?: string;
  color?: string;
  automation_amount?: number;
  automation_frequency?: string;
  automation_next_run_date?: string;
  automation_is_active?: boolean;
}

export type Rule = {
  id: string;
  category_id?: string;
  savings_goal_id?: string;
  name: string;
  description?: string;
  keywords?: string[];
  regex_pattern?: string;
  min_amount?: number;
  max_amount?: number;
  is_active: boolean;
  priority: number;
  category?: Category;
  savings_goal?: SavingsGoal;
}