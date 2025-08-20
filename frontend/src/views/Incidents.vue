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
