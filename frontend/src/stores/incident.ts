import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Alert {
  id: string
  timestamp: string
  source: string
  type: 'security' | 'performance' | 'infrastructure' | 'application'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  metadata: Record<string, any>
}

interface Classification {
  incident_id: string
  category: string
  subcategory: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  reasoning: string
  estimated_impact: string
  recommended_escalation: string
  generated_at: string
}

interface ResolutionStep {
  step_number: number
  action: string
  expected_outcome: string
  verification_method: string
  estimated_duration: string
  dependencies: string[]
}

interface Resolution {
  incident_id: string
  matched_runbooks: string[]
  steps: ResolutionStep[]
  estimated_time: string
  risk_level: string
  rollback_plan: string
  contacts: string[]
  generated_at: string
}

interface TimelineEvent {
  timestamp: string
  event_type: 'detection' | 'classification' | 'escalation' | 'resolution' | 'verification'
  description: string
  actor: string
  metadata: Record<string, any>
}

interface PostMortem {
  incident_id: string
  summary: string
  timeline: TimelineEvent[]
  root_cause: string
  contributing_factors: string[]
  impact_assessment: string
  lessons_learned: string[]
  action_items: string[]
  generated_at: string
  markdown_report: string
}

interface Incident {
  id: string
  alert: Alert
  classification?: Classification
  resolution?: Resolution
  postmortem?: PostMortem
  status: 'open' | 'analyzing' | 'resolving' | 'resolved' | 'closed'
  created_at: string
  updated_at: string
}

export const useIncidentStore = defineStore('incident', () => {
  const incidents = ref<Incident[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties
  const activeIncidents = computed(() => 
    incidents.value.filter(incident => 
      ['open', 'analyzing', 'resolving'].includes(incident.status)
    )
  )

  const recentIncidents = computed(() => 
    incidents.value
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10)
  )

  const incidentsByStatus = computed(() => {
    return incidents.value.reduce((acc, incident) => {
      acc[incident.status] = (acc[incident.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  })

  const severityStats = computed(() => {
    const stats = { critical: 0, high: 0, medium: 0, low: 0 }
    incidents.value.forEach(incident => {
      if (incident.alert.severity in stats) {
        stats[incident.alert.severity as keyof typeof stats]++
      }
    })
    return stats
  })

  // Actions
  function addIncident(incident: Incident) {
    incidents.value.push(incident)
  }

  function updateIncident(incidentId: string, updates: Partial<Incident>) {
    const index = incidents.value.findIndex(incident => incident.id === incidentId)
    if (index !== -1) {
      incidents.value[index] = { ...incidents.value[index], ...updates }
    }
  }

  function updateIncidentStatus(incidentId: string, status: Incident['status']) {
    updateIncident(incidentId, { 
      status, 
      updated_at: new Date().toISOString() 
    })
  }

  function getIncidentById(incidentId: string): Incident | undefined {
    return incidents.value.find(incident => incident.id === incidentId)
  }

  function clearError() {
    error.value = null
  }

  function setLoading(value: boolean) {
    loading.value = value
  }

  function setError(message: string) {
    error.value = message
  }

  // Reset store
  function $reset() {
    incidents.value = []
    loading.value = false
    error.value = null
  }

  return {
    // State
    incidents,
    loading,
    error,
    
    // Computed
    activeIncidents,
    recentIncidents,
    incidentsByStatus,
    severityStats,
    
    // Actions
    addIncident,
    updateIncident,
    updateIncidentStatus,
    getIncidentById,
    clearError,
    setLoading,
    setError,
    $reset
  }
})
