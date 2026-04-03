import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTasks, createTask } from '../api/tasks'
import type { Task } from '../types'
import Navbar from '../components/Navbar'
import TaskCard from '../components/TaskCard'
import ActivityFeed from '../components/ActivityFeed'

function TaskSkeleton() {
  return <div className="bg-gray-100 rounded-lg h-20 animate-pulse" />
}

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const projectId = Number(id)
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [dueDate, setDueDate] = useState('')
  const queryClient = useQueryClient()

  const { data: tasks = [], isLoading } = useQuery<Task[]>({
    queryKey: ['tasks', projectId],
    queryFn: () => getTasks(projectId),
  })

  const createMutation = useMutation({
    mutationFn: () => createTask(projectId, {
      title,
      description: description || undefined,
      due_date: dueDate || undefined,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] })
      queryClient.invalidateQueries({ queryKey: ['activity', projectId] })
      setTitle('')
      setDescription('')
      setDueDate('')
      setShowForm(false)
    },
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-6 py-8 flex gap-6">
        {/* Main content */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-800">Tasks</h1>
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
            >
              + New Task
            </button>
          </div>

          {showForm && (
            <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6 shadow-sm">
              <h2 className="font-semibold text-gray-700 mb-4">Create New Task</h2>
              <div className="space-y-3">
                <input
                  value={title} onChange={(e) => setTitle(e.target.value)}
                  placeholder="Task title"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <textarea
                  value={description} onChange={(e) => setDescription(e.target.value)}
                  placeholder="Description (optional)"
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <input
                  type="datetime-local" value={dueDate} onChange={(e) => setDueDate(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => createMutation.mutate()}
                    disabled={!title.trim()}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
                  >
                    Create Task
                  </button>
                  <button onClick={() => setShowForm(false)} className="text-sm text-gray-500 hover:text-gray-700">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => <TaskSkeleton key={i} />)}
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <p className="text-4xl mb-3">✅</p>
              <p className="font-medium">No tasks yet</p>
              <p className="text-sm mt-1">Add your first task to get started!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => <TaskCard key={task.id} task={task} />)}
            </div>
          )}
        </div>

        {/* Activity sidebar */}
        <div className="w-72 shrink-0">
          <div className="bg-white border border-gray-200 rounded-xl p-5 sticky top-6">
            <ActivityFeed projectId={projectId} />
          </div>
        </div>
      </div>
    </div>
  )
}
