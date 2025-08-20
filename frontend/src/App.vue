<template>
  <div id="app">
    <div class="app-layout">
      <!-- Sidebar Navigation -->
      <nav class="sidebar">
        <div class="sidebar-header">
          <div class="logo">
            <span class="logo-icon">🚨</span>
            <span class="logo-text">Crisis Commander</span>
          </div>
        </div>
        
        <div class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.name === 'dashboard' }">
            <span class="nav-icon">📊</span>
            <span class="nav-text">Dashboard</span>
          </router-link>
          
          <router-link to="/incidents" class="nav-item" :class="{ active: $route.name === 'incidents' }">
            <span class="nav-icon">🔥</span>
            <span class="nav-text">Incidents</span>
            <span v-if="activeIncidentCount > 0" class="nav-badge">{{ activeIncidentCount }}</span>
          </router-link>
          
          <router-link to="/simulation" class="nav-item" :class="{ active: $route.name === 'simulation' }">
            <span class="nav-icon">⚡</span>
            <span class="nav-text">Simulation</span>
          </router-link>
        </div>
        
        <!-- Connection Status -->
        <div class="sidebar-footer">
          <div class="connection-status" :class="{ connected: isConnected }">
            <div class="status-dot"></div>
            <span class="status-text">{{ isConnected ? 'Connected' : 'Disconnected' }}</span>
          </div>
        </div>
      </nav>
      
      <!-- Main Content -->
      <main class="main-content">
        <div class="p-6">
          <router-view />
        </div>
      </main>
      
      <!-- Notification Toast -->
      <div v-if="showNotification" class="notification-toast" :class="notificationType">
        <div class="notification-content">
          <span class="notification-icon">{{ notificationIcon }}</span>
          <span class="notification-message">{{ notificationMessage }}</span>
        </div>
        <button @click="hideNotification" class="notification-close">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'
import { useIncidentStore } from '@/stores/incidents'

const wsStore = useWebSocketStore()
const incidentStore = useIncidentStore()

// Notification system
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info')
const notificationTimeout = ref<NodeJS.Timeout | null>(null)

const isConnected = computed(() => wsStore.isConnected)
const activeIncidentCount = computed(() => 
  incidentStore.incidents.filter(i => i.status === 'active').length
)

const notificationIcon = computed(() => {
  switch (notificationType.value) {
    case 'success': return '✅'
    case 'warning': return '⚠️'
    case 'error': return '❌'
    default: return 'ℹ️'
  }
})

function showNotificationMessage(message: string, type: string = 'info') {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true
  
  if (notificationTimeout.value) {
    clearTimeout(notificationTimeout.value)
  }
  
  notificationTimeout.value = setTimeout(() => {
    hideNotification()
  }, 5000)
}

function hideNotification() {
  showNotification.value = false
  if (notificationTimeout.value) {
    clearTimeout(notificationTimeout.value)
    notificationTimeout.value = null
  }
}

onMounted(() => {
  // Connect to WebSocket on app startup
  wsStore.connect()
  
  // Listen for WebSocket messages and show notifications
  wsStore.onMessage((message) => {
    if (message.type === 'incident_created') {
      showNotificationMessage('New incident detected!', 'warning')
      // Refresh incidents to reflect new one
      incidentStore.fetchIncidents()
    } else if (message.type === 'incident_resolved') {
      showNotificationMessage('Incident resolved successfully!', 'success')
      incidentStore.fetchIncidents()
    } else if (message.type === 'incident_completed') {
      showNotificationMessage('Incident completed with postmortem.', 'success')
      incidentStore.fetchIncidents()
    } else if (message.type === 'status_update') {
      // Light refresh to reflect status changes
      incidentStore.fetchIncidents()
    } else if (message.type === 'agent_update') {
      showNotificationMessage(`Agent update: ${message.data.status}`, 'info')
    } else if (message.type === 'agent_progress') {
      // Show brief progress toast
      const task = message.data?.task || 'Working'
      showNotificationMessage(`${message.data?.agent_name || 'Agent'}: ${task}`, 'info')
    } else if (message.type === 'agent_completed') {
      showNotificationMessage(`${message.data?.agent_name || 'Agent'} completed`, 'success')
    } else if (message.type === 'agent_error') {
      const err = message.data?.error || 'Unknown error'
      showNotificationMessage(`${message.data?.agent_name || 'Agent'} error: ${err}`, 'error')
    }
  })
})
</script>

<style>
/* Import Inter font first */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar Styles */
.sidebar {
  width: 260px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 1000;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.1rem;
  font-weight: 600;
}

.nav-menu {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-right: 3px solid #fff;
}

.nav-icon {
  font-size: 1.125rem;
  width: 20px;
  text-align: center;
}

.nav-text {
  font-weight: 500;
}

.nav-badge {
  background: #ef4444;
  color: white;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
  margin-left: auto;
}

.sidebar-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  transition: background-color 0.3s ease;
}

.connection-status.connected .status-dot {
  background: #10b981;
}

/* Main Content */
.main-content {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  background: #f5f7fa;
}

/* Notification Toast */
.notification-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3b82f6;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 10000;
  min-width: 300px;
  animation: slideIn 0.3s ease;
}

.notification-toast.success {
  border-left-color: #10b981;
}

.notification-toast.warning {
  border-left-color: #f59e0b;
}

.notification-toast.error {
  border-left-color: #ef4444;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.notification-icon {
  font-size: 1.125rem;
}

.notification-message {
  font-weight: 500;
  color: #374151;
}

.notification-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.notification-close:hover {
  background: #f3f4f6;
  color: #374151;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .notification-toast {
    right: 10px;
    left: 10px;
    min-width: auto;
  }
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
