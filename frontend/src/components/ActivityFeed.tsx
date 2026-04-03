import { useQuery } from '@tanstack/react-query'
import { getActivity } from '../api/projects'
import type { ActivityLog } from '../types'

export default function ActivityFeed({ projectId }: { projectId: number }) {
  const { data: logs = [], isLoading } = useQuery<ActivityLog[]>({
    queryKey: ['activity', projectId],
    queryFn: () => getActivity(projectId),
  })

  if (isLoading) return (
    <div className="space-y-2">
      {[1,2,3].map(i => <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />)}
    </div>
  )

  return (
    <div>
      <h3 className="font-semibold text-gray-700 mb-3">Activity</h3>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {logs.length === 0 && <p className="text-sm text-gray-400">No activity yet.</p>}
        {logs.map((log) => (
          <div key={log.id} className="text-xs text-gray-600 border-l-2 border-indigo-200 pl-3 py-1">
            <p className="font-medium">{log.action.replace(/_/g, ' ')}</p>
            {log.detail && <p className="text-gray-400">{log.detail}</p>}
            <p className="text-gray-300 mt-0.5">{new Date(log.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
