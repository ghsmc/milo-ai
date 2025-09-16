import React, { useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { ProfessionalLayout } from './components/ProfessionalLayout';
import { ProfessionalSearch } from './components/ProfessionalSearch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  Building2, 
  TrendingUp, 
  Star,
  MapPin,
  Calendar,
  ArrowRight,
  BarChart3
} from 'lucide-react';

export const AppProfessional: React.FC = () => {
  const { user } = useUser();
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data for demonstration
  const stats = [
    { label: 'Total Alumni', value: '39,363', icon: Users, change: '+2.1%' },
    { label: 'Companies', value: '1,247', icon: Building2, change: '+5.3%' },
    { label: 'Active Opportunities', value: '2,156', icon: TrendingUp, change: '+12.4%' },
    { label: 'Success Rate', value: '87%', icon: Star, change: '+3.2%' }
  ];

  const recentActivity = [
    {
      type: 'New Alumni',
      description: 'Sarah Chen joined Goldman Sachs as Investment Banking Analyst',
      time: '2 hours ago',
      avatar: 'SC'
    },
    {
      type: 'Opportunity',
      description: 'Google posted 3 new Software Engineer positions',
      time: '4 hours ago',
      avatar: 'G'
    },
    {
      type: 'Connection',
      description: 'Michael Rodriguez connected with 5 alumni at McKinsey',
      time: '6 hours ago',
      avatar: 'MR'
    }
  ];

  const topCompanies = [
    { name: 'Goldman Sachs', alumni: 245, growth: '+8%' },
    { name: 'Google', alumni: 189, growth: '+12%' },
    { name: 'McKinsey & Company', alumni: 156, growth: '+5%' },
    { name: 'Microsoft', alumni: 134, growth: '+15%' },
    { name: 'JP Morgan', alumni: 128, growth: '+3%' }
  ];

  return (
    <ProfessionalLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Welcome back, {user?.firstName || 'User'}!
            </h1>
            <p className="text-muted-foreground">
              Here's what's happening in your network today.
            </p>
          </div>
          <Button>
            <BarChart3 className="w-4 h-4 mr-2" />
            View Analytics
          </Button>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.label}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">{stat.change}</span> from last month
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="search">Search</TabsTrigger>
            <TabsTrigger value="network">Network</TabsTrigger>
            <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentActivity.map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
                          {activity.avatar}
                        </div>
                        <div className="flex-1 space-y-1">
                          <p className="text-sm font-medium">{activity.description}</p>
                          <p className="text-xs text-muted-foreground">{activity.time}</p>
                        </div>
                        <Badge variant="outline">{activity.type}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Top Companies */}
              <Card>
                <CardHeader>
                  <CardTitle>Top Companies</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {topCompanies.map((company, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
                            {company.name.charAt(0)}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{company.name}</p>
                            <p className="text-xs text-muted-foreground">{company.alumni} alumni</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant="secondary" className="text-green-600">
                            {company.growth}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="search">
            <ProfessionalSearch />
          </TabsContent>

          <TabsContent value="network" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Your Network</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Network features coming soon...
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="opportunities" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Opportunities</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Opportunity matching coming soon...
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </ProfessionalLayout>
  );
};
