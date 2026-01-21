-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table (for budgeting)
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    -- Self-reference: points back to the ID of another category
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    icon TEXT, 
    color TEXT, 
    is_income BOOLEAN DEFAULT FALSE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE -- Allow custom user categories
);

-- Index to quickly find all subcategories of a parent
CREATE INDEX idx_categories_parent ON categories(parent_id);

-- Accounts table (Links to Powens 'account' object)
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    powens_account_id TEXT UNIQUE, -- ID provided by Powens
    bank_name TEXT,
    balance DECIMAL(12, 2) DEFAULT 0.00,
    currency TEXT DEFAULT 'EUR'
);

CREATE TABLE account_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    balance DECIMAL(12, 2) NOT NULL,
    snapshot_date DATE NOT NULL,
    UNIQUE(account_id, snapshot_date)
);

-- Transactions table (Links to Powens 'transaction' object)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    powens_transaction_id TEXT UNIQUE, 
    date DATE NOT NULL,
    label TEXT NOT NULL, -- The transaction description
    amount DECIMAL(12, 2) NOT NULL,
    raw_data JSONB, -- Store the full Powens JSON here for safety
    is_deleted BOOLEAN DEFAULT FALSE,
    savings_goal_id UUID REFERENCES savings_goals(id) ON DELETE SET NULL
);

-- Budgets table
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL,
    period budget_period DEFAULT 'monthly',
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL,
    is_fixed BOOLEAN DEFAULT FALSE, -- TRUE for "Rent", FALSE for "Groceries"
    UNIQUE(user_id, category_id, period)
);

-- Index for fast graph queries by date
CREATE INDEX idx_transactions_date ON transactions(date);

-- Enums for cleaner data
CREATE TYPE budget_period AS ENUM ('daily', 'weekly', 'monthly', 'trimestrial', 'quarterly', 'yearly');

-- Savings Goals ("Virtual Accounts")
CREATE TABLE savings_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    target_amount DECIMAL(12, 2), -- "Max amount" goal
    current_amount DECIMAL(12, 2) DEFAULT 0.00,
    color TEXT,
    icon TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Savings Automations (The "10€ Monthly" logic)
CREATE TABLE savings_automations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID REFERENCES savings_goals(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL,
    frequency budget_period NOT NULL,
    next_run_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
