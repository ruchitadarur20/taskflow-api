export const useDueDateBadge = (dueDate?: string) => {
  if (!dueDate) return null
  const due = new Date(dueDate)
  const now = new Date()
  const diffDays = (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)

  if (diffDays < 0) return { label: 'Overdue', className: 'bg-red-100 text-red-700' }
  if (diffDays <= 3) return { label: 'Due soon', className: 'bg-yellow-100 text-yellow-700' }
  return { label: due.toLocaleDateString(), className: 'bg-green-100 text-green-700' }
}
