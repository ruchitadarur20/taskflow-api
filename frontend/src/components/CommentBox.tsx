import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getComments, addComment, deleteComment } from '../api/comments'
import { useAuthStore } from '../store/authStore'
import type { Comment } from '../types'

export default function CommentBox({ taskId }: { taskId: number }) {
  const [content, setContent] = useState('')
  const queryClient = useQueryClient()
  const user = useAuthStore((s) => s.user)

  const { data: comments = [], isLoading } = useQuery<Comment[]>({
    queryKey: ['comments', taskId],
    queryFn: () => getComments(taskId),
  })

  const addMutation = useMutation({
    mutationFn: () => addComment(taskId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', taskId] })
      setContent('')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (commentId: number) => deleteComment(taskId, commentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['comments', taskId] }),
  })

  if (isLoading) return <CommentSkeleton />

  return (
    <div>
      <h3 className="font-semibold text-gray-700 mb-3">Comments ({comments.length})</h3>
      <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
        {comments.length === 0 && (
          <p className="text-sm text-gray-400">No comments yet. Be the first!</p>
        )}
        {comments.map((c) => (
          <div key={c.id} className="bg-gray-50 rounded-lg p-3 text-sm">
            <div className="flex justify-between items-start">
              <p className="text-gray-800">{c.content}</p>
              {user?.id === c.author_id && (
                <button
                  onClick={() => deleteMutation.mutate(c.id)}
                  className="text-gray-400 hover:text-red-500 ml-2 text-xs shrink-0"
                >
                  Delete
                </button>
              )}
            </div>
            <p className="text-xs text-gray-400 mt-1">{new Date(c.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && content.trim() && addMutation.mutate()}
          placeholder="Add a comment..."
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <button
          onClick={() => addMutation.mutate()}
          disabled={!content.trim()}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
        >
          Post
        </button>
      </div>
    </div>
  )
}

function CommentSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2].map((i) => (
        <div key={i} className="bg-gray-100 rounded-lg p-3 animate-pulse h-14" />
      ))}
    </div>
  )
}
