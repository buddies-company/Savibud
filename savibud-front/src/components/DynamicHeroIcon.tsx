// Import all icons for dynamic string-based lookup
import * as Icons from '@heroicons/react/24/outline';

/**
 * Helper to render HeroIcons from a string
 */
export const DynamicHeroIcon = ({ iconName, className }: { iconName: string; className?: string }) => {
  const IconComponent = (Icons as any)[iconName] || Icons.TagIcon;
  return <IconComponent className={className} />;
};