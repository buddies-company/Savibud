import { useState, useEffect } from 'react';
import { Button, Modal, Input, Card, Select } from '@soilhat/react-components';
import { PlusIcon, TrashIcon, PencilSquareIcon, CheckIcon } from '@heroicons/react/24/outline';
import { callApi } from '../services/api';
import { Rule, Category, SavingsGoal } from '../utils/constants/types';

export const RulesManager = ({ categories }: { categories: Category[] }) => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [savingsGoals, setSavingsGoals] = useState<SavingsGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [targetType, setTargetType] = useState<'category' | 'savings'>('category');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category_id: '',
    savings_goal_id: '',
    keywords: '',
    regex_pattern: '',
    min_amount: '',
    max_amount: '',
    priority: 100,
    is_active: true
  });

  const fetchRules = async () => {
    try {
      setLoading(true);
      const [rulesRes, goalsRes] = await Promise.all([
        callApi<Rule[]>("/rules", "GET"),
        callApi<SavingsGoal[]>("/savings_goals", "GET")
      ]);
      setRules(rulesRes.data);
      setSavingsGoals(goalsRes.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleCreateClick = () => {
    setEditingRule(null);
    setTargetType('category');
    setFormData({
      name: '',
      description: '',
      category_id: '',
      savings_goal_id: '',
      keywords: '',
      regex_pattern: '',
      min_amount: '',
      max_amount: '',
      priority: 100,
      is_active: true
    });
    setShowModal(true);
  };

  const handleEditClick = (rule: Rule) => {
    setEditingRule(rule);
    setTargetType(rule.category_id ? 'category' : 'savings');
    setFormData({
      name: rule.name,
      description: rule.description || '',
      category_id: rule.category_id || '',
      savings_goal_id: rule.savings_goal_id || '',
      keywords: rule.keywords?.join(', ') || '',
      regex_pattern: rule.regex_pattern || '',
      min_amount: rule.min_amount?.toString() || '',
      max_amount: rule.max_amount?.toString() || '',
      priority: rule.priority,
      is_active: rule.is_active
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!formData.name) {
      alert("Please fill in rule name");
      return;
    }

    if (targetType === 'category' && !formData.category_id) {
      alert("Please select a target category");
      return;
    }

    if (targetType === 'savings' && !formData.savings_goal_id) {
      alert("Please select a target savings goal");
      return;
    }

    try {
      const payload = {
        name: formData.name,
        description: formData.description,
        category_id: targetType === 'category' ? formData.category_id : null,
        savings_goal_id: targetType === 'savings' ? formData.savings_goal_id : null,
        keywords: formData.keywords
          .split(',')
          .map(k => k.trim())
          .filter(k => k),
        regex_pattern: formData.regex_pattern || null,
        min_amount: formData.min_amount ? Number(formData.min_amount) : null,
        max_amount: formData.max_amount ? Number(formData.max_amount) : null,
        priority: formData.priority,
        is_active: formData.is_active,
      };

      if (editingRule) {
        await callApi(`/rules/${editingRule.id}`, "PUT", undefined, payload);
      } else {
        await callApi("/rules", "POST", undefined, payload);
      }
      setShowModal(false);
      fetchRules();
    } catch (error) {
      console.error("Failed to save rule", error);
      alert("Failed to save rule");
    }
  };

  const handleDelete = async (ruleId: string) => {
    if (!confirm("Are you sure you want to delete this rule?")) return;
    try {
      await callApi(`/rules/${ruleId}`, "DELETE");
      fetchRules();
    } catch (error) {
      console.error("Failed to delete rule", error);
    }
  };

  const getTargetName = (rule: Rule) => {
    if (rule.category_id) {
      return `Category: ${categories.find(c => c.id === rule.category_id)?.name}`;
    }
    if (rule.savings_goal_id) {
      return `Savings Goal: ${savingsGoals.find(g => g.id === rule.savings_goal_id)?.name}`;
    }
    return 'Unknown Target';
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-bold text-text-primary dark:text-text-primary-dark">Categorization Rules</h2>
        <Button size="small" leftIcon={<PlusIcon className="h-4 w-4" />} onClick={handleCreateClick}>
          Add Rule
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin h-8 w-8 border-2 border-primary dark:border-primary-dark border-t-transparent rounded-full" />
        </div>
      ) : rules.length === 0 ? (
        <Card>
          <div className="text-center py-8">
            <p className="text-text-secondary dark:text-text-secondary-dark">No rules yet. Create your first rule to automatically categorize transactions.</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-2">
          {rules.map((rule) => (
            <Card key={rule.id} className="flex items-center justify-between p-4">
              <div className="flex-1">
                <h3 className="font-bold text-text-primary dark:text-text-primary-dark">{rule.name}</h3>
                <p className="text-xs text-text-secondary dark:text-text-secondary-dark mt-1">
                  {rule.description && <>{rule.description} • </>}
                  {getTargetName(rule)}
                  {rule.keywords && rule.keywords.length > 0 && <> • Keywords: {rule.keywords.join(', ')}</>}
                  {rule.regex_pattern && <> • Pattern: {rule.regex_pattern}</>}
                  {rule.min_amount || rule.max_amount ? <> • Amount: €{rule.min_amount || 0} - €{rule.max_amount || '∞'}</> : null}
                </p>
                <div className="flex gap-2 mt-2">
                  <span className={`text-[10px] font-bold px-2 py-1 rounded-lg ${rule.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                    {rule.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-1 rounded-lg bg-blue-100 text-blue-700">
                    Priority: {rule.priority}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" color_name="light" size="small" onClick={() => handleEditClick(rule)}>
                  <PencilSquareIcon className="h-4 w-4" />
                </Button>
                <Button variant="ghost" color_name="light" size="small" onClick={() => handleDelete(rule.id)}>
                  <TrashIcon className="h-4 w-4 text-state-danger dark:text-state-danger-dark" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal open={showModal} onClose={() => setShowModal(false)}>
        <div className="p-6 bg-surface-card dark:bg-surface-card-dark rounded-3xl space-y-4 w-full max-w-2xl">
          <h3 className="text-xl font-bold text-text-primary dark:text-text-primary-dark">
            {editingRule ? 'Edit Rule' : 'Create New Rule'}
          </h3>

          <div className="space-y-4">
            <Input
              label='Rule Name'
              name="Rule Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Spotify Subscription"
            />
            <Input
              label = "Description"
              name="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Optional description"
            />
            
            <div>
              <label className="text-sm font-bold text-text-primary dark:text-text-primary-dark mb-2 block">
                Assign To
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setTargetType('category')}
                  className={`flex-1 px-4 py-2 rounded-lg font-semibold transition-colors ${
                    targetType === 'category'
                      ? 'bg-primary text-white dark:bg-primary-dark'
                      : 'bg-surface-base dark:bg-surface-base-dark text-text-primary dark:text-text-primary-dark hover:bg-surface-panel dark:hover:bg-surface-panel-dark'
                  }`}
                >
                  Category
                </button>
                <button
                  onClick={() => setTargetType('savings')}
                  className={`flex-1 px-4 py-2 rounded-lg font-semibold transition-colors ${
                    targetType === 'savings'
                      ? 'bg-primary text-white dark:bg-primary-dark'
                      : 'bg-surface-base dark:bg-surface-base-dark text-text-primary dark:text-text-primary-dark hover:bg-surface-panel dark:hover:bg-surface-panel-dark'
                  }`}
                >
                  Savings Goal
                </button>
              </div>
            </div>

            {targetType === 'category' ? (
              <Select
                label="Target Category"
                value={formData.category_id}
                onChange={(val) => setFormData({ ...formData, category_id: val as string })}
                options={categories.map(cat => ({ value: cat.id, label: cat.name }))}
                placeholder="Select category..."
              />
            ) : (
              <Select
                label="Target Savings Goal"
                value={formData.savings_goal_id}
                onChange={(val) => setFormData({ ...formData, savings_goal_id: val as string })}
                options={savingsGoals.map(goal => ({ value: goal.id, label: goal.name }))}
                placeholder="Select savings goal..."
              />
            )}

            <Input
              label='Keywords (comma-separated)'
              name="Keywords (comma-separated)"
              value={formData.keywords}
              onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
              placeholder="e.g., spotify, netflix, amazon"
            />

            <Input
              label='Regex Pattern'
              name="Regex Pattern"
              value={formData.regex_pattern}
              onChange={(e) => setFormData({ ...formData, regex_pattern: e.target.value })}
              placeholder="e.g., .*grocery.*"
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Min Amount (€)"
                name="Min Amount (€)"
                type="number"
                value={formData.min_amount}
                onChange={(e) => setFormData({ ...formData, min_amount: e.target.value })}
                placeholder="0.00"
              />
              <Input
                label="Max Amount (€)"
                name="Max Amount (€)"
                type="number"
                value={formData.max_amount}
                onChange={(e) => setFormData({ ...formData, max_amount: e.target.value })}
                placeholder="1000.00"
              />
            </div>

            <Input
              label="Priority (higher first)"
              name="Priority (higher first)"
              type="number"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: Number(e.target.value) })}
            />

            <div className="flex items-center gap-2">
              <Input
                label="Active"
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4 border-t border-border dark:border-border-dark">
            <Button variant="ghost" color_name="light" onClick={() => setShowModal(false)} className="flex-1">
              Cancel
            </Button>
            <Button 
              className="flex-1"
              onClick={handleSave}
              leftIcon={<CheckIcon className="h-4 w-4" />}
            >
              {editingRule ? 'Update' : 'Create'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
