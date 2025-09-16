import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { UserProfileButton } from './AuthComponents';
import { 
  Search, 
  Bell, 
  Settings, 
  LogOut, 
  User,
  BarChart3,
  Users,
  Briefcase
} from 'lucide-react';

export const ProfessionalHeader: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-red-600 flex items-center justify-center text-white text-sm font-bold shadow-sm border border-red-700 rounded-sm">
              人
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-semibold text-foreground">Milo</span>
              <span className="text-xs text-muted-foreground">AI Career Platform</span>
            </div>
          </div>
          
          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6 ml-8">
            <Button variant="ghost" size="sm" className="text-sm">
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
            <Button variant="ghost" size="sm" className="text-sm">
              <Users className="w-4 h-4 mr-2" />
              Alumni
            </Button>
            <Button variant="ghost" size="sm" className="text-sm">
              <Briefcase className="w-4 h-4 mr-2" />
              Opportunities
            </Button>
            <Button variant="ghost" size="sm" className="text-sm">
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </Button>
          </nav>
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center space-x-4">
          {/* Search Bar */}
          <div className="hidden lg:block">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <input
                type="text"
                placeholder="Search alumni, companies, roles..."
                className="pl-10 pr-4 py-2 w-64 text-sm border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
              />
            </div>
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="w-4 h-4" />
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              3
            </Badge>
          </Button>

          <Separator orientation="vertical" className="h-6" />

          {/* User Profile */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatars/01.png" alt="User" />
                  <AvatarFallback>GM</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">George McCain</p>
                  <p className="text-xs leading-none text-muted-foreground">
                    george@example.com
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};
