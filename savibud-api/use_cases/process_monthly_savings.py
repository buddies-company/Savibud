from datetime import date
from dateutil.relativedelta import relativedelta
from adapters.ports.saving_repository import SavingsGoalRepository


class ProcessMonthlySavings:
    """Use case to process monthly savings automations for all users."""

    def __init__(self, repo: SavingsGoalRepository):
        self.repo = repo

    def execute(self):
        """Process monthly savings automations for all users."""
        # 1. Fetch all users who have active automations
        # This keeps the Use Case unaware of HOW users are stored
        user_ids = self.repo.get_all_user_ids_with_automations()

        for user_id in user_ids:
            # 2. Get due automations specifically for this user
            automations = self.repo.get_due_automations(
                user_id=user_id, as_of_date=date.today()
            )

            for goal in automations:
                # 3. Create the virtual transaction
                self.repo.create_virtual_transaction(
                    user_id=user_id,
                    goal_id=goal.id,
                    amount=goal.automation_amount if goal.automation_amount else 0,
                    label=f"Auto-save: {goal.name}",  # Use name for better UX
                )

                # 4. Update the next run date
                new_date = self._calculate_next_date(
                    goal.automation_next_run_date, goal.automation_frequency
                )
                self.repo.update_automation_date(goal.id, new_date)

    def _calculate_next_date(self, current_date, frequency):
        mapping = {"monthly": 1, "trimestrial": 3, "quarterly": 3, "yearly": 12}
        months = mapping.get(frequency, 1)
        return current_date + relativedelta(months=months)
