import { useNavigate } from 'react-router-dom'
import type { Task } from '../types'
import { useDueDateBadge } from '../hooks/useDueDateBadge'

const statusColors: Record<string, string> = {
  todo: 'bg-gray-100 text-gray-600',
  in_progress: 'bg-blue-100 text-blue-700',
  done: 'bg-green-100 text-green-700',
}

const statusLabels: Record<string, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  done: 'Done',
}

export default function TaskCard({ task }: { task: Task }) {
  const navigate = useNavigate()
  const dueBadge = useDueDateBadge(task.due_date)

  return (
    <div
      onClick={() => navigate(`/projects/${task.project_id}/tasks/${task.id}`)}
      className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md hover:border-indigo-300 transition"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-gray-800 text-sm">{task.title}</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${statusColors[task.status]}`}>
          {statusLabels[task.status]}
        </span>
      </div>
      {task.description && (
        <p className="text-xs text-gray-500 mt-1 line-clamp-2">{task.description}</p>
      )}
      {dueBadge && (
        <span className={`inline-block mt-2 text-xs px-2 py-0.5 rounded-full font-medium ${dueBadge.className}`}>
          {dueBadge.label}
        </span>
      )}
    </div>
  )
}
