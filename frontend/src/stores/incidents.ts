import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Incident {
  incident_id: string
  status: string
  created_at: string
  resolved_at?: string
  alert: {
    alert_type?: string
    severity?: string
    message?: string
    affected_services?: string[]
    metrics?: Record<string, any>
    source_system?: string
    environment?: string
    timestamp?: string
  }
  classification: {
    category?: string
    severity?: string
    confidence?: number
    tags?: string[]
    estimated_impact?: string
    reasoning?: string
  }
  resolution: {
    recommended_steps: Array<{
      step_number: number
      description: string
      command?: string
      expected_result: string
      automation_possible: boolean
      risk_level: string
      rollback_command?: string
    }>
    estimated_time_minutes: number
    success_probability: number
    human_approval_required: boolean
    parallel_actions: string[]
    rollback_plan: string[]
    prerequisites: string[]
    reasoning: string
  }
  timeline: Array<{
    timestamp: string
    event: string
    details: any
  }>
  postmortem?: {
    summary: string
    root_cause: string
    lessons_learned: string[]
    action_items: string[]
    agent_performance: Record<string, any>
    recommendations: string[]
    markdown_report: string
  }
}

export const useIncidentStore = defineStore('incidents', () => {
  const incidents = ref<Incident[]>([])
  const activeIncidents = ref<Incident[]>([])
  const resolvedIncidents = ref<Incident[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`

  const fetchIncidents = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Fetch active and completed separately to match backend
      const [activeRes, completedRes] = await Promise.all([
        fetch(`${API_BASE}/incidents/active`),
        fetch(`${API_BASE}/incidents/completed`)
      ])

      if (!activeRes.ok || !completedRes.ok) {
        throw new Error(`Failed to load incidents`)
      }

      const activeData: Incident[] = await activeRes.json()
      const completedData: Incident[] = await completedRes.json()

      // Normalize status strings
      activeIncidents.value = (activeData || []).map(i => ({
        ...i,
        status: (i.status || 'active').toString().toLowerCase()
      }))
      resolvedIncidents.value = (completedData || []).map(i => ({
        ...i,
        status: (i.status || 'resolved').toString().toLowerCase()
      }))
      incidents.value = [...activeIncidents.value, ...resolvedIncidents.value]
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch incidents'
      console.error('Failed to fetch incidents:', err)
    } finally {
      loading.value = false
    }
  }

  const getIncident = async (incidentId: string): Promise<Incident | null> => {
    try {
      const response = await fetch(`${API_BASE}/incidents/${incidentId}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch incident'
      console.error('Failed to fetch incident:', err)
      return null
    }
  }

  const createAlert = async (alertData: any): Promise<Incident | null> => {
    try {
      const response = await fetch(`${API_BASE}/incidents/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ alert: alertData })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const incident = await response.json()
      
      // Add to store
      incidents.value.push(incident)
      if (incident.status === 'active') {
        activeIncidents.value.push(incident)
      }
      
      return incident
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create alert'
      console.error('Failed to create alert:', err)
      return null
    }
  }

  // Resolve incident via backend
  const resolveIncident = async (incidentId: string): Promise<Incident | null> => {
    try {
      const response = await fetch(`${API_BASE}/incidents/${incidentId}/resolve`, { method: 'POST' })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const updated: Incident = await response.json()
      updateIncident(incidentId, updated)
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to resolve incident'
      console.error('Failed to resolve incident:', err)
      return null
    }
  }

  const addIncident = (incident: Incident) => {
    incidents.value.push(incident)
    if (incident.status === 'active') {
      activeIncidents.value.push(incident)
    } else {
      resolvedIncidents.value.push(incident)
    }
  }

  const updateIncident = (incidentId: string, updates: Partial<Incident>) => {
    const index = incidents.value.findIndex(i => i.incident_id === incidentId)
    if (index !== -1) {
      incidents.value[index] = { ...incidents.value[index], ...updates }
      
      // Update status-specific arrays
      const incident = incidents.value[index]
      const activeIndex = activeIncidents.value.findIndex(i => i.incident_id === incidentId)
      const resolvedIndex = resolvedIncidents.value.findIndex(i => i.incident_id === incidentId)
      
      if (incident.status === 'active' && activeIndex === -1) {
        // Moved to active
        if (resolvedIndex !== -1) {
          resolvedIncidents.value.splice(resolvedIndex, 1)
        }
        activeIncidents.value.push(incident)
      } else if (incident.status === 'resolved' && resolvedIndex === -1) {
        // Moved to resolved
        if (activeIndex !== -1) {
          activeIncidents.value.splice(activeIndex, 1)
        }
        resolvedIncidents.value.push(incident)
      }
    }
  }

  // Derived/computed helpers used by views
  const recentIncidents = computed(() =>
    [...incidents.value]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10)
  )

  const severityStats = computed(() => {
    const stats = { critical: 0, high: 0, medium: 0, low: 0 }
    incidents.value.forEach(incident => {
      const sev = (incident.classification?.severity || incident.alert?.severity || '').toLowerCase()
      if (sev in stats) {
        // @ts-ignore
        stats[sev as keyof typeof stats] += 1
      }
    })
    return stats
  })

  // Reset store (used by Simulation view)
  const $reset = () => {
    incidents.value = []
    activeIncidents.value = []
    resolvedIncidents.value = []
    loading.value = false
    error.value = null
  }

  return {
    incidents,
    activeIncidents,
    resolvedIncidents,
    loading,
    error,
    fetchIncidents,
    getIncident,
    createAlert,
    resolveIncident,
    addIncident,
    updateIncident,
    recentIncidents,
    severityStats,
    $reset
  }
})
