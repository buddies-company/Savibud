"""Apply categorization rules to transactions."""

import re
from decimal import Decimal
from uuid import UUID

from adapters.ports.rule_repository import RuleRepository
from entities.rule import Rule
from entities.transaction import Transaction


class RuleEngine:
    """Engine to match and apply categorization rules to transactions."""

    def __init__(self, rule_repo: RuleRepository):
        """Initialize with rule repository."""
        self.rule_repo = rule_repo

    def apply_rules(self, transaction: Transaction, user_id: UUID) -> Transaction:
        """
        Apply categorization/assignment rules to a transaction.

        Rules are matched in priority order (highest first).
        Only the first matching rule is applied.
        Can assign either a category or a savings goal, but not both.

        Args:
            transaction: Transaction to categorize/assign
            user_id: User ID to filter rules

        Returns:
            Updated transaction with category_id or savings_goal_id set if rule matched
        """
        # Skip if already categorized/savings or is internal
        if transaction.category_id or transaction.savings_goal_id or transaction.is_internal:
            return transaction

        # Get active rules for user, sorted by priority (descending)
        rules = self.rule_repo.read(user_id=user_id, is_active=True)
        rules = sorted(rules, key=lambda r: r.priority, reverse=True)

        # Try each rule in priority order
        for rule in rules:
            if self._matches_rule(transaction, rule):
                # Apply category if rule has one
                if rule.category_id:
                    transaction.category_id = rule.category_id
                # Apply savings goal if rule has one
                elif rule.savings_goal_id:
                    transaction.savings_goal_id = rule.savings_goal_id
                return transaction

        return transaction

    def _matches_rule(self, transaction: Transaction, rule: Rule) -> bool:
        """
        Check if a transaction matches a rule.

        A transaction matches if ANY of the conditions are met (OR logic):
        - Keywords in label
        - Regex pattern matches label
        - Amount is within range

        Args:
            transaction: Transaction to check
            rule: Rule to match against

        Returns:
            True if transaction matches rule
        """
        label = transaction.label.lower() if transaction.label else ""
        amount = float(transaction.amount)

        # Check keywords
        if rule.keywords:
            for keyword in rule.keywords:
                if keyword.lower() in label:
                    return True

        # Check regex pattern
        if rule.regex_pattern:
            try:
                if re.search(rule.regex_pattern, label, re.IGNORECASE):
                    return True
            except re.error:
                # Skip invalid regex patterns
                pass

        # Check amount range
        min_match = rule.min_amount is None or amount >= rule.min_amount
        max_match = rule.max_amount is None or amount <= rule.max_amount
        if min_match and max_match:
            # Both min and max exist, so this is an AND condition
            if rule.min_amount is not None and rule.max_amount is not None:
                return True

        return False
