import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTask, updateTaskStatus, deleteTask } from '../api/tasks'
import type { Task } from '../types'
import Navbar from '../components/Navbar'
import CommentBox from '../components/CommentBox'
import { useDueDateBadge } from '../hooks/useDueDateBadge'

const statusOptions = ['todo', 'in_progress', 'done'] as const

export default function TaskDetailPage() {
  const { id, taskId } = useParams<{ id: string; taskId: string }>()
  const projectId = Number(id)
  const tId = Number(taskId)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: task, isLoading } = useQuery<Task>({
    queryKey: ['task', tId],
    queryFn: () => getTask(tId),
  })

  const statusMutation = useMutation({
    mutationFn: (status: string) => updateTaskStatus(tId, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['task', tId] }),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteTask(tId),
    onSuccess: () => navigate(`/projects/${projectId}`),
  })

  const dueBadge = useDueDateBadge(task?.due_date)

  if (isLoading) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto px-6 py-8 space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/2 animate-pulse" />
        <div className="h-4 bg-gray-100 rounded w-full animate-pulse" />
        <div className="h-4 bg-gray-100 rounded w-3/4 animate-pulse" />
      </div>
    </div>
  )

  if (!task) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto px-6 py-8">
        <button
          onClick={() => navigate(`/projects/${projectId}`)}
          className="text-sm text-gray-500 hover:text-indigo-600 mb-6 flex items-center gap-1"
        >
          ← Back to project
        </button>

        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm mb-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <h1 className="text-xl font-bold text-gray-800">{task.title}</h1>
            <button
              onClick={() => deleteMutation.mutate()}
              className="text-xs text-red-400 hover:text-red-600 shrink-0"
            >
              Delete
            </button>
          </div>

          {task.description && (
            <p className="text-gray-600 text-sm mb-4">{task.description}</p>
          )}

          <div className="flex flex-wrap items-center gap-3">
            {/* Status selector */}
            <select
              value={task.status}
              onChange={(e) => statusMutation.mutate(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {statusOptions.map((s) => (
                <option key={s} value={s}>
                  {s === 'todo' ? 'To Do' : s === 'in_progress' ? 'In Progress' : 'Done'}
                </option>
              ))}
            </select>

            {/* Due date badge */}
            {dueBadge && (
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${dueBadge.className}`}>
                {dueBadge.label}
              </span>
            )}

            {task.due_date && (
              <span className="text-xs text-gray-400">
                Due: {new Date(task.due_date).toLocaleString()}
              </span>
            )}
          </div>
        </div>

        {/* Comments */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <CommentBox taskId={tId} />
        </div>
      </div>
    </div>
  )
}
