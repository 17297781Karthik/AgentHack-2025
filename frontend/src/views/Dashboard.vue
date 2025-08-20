<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-white">DevOps Crisis Dashboard</h1>
      <div class="flex items-center space-x-4">
        <button 
          @click="refreshData"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
          :disabled="loading"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Status Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Active Incidents -->
      <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm font-medium">Active Incidents</p>
            <p class="text-3xl font-bold text-white">{{ incidentStore.activeIncidents.length }}</p>
          </div>
          <div class="bg-red-500 bg-opacity-20 p-3 rounded-lg">
            <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
        </div>
        <div class="mt-4">
          <div class="flex items-center text-sm">
            <span class="text-green-400">+{{ newIncidentsToday }}</span>
            <span class="text-gray-400 ml-1">today</span>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm font-medium">System Health</p>
            <p class="text-3xl font-bold text-green-400">{{ systemHealthPercent }}%</p>
          </div>
          <div class="bg-green-500 bg-opacity-20 p-3 rounded-lg">
            <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <div class="mt-4">
          <div class="flex items-center text-sm">
            <span class="text-gray-400">{{ healthyServices }}/{{ totalServices }} services healthy</span>
          </div>
        </div>
      </div>

      <!-- Average Resolution Time -->
      <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm font-medium">Avg Resolution Time</p>
            <p class="text-3xl font-bold text-blue-400">{{ averageResolutionTime }}</p>
          </div>
          <div class="bg-blue-500 bg-opacity-20 p-3 rounded-lg">
            <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <div class="mt-4">
          <div class="flex items-center text-sm">
            <span class="text-green-400">-15%</span>
            <span class="text-gray-400 ml-1">vs last week</span>
          </div>
        </div>
      </div>

      <!-- AI Agent Status -->
      <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm font-medium">AI Agents</p>
            <p class="text-3xl font-bold text-purple-400">{{ activeAgents }}/3</p>
          </div>
          <div class="bg-purple-500 bg-opacity-20 p-3 rounded-lg">
            <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
          </div>
        </div>
        <div class="mt-4">
          <div class="flex items-center text-sm">
            <span class="text-green-400">●</span>
            <span class="text-gray-400 ml-1">All agents online</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Incident Severity Chart -->
      <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 class="text-lg font-semibold text-white mb-4">Incident Severity Distribution</h3>
        <div class="h-64">
          <canvas ref="severityChart"></canvas>
        </div>
      </div>

      <!-- Incident Timeline Chart -->
      <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 class="text-lg font-semibold text-white mb-4">Incidents Over Time</h3>
        <div class="h-64">
          <canvas ref="timelineChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Recent Incidents Table -->
    <div class="bg-gray-800 rounded-lg border border-gray-700">
      <div class="px-6 py-4 border-b border-gray-700">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-semibold text-white">Recent Incidents</h3>
          <router-link 
            to="/incidents" 
            class="text-blue-400 hover:text-blue-300 text-sm font-medium"
          >
            View All →
          </router-link>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Severity</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700">
            <tr v-for="incident in incidentStore.recentIncidents" :key="incident.incident_id" class="hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                {{ incident.incident_id.substring(0, 8) }}...
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-white">
                {{ incident.alert?.message || 'Incident' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getSeverityClass(incident.classification?.severity || incident.alert?.severity || 'low')"
                >
                  {{ (incident.classification?.severity || incident.alert?.severity || 'low').toUpperCase() }}
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
                <router-link 
                  :to="`/incidents/${incident.incident_id}`"
                  class="text-blue-400 hover:text-blue-300 font-medium"
                >
                  View Details
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="incidentStore.incidents.length === 0" class="text-center py-8">
          <p class="text-gray-400">No incidents to display</p>
          <router-link 
            to="/simulation" 
            class="text-blue-400 hover:text-blue-300 mt-2 inline-block"
          >
            Run a simulation to generate sample incidents
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useIncidentStore } from '../stores/incidents'
import Chart from 'chart.js/auto'

const incidentStore = useIncidentStore()
const loading = ref(false)
const severityChart = ref<HTMLCanvasElement>()
const timelineChart = ref<HTMLCanvasElement>()

// Computed properties for dashboard stats
const newIncidentsToday = computed(() => {
  const today = new Date().toDateString()
  return incidentStore.incidents.filter(incident => 
    new Date(incident.created_at).toDateString() === today
  ).length
})

const systemHealthPercent = computed(() => {
  // Mock calculation based on incidents
  const criticalIncidents = incidentStore.activeIncidents.filter(i => 
    (i.classification?.severity || i.alert?.severity) === 'critical'
  ).length
  const highIncidents = incidentStore.activeIncidents.filter(i => 
    (i.classification?.severity || i.alert?.severity) === 'high'
  ).length
  
  const baseHealth = 100
  const healthImpact = (criticalIncidents * 20) + (highIncidents * 10)
  return Math.max(0, baseHealth - healthImpact)
})

const healthyServices = computed(() => {
  return Math.max(0, totalServices.value - Math.floor(incidentStore.activeIncidents.length / 2))
})

const totalServices = ref(12) // Mock total services

const averageResolutionTime = computed(() => {
  // Mock calculation
  return '2.3h'
})

const activeAgents = ref(3) // All agents are active

async function refreshData() {
  loading.value = true
  try {
    // In a real app, this would fetch fresh data from the API
    await new Promise(resolve => setTimeout(resolve, 1000))
  } finally {
    loading.value = false
  }
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
    active: 'bg-blue-500 text-white',
    resolved: 'bg-green-500 text-white',
    open: 'bg-red-500 text-white',
    analyzing: 'bg-yellow-500 text-black',
    resolving: 'bg-blue-500 text-white',
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

function createSeverityChart() {
  if (!severityChart.value) return
  
  const ctx = severityChart.value.getContext('2d')
  if (!ctx) return

  const severityData = incidentStore.severityStats
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [
          severityData.critical,
          severityData.high,
          severityData.medium,
          severityData.low
        ],
        backgroundColor: [
          '#ef4444', // red-500
          '#f97316', // orange-500
          '#eab308', // yellow-500
          '#22c55e'  // green-500
        ],
        borderWidth: 2,
        borderColor: '#374151'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#d1d5db',
            padding: 20,
            usePointStyle: true
          }
        }
      }
    }
  })
}

function createTimelineChart() {
  if (!timelineChart.value) return
  
  const ctx = timelineChart.value.getContext('2d')
  if (!ctx) return

  // Generate mock data for the last 7 days
  const days = []
  const incidentCounts = []
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    days.push(date.toLocaleDateString('en-US', { weekday: 'short' }))
    
    // Mock incident count for each day
    incidentCounts.push(Math.floor(Math.random() * 10) + 1)
  }
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: days,
      datasets: [{
        label: 'Incidents',
        data: incidentCounts,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: '#374151'
          },
          ticks: {
            color: '#d1d5db'
          }
        },
        x: {
          grid: {
            color: '#374151'
          },
          ticks: {
            color: '#d1d5db'
          }
        }
      }
    }
  })
}

onMounted(async () => {
  await incidentStore.fetchIncidents()
  await nextTick()
  createSeverityChart()
  createTimelineChart()
})
</script>
