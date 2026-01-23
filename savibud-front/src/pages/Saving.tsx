import { Heading , Button, Card } from '@soilhat/react-components';
import { 
  PlusIcon, 
  FlagIcon, 
  ArrowTrendingUpIcon, 
  EllipsisHorizontalIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';

export const SavingsPage = () => {
  const meta = [
    { key: 'total', value: '€22,450.00 Total Saved', svg: <FlagIcon className="h-4 w-4" /> },
    { key: 'monthly', value: '€1,200.00/mo pacing', svg: <ArrowTrendingUpIcon className="h-4 w-4" /> },
  ];

  return (
    <div className="min-h-screen bg-surface-base dark:bg-surface-base-dark transition-colors duration-200">
      <Heading title="Savings Goals" variant="page" meta={meta}>
        <Button size="small" leftIcon={<PlusIcon className="h-4 w-4" />}>
          Create Goal
        </Button>
      </Heading>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <GoalCard 
            title="House Deposit" 
            current={18500} 
            target={50000} 
            color="bg-primary"
            icon="🏠"
          />
          <GoalCard 
            title="Emergency Fund" 
            current={3200} 
            target={10000} 
            color="bg-state-success"
            icon="🛡️"
          />
          <GoalCard 
            title="Summer Trip" 
            current={750} 
            target={2500} 
            color="bg-state-warning"
            icon="✈️"
          />
        </div>
      </main>
    </div>
  );
};

const GoalCard = ({ title, current, target, color, icon }: any) => {
  const progress = Math.min((current / target) * 100, 100);

  return (
    <Card>
      <div className="flex justify-between items-start mb-4">
        <div className="text-3xl">{icon}</div>
        <Button variant="ghost" color_name="light" className="p-1">
          <EllipsisHorizontalIcon className="h-5 w-5" />
        </Button>
      </div>
      
      <h3 className="text-lg font-bold text-text-primary dark:text-text-primary-dark mb-1">{title}</h3>
      <p className="text-sm text-text-secondary dark:text-text-secondary-dark mb-6">
        €{current.toLocaleString()} of €{target.toLocaleString()}
      </p>

      <div className="relative w-full h-3 bg-surface-base dark:bg-surface-base-dark rounded-full overflow-hidden mb-4">
        <div 
          className={`absolute top-0 left-0 h-full ${color} transition-all duration-500`} 
          style={{ width: `${progress}%` }} 
        />
      </div>

      <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary dark:text-text-secondary-dark">
        <CalendarDaysIcon className="h-4 w-4" />
        <span>Next Auto-save: €250.00</span>
      </div>
    </Card>
  );
};

export default SavingsPage;