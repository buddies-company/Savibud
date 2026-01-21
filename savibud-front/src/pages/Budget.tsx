import { useEffect, useState, useMemo } from 'react';
import {
  Heading,
  Button,
  Modal,
  Input,
  Card,
  CategoryTree,
  SearchableCombobox,
  Select
} from '@soilhat/react-components';
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  LockClosedIcon,
  FolderIcon,
  TagIcon,
  BanknotesIcon,
  ExclamationTriangleIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import * as Icons from '@heroicons/react/24/outline';
import { BudgetEntry, Category } from '../utils/constants/types';
import { callApi } from '../services/api';
import { DynamicHeroIcon } from '../components/DynamicHeroIcon';


export default function BudgetPlanningPage() {
  const [activeTab, setActiveTab] = useState('expenses');
  const [modalMode, setModalMode] = useState<'none' | 'category' | 'budget' | 'delete-cat' | 'delete-budget'>('none');
  const [isLoading, setIsLoading] = useState(false);
  const [iconSearch, setIconSearch] = useState('');

  // Data States
  const [categories, setCategories] = useState<Category[]>([]);
  const [budgets, setBudgets] = useState<BudgetEntry[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);

  const fetchData = async () => {
    const [catRes, budRes] = await Promise.all([
      callApi<Category[]>("/categories", "GET"),
      callApi<BudgetEntry[]>("/budgets", "GET")
    ]);
    setCategories(catRes.data);
    setBudgets(budRes.data);
  };

  useEffect(() => { fetchData(); }, []);

  const handleClose = () => {
    setModalMode('none');
    setSelectedItem(null);
    setIconSearch('');
  };

  /**
   * Logic: Resolve which icon to show.
   * 1. Category's own icon
   * 2. Parent's icon (recursive)
   * 3. Default TagIcon
   */
  const getInheritedIcon = (item: any): string => {
    if (item?.icon) return item.icon;
    if (item?.parent_id) {
      const parent = categories.find((c) => c.id === item.parent_id);
      if (parent) return getInheritedIcon(parent);
    }
    return 'TagIcon';
  };

  /**
   * Icon Picker Logic: Filter the list of available HeroIcons
   */
  const filteredIconNames = useMemo(() => {
    const allNames = Object.keys(Icons).filter(name => name.endsWith('Icon'));
    if (!iconSearch) return allNames.slice(0, 28); 
    return allNames
      .filter(name => name.toLowerCase().includes(iconSearch.toLowerCase()))
      .slice(0, 28);
  }, [iconSearch]);

  const handleSaveCategory = async () => {
    setIsLoading(true);
    const isEdit = !!selectedItem?.id;
    const url = isEdit ? `/categories/${selectedItem.id}` : "/categories";
    try {
      const payload = {
        ...selectedItem,
        parent_id: selectedItem.parent_id === 'none' ? null : selectedItem.parent_id,
        icon: selectedItem.icon || null
      };
      await callApi(url, isEdit ? "PUT" : "POST", undefined, payload);
      await fetchData();
      handleClose();
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveBudget = async () => {
    setIsLoading(true);
    const isEdit = !!selectedItem?.id;
    const url = isEdit ? `/budgets/${selectedItem.id}` : "/budgets";
    try {
      await callApi(url, isEdit ? "PUT" : "POST", undefined, selectedItem);
      await fetchData();
      handleClose();
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    const type = modalMode === 'delete-cat' ? 'categories' : 'budgets';
    try {
      await callApi(`/${type}/${selectedItem.id}`, "DELETE");
      await fetchData();
      handleClose();
    } finally {
      setIsLoading(false);
    }
  };

  const filteredBudgets = budgets.filter(b => b.category.is_income === (activeTab === 'income'));

  return (
    <div className="min-h-screen bg-surface-base dark:bg-surface-base-dark transition-colors duration-200">
      <Heading
        title="Planning"
        variant="page"
        filters={[
          { key: 'expenses', value: 'Expenses', active: activeTab === 'expenses', props: { onClick: () => setActiveTab('expenses') } },
          { key: 'income', value: 'Income', active: activeTab === 'income', props: { onClick: () => setActiveTab('income') } },
          { key: 'structure', value: 'Categories', active: activeTab === 'structure', props: { onClick: () => setActiveTab('structure') } },
        ]}
      >
        <Button variant="ghost" color_name="light" size="small" leftIcon={<FolderIcon className="h-4 w-4" />} onClick={() => { setSelectedItem({ name: '', color: '#3b82f6', is_income: false, parent_id: 'none', icon: '' }); setModalMode('category'); }}>
          New Category
        </Button>
        <Button size="small" leftIcon={<PlusIcon className="h-4 w-4" />} onClick={() => { setSelectedItem({ amount: 0, is_fixed: false }); setModalMode('budget'); }}>
          Add Budget
        </Button>
      </Heading>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'structure' ? (
          <Card className="max-w-2xl rounded-3xl bg-surface-card dark:bg-surface-card-dark border-border dark:border-border-dark shadow-xl">
            <Card.Header title="Category Structure" />
            <Card.Body>
              <CategoryTree
                items={categories}
                renderItem={(item, level, { isExpanded, toggle, hasChildren }) => (
                  <div className="group flex items-center justify-between p-3 hover:bg-surface-base/50 dark:hover:bg-surface-base-dark/50 rounded-2xl transition-all mb-1 border border-transparent hover:border-border dark:hover:border-border-dark">
                    <div className="flex items-center gap-4">
                      <button onClick={toggle} className={`p-1 rounded-lg hover:bg-surface-panel dark:hover:bg-surface-panel-dark ${!hasChildren && 'invisible'}`}>
                        {isExpanded ? <ChevronDownIcon className="h-4 w-4" /> : <ChevronRightIcon className="h-4 w-4" />}
                      </button>
                      
                      <div className="w-10 h-10 rounded-2xl flex items-center justify-center shadow-sm" style={{ backgroundColor: (item.color as string) || '#3b82f6' }}>
                        <DynamicHeroIcon iconName={getInheritedIcon(item)} className="h-5 w-5 text-white" />
                      </div>

                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-text-primary dark:text-text-primary-dark">{item.name as string}</span>
                        <span className="text-[10px] text-text-secondary dark:text-text-secondary-dark opacity-50 uppercase tracking-widest">{getInheritedIcon(item).replace('Icon', '')}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => { setSelectedItem(item); setModalMode('category'); }} className="p-2 text-text-secondary hover:text-primary dark:hover:text-primary-dark hover:bg-white dark:hover:bg-surface-panel-dark rounded-xl shadow-sm transition-all"><PencilSquareIcon className="h-4 w-4" /></button>
                      <button onClick={() => { setSelectedItem(item); setModalMode('delete-cat'); }} className="p-2 text-text-secondary hover:text-state-danger dark:hover:text-state-danger-dark hover:bg-white dark:hover:bg-surface-panel-dark rounded-xl shadow-sm transition-all"><TrashIcon className="h-4 w-4" /></button>
                    </div>
                  </div>
                )}
              />
            </Card.Body>
          </Card>
        ) : (
          <div className="bg-surface-card dark:bg-surface-card-dark rounded-3xl border border-border dark:border-border-dark shadow-sm overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-surface-base/50 dark:bg-surface-base-dark/50 border-b border-border dark:border-border-dark">
                <tr>
                  <th className="px-6 py-4 text-[10px] font-black uppercase text-text-secondary dark:text-text-secondary-dark tracking-widest">Category</th>
                  <th className="px-6 py-4 text-[10px] font-black uppercase text-text-secondary dark:text-text-secondary-dark tracking-widest text-right">Budgeted</th>
                  <th className="px-6 py-4 text-[10px] font-black uppercase text-text-secondary dark:text-text-secondary-dark tracking-widest text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border dark:divide-border-dark">
                {filteredBudgets.map(b => (
                  <tr key={b.id} className="group hover:bg-surface-base/30 dark:hover:bg-surface-base-dark/70 transition-colors">
                    <td className="px-6 py-4 flex items-center gap-4">
                      <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-sm" style={{ backgroundColor: b.category.color }}>
                        <DynamicHeroIcon iconName={getInheritedIcon(b.category)} className="h-5 w-5" />
                      </div>
                      <div>
                        <span className="font-bold text-sm text-text-primary dark:text-text-primary-dark">{b.category.name}</span>
                        {b.is_fixed && <div className="text-[10px] text-primary dark:text-primary-dark font-black uppercase flex items-center gap-1 mt-0.5"><LockClosedIcon className="h-2.5 w-2.5" /> Fixed Bill</div>}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-text-primary dark:text-text-primary-dark">€{Number(b.amount).toFixed(2)}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => { setSelectedItem(b); setModalMode('budget'); }} className="p-2 hover:bg-primary/10 rounded-full transition-colors text-text-primary dark:text-text-primary-dark"><PencilSquareIcon className="h-4 w-4" /></button>
                        <button onClick={() => { setSelectedItem(b); setModalMode('delete-budget'); }} className="p-2 hover:bg-state-danger/10 text-state-danger rounded-full transition-colors"><TrashIcon className="h-4 w-4" /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {/* --- CATEGORY MODAL --- */}
      <Modal open={modalMode === 'category'} onClose={handleClose}>
        <div className="p-6 bg-surface-card dark:bg-surface-card-dark rounded-3xl">
          <Heading title={selectedItem?.id ? "Edit Category" : "New Category"} variant="section" />
          
          {/* Dynamic Preview Circle */}
          <div className="flex flex-col items-center py-6 gap-2">
            <div className="w-20 h-20 rounded-[2.5rem] shadow-2xl flex items-center justify-center transition-all duration-300" style={{ backgroundColor: selectedItem?.color || '#3b82f6' }}>
              <DynamicHeroIcon iconName={getInheritedIcon(selectedItem)} className="h-10 w-10 text-white" />
            </div>
            <span className="text-[10px] font-black text-text-secondary dark:text-text-secondary-dark uppercase tracking-widest opacity-60">Visual Preview</span>
          </div>

          <div className="space-y-5">
            <Input label="Category Name" value={selectedItem?.name || ''} onChange={(e) => setSelectedItem({...selectedItem, name: e.target.value})} leftIcon={<TagIcon className="h-5 w-5" />} />
            
            <Select label="Parent Category" value={selectedItem?.parent_id || 'none'} onChange={(val) => setSelectedItem({...selectedItem, parent_id: val})} options={[{ value: 'none', label: 'None (Root Category)' }, ...categories.filter(c => c.id !== selectedItem?.id).map(c => ({ value: c.id, label: c.name }))]} />

            {/* Icon Selection Panel */}
            <div className="space-y-2">
              <div className="flex items-center justify-between px-1">
                <label className="text-[10px] font-black uppercase text-text-secondary dark:text-text-secondary-dark">Pick an Icon</label>
                {selectedItem?.icon && (
                  <button onClick={() => setSelectedItem({...selectedItem, icon: ''})} className="text-[10px] text-primary dark:text-primary-dark font-bold flex items-center gap-1">
                    <XMarkIcon className="h-3 w-3" /> Use Default/Inherited
                  </button>
                )}
              </div>
              <div className="p-3 bg-surface-base dark:bg-surface-base-dark rounded-2xl border border-border dark:border-border-dark space-y-3">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-4 w-4 text-text-secondary dark:text-text-secondary-dark" />
                  <input type="text" placeholder="Search HeroIcons..." className="w-full bg-transparent border-none focus:ring-0 text-sm pl-9 text-text-primary dark:text-text-primary-dark" value={iconSearch} onChange={(e) => setIconSearch(e.target.value)} />
                </div>
                <div className="grid grid-cols-7 gap-2 max-h-40 overflow-y-auto pr-1">
                  {filteredIconNames.map((name) => (
                    <button key={name} onClick={() => setSelectedItem({...selectedItem, icon: name})} className={`p-2 rounded-xl transition-all flex items-center justify-center ${selectedItem?.icon === name ? 'bg-primary text-white shadow-lg scale-110' : 'hover:bg-surface-panel dark:hover:bg-surface-panel-dark text-text-secondary dark:text-text-secondary-dark'}`}>
                      <DynamicHeroIcon iconName={name} className="h-5 w-5" />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input label="Theme Color" type="color" className="h-12" value={selectedItem?.color || '#3b82f6'} onChange={(e) => setSelectedItem({...selectedItem, color: e.target.value})} />
              <Input label="Income Category" type="checkbox" checked={selectedItem?.is_income} onChange={(e) => setSelectedItem({...selectedItem, is_income: e.target.checked})} hint="Tracks earnings" />
            </div>
          </div>

          <div className="flex gap-3 mt-8">
            <Button className="flex-1" onClick={handleSaveCategory} isLoading={isLoading}>Save Category</Button>
            <Button variant="ghost" color_name="light" className="flex-1" onClick={handleClose}>Cancel</Button>
          </div>
        </div>
      </Modal>

      {/* --- BUDGET MODAL --- */}
      <Modal open={modalMode === 'budget'} onClose={handleClose}>
        <div className="p-6 bg-surface-card dark:bg-surface-card-dark rounded-3xl">
          <Heading title={selectedItem?.id ? "Edit Budget" : "New Budget"} variant="section" />
          <div className="space-y-6 mt-6">
            <SearchableCombobox 
              label="Target Category"
              defaultValue={selectedItem?.category_id}
              options={categories.map(c => ({ value: c.id, label: c.name }))}
              onChange={(id) => setSelectedItem({...selectedItem, category_id: id})}
            />
            <Input label="Monthly Limit" type="number" value={selectedItem?.amount} onChange={(e) => setSelectedItem({...selectedItem, amount: e.target.value})} leftIcon={<BanknotesIcon className="h-5 w-5" />} />
            <Input type="checkbox" label="Mark as Fixed Bill" hint="Deducted immediately from monthly allowance." checked={selectedItem?.is_fixed} onChange={(e) => setSelectedItem({...selectedItem, is_fixed: e.target.checked})} />
          </div>
          <div className="flex gap-3 mt-8">
            <Button className="flex-1" onClick={handleSaveBudget} isLoading={isLoading}>Confirm Budget</Button>
            <Button variant="ghost" color_name="light" className="flex-1" onClick={handleClose}>Cancel</Button>
          </div>
        </div>
      </Modal>

      {/* --- DELETE MODAL --- */}
      <Modal open={modalMode === 'delete-cat' || modalMode === 'delete-budget'} onClose={handleClose}>
        <div className="p-8 text-center bg-surface-card dark:bg-surface-card-dark rounded-3xl">
          <div className="h-20 w-20 bg-state-danger/10 dark:bg-state-danger-dark/90 rounded-full flex items-center justify-center mx-auto mb-6">
            <ExclamationTriangleIcon className="h-10 w-10 text-state-danger dark:text-state-danger-dark" />
          </div>
          <h3 className="text-xl font-bold text-text-primary dark:text-text-primary-dark">Permanently delete?</h3>
          <p className="text-sm text-text-secondary dark:text-text-secondary-dark mt-3">This action will affect your historical reports and cannot be undone.</p>
          <div className="flex flex-col gap-3 mt-8">
            <Button color_name="danger" onClick={handleDelete} isLoading={isLoading}>Delete Permanently</Button>
            <Button variant="ghost" color_name="light" onClick={handleClose}>Keep and Go Back</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}