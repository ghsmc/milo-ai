import React from 'react';
import { Person } from '../types/milo';

interface PeopleTableProps {
  people: Person[];
  title?: string;
  maxRows?: number;
}

const PeopleTable: React.FC<PeopleTableProps> = ({ 
  people, 
  title = "Yale Alumni", 
  maxRows = 10 
}) => {
  if (!people || people.length === 0) {
    return null;
  }

  const displayPeople = people.slice(0, maxRows);

  const formatExperience = (person: Person) => {
    if (!person.experience_history || person.experience_history.length === 0) {
      return 'No experience data';
    }
    
    const currentRole = person.experience_history[0];
    const yearsExp = person.career_progression?.years_experience || 0;
    
    return `${currentRole.title} (${yearsExp} years exp)`;
  };

  const formatSkills = (person: Person) => {
    if (!person.key_skills || person.key_skills.length === 0) {
      return 'Not specified';
    }
    return person.key_skills.slice(0, 3).join(', ');
  };

  const getNetworkingScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getNetworkingScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Limited';
  };

  return (
    <div className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
      <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
        <h3 className="text-lg font-semibold text-white">
          {title} ({people.length} total)
        </h3>
        {maxRows < people.length && (
          <p className="text-sm text-gray-400 mt-1">
            Showing top {maxRows} results
          </p>
        )}
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-800 border-b border-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Name & Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Company & Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Education
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Experience
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Skills
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Network Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-gray-900 divide-y divide-gray-700">
            {displayPeople.map((person, index) => (
              <tr key={`${person.name}-${index}`} className="hover:bg-gray-800 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                        <span className="text-white font-semibold text-sm">
                          {person.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-white">
                        {person.name}
                      </div>
                      <div className="text-sm text-gray-400">
                        {person.position}
                      </div>
                    </div>
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-white font-medium">
                    {person.company}
                  </div>
                  <div className="text-sm text-gray-400">
                    {person.location}
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-white">
                    {person.major || 'Not specified'}
                  </div>
                  <div className="text-sm text-gray-400">
                    {person.degree && person.graduation_year !== 'XX' 
                      ? `${person.degree} '${person.graduation_year}`
                      : person.graduation_year !== 'XX' 
                        ? `'${person.graduation_year}`
                        : 'Graduation year unknown'
                    }
                  </div>
                </td>
                
                <td className="px-6 py-4">
                  <div className="text-sm text-white">
                    {formatExperience(person)}
                  </div>
                  <div className="text-sm text-gray-400">
                    {person.career_progression?.career_stage || 'Unknown stage'}
                  </div>
                </td>
                
                <td className="px-6 py-4">
                  <div className="text-sm text-white">
                    {formatSkills(person)}
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className={`text-sm font-medium ${getNetworkingScoreColor(person.networking_score || 0)}`}>
                      {person.networking_score || 0}/100
                    </span>
                    <span className="ml-2 text-xs text-gray-400">
                      ({getNetworkingScoreLabel(person.networking_score || 0)})
                    </span>
                  </div>
                </td>
                
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button className="text-blue-400 hover:text-blue-300 transition-colors">
                      Connect
                    </button>
                    <button className="text-green-400 hover:text-green-300 transition-colors">
                      Message
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {maxRows < people.length && (
        <div className="bg-gray-800 px-6 py-3 border-t border-gray-700">
          <p className="text-sm text-gray-400 text-center">
            ... and {people.length - maxRows} more alumni
          </p>
        </div>
      )}
    </div>
  );
};

export default PeopleTable;
