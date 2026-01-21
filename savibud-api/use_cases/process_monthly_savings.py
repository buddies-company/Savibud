from datetime import date

from dateutil.relativedelta import relativedelta

from adapters.ports.saving_repository import SavingsAutomationRepository


class ProcessMonthlySavings:
    def __init__(self, repo: SavingsAutomationRepository):
        self.repo = repo

    def execute(self):
        # 1. Get all active automations due today or earlier
        automations = self.repo.get_due_automations(date.today())

        for auto in automations:
            # 2. Create the virtual transaction
            self.repo.create_virtual_transaction(
                goal_id=auto.goal_id, amount=auto.amount, label=f"Auto-save: {auto.id}"
            )
            # 3. Update the next run date based on frequency
            new_date = self._calculate_next_date(auto.next_run_date, auto.frequency)
            self.repo.update_automation_date(auto.id, new_date)

    def _calculate_next_date(self, current_date, frequency):
        mapping = {"monthly": 1, "trimestrial": 3, "quarterly": 3, "yearly": 12}
        months = mapping.get(frequency, 1)
        return current_date + relativedelta(months=months)
