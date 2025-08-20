import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export const useWebSocketStore = defineStore('websocket', () => {
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectInterval = ref<number | null>(null)
  const messageHandlers = ref<Array<(message: WebSocketMessage) => void>>([])
  const connectionAttempts = ref(0)
  const maxReconnectAttempts = 5

  const wsUrl = computed(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const port = '8000' // FastAPI backend port
    return `${protocol}//${host}:${port}/ws`
  })

  function connect() {
    try {
      socket.value = new WebSocket(wsUrl.value)
      
      socket.value.onopen = () => {
        console.log('WebSocket connected')
        isConnected.value = true
        connectionAttempts.value = 0
        
        // Clear any existing reconnect interval
        if (reconnectInterval.value) {
          clearInterval(reconnectInterval.value)
          reconnectInterval.value = null
        }
      }
      
      socket.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log('WebSocket message received:', message)
          
          // Call all registered message handlers
          messageHandlers.value.forEach(handler => {
            try {
              handler(message)
            } catch (error) {
              console.error('Error in message handler:', error)
            }
          })
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      socket.value.onclose = () => {
        console.log('WebSocket disconnected')
        isConnected.value = false
        socket.value = null
        
        // Attempt to reconnect if we haven't exceeded max attempts
        if (connectionAttempts.value < maxReconnectAttempts) {
          scheduleReconnect()
        } else {
          console.error('Max reconnection attempts reached')
        }
      }
      
      socket.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        isConnected.value = false
      }
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      scheduleReconnect()
    }
  }

  function disconnect() {
    if (socket.value) {
      socket.value.close()
    }
    
    if (reconnectInterval.value) {
      clearInterval(reconnectInterval.value)
      reconnectInterval.value = null
    }
    
    isConnected.value = false
    socket.value = null
    connectionAttempts.value = 0
  }

  function scheduleReconnect() {
    if (reconnectInterval.value) {
      return // Already scheduled
    }
    
    connectionAttempts.value++
    const delay = Math.min(1000 * Math.pow(2, connectionAttempts.value), 30000) // Exponential backoff, max 30s
    
    console.log(`Scheduling reconnect attempt ${connectionAttempts.value} in ${delay}ms`)
    
    reconnectInterval.value = window.setTimeout(() => {
      reconnectInterval.value = null
      connect()
    }, delay)
  }

  function sendMessage(message: any) {
    if (socket.value && isConnected.value) {
      try {
        socket.value.send(JSON.stringify(message))
        return true
      } catch (error) {
        console.error('Error sending WebSocket message:', error)
        return false
      }
    } else {
      console.warn('WebSocket not connected, cannot send message')
      return false
    }
  }

  function onMessage(handler: (message: WebSocketMessage) => void) {
    messageHandlers.value.push(handler)
    
    // Return unsubscribe function
    return () => {
      const index = messageHandlers.value.indexOf(handler)
      if (index > -1) {
        messageHandlers.value.splice(index, 1)
      }
    }
  }

  function removeMessageHandler(handler: (message: WebSocketMessage) => void) {
    const index = messageHandlers.value.indexOf(handler)
    if (index > -1) {
      messageHandlers.value.splice(index, 1)
    }
  }

  // Reset store
  function $reset() {
    disconnect()
    messageHandlers.value = []
    connectionAttempts.value = 0
  }

  return {
    // State
    isConnected,
    connectionAttempts,
    
    // Actions
    connect,
    disconnect,
    sendMessage,
    onMessage,
    removeMessageHandler,
    $reset
  }
})
