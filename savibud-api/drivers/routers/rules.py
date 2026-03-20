"""Rules management endpoints for automatic categorization."""

from fastapi import APIRouter, Depends

from adapters.ports.rule_repository import RuleRepository
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from entities.rule import Rule, RuleRead
from entities.user import User

router = APIRouter(prefix="/rules")


@router.get("", response_model=list[RuleRead])
def list_rules(
    user: User = Depends(connected_user),
    rule_repo: RuleRepository = Depends(get_repository("rule")),
):
    """List all rules for the authenticated user."""
    return rule_repo.read(user_id=user.id)


@router.post("", status_code=201, response_model=RuleRead)
def create_rule(
    rule: Rule,
    user: User = Depends(connected_user),
    rule_repo: RuleRepository = Depends(get_repository("rule")),
):
    """
    Create a new rule for the authenticated user.
    
    Must provide either category_id OR savings_goal_id (not both, not neither).
    """
    # Validate that at least one target is provided
    if not rule.category_id and not rule.savings_goal_id:
        raise ValueError("Rule must target either a category or a savings goal")
    
    # Validate that not both are provided
    if rule.category_id and rule.savings_goal_id:
        raise ValueError("Rule cannot target both a category and a savings goal")
    
    rule.user_id = user.id
    return rule_repo.create(rule)


@router.get("/{rule_id}", response_model=RuleRead)
def get_rule(
    rule_id: str,
    user: User = Depends(connected_user),
    rule_repo: RuleRepository = Depends(get_repository("rule")),
):
    """Get a specific rule by ID."""
    rule = rule_repo.read(user_id=user.id, id=rule_id)
    if not rule:
        raise PermissionError("Access denied")
    return rule[0]


@router.put("/{rule_id}", response_model=RuleRead)
def update_rule(
    rule_id: str,
    rule_data: Rule,
    user: User = Depends(connected_user),
    rule_repo: RuleRepository = Depends(get_repository("rule")),
):
    """
    Update a rule.
    
    Must have either category_id OR savings_goal_id (not both, not neither).
    """
    rule = rule_repo.read(user_id=user.id, id=rule_id)
    if not rule:
        raise PermissionError("Access denied")
    
    # Validate that at least one target is provided
    if not rule_data.category_id and not rule_data.savings_goal_id:
        raise ValueError("Rule must target either a category or a savings goal")
    
    # Validate that not both are provided
    if rule_data.category_id and rule_data.savings_goal_id:
        raise ValueError("Rule cannot target both a category and a savings goal")
    
    return rule_repo.update(
        rule_id,
        **rule_data.model_dump(exclude_unset=True, exclude={"user_id"})
    )


@router.delete("/{rule_id}")
def delete_rule(
    rule_id: str,
    user: User = Depends(connected_user),
    rule_repo: RuleRepository = Depends(get_repository("rule")),
):
    """Delete a rule."""
    rule = rule_repo.read(user_id=user.id, id=rule_id)
    if not rule:
        raise PermissionError("Access denied")
    
    rule_repo.delete(rule[0])
    return {"message": "Rule deleted"}
