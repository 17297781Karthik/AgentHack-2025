<template>
  <div v-if="incident" class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-start">
      <div>
        <div class="flex items-center space-x-3 mb-2">
          <button 
            @click="$router.back()"
            class="text-gray-400 hover:text-white"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1 class="text-3xl font-bold text-white">Incident Details</h1>
        </div>
        <p class="text-gray-400">{{ incident.alert?.message }}</p>
      </div>
      
      <div class="flex items-center space-x-3">
        <span 
          class="px-3 py-1 text-sm font-medium rounded-full"
          :class="getSeverityClass(incident.classification?.severity || incident.alert?.severity || 'low')"
        >
          {{ (incident.classification?.severity || incident.alert?.severity || 'low').toUpperCase() }}
        </span>
        <span 
          class="px-3 py-1 text-sm font-medium rounded-full"
          :class="getStatusClass(incident.status)"
        >
          {{ incident.status.toUpperCase() }}
        </span>
      </div>
    </div>

    <!-- Incident Overview -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Incident Info -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Alert Details -->
        <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 class="text-xl font-semibold text-white mb-4">Alert Details</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-sm text-gray-400">Incident ID</label>
              <p class="text-white font-mono">{{ incident.incident_id }}</p>
            </div>
            <div>
              <label class="text-sm text-gray-400">Source</label>
              <p class="text-white">{{ incident.alert?.source_system }}</p>
            </div>
            <div>
              <label class="text-sm text-gray-400">Type</label>
              <p class="text-white capitalize">{{ incident.alert?.alert_type }}</p>
            </div>
            <div>
              <label class="text-sm text-gray-400">Created At</label>
              <p class="text-white">{{ formatDateTime(incident.created_at) }}</p>
            </div>
          </div>
          
          <div class="mt-4">
            <label class="text-sm text-gray-400">Description</label>
            <p class="text-white mt-1">{{ incident.alert?.message }}</p>
          </div>
          
          <!-- Metadata -->
          <div v-if="incident.alert.metadata && Object.keys(incident.alert.metadata).length > 0" class="mt-4">
            <label class="text-sm text-gray-400">Metadata</label>
            <div class="mt-2 bg-gray-900 rounded p-3 text-sm">
              <pre class="text-gray-300 whitespace-pre-wrap">{{ JSON.stringify(incident.alert.metadata, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <!-- Classification Results -->
        <div v-if="incident.classification" class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 class="text-xl font-semibold text-white mb-4">AI Classification</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-sm text-gray-400">Category</label>
              <p class="text-white">{{ incident.classification.category }}</p>
            </div>
            <div>
              <label class="text-sm text-gray-400">Tags</label>
              <p class="text-white">{{ (incident.classification.tags || []).join(', ') }}</p>
            </div>
            <div>
              <label class="text-sm text-gray-400">Confidence</label>
              <div class="flex items-center space-x-2">
                <div class="flex-1 bg-gray-700 rounded-full h-2">
                  <div 
                    class="bg-blue-500 h-2 rounded-full" 
                    :style="{ width: `${(incident.classification.confidence || 0) * 100}%` }"
                  ></div>
                </div>
                <span class="text-white text-sm">{{ Math.round((incident.classification.confidence || 0) * 100) }}%</span>
              </div>
            </div>
            <div>
              <label class="text-sm text-gray-400">Estimated Impact</label>
              <p class="text-white">{{ incident.classification.estimated_impact }}</p>
            </div>
          </div>
          
          <div class="mt-4">
            <label class="text-sm text-gray-400">AI Reasoning</label>
            <p class="text-white mt-1">{{ incident.classification.reasoning }}</p>
          </div>
          
          <div class="mt-4">
            <label class="text-sm text-gray-400">Estimated Impact</label>
            <p class="text-white mt-1">{{ incident.classification.estimated_impact }}</p>
          </div>
        </div>

        <!-- Resolution Steps -->
        <div v-if="incident.resolution" class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 class="text-xl font-semibold text-white mb-4">Resolution Guidance</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label class="text-sm text-gray-400">Estimated Time (min)</label>
              <p class="text-white">{{ incident.resolution.estimated_time_minutes }}</p>
            </div>
            <div>
              <label class="text-sm text-gray-400">Risk Level</label>
              <p class="text-white">{{ incident.resolution.risk_level }}</p>
            </div>
            <div>
              <label class="text-sm text-gray-400">Matched Runbooks</label>
              <p class="text-white">{{ (incident.resolution.parallel_actions || []).length }}</p>
            </div>
          </div>
          
          <!-- Resolution Steps -->
          <div class="space-y-4">
            <h3 class="text-lg font-medium text-white">Resolution Steps</h3>
            <div 
              v-for="step in incident.resolution.recommended_steps" 
              :key="step.step_number"
              class="bg-gray-700 rounded-lg p-4"
            >
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs text-white font-medium">
                  {{ step.step_number }}
                </div>
                <div class="flex-1">
                  <h4 class="text-white font-medium">{{ step.description }}</h4>
                  <p class="text-gray-300 text-sm mt-1">{{ step.expected_result }}</p>
                  <div class="mt-2 text-xs text-gray-400">
                    <span>Automation: {{ step.automation_possible ? 'Yes' : 'No' }}</span>
                    <span class="ml-4">Risk: {{ step.risk_level }}</span>
                  </div>
                  <div v-if="step.rollback_command" class="mt-2">
                    <span class="text-xs text-gray-400">Rollback: </span>
                    <span class="text-xs text-gray-300">{{ step.rollback_command }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Rollback Plan -->
          <div class="mt-6">
            <h3 class="text-lg font-medium text-white mb-2">Rollback Plan</h3>
            <div class="bg-gray-700 rounded-lg p-4">
              <p class="text-gray-300">{{ (incident.resolution.rollback_plan || []).join(', ') }}</p>
            </div>
          </div>
          
          <!-- Parallel Actions -->
          <div v-if="(incident.resolution.parallel_actions || []).length > 0" class="mt-6">
            <h3 class="text-lg font-medium text-white mb-2">Parallel Actions</h3>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="action in incident.resolution.parallel_actions" 
                :key="action"
                class="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300"
              >
                {{ action }}
              </span>
            </div>
          </div>
        </div>

        <!-- Post-Mortem -->
        <div v-if="incident.postmortem" class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 class="text-xl font-semibold text-white mb-4">Post-Mortem Report</h2>
          
          <div class="space-y-6">
            <!-- Summary -->
            <div>
              <h3 class="text-lg font-medium text-white mb-2">Summary</h3>
              <p class="text-gray-300">{{ incident.postmortem.summary }}</p>
            </div>
            
            <!-- Root Cause -->
            <div>
              <h3 class="text-lg font-medium text-white mb-2">Root Cause</h3>
              <p class="text-gray-300">{{ incident.postmortem.root_cause }}</p>
            </div>
            
            <!-- Contributing Factors -->
            <div v-if="incident.postmortem.contributing_factors.length > 0">
              <h3 class="text-lg font-medium text-white mb-2">Contributing Factors</h3>
              <ul class="list-disc list-inside text-gray-300 space-y-1">
                <li v-for="factor in incident.postmortem.contributing_factors" :key="factor">
                  {{ factor }}
                </li>
              </ul>
            </div>
            
            <!-- Impact Assessment -->
            <div>
              <h3 class="text-lg font-medium text-white mb-2">Impact Assessment</h3>
              <p class="text-gray-300">{{ incident.postmortem.impact_assessment }}</p>
            </div>
            
            <!-- Lessons Learned -->
            <div v-if="incident.postmortem.lessons_learned.length > 0">
              <h3 class="text-lg font-medium text-white mb-2">Lessons Learned</h3>
              <ul class="list-disc list-inside text-gray-300 space-y-1">
                <li v-for="lesson in incident.postmortem.lessons_learned" :key="lesson">
                  {{ lesson }}
                </li>
              </ul>
            </div>
            
            <!-- Action Items -->
            <div v-if="incident.postmortem.action_items.length > 0">
              <h3 class="text-lg font-medium text-white mb-2">Action Items</h3>
              <ul class="list-disc list-inside text-gray-300 space-y-1">
                <li v-for="item in incident.postmortem.action_items" :key="item">
                  {{ item }}
                </li>
              </ul>
            </div>
            
            <!-- Download Report -->
            <div class="pt-4 border-t border-gray-700">
              <button 
                @click="downloadPostMortem"
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <span>Download Report</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Timeline -->
        <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 class="text-xl font-semibold text-white mb-4">Timeline</h2>
          
          <div class="space-y-4">
            <div 
              v-for="(event, index) in timelineEvents" 
              :key="index"
              class="flex space-x-3"
            >
              <div class="flex-shrink-0">
                <div 
                  class="w-3 h-3 rounded-full mt-1"
                  :class="getEventColor(event.type)"
                ></div>
              </div>
              <div class="flex-1">
                <div class="flex justify-between items-start">
                  <p class="text-white text-sm font-medium">{{ event.description }}</p>
                  <span class="text-xs text-gray-400">{{ formatTime(event.timestamp) }}</span>
                </div>
                <p class="text-xs text-gray-400 mt-1">{{ event.actor }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 class="text-xl font-semibold text-white mb-4">Actions</h2>
          
          <div class="space-y-3">
            <button
              v-if="incident.status === 'open'"
              @click="updateStatus('analyzing')"
              class="w-full bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-left"
            >
              Start Analysis
            </button>
            
            <button
              v-if="incident.status === 'analyzing'"
              @click="updateStatus('resolving')"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-left"
            >
              Begin Resolution
            </button>
            
            <button
              v-if="incident.status === 'resolving'"
              @click="updateStatus('resolved')"
              class="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-left"
            >
              Mark Resolved
            </button>
            
            <button
              v-if="incident.status === 'resolved'"
              @click="updateStatus('closed')"
              class="w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-left"
            >
              Close Incident
            </button>
            
            <button
              @click="refreshIncident"
              class="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-left"
            >
              Refresh Data
            </button>
          </div>
        </div>

        <!-- Related Incidents -->
        <div v-if="relatedIncidents.length > 0" class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 class="text-xl font-semibold text-white mb-4">Related Incidents</h2>
          
          <div class="space-y-3">
            <div 
              v-for="related in relatedIncidents" 
              :key="related.id"
              class="border border-gray-600 rounded-lg p-3"
            >
              <router-link 
                :to="`/incidents/${related.incident_id}`"
                class="text-blue-400 hover:text-blue-300 text-sm font-medium"
              >
                {{ related.alert?.message }}
              </router-link>
              <p class="text-xs text-gray-400 mt-1">
                {{ formatDate(related.created_at) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Loading State -->
  <div v-else-if="loading" class="flex justify-center items-center min-h-64">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>

  <!-- Not Found State -->
  <div v-else class="text-center py-12">
    <h2 class="text-2xl font-bold text-white mb-4">Incident Not Found</h2>
    <p class="text-gray-400 mb-6">The incident you're looking for doesn't exist or has been removed.</p>
    <router-link 
      to="/incidents"
      class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
    >
      Back to Incidents
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useIncidentStore } from '../stores/incidents'

interface Props {
  id: string
}

const props = defineProps<Props>()
const route = useRoute()
const incidentStore = useIncidentStore()

const loading = ref(false)

// Get incident from store
const incident = computed(() => {
  const id = props.id || route.params.id as string
  return incidentStore.incidents.find(i => i.incident_id === id)
})

// Timeline events computed from incident data
const timelineEvents = computed(() => {
  if (!incident.value) return []
  
  const events = [
    {
      timestamp: incident.value.created_at,
      type: 'detection',
      description: 'Incident detected',
      actor: 'Monitoring System'
    }
  ]
  
  if (incident.value.classification) {
    events.push({
      timestamp: incident.value.classification.generated_at,
      type: 'classification',
      description: 'Incident classified',
      actor: 'AI Classifier'
    })
  }
  
  if (incident.value.resolution) {
    events.push({
      timestamp: incident.value.resolution.generated_at,
      type: 'resolution',
      description: 'Resolution guidance generated',
      actor: 'AI Resolution Advisor'
    })
  }
  
  if (incident.value.postmortem) {
    events.push({
      timestamp: incident.value.postmortem.generated_at,
      type: 'postmortem',
      description: 'Post-mortem report generated',
      actor: 'AI PostMortem Generator'
    })
  }
  
  return events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
})

// Related incidents (mock for now)
const relatedIncidents = computed(() => {
  if (!incident.value) return []
  
  return incidentStore.incidents
    .filter(i => 
      i.incident_id !== incident.value!.incident_id && 
      (i.classification?.category || '') === (incident.value!.classification?.category || '')
    )
    .slice(0, 3)
})

function getSeverityClass(severity: string) {
  const classes = {
    critical: 'bg-red-500 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-500 text-black',
    low: 'bg-green-500 text-white'
  }
  return classes[severity as keyof typeof classes] || 'bg-gray-500 text-white'
}

function getStatusClass(status: string) {
  const classes = {
    active: 'bg-blue-500 text-white',
    resolved: 'bg-green-500 text-white',
    open: 'bg-red-500 text-white',
    analyzing: 'bg-yellow-500 text-black',
    resolving: 'bg-blue-500 text-white',
    closed: 'bg-gray-500 text-white'
  }
  return classes[status as keyof typeof classes] || 'bg-gray-500 text-white'
}

function getEventColor(eventType: string) {
  const colors = {
    detection: 'bg-red-400',
    classification: 'bg-yellow-400',
    resolution: 'bg-blue-400',
    postmortem: 'bg-green-400'
  }
  return colors[eventType as keyof typeof colors] || 'bg-gray-400'
}

function formatDateTime(dateString: string) {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatTime(dateString: string) {
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function updateStatus(status: string) {
  if (incident.value) {
    incidentStore.updateIncident(incident.value.incident_id, { status })
  }
}

function refreshIncident() {
  // In a real app, this would fetch fresh data from the API
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

function downloadPostMortem() {
  if (!incident.value?.postmortem) return
  
  const blob = new Blob([incident.value.postmortem.markdown_report], { 
    type: 'text/markdown' 
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `postmortem-${incident.value.incident_id}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  if (!incident.value) {
    loading.value = true
    const id = (route.params.id as string) || ''
    incidentStore.getIncident(id).then(() => {
      loading.value = false
    }).catch(() => {
      loading.value = false
    })
  }
})
</script>
