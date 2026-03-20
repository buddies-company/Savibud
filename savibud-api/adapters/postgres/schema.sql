-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enums for cleaner data
CREATE TYPE budget_period AS ENUM ('daily', 'weekly', 'monthly', 'trimestrial', 'quarterly', 'yearly');

-- Categories table (for budgeting)
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    -- Self-reference: points back to the ID of another category
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    icon TEXT, 
    color TEXT, 
    is_income BOOLEAN DEFAULT FALSE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- Allow custom user categories
    amount DECIMAL(12, 2) NULL,
    period budget_period DEFAULT 'monthly',
    budget_start_date DATE DEFAULT NULL,
    budget_end_date DATE DEFAULT NULL,
    is_fixed BOOLEAN DEFAULT FALSE, -- TRUE for "Rent", FALSE for "Groceries"
    UNIQUE(user_id, category_id, period)
);

-- Index to quickly find all subcategories of a parent
CREATE INDEX idx_categories_parent ON categories(parent_id);

-- Accounts table (Links to Powens 'account' object)
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    powens_account_id TEXT UNIQUE, -- ID provided by Powens
    name TEXT NOT NULL,
    bank_name TEXT,
    balance DECIMAL(12, 2) DEFAULT 0.00,
    currency TEXT DEFAULT 'EUR'
);

-- Manual Accounts table (For user-created accounts not linked to Powens)
CREATE TABLE manual_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    account_type TEXT NOT NULL,  -- 'loan' or 'savings'
    current_balance DECIMAL(12, 2) DEFAULT 0.00,
    currency TEXT DEFAULT 'EUR',
    
    # Loan-specific fields
    loan_initial_amount DECIMAL(12, 2) DEFAULT NULL,
    loan_interest_rate DECIMAL(5, 3) DEFAULT NULL,  -- Annual percentage
    loan_duration_months INTEGER DEFAULT NULL,  -- Total loan duration
    loan_start_date DATE DEFAULT NULL,
    loan_monthly_payment DECIMAL(12, 2) DEFAULT NULL,  -- Calculated
    
    # Metadata
    icon TEXT DEFAULT 'BanknotesIcon',
    color TEXT DEFAULT '#3b82f6',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE TABLE snapshot_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,  -- For Powens accounts
    manual_account_id UUID REFERENCES manual_accounts(id) ON DELETE CASCADE,  -- For manual accounts
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    balance DECIMAL(12, 2) NOT NULL,
    snapshot_date DATE NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (account_id IS NOT NULL OR manual_account_id IS NOT NULL),
    UNIQUE(account_id, snapshot_date),
    UNIQUE(manual_account_id, snapshot_date)
);

CREATE INDEX idx_snapshot_accounts_user_id ON snapshot_accounts(user_id);
CREATE INDEX idx_snapshot_accounts_snapshot_date ON snapshot_accounts(snapshot_date);


-- Transactions table (Links to Powens 'transaction' object)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    powens_transaction_id TEXT UNIQUE NULL, 
    date DATE NOT NULL,
    label TEXT NOT NULL, -- The transaction description
    amount DECIMAL(12, 2) NOT NULL,
    raw_data JSONB, -- Store the full Powens JSON here for safety
    is_deleted BOOLEAN DEFAULT FALSE,
    savings_goal_id UUID REFERENCES savings_goals(id) ON DELETE SET NULL
);

-- Index for fast graph queries by date
CREATE INDEX idx_transactions_date ON transactions(date);

-- Savings Goals ("Virtual Accounts")
CREATE TABLE savings_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    target_amount DECIMAL(12, 2), -- "Max amount" goal
    current_amount DECIMAL(12, 2) DEFAULT 0.00,
    color TEXT,
    icon TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    automation_amount DECIMAL(12, 2) NOT NULL,
    automation_frequency budget_period NOT NULL,
    automation_next_run_date DATE NOT NULL,
    automation_is_active BOOLEAN DEFAULT TRUE
    UNIQUE(user_id, name)
);

CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    
    keywords TEXT[] DEFAULT NULL,  -- e.g., ["spotify", "netflix"]
    regex_pattern TEXT DEFAULT NULL,  -- e.g., ".*grocery.*"
    min_amount DECIMAL(12, 2) DEFAULT NULL,
    max_amount DECIMAL(12, 2) DEFAULT NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 100  -- Higher priority rules applied first
);