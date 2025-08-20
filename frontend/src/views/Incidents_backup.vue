<template>
  <div class="incidents-page">
    <!-- Page Header -->
    <header class="page-header">
      <div class="header-content">
        <div class="page-title">
          <h1>Incident Management</h1>
          <p class="page-subtitle">Monitor and manage all system incidents</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value active">{{ activeIncidentsCount }}</span>
            <span class="stat-label">Active</span>
          </div>
          <div class="stat-item">
            <span class="stat-value resolved">{{ resolvedIncidentsCount }}</span>
            <span class="stat-label">Resolved</span>
          </div>
          <div class="stat-item">
            <span class="stat-value total">{{ totalIncidentsCount }}</span>
            <span class="stat-label">Total</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Simple Incident List -->
    <div class="incidents-container">
      <div v-if="incidents.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No incidents found</h3>
        <p>All systems are running normally</p>
      </div>
      
      <div 
        v-for="incident in incidents" 
        :key="incident.incident_id"
        class="incident-card"
        :class="incident.status"
        @click="selectIncident(incident)"
      >
        <div class="card-header">
          <span class="incident-id">{{ incident.incident_id }}</span>
          <span class="status-badge" :class="incident.status">
            {{ incident.status.toUpperCase() }}
          </span>
        </div>
        
        <div class="card-content">
          <h3>{{ incident.alert?.message || 'Unknown Incident' }}</h3>
          <p class="incident-details">
            <strong>Category:</strong> {{ incident.classification?.category || 'Unknown' }} |
            <strong>Severity:</strong> {{ incident.classification?.severity || 'Unknown' }}
          </p>
          <p class="affected-services">
            <strong>Affected:</strong> {{ incident.alert?.affected_services?.join(', ') || 'Unknown services' }}
          </p>
        </div>
        
        <div class="card-actions">
          <button @click.stop="viewIncidentDetails(incident)" class="btn-primary">
            View Details
          </button>
          <button 
            v-if="incident.status === 'active'"
            @click.stop="resolveIncident(incident.incident_id)" 
            class="btn-success"
          >
            Resolve
          </button>
        </div>
      </div>
    </div>

    <!-- Simple Modal -->
    <div v-if="selectedIncident" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Incident Details</h2>
          <button @click="closeModal" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <p><strong>ID:</strong> {{ selectedIncident.incident_id }}</p>
          <p><strong>Status:</strong> {{ selectedIncident.status }}</p>
          <p><strong>Message:</strong> {{ selectedIncident.alert?.message }}</p>
          <p><strong>Category:</strong> {{ selectedIncident.classification?.category }}</p>
          <p><strong>Severity:</strong> {{ selectedIncident.classification?.severity }}</p>
          <p><strong>Created:</strong> {{ formatDateTime(selectedIncident.created_at) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useIncidentStore } from '@/stores/incidents'
import type { Incident } from '@/stores/incidents'

const incidentStore = useIncidentStore()

// Component state
const selectedIncident = ref<Incident | null>(null)

// Computed properties
const incidents = computed(() => incidentStore.incidents)

const activeIncidentsCount = computed(() => 
  incidents.value.filter(i => i.status === 'active').length
)

const resolvedIncidentsCount = computed(() => 
  incidents.value.filter(i => i.status === 'resolved').length
)

const totalIncidentsCount = computed(() => incidents.value.length)

// Methods
function selectIncident(incident: Incident) {
  selectedIncident.value = incident
}

function viewIncidentDetails(incident: Incident) {
  selectedIncident.value = incident
}

function closeModal() {
  selectedIncident.value = null
}

async function resolveIncident(incidentId: string) {
  try {
    await incidentStore.resolveIncident(incidentId)
    if (selectedIncident.value?.incident_id === incidentId) {
      closeModal()
    }
  } catch (error) {
    console.error('Failed to resolve incident:', error)
  }
}

function formatDateTime(timestamp: string) {
  return new Date(timestamp).toLocaleString()
}

// Lifecycle
onMounted(() => {
  incidentStore.fetchIncidents()
})
</script>

<style scoped>
.incidents-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-header {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin: 1.5rem;
  margin-bottom: 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.page-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  font-size: 1rem;
  margin: 0.5rem 0 0 0;
}

.header-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.875rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-value.active { color: #dc2626; }
.stat-value.resolved { color: #16a34a; }
.stat-value.total { color: #3b82f6; }

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.incidents-container {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.incident-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.incident-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.incident-card.active {
  border-left-color: #dc2626;
}

.incident-card.resolved {
  border-left-color: #16a34a;
  opacity: 0.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.incident-id {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #fef2f2;
  color: #dc2626;
}

.status-badge.resolved {
  background: #f0fdf4;
  color: #16a34a;
}

.card-content h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.75rem;
}

.incident-details,
.affected-services {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-success {
  background: #10b981;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-success:hover {
  background: #059669;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body p {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: #374151;
}

/* Responsive Design */
@media (max-width: 768px) {
  .incidents-container {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
  
  .page-header {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-stats {
    width: 100%;
    justify-content: space-around;
  }
}
</style>

    <!-- Filters -->
    <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Status</label>
          <select 
            v-model="filters.status" 
            @change="applyFilters"
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="analyzing">Analyzing</option>
            <option value="resolving">Resolving</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Severity</label>
          <select 
            v-model="filters.severity" 
            @change="applyFilters"
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Type</label>
          <select 
            v-model="filters.type" 
            @change="applyFilters"
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="security">Security</option>
            <option value="performance">Performance</option>
            <option value="infrastructure">Infrastructure</option>
            <option value="application">Application</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Search</label>
          <input 
            v-model="filters.search" 
            @input="applyFilters"
            type="text" 
            placeholder="Search incidents..."
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
          >
        </div>
      </div>
      
      <div class="flex justify-between items-center mt-4">
        <div class="text-sm text-gray-400">
          Showing {{ filteredIncidents.length }} of {{ incidentStore.incidents.length }} incidents
        </div>
        
        <button 
          @click="clearFilters"
          class="text-blue-400 hover:text-blue-300 text-sm font-medium"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Incidents Table -->
    <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                <button @click="setSortBy('id')" class="flex items-center space-x-1 hover:text-white">
                  <span>Incident ID</span>
                  <svg v-if="sortBy === 'id'" class="w-3 h-3" :class="{ 'rotate-180': sortDirection === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                  </svg>
                </button>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                <button @click="setSortBy('title')" class="flex items-center space-x-1 hover:text-white">
                  <span>Title</span>
                  <svg v-if="sortBy === 'title'" class="w-3 h-3" :class="{ 'rotate-180': sortDirection === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                  </svg>
                </button>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                <button @click="setSortBy('severity')" class="flex items-center space-x-1 hover:text-white">
                  <span>Severity</span>
                  <svg v-if="sortBy === 'severity'" class="w-3 h-3" :class="{ 'rotate-180': sortDirection === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                  </svg>
                </button>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                <button @click="setSortBy('status')" class="flex items-center space-x-1 hover:text-white">
                  <span>Status</span>
                  <svg v-if="sortBy === 'status'" class="w-3 h-3" :class="{ 'rotate-180': sortDirection === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                  </svg>
                </button>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                <button @click="setSortBy('created_at')" class="flex items-center space-x-1 hover:text-white">
                  <span>Created</span>
                  <svg v-if="sortBy === 'created_at'" class="w-3 h-3" :class="{ 'rotate-180': sortDirection === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                  </svg>
                </button>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            <tr 
              v-for="incident in paginatedIncidents" 
              :key="incident.id" 
              class="hover:bg-gray-700 transition-colors duration-200"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300 font-mono">
                {{ incident.id.substring(0, 8) }}...
              </td>
              <td class="px-6 py-4 text-sm text-white max-w-xs">
                <div class="truncate" :title="incident.alert.title">
                  {{ incident.alert.title }}
                </div>
                <div class="text-xs text-gray-400 mt-1 truncate" :title="incident.alert.description">
                  {{ incident.alert.description }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                <span class="capitalize">{{ incident.alert.type }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getSeverityClass(incident.alert.severity)"
                >
                  {{ incident.alert.severity.toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getStatusClass(incident.status)"
                >
                  {{ incident.status.toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                {{ formatDate(incident.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex space-x-2">
                  <router-link 
                    :to="`/incidents/${incident.id}`"
                    class="text-blue-400 hover:text-blue-300 font-medium"
                  >
                    View
                  </router-link>
                  <button 
                    v-if="incident.status === 'open'"
                    @click="updateIncidentStatus(incident.id, 'analyzing')"
                    class="text-yellow-400 hover:text-yellow-300 font-medium"
                  >
                    Analyze
                  </button>
                  <button 
                    v-if="incident.status === 'resolved'"
                    @click="updateIncidentStatus(incident.id, 'closed')"
                    class="text-green-400 hover:text-green-300 font-medium"
                  >
                    Close
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Empty State -->
      <div v-if="filteredIncidents.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-400">No incidents found</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ incidentStore.incidents.length === 0 ? 'Get started by running a simulation.' : 'Try adjusting your filters.' }}
        </p>
        <div class="mt-6">
          <router-link 
            to="/simulation"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Run Simulation
          </router-link>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-between items-center">
      <div class="text-sm text-gray-400">
        Page {{ currentPage }} of {{ totalPages }} ({{ filteredIncidents.length }} total incidents)
      </div>
      
      <div class="flex space-x-2">
        <button
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-1 text-sm bg-gray-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
        >
          Previous
        </button>
        
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="currentPage = page"
          class="px-3 py-1 text-sm rounded"
          :class="page === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-700 text-white hover:bg-gray-600'"
        >
          {{ page }}
        </button>
        
        <button
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-1 text-sm bg-gray-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useIncidentStore } from '@/stores/incidents'
import IncidentList from '@/components/IncidentList.vue'
import IncidentDetails from '@/components/IncidentDetails.vue'
import type { Incident } from '@/stores/incidents'

const incidentStore = useIncidentStore()

// Component state
const selectedIncident = ref<Incident | null>(null)
const showTimelineModal = ref(false)
const timelineIncident = ref<Incident | null>(null)

// Computed properties
const incidents = computed(() => incidentStore.incidents)

const activeIncidentsCount = computed(() => 
  incidents.value.filter(i => i.status === 'active').length
)

const resolvedIncidentsCount = computed(() => 
  incidents.value.filter(i => i.status === 'resolved').length
)

const totalIncidentsCount = computed(() => incidents.value.length)

// Methods
function selectIncident(incident: Incident) {
  selectedIncident.value = incident
}

function viewIncidentDetails(incident: Incident) {
  selectedIncident.value = incident
}

function viewIncidentTimeline(incident: Incident) {
  timelineIncident.value = incident
  showTimelineModal.value = true
}

function closeModal() {
  selectedIncident.value = null
}

function closeTimelineModal() {
  showTimelineModal.value = false
  timelineIncident.value = null
}

async function resolveIncident(incidentId: string) {
  try {
    await incidentStore.resolveIncident(incidentId)
    // Close modal if the resolved incident was selected
    if (selectedIncident.value?.incident_id === incidentId) {
      closeModal()
    }
  } catch (error) {
    console.error('Failed to resolve incident:', error)
  }
}

function formatDateTime(timestamp: string) {
  return new Date(timestamp).toLocaleString()
}

// Lifecycle
onMounted(() => {
  // Load incidents when component mounts
  incidentStore.fetchIncidents()
})
</script>
      case 'title':
        aValue = a.alert.title
        bValue = b.alert.title
        break
      case 'severity':
        const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
        aValue = severityOrder[a.alert.severity as keyof typeof severityOrder]
        bValue = severityOrder[b.alert.severity as keyof typeof severityOrder]
        break
      case 'status':
        aValue = a.status
        bValue = b.status
        break
      case 'created_at':
      default:
        aValue = new Date(a.created_at).getTime()
        bValue = new Date(b.created_at).getTime()
        break
    }
    
    if (sortDirection.value === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
    }
  })
  
  return incidents
})

const totalPages = computed(() => Math.ceil(filteredIncidents.value.length / itemsPerPage))

const paginatedIncidents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredIncidents.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Watch for filter changes to reset pagination
watch(filters, () => {
  currentPage.value = 1
}, { deep: true })

// Methods
async function refreshIncidents() {
  loading.value = true
  try {
    // In a real app, this would fetch fresh data from the API
    await new Promise(resolve => setTimeout(resolve, 1000))
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  // Filters are reactive, so they apply automatically
  currentPage.value = 1
}

function clearFilters() {
  filters.status = ''
  filters.severity = ''
  filters.type = ''
  filters.search = ''
}

function setSortBy(field: string) {
  if (sortBy.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortDirection.value = 'desc'
  }
}

function updateIncidentStatus(incidentId: string, status: string) {
  incidentStore.updateIncidentStatus(incidentId, status as any)
}

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
    open: 'bg-red-500 text-white',
    analyzing: 'bg-yellow-500 text-black',
    resolving: 'bg-blue-500 text-white',
    resolved: 'bg-green-500 text-white',
    closed: 'bg-gray-500 text-white'
  }
  return classes[status as keyof typeof classes] || 'bg-gray-500 text-white'
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
