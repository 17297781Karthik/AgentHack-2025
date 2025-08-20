<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-white">Incident Simulation</h1>
        <p class="text-gray-400 mt-2">Test the DevOps Crisis Commander with realistic incident scenarios</p>
      </div>
    </div>

    <!-- Simulation Controls -->
    <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 class="text-xl font-semibold text-white mb-4">Simulation Controls</h2>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Scenario Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Select Scenario Type
          </label>
          <select 
            v-model="selectedScenario" 
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Choose a scenario...</option>
            <option value="database_performance">Database Performance Issue</option>
            <option value="security_breach">Security Breach Detection</option>
            <option value="service_outage">Critical Service Outage</option>
            <option value="memory_leak">Application Memory Leak</option>
            <option value="network_latency">Network Latency Spike</option>
            <option value="disk_space">Disk Space Critical</option>
            <option value="ssl_expiry">SSL Certificate Expiry</option>
            <option value="authentication_failure">Authentication System Failure</option>
            <option value="backup_failure">Backup System Failure</option>
            <option value="random">Random Scenario</option>
          </select>
        </div>

        <!-- Severity Level -->
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Severity Level
          </label>
          <select 
            v-model="selectedSeverity" 
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Auto-detect</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      <!-- Simulation Buttons -->
      <div class="flex space-x-4 mt-6">
        <button
          @click="runSingleSimulation"
          :disabled="!selectedScenario || isRunning"
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg flex items-center space-x-2"
        >
          <svg v-if="isRunning" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span>{{ isRunning ? 'Running...' : 'Run Single Simulation' }}</span>
        </button>

        <button
          @click="runBatchSimulation"
          :disabled="isRunning"
          class="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg flex items-center space-x-2"
        >
          <span>Run Batch Simulation (5x)</span>
        </button>

        <button
          @click="clearSimulations"
          :disabled="isRunning"
          class="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg flex items-center space-x-2"
        >
          <span>Clear All</span>
        </button>
      </div>
    </div>

    <!-- AI Agent Status -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div 
        v-for="agent in agentStatus" 
        :key="agent.name"
        class="bg-gray-800 rounded-lg p-6 border border-gray-700"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">{{ agent.name }}</h3>
          <div 
            class="w-3 h-3 rounded-full"
            :class="agent.status === 'active' ? 'bg-green-400' : agent.status === 'busy' ? 'bg-yellow-400' : 'bg-red-400'"
          ></div>
        </div>
        
        <p class="text-gray-400 text-sm mb-3">{{ agent.description }}</p>
        
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">Status:</span>
            <span class="text-white capitalize">{{ agent.status }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">Processed:</span>
            <span class="text-white">{{ agent.processedCount }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">Avg Time:</span>
            <span class="text-white">{{ agent.avgProcessingTime }}s</span>
          </div>
        </div>

        <!-- Progress bar for active agents -->
        <div v-if="agent.status === 'busy'" class="mt-4">
          <div class="w-full bg-gray-700 rounded-full h-2">
            <div 
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: agent.progress + '%' }"
            ></div>
          </div>
          <p class="text-xs text-gray-400 mt-1">{{ agent.currentTask }}</p>
        </div>
      </div>
    </div>

    <!-- Simulation Log -->
    <div class="bg-gray-800 rounded-lg border border-gray-700">
      <div class="px-6 py-4 border-b border-gray-700">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-semibold text-white">Simulation Log</h3>
          <button 
            @click="clearLog"
            class="text-gray-400 hover:text-white text-sm"
          >
            Clear Log
          </button>
        </div>
      </div>
      
      <div class="h-96 overflow-y-auto p-4">
        <div v-if="simulationLog.length === 0" class="text-gray-400 text-center py-8">
          No simulation activity yet. Run a simulation to see the AI agents in action.
        </div>
        
        <div 
          v-for="(entry, index) in simulationLog" 
          :key="index"
          class="mb-3 p-3 bg-gray-700 rounded border-l-4"
          :class="getLogEntryClass(entry.level)"
        >
          <div class="flex justify-between items-start mb-1">
            <span class="text-sm font-medium text-white">{{ entry.message }}</span>
            <span class="text-xs text-gray-400">{{ formatTime(entry.timestamp) }}</span>
          </div>
          <div v-if="entry.details" class="text-xs text-gray-300 mt-1">
            {{ entry.details }}
          </div>
          <div v-if="entry.data" class="text-xs text-gray-400 mt-2 font-mono">
            <pre class="whitespace-pre-wrap">{{ JSON.stringify(entry.data, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useIncidentStore } from '../stores/incidents'
import { useWebSocketStore } from '../stores/websocket'
import axios from 'axios'

interface LogEntry {
  timestamp: Date
  level: 'info' | 'success' | 'warning' | 'error'
  message: string
  details?: string
  data?: any
}

interface AgentStatus {
  name: string
  description: string
  status: 'active' | 'busy' | 'error'
  processedCount: number
  avgProcessingTime: number
  progress: number
  currentTask?: string
}

const incidentStore = useIncidentStore()
const websocketStore = useWebSocketStore()

const selectedScenario = ref('')
const selectedSeverity = ref('')
const isRunning = ref(false)
const simulationLog = ref<LogEntry[]>([])

const agentStatus = reactive<AgentStatus[]>([
  {
    name: 'Incident Classifier',
    description: 'Analyzes and categorizes incoming incidents',
    status: 'active',
    processedCount: 0,
    avgProcessingTime: 2.3,
    progress: 0
  },
  {
    name: 'Resolution Advisor',
    description: 'Provides contextual resolution guidance',
    status: 'active',
    processedCount: 0,
    avgProcessingTime: 4.1,
    progress: 0
  },
  {
    name: 'PostMortem Generator',
    description: 'Creates comprehensive incident reports',
    status: 'active',
    processedCount: 0,
    avgProcessingTime: 6.8,
    progress: 0
  }
])

const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`
const scenarios = ref<Record<string, { name: string; description: string; severity: string; type: string; affected_services: string[] }>>({})

async function runSingleSimulation() {
  if (!selectedScenario.value || isRunning.value) return
  
  isRunning.value = true
  addLogEntry('info', 'Starting single incident simulation...', `Scenario: ${selectedScenario.value}`)
  
  try {
    const response = await axios.post(`${API_BASE_URL}/incidents/simulate`, {
      scenario_name: selectedScenario.value || undefined
    })
    
    addLogEntry('success', 'Simulation request sent successfully', `Incident ID: ${response.data.incident_id}`)
    
    // Simulate agent processing
    await simulateAgentProcessing()
    
  } catch (error) {
    console.error('Simulation error:', error)
    addLogEntry('error', 'Simulation failed', error instanceof Error ? error.message : 'Unknown error')
  } finally {
    isRunning.value = false
  }
}

async function runBatchSimulation() {
  if (isRunning.value) return
  
  isRunning.value = true
  addLogEntry('info', 'Starting batch simulation...', '5 incidents will be generated')
  
  try {
    const scenarioList = Object.keys(scenarios.value)
    for (let i = 0; i < 5; i++) {
      const scenario = scenarioList[i % (scenarioList.length || 1)] || undefined
      
      addLogEntry('info', `Generating incident ${i + 1}/5`, `Scenario: ${scenario}`)
      
      const response = await axios.post(`${API_BASE_URL}/incidents/simulate`, {
        scenario_name: scenario
      })
      
      addLogEntry('success', `Incident ${i + 1} created`, `ID: ${response.data.incident_id}`)
      
      // Delay between simulations
      await new Promise(resolve => setTimeout(resolve, 2000))
    }
    
    addLogEntry('success', 'Batch simulation completed', 'All 5 incidents generated successfully')
    
  } catch (error) {
    console.error('Batch simulation error:', error)
    addLogEntry('error', 'Batch simulation failed', error instanceof Error ? error.message : 'Unknown error')
  } finally {
    isRunning.value = false
  }
}

async function simulateAgentProcessing() {
  // Simulate the three-agent workflow
  const agents = ['Incident Classifier', 'Resolution Advisor', 'PostMortem Generator']
  
  for (let i = 0; i < agents.length; i++) {
    const agent = agentStatus[i]
    agent.status = 'busy'
    agent.currentTask = `Processing incident...`
    agent.progress = 0
    
    addLogEntry('info', `${agent.name} started processing`, 'Analyzing incident data...')
    
    // Simulate progress
    for (let progress = 0; progress <= 100; progress += 10) {
      agent.progress = progress
      await new Promise(resolve => setTimeout(resolve, 200))
    }
    
    agent.status = 'active'
    agent.processedCount++
    agent.progress = 0
    agent.currentTask = undefined
    
    addLogEntry('success', `${agent.name} completed processing`, `Processing time: ${agent.avgProcessingTime}s`)
  }
}

function clearSimulations() {
  // In a real app, this would call an API to clear incidents
  incidentStore.$reset()
  addLogEntry('info', 'All simulations cleared', 'Incident store has been reset')
}

function addLogEntry(level: LogEntry['level'], message: string, details?: string, data?: any) {
  simulationLog.value.unshift({
    timestamp: new Date(),
    level,
    message,
    details,
    data
  })
  
  // Keep only last 100 entries
  if (simulationLog.value.length > 100) {
    simulationLog.value = simulationLog.value.slice(0, 100)
  }
}

function clearLog() {
  simulationLog.value = []
}

function getLogEntryClass(level: string) {
  const classes = {
    info: 'border-blue-500',
    success: 'border-green-500',
    warning: 'border-yellow-500',
    error: 'border-red-500'
  }
  return classes[level as keyof typeof classes] || 'border-gray-500'
}

function formatTime(date: Date) {
  return date.toLocaleTimeString('en-US', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// WebSocket message handler
let unsubscribeWebSocket: (() => void) | null = null

onMounted(async () => {
  // Listen for WebSocket messages about incident processing
  unsubscribeWebSocket = websocketStore.onMessage((message) => {
    if (message.type === 'incident_created') {
      addLogEntry('success', 'New incident detected', `ID: ${message.data.incident_id}`)
    } else if (message.type === 'agent_progress') {
      const agentName = message.data.agent_name
      const agent = agentStatus.find(a => a.name.toLowerCase().includes(agentName.toLowerCase()))
      if (agent) {
        agent.status = 'busy'
        agent.currentTask = message.data.task
        agent.progress = message.data.progress || 0
      }
      addLogEntry('info', `${agentName} progress update`, message.data.task)
    } else if (message.type === 'agent_completed') {
      const agentName = message.data.agent_name
      const agent = agentStatus.find(a => a.name.toLowerCase().includes(agentName.toLowerCase()))
      if (agent) {
        agent.status = 'active'
        agent.processedCount++
        agent.progress = 0
        agent.currentTask = undefined
      }
      addLogEntry('success', `${agentName} completed`, `Duration: ${message.data.duration}s`)
    }
  })

  // Load scenarios from backend for better UX
  try {
    const { data } = await axios.get(`${API_BASE_URL}/scenarios`)
    scenarios.value = data || {}
  } catch (e) {
    console.warn('Failed to load scenarios list from backend', e)
  }
})

onUnmounted(() => {
  if (unsubscribeWebSocket) {
    unsubscribeWebSocket()
  }
})
</script>
