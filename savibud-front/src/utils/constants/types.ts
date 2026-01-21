export type User = {
  username: string;
  avatar?: string | null;
};

export type LoginData = {
  username: string;
  password: string;
};

export type Account = {
  id: string;
  bank_name: string;
  balance: number;
  currency: string;
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
}

export type Category = {
  id: string;
  name: string;
  parent_id: string | null;
  color: string;
  icon: string | null;
  is_income: boolean;
}

export type BudgetEntry = {
  id: string;
  category_id: string;
  period: string;
  start_date: Date,
  end_date: Date,
  amount: number;
  is_fixed: boolean;
  category: Category;
}