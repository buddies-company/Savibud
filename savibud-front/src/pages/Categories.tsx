import { useState } from 'react';
import { Button, Modal } from '@soilhat/react-components';
import { 
  FolderIcon, TagIcon } from '@heroicons/react/24/outline';

const CategoryForm = ({ categories, onSubmit, initialData }: any) => {
  const [formData, setFormData] = useState(initialData || {
    name: '',
    parent_id: '',
    color: '#3b82f6',
    icon: 'TagIcon',
    is_income: false
  });

  // Filter out sub-categories to only show potential parents (Level 1)
  const potentialParents = categories.filter((c: any) => !c.parent_id);

  return (
    <div className="space-y-5">
      {/* Name Input */}
      <div>
        <label className="block text-xs font-bold text-text-secondary uppercase tracking-wider mb-2">
          Category Name
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <TagIcon className="h-5 w-5 text-text-secondary" />
          </div>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="block w-full pl-10 pr-3 py-2.5 bg-surface-base dark:bg-surface-base-dark border border-border dark:border-border-dark rounded-xl text-text-primary dark:text-text-primary-dark focus:ring-2 focus:ring-primary outline-none transition-all"
            placeholder="e.g. Groceries or Salary"
          />
        </div>
      </div>

      {/* Parent Selection (Nesting) */}
      <div>
        <label className="block text-xs font-bold text-text-secondary uppercase tracking-wider mb-2">
          Nest Under (Optional)
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <FolderIcon className="h-5 w-5 text-text-secondary" />
          </div>
          <select
            value={formData.parent_id}
            onChange={(e) => setFormData({...formData, parent_id: e.target.value})}
            className="block w-full pl-10 pr-3 py-2.5 bg-surface-base dark:bg-surface-base-dark border border-border dark:border-border-dark rounded-xl text-text-primary dark:text-text-primary-dark focus:ring-2 focus:ring-primary outline-none appearance-none"
          >
            <option value="">Main Category (No Parent)</option>
            {potentialParents.map((parent: any) => (
              <option key={parent.id} value={parent.id}>{parent.name}</option>
            ))}
          </select>
        </div>
        <p className="mt-2 text-xs text-text-secondary">Sub-categories help group spending (e.g. "Apples" under "Groceries").</p>
      </div>

      {/* Color & Icon Row */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-bold text-text-secondary uppercase tracking-wider mb-2">Theme Color</label>
          <input 
            type="color" 
            value={formData.color}
            onChange={(e) => setFormData({...formData, color: e.target.value})}
            className="h-10 w-full rounded-lg cursor-pointer bg-surface-base dark:bg-surface-base-dark border border-border dark:border-border-dark p-1" 
          />
        </div>
        <div>
           <label className="block text-xs font-bold text-text-secondary uppercase tracking-wider mb-2">Type</label>
           <div className="flex bg-surface-base dark:bg-surface-base-dark rounded-lg p-1 border border-border dark:border-border-dark">
              <button 
                onClick={() => setFormData({...formData, is_income: false})}
                className={`flex-1 py-1 text-xs font-bold rounded-md transition-all ${!formData.is_income ? 'bg-primary text-white' : 'text-text-secondary'}`}
              >Expense</button>
              <button 
                onClick={() => setFormData({...formData, is_income: true})}
                className={`flex-1 py-1 text-xs font-bold rounded-md transition-all ${formData.is_income ? 'bg-state-success text-white' : 'text-text-secondary'}`}
              >Income</button>
           </div>
        </div>
      </div>
    </div>
  );
};

const CategoryManagement = ({ categories, isOpen, onClose }: any) => {
  return (
    <Modal open={isOpen} onClose={onClose}>
      {/* Header logic (handled inside the Modal body) */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-text-primary dark:text-text-primary-dark">Manage Category</h2>
        <p className="text-sm text-text-secondary">Define how transactions are grouped in your budget.</p>
      </div>

      <CategoryForm categories={categories} />

      <Modal.Footer>
        <Button onClick={() => console.log('Save')} size="small">
          Save Category
        </Button>
        <Button variant="ghost" color_name="light" size="small" onClick={onClose}>
          Cancel
        </Button>
      </Modal.Footer>
    </Modal>
  );
};
