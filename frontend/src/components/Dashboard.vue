<template>
  <div class="crisis-dashboard">
    <!-- Page          <button @click="triggerDemo" class="action-card">
            <div class="action-icon">🚀</div>
            <h3>Demo Incident</h3>
            <p>Create test incident</p>
          </button>er -->
    <header class="page-header">
      <div class="header-content">
        <div class="page-title">
          <h1>Crisis Dashboard</h1>
          <p class="page-subtitle">Real-time monitoring and incident management</p>
        </div>
        <div class="header-actions">
          <button @click="refreshIncidents" class="refresh-btn" :disabled="loading">
            <span class="refresh-icon" :class="{ spinning: loading }">🔄</span>
            Refresh
          </button>
          <button @click="triggerDemo" class="demo-btn">
            <span>⚡</span>
            Demo Incident
          </button>
        </div>
      </div>
    </header>

    <main class="dashboard-main">
      <!-- Quick Stats -->
      <section class="stats-overview">
        <div class="stat-card critical">
          <div class="stat-value">{{ dashboardData.active_incidents || 0 }}</div>
          <div class="stat-label">Active Incidents</div>
        </div>
        <div class="stat-card success">
          <div class="stat-value">{{ dashboardData.resolved_incidents || 0 }}</div>
          <div class="stat-label">Resolved Today</div>
        </div>
        <div class="stat-card info">
          <div class="stat-value">{{ dashboardData.total_incidents || 0 }}</div>
          <div class="stat-label">Total Incidents</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-value">{{ averageResolutionTime }}</div>
          <div class="stat-label">Avg Resolution</div>
        </div>
      </section>

      <!-- Quick Actions -->
      <section class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="actions-grid">
          <router-link to="/incidents" class="action-card">
            <div class="action-icon">🔥</div>
            <h3>View All Incidents</h3>
            <p>Manage and monitor incidents</p>
          </router-link>
          
          <router-link to="/simulation" class="action-card">
            <div class="action-icon">⚡</div>
            <h3>Run Simulation</h3>
            <p>Test incident response</p>
          </router-link>
          
          <button @click="triggerDemo" class="action-card">
            <div class="action-icon">�</div>
            <h3>Demo Incident</h3>
            <p>Create test incident</p>
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useIncidentStore } from '@/stores/incidents'
import { useWebSocketStore } from '@/stores/websocket'
import IncidentDetails from '@/components/IncidentDetails.vue'

// Stores
const incidentStore = useIncidentStore()
const wsStore = useWebSocketStore()

// Reactive data
const dashboardData = ref({
  active_incidents: 0,
  resolved_incidents: 0,
  total_incidents: 0
})

const activeIncidents = ref([])
const selectedIncident = ref(null)
const notifications = ref([])
const isConnected = ref(false)
const loading = ref(false)
const activeAgents = ref(3)

const recentActivity = ref([
  {
    id: 1,
    timestamp: new Date().toISOString(),
    type: 'System',
    message: 'Crisis Commander started'
  }
])

const demoScenarios = ref([
  { name: 'High CPU', icon: '🔥', type: 'cpu_high' },
  { name: 'Database Down', icon: '💾', type: 'db_connection' },
  { name: 'Memory Leak', icon: '🧠', type: 'memory_leak' },
  { name: 'Network Issue', icon: '🌐', type: 'network_timeout' }
])

// Computed
const averageResolutionTime = computed(() => {
  return dashboardData.value.resolved_incidents > 0 
    ? '12m' 
    : '0m'
})

// Methods
const refreshIncidents = async () => {
  try {
    const response = await fetch('http://localhost:8000/metrics/dashboard')
    dashboardData.value = await response.json()
    
    const incidentsResponse = await fetch('http://localhost:8000/incidents')
    activeIncidents.value = await incidentsResponse.json()
    
    addNotification('Data refreshed', 'success')
  } catch (error) {
    console.error('Failed to refresh:', error)
    addNotification('Failed to refresh data', 'error')
  }
}

const triggerDemo = () => {
  triggerScenario(demoScenarios.value[0])
}

const triggerScenario = async (scenario) => {
  try {
    const alertData = {
      alert_type: scenario.type,
      severity: 'high',
      metrics: { cpu_usage: 95.0 },
      message: `Demo ${scenario.name} scenario triggered`,
      affected_services: ['demo-service'],
      timestamp: new Date().toISOString(),
      source: 'demo',
      environment: 'staging'
    }
    
    const response = await fetch('http://localhost:8000/alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(alertData)
    })
    
    if (response.ok) {
      const incident = await response.json()
      addNotification(`Demo incident created: ${incident.incident_id}`, 'success')
      refreshIncidents()
    }
  } catch (error) {
    console.error('Failed to trigger scenario:', error)
    addNotification('Failed to trigger demo scenario', 'error')
  }
}

const viewIncident = (incident) => {
  selectedIncident.value = incident
}

const closeModal = () => {
  selectedIncident.value = null
}

const resolveIncident = async (incidentId) => {
  try {
    const response = await fetch(`http://localhost:8000/incidents/${incidentId}/resolve`, {
      method: 'POST'
    })
    
    if (response.ok) {
      addNotification(`Incident ${incidentId} resolved`, 'success')
      refreshIncidents()
      if (selectedIncident.value?.incident_id === incidentId) {
        closeModal()
      }
    }
  } catch (error) {
    console.error('Failed to resolve incident:', error)
    addNotification('Failed to resolve incident', 'error')
  }
}

const getSeverityClass = (severity) => {
  return {
    'severity-critical': severity === 'critical',
    'severity-high': severity === 'high',
    'severity-medium': severity === 'medium',
    'severity-low': severity === 'low'
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const addNotification = (message, type = 'info') => {
  const notification = {
    id: Date.now(),
    message,
    type
  }
  notifications.value.push(notification)
  
  setTimeout(() => {
    const index = notifications.value.findIndex(n => n.id === notification.id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }, 5000)
}

// Lifecycle
onMounted(() => {
  refreshIncidents()
  // Setup periodic refresh
  setInterval(refreshIncidents, 30000) // Refresh every 30 seconds
})
</script>

<style scoped>
.crisis-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  font-family: 'Inter', sans-serif;
  padding: 1.5rem;
}

.page-header {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.refresh-btn, .demo-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn {
  background: #f3f4f6;
  color: #374151;
}

.refresh-btn:hover {
  background: #e5e7eb;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.demo-btn {
  background: #3b82f6;
  color: white;
}

.demo-btn:hover {
  background: #2563eb;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.dashboard-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #e5e7eb;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stat-card.critical { border-left-color: #ef4444; }
.stat-card.success { border-left-color: #10b981; }
.stat-card.info { border-left-color: #3b82f6; }
.stat-card.warning { border-left-color: #f59e0b; }

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-card.critical .stat-value { color: #ef4444; }
.stat-card.success .stat-value { color: #10b981; }
.stat-card.info .stat-value { color: #3b82f6; }
.stat-card.warning .stat-value { color: #f59e0b; }

.stat-label {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Quick Actions Section */
.quick-actions {
  margin-bottom: 2rem;
}

.quick-actions h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 2px solid transparent;
  transition: all 0.2s ease;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  display: block;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.action-card p {
  color: #6b7280;
  font-size: 0.875rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
