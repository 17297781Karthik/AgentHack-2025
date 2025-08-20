<template>
  <div class="incident-list">
    <!-- Search and Filter Bar -->
    <div class="search-filter-bar">
      <div class="search-section">
        <div class="search-input-container">
          <span class="search-icon">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search incidents..."
            class="search-input"
          />
        </div>
      </div>
      
      <div class="filters-section">
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="resolved">Resolved</option>
        </select>
        
        <select v-model="severityFilter" class="filter-select">
          <option value="">All Severity</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        
        <select v-model="categoryFilter" class="filter-select">
          <option value="">All Categories</option>
          <option value="performance">Performance</option>
          <option value="security">Security</option>
          <option value="infrastructure">Infrastructure</option>
          <option value="application">Application</option>
        </select>
        
        <button @click="clearFilters" class="clear-filters-btn">
          Clear Filters
        </button>
      </div>
    </div>
    
    <!-- Incidents Grid -->
    <div class="incidents-grid">
      <div v-if="filteredIncidents.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No incidents found</h3>
        <p>{{ searchQuery || hasActiveFilters ? 'Try adjusting your search or filters' : 'All systems are running normally' }}</p>
      </div>
      
      <div 
        v-for="incident in paginatedIncidents" 
        :key="incident.incident_id"
        class="incident-card"
        :class="[
          `severity-${incident.classification?.severity || 'unknown'}`,
          { 'resolved': incident.status === 'resolved' }
        ]"
        @click="$emit('selectIncident', incident)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="incident-id">
            <span class="id-label">ID:</span>
            <span class="id-value">{{ incident.incident_id }}</span>
          </div>
          <div class="incident-status">
            <span class="status-badge" :class="incident.status">
              {{ incident.status.toUpperCase() }}
            </span>
          </div>
        </div>
        
        <!-- Card Content -->
        <div class="card-content">
          <h3 class="incident-title">{{ incident.alert?.message || 'Unknown Incident' }}</h3>
          
          <div class="incident-meta">
            <div class="meta-item">
              <span class="meta-label">Category:</span>
              <span class="badge category">{{ incident.classification?.category || 'Unknown' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Severity:</span>
              <span class="badge severity" :class="incident.classification?.severity">
                {{ incident.classification?.severity || 'Unknown' }}
              </span>
            </div>
          </div>
          
          <div class="affected-services">
            <span class="services-label">Affected Services:</span>
            <div class="services-list">
              <span 
                v-for="service in incident.alert?.affected_services || ['Unknown']"
                :key="service"
                class="service-tag"
              >
                {{ service }}
              </span>
            </div>
          </div>
          
          <div class="incident-timing">
            <div class="timing-item">
              <span class="timing-label">Created:</span>
              <span class="timing-value">{{ formatDateTime(incident.created_at) }}</span>
            </div>
            <div v-if="incident.resolved_at" class="timing-item">
              <span class="timing-label">Resolved:</span>
              <span class="timing-value">{{ formatDateTime(incident.resolved_at) }}</span>
            </div>
            <div v-if="!incident.resolved_at" class="timing-item">
              <span class="timing-label">Duration:</span>
              <span class="timing-value duration">{{ getIncidentDuration(incident.created_at) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Card Actions -->
        <div class="card-actions">
          <button 
            @click.stop="$emit('viewDetails', incident)"
            class="action-btn primary"
          >
            <span class="btn-icon">👁️</span>
            View Details
          </button>
          
          <button 
            v-if="incident.status === 'active'"
            @click.stop="$emit('resolveIncident', incident.incident_id)"
            class="action-btn success"
          >
            <span class="btn-icon">✅</span>
            Resolve
          </button>
          
          <button 
            @click.stop="$emit('viewTimeline', incident)"
            class="action-btn secondary"
          >
            <span class="btn-icon">📈</span>
            Timeline
          </button>
        </div>
      </div>
    </div>
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        @click="currentPage--" 
        :disabled="currentPage <= 1"
        class="pagination-btn"
      >
        ← Previous
      </button>
      
      <div class="page-numbers">
        <button 
          v-for="page in visiblePages"
          :key="page"
          @click="currentPage = page"
          class="page-btn"
          :class="{ active: page === currentPage }"
        >
          {{ page }}
        </button>
      </div>
      
      <button 
        @click="currentPage++" 
        :disabled="currentPage >= totalPages"
        class="pagination-btn"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineEmits } from 'vue'
import type { Incident } from '@/stores/incidents'

interface Props {
  incidents: Incident[]
}

const props = defineProps<Props>()
const emit = defineEmits(['selectIncident', 'viewDetails', 'resolveIncident', 'viewTimeline'])

// Search and filter state
const searchQuery = ref('')
const statusFilter = ref('')
const severityFilter = ref('')
const categoryFilter = ref('')

// Pagination state
const currentPage = ref(1)
const itemsPerPage = ref(9)

// Computed properties
const hasActiveFilters = computed(() => 
  statusFilter.value || severityFilter.value || categoryFilter.value
)

const filteredIncidents = computed(() => {
  let filtered = props.incidents

  // Apply search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(incident => 
      incident.incident_id.toLowerCase().includes(query) ||
      incident.alert?.message?.toLowerCase().includes(query) ||
      incident.classification?.category?.toLowerCase().includes(query) ||
      incident.alert?.affected_services?.some(service => 
        service.toLowerCase().includes(query)
      )
    )
  }

  // Apply filters
  if (statusFilter.value) {
    filtered = filtered.filter(incident => incident.status === statusFilter.value)
  }

  if (severityFilter.value) {
    filtered = filtered.filter(incident => 
      incident.classification?.severity === severityFilter.value
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(incident => 
      incident.classification?.category === categoryFilter.value
    )
  }

  return filtered
})

const totalPages = computed(() => 
  Math.ceil(filteredIncidents.value.length / itemsPerPage.value)
)

const paginatedIncidents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredIncidents.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
function clearFilters() {
  searchQuery.value = ''
  statusFilter.value = ''
  severityFilter.value = ''
  categoryFilter.value = ''
  currentPage.value = 1
}

function formatDateTime(timestamp: string) {
  return new Date(timestamp).toLocaleString()
}

function getIncidentDuration(startTime: string) {
  const start = new Date(startTime)
  const now = new Date()
  const diff = now.getTime() - start.getTime()
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}
</script>

<style scoped>
.incident-list {
  padding: 1.5rem;
}

/* Search and Filter Bar */
.search-filter-bar {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.search-section {
  flex: 1;
  min-width: 300px;
}

.search-input-container {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.filters-section {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

.clear-filters-btn {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.clear-filters-btn:hover {
  background: #e5e7eb;
}

/* Incidents Grid */
.incidents-grid {
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

.empty-state h3 {
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
  color: #374151;
}

/* Incident Cards */
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

.incident-card.severity-critical { border-left-color: #dc2626; }
.incident-card.severity-high { border-left-color: #ea580c; }
.incident-card.severity-medium { border-left-color: #d97706; }
.incident-card.severity-low { border-left-color: #65a30d; }

.incident-card.resolved {
  opacity: 0.7;
  background: #f9fafb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.incident-id {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.id-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.id-value {
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

.incident-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.incident-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.meta-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge.category {
  background: #eff6ff;
  color: #1d4ed8;
}

.badge.severity.critical {
  background: #fef2f2;
  color: #dc2626;
}

.badge.severity.high {
  background: #fff7ed;
  color: #ea580c;
}

.badge.severity.medium {
  background: #fffbeb;
  color: #d97706;
}

.badge.severity.low {
  background: #f7fee7;
  color: #65a30d;
}

.affected-services {
  margin-bottom: 1rem;
}

.services-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  display: block;
  margin-bottom: 0.5rem;
}

.services-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.service-tag {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.incident-timing {
  margin-bottom: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.timing-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.timing-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.timing-value {
  font-size: 0.875rem;
  color: #374151;
}

.timing-value.duration {
  color: #dc2626;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: none;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.primary {
  background: #3b82f6;
  color: white;
}

.action-btn.primary:hover {
  background: #2563eb;
}

.action-btn.success {
  background: #10b981;
  color: white;
}

.action-btn.success:hover {
  background: #059669;
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.secondary:hover {
  background: #e5e7eb;
}

.btn-icon {
  font-size: 0.875rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f3f4f6;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-btn {
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover {
  background: #f3f4f6;
}

.page-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

/* Responsive Design */
@media (max-width: 768px) {
  .incidents-grid {
    grid-template-columns: 1fr;
  }
  
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters-section {
    justify-content: center;
  }
  
  .card-actions {
    justify-content: center;
  }
}
</style>
