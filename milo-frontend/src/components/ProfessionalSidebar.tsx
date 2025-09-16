import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Search, 
  Users, 
  Briefcase, 
  BarChart3, 
  Settings, 
  Star,
  TrendingUp,
  Building2,
  GraduationCap,
  Target,
  MessageSquare
} from 'lucide-react';

interface ProfessionalSidebarProps {
  className?: string;
}

export const ProfessionalSidebar: React.FC<ProfessionalSidebarProps> = ({ className }) => {
  const navigationItems = [
    {
      title: "Search",
      icon: Search,
      href: "/search",
      badge: null
    },
    {
      title: "Alumni Network",
      icon: Users,
      href: "/alumni",
      badge: "39K"
    },
    {
      title: "Opportunities",
      icon: Briefcase,
      href: "/opportunities",
      badge: "2.1K"
    },
    {
      title: "Analytics",
      icon: BarChart3,
      href: "/analytics",
      badge: null
    },
    {
      title: "Trending",
      icon: TrendingUp,
      href: "/trending",
      badge: "Hot"
    }
  ];

  const quickActions = [
    {
      title: "Companies",
      icon: Building2,
      href: "/companies"
    },
    {
      title: "Majors",
      icon: GraduationCap,
      href: "/majors"
    },
    {
      title: "Goals",
      icon: Target,
      href: "/goals"
    },
    {
      title: "Chat",
      icon: MessageSquare,
      href: "/chat"
    }
  ];

  return (
    <div className={`flex h-full w-64 flex-col bg-background border-r ${className}`}>
      {/* Header */}
      <div className="flex h-16 items-center border-b px-6">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-red-600 flex items-center justify-center text-white text-xs font-bold shadow-sm border border-red-700 rounded-sm">
            人
          </div>
          <span className="text-lg font-semibold">Milo</span>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 overflow-auto py-4">
        <div className="px-3">
          <div className="space-y-1">
            {navigationItems.map((item) => (
              <Button
                key={item.title}
                variant="ghost"
                className="w-full justify-start text-sm h-9"
                asChild
              >
                <a href={item.href} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <item.icon className="mr-3 h-4 w-4" />
                    {item.title}
                  </div>
                  {item.badge && (
                    <Badge 
                      variant={item.badge === "Hot" ? "destructive" : "secondary"}
                      className="text-xs"
                    >
                      {item.badge}
                    </Badge>
                  )}
                </a>
              </Button>
            ))}
          </div>
        </div>

        <Separator className="my-4" />

        {/* Quick Actions */}
        <div className="px-3">
          <h3 className="mb-3 px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Quick Actions
          </h3>
          <div className="space-y-1">
            {quickActions.map((item) => (
              <Button
                key={item.title}
                variant="ghost"
                className="w-full justify-start text-sm h-8 text-muted-foreground hover:text-foreground"
                asChild
              >
                <a href={item.href} className="flex items-center">
                  <item.icon className="mr-3 h-4 w-4" />
                  {item.title}
                </a>
              </Button>
            ))}
          </div>
        </div>

        <Separator className="my-4" />

        {/* Favorites */}
        <div className="px-3">
          <h3 className="mb-3 px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Favorites
          </h3>
          <div className="space-y-1">
            <Button
              variant="ghost"
              className="w-full justify-start text-sm h-8 text-muted-foreground hover:text-foreground"
            >
              <Star className="mr-3 h-4 w-4" />
              Goldman Sachs
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-sm h-8 text-muted-foreground hover:text-foreground"
            >
              <Star className="mr-3 h-4 w-4" />
              McKinsey & Company
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-sm h-8 text-muted-foreground hover:text-foreground"
            >
              <Star className="mr-3 h-4 w-4" />
              Google
            </Button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t p-4">
        <Button variant="ghost" className="w-full justify-start text-sm">
          <Settings className="mr-3 h-4 w-4" />
          Settings
        </Button>
      </div>
    </div>
  );
};
