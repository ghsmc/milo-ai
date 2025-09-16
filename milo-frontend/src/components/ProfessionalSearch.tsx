import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  Filter, 
  Users, 
  Building2, 
  MapPin, 
  Calendar,
  TrendingUp,
  Star
} from 'lucide-react';

export const ProfessionalSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const recentSearches = [
    "Software Engineer at Google",
    "Investment Banking Analyst",
    "Consultant at McKinsey",
    "Product Manager",
    "Data Scientist"
  ];

  const trendingSearches = [
    { query: "AI/ML Engineer", count: "2.3K alumni" },
    { query: "Investment Banking", count: "1.8K alumni" },
    { query: "Product Management", count: "1.5K alumni" },
    { query: "Consulting", count: "1.2K alumni" },
    { query: "Quantitative Finance", count: "980 alumni" }
  ];

  const featuredCompanies = [
    { name: "Goldman Sachs", alumni: "245", logo: "🏦" },
    { name: "Google", alumni: "189", logo: "🔍" },
    { name: "McKinsey & Company", alumni: "156", logo: "💼" },
    { name: "Microsoft", alumni: "134", logo: "🪟" },
    { name: "JP Morgan", alumni: "128", logo: "🏛️" }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Main Search Bar */}
      <Card className="border-2">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
              <Input
                type="text"
                placeholder="Search alumni, companies, roles, or skills..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 h-12 text-lg border-2 focus:border-red-500"
              />
            </div>
            <Button size="lg" className="h-12 px-8">
              <Search className="w-5 h-5 mr-2" />
              Search
            </Button>
            <Button variant="outline" size="lg" className="h-12">
              <Filter className="w-5 h-5 mr-2" />
              Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Search Tabs */}
      <Tabs defaultValue="trending" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="trending">Trending</TabsTrigger>
          <TabsTrigger value="recent">Recent</TabsTrigger>
          <TabsTrigger value="companies">Companies</TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
        </TabsList>

        <TabsContent value="trending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Trending Searches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {trendingSearches.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors">
                    <div className="flex items-center">
                      <Badge variant="outline" className="mr-3">
                        #{index + 1}
                      </Badge>
                      <span className="font-medium">{item.query}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{item.count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Searches</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {recentSearches.map((search, index) => (
                  <div key={index} className="flex items-center justify-between p-2 rounded hover:bg-muted/50 cursor-pointer">
                    <span className="text-sm">{search}</span>
                    <Button variant="ghost" size="sm">
                      <Search className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="companies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Building2 className="w-5 h-5 mr-2" />
                Featured Companies
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {featuredCompanies.map((company, index) => (
                  <div key={index} className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors">
                    <div className="flex items-center">
                      <span className="text-2xl mr-3">{company.logo}</span>
                      <div>
                        <div className="font-medium">{company.name}</div>
                        <div className="text-sm text-muted-foreground">{company.alumni} Yale alumni</div>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Users className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Popular Roles</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  "Software Engineer", "Investment Banking Analyst", "Consultant",
                  "Product Manager", "Data Scientist", "Quantitative Analyst",
                  "Strategy Associate", "Business Analyst", "Research Scientist"
                ].map((role, index) => (
                  <Button key={index} variant="outline" className="h-auto p-3 text-left justify-start">
                    <div>
                      <div className="font-medium text-sm">{role}</div>
                      <div className="text-xs text-muted-foreground">View alumni</div>
                    </div>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
