<template>
  <div class="incident-details">
    <div class="modal-header">
      <h2>🚨 Incident Details</h2>
      <button @click="$emit('close')" class="close-btn">✕</button>
    </div>
    
    <div class="modal-body">
      <!-- Incident Overview -->
      <section class="details-section">
        <h3>📋 Overview</h3>
        <div class="overview-grid">
          <div class="info-item">
            <label>Incident ID:</label>
            <span class="incident-id">{{ incident.incident_id }}</span>
          </div>
          <div class="info-item">
            <label>Status:</label>
            <span class="status-badge" :class="incident.status">{{ incident.status }}</span>
          </div>
          <div class="info-item">
            <label>Created:</label>
            <span>{{ formatDateTime(incident.created_at) }}</span>
          </div>
          <div class="info-item">
            <label>Category:</label>
            <span class="badge">{{ incident.classification?.category || 'Unknown' }}</span>
          </div>
          <div class="info-item">
            <label>Severity:</label>
            <span class="badge severity" :class="`severity-${incident.classification?.severity}`">
              {{ incident.classification?.severity || 'Unknown' }}
            </span>
          </div>
          <div class="info-item">
            <label>Confidence:</label>
            <span>{{ Math.round((incident.classification?.confidence || 0) * 100) }}%</span>
          </div>
        </div>
      </section>

      <!-- Alert Details -->
      <section class="details-section">
        <h3>🔔 Alert Information</h3>
        <div class="alert-details">
          <div class="alert-message">
            <strong>Message:</strong> {{ incident.alert?.message || 'No message' }}
          </div>
          <div class="alert-meta">
            <div><strong>Type:</strong> {{ incident.alert?.alert_type || 'Unknown' }}</div>
            <div><strong>Source:</strong> {{ incident.alert?.source || 'Unknown' }}</div>
            <div><strong>Environment:</strong> {{ incident.alert?.environment || 'Unknown' }}</div>
          </div>
          <div class="affected-services">
            <strong>Affected Services:</strong>
            <div class="services-list">
              <span v-for="service in incident.alert?.affected_services" 
                    :key="service" 
                    class="service-tag">
                {{ service }}
              </span>
            </div>
          </div>
          <div v-if="incident.alert?.metrics" class="metrics">
            <strong>Metrics:</strong>
            <div class="metrics-grid">
              <div v-for="(value, key) in incident.alert.metrics" 
                   :key="key" 
                   class="metric-item">
                <span class="metric-name">{{ formatMetricName(String(key)) }}:</span>
                <span class="metric-value">{{ formatMetricValue(String(key), value) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Classification Results -->
      <section v-if="incident.classification" class="details-section">
        <h3>🔍 AI Classification</h3>
        <div class="classification-results">
          <div class="classification-tags">
            <strong>Tags:</strong>
            <span v-for="tag in incident.classification.tags" 
                  :key="tag" 
                  class="tag">
              {{ tag }}
            </span>
          </div>
          <div class="impact-assessment">
            <strong>Estimated Impact:</strong>
            <p>{{ incident.classification.estimated_impact }}</p>
          </div>
          <div class="reasoning">
            <strong>Classification Reasoning:</strong>
            <p>{{ incident.classification.reasoning }}</p>
          </div>
        </div>
      </section>

      <!-- Resolution Plan -->
      <section v-if="incident.resolution" class="details-section">
        <h3>🛠️ Resolution Plan</h3>
        <div class="resolution-overview">
          <div class="resolution-meta">
            <div><strong>Estimated Time:</strong> {{ incident.resolution.estimated_time_minutes }} minutes</div>
            <div><strong>Success Probability:</strong> {{ Math.round(incident.resolution.success_probability * 100) }}%</div>
            <div><strong>Human Approval Required:</strong> {{ incident.resolution.human_approval_required ? 'Yes' : 'No' }}</div>
          </div>
          
          <div class="prerequisites" v-if="incident.resolution.prerequisites?.length">
            <strong>Prerequisites:</strong>
            <ul>
              <li v-for="prereq in incident.resolution.prerequisites" :key="prereq">
                {{ prereq }}
              </li>
            </ul>
          </div>

          <div class="resolution-steps">
            <strong>Resolution Steps:</strong>
            <div class="steps-list">
              <div v-for="step in incident.resolution.recommended_steps" 
                   :key="step.step_number" 
                   class="step-card">
                <div class="step-header">
                  <span class="step-number">{{ step.step_number }}</span>
                  <span class="step-title">{{ step.description }}</span>
                  <span class="risk-level" :class="`risk-${step.risk_level}`">
                    {{ step.risk_level }} risk
                  </span>
                </div>
                <div class="step-details" v-if="step.command">
                  <strong>Command:</strong>
                  <code class="command">{{ step.command }}</code>
                </div>
                <div class="step-details">
                  <strong>Expected Result:</strong>
                  <span>{{ step.expected_result }}</span>
                </div>
                <div class="step-meta">
                  <span>Automation: {{ step.automation_possible ? 'Possible' : 'Manual' }}</span>
                  <span v-if="step.rollback_command">Rollback Available</span>
                </div>
              </div>
            </div>
          </div>

          <div class="parallel-actions" v-if="incident.resolution.parallel_actions?.length">
            <strong>Parallel Actions:</strong>
            <ul>
              <li v-for="action in incident.resolution.parallel_actions" :key="action">
                {{ action }}
              </li>
            </ul>
          </div>

          <div class="rollback-plan" v-if="incident.resolution.rollback_plan?.length">
            <strong>Rollback Plan:</strong>
            <ol>
              <li v-for="step in incident.resolution.rollback_plan" :key="step">
                {{ step }}
              </li>
            </ol>
          </div>

          <div class="reasoning">
            <strong>Resolution Reasoning:</strong>
            <p>{{ incident.resolution.reasoning }}</p>
          </div>
        </div>
      </section>

      <!-- Timeline -->
      <section v-if="incident.timeline?.length" class="details-section">
        <h3>⏱️ Timeline</h3>
        <div class="timeline">
          <div v-for="event in incident.timeline" 
               :key="event.timestamp" 
               class="timeline-item">
            <div class="timeline-time">{{ formatDateTime(event.timestamp) }}</div>
            <div class="timeline-content">
              <div class="timeline-event">{{ event.event }}</div>
              <div v-if="event.details" class="timeline-details">
                {{ typeof event.details === 'string' ? event.details : JSON.stringify(event.details) }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Postmortem (if resolved) -->
      <section v-if="incident.postmortem" class="details-section">
        <h3>📊 Post-Mortem Report</h3>
        <div class="postmortem">
          <div class="postmortem-summary">
            <strong>Summary:</strong>
            <p>{{ incident.postmortem.summary }}</p>
          </div>
          
          <div class="root-cause">
            <strong>Root Cause:</strong>
            <p>{{ incident.postmortem.root_cause }}</p>
          </div>

          <div class="lessons-learned" v-if="incident.postmortem.lessons_learned?.length">
            <strong>Lessons Learned:</strong>
            <ul>
              <li v-for="lesson in incident.postmortem.lessons_learned" :key="lesson">
                {{ lesson }}
              </li>
            </ul>
          </div>

          <div class="action-items" v-if="incident.postmortem.action_items?.length">
            <strong>Action Items:</strong>
            <ul>
              <li v-for="item in incident.postmortem.action_items" :key="item">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>

    <div class="modal-footer">
      <button @click="$emit('close')" class="btn-secondary">Close</button>
      <button v-if="incident.status === 'active'" 
              @click="$emit('resolve', incident.incident_id)" 
              class="btn-primary">
        Mark as Resolved
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  incident: {
    type: Object,
    required: true
  }
})

defineEmits(['close', 'resolve'])

const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

const formatMetricName = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatMetricValue = (key: string, value: any) => {
  if (key.includes('usage') || key.includes('percent')) {
    return `${value}%`
  }
  if (key.includes('bytes') || key.includes('size')) {
    return `${value} bytes`
  }
  return value
}
</script>

<style scoped>
.incident-details {
  width: 100%;
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: rgba(0,0,0,0.1);
}

.modal-body {
  padding: 1.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

.details-section {
  margin-bottom: 2rem;
}

.details-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.875rem;
}

.incident-id {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.active {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.resolved {
  background: #d1fae5;
  color: #065f46;
}

.badge {
  padding: 0.25rem 0.75rem;
  background: #e5e7eb;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge.severity {
  background: #fef3c7;
  color: #92400e;
}

.severity-critical {
  background: #fee2e2 !important;
  color: #991b1b !important;
}

.severity-high {
  background: #fef3c7 !important;
  color: #92400e !important;
}

.severity-medium {
  background: #dbeafe !important;
  color: #1e40af !important;
}

.severity-low {
  background: #d1fae5 !important;
  color: #065f46 !important;
}

.alert-details {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.alert-message {
  margin-bottom: 1rem;
  font-size: 1rem;
}

.alert-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.services-list {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.service-tag {
  background: #3b82f6;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.metric-item {
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}

.metric-name {
  font-weight: 600;
  color: #6b7280;
}

.metric-value {
  font-weight: 700;
  color: #1f2937;
  margin-left: 0.5rem;
}

.classification-results > div {
  margin-bottom: 1rem;
}

.classification-tags .tag {
  background: #e0e7ff;
  color: #3730a3;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}

.resolution-overview > div {
  margin-bottom: 1.5rem;
}

.resolution-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  background: #f0f9ff;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #0ea5e9;
}

.prerequisites ul, .parallel-actions ul, .rollback-plan ol, .lessons-learned ul, .action-items ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.steps-list {
  margin-top: 1rem;
}

.step-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 0.75rem;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.step-number {
  background: #3b82f6;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  flex-shrink: 0;
}

.step-title {
  flex: 1;
  font-weight: 600;
}

.risk-level {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.risk-low {
  background: #d1fae5;
  color: #065f46;
}

.risk-medium {
  background: #fef3c7;
  color: #92400e;
}

.risk-high {
  background: #fee2e2;
  color: #991b1b;
}

.step-details {
  margin-bottom: 0.75rem;
}

.command {
  background: #1f2937;
  color: #f9fafb;
  padding: 0.5rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
  display: block;
  margin-top: 0.25rem;
  overflow-x: auto;
}

.step-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0.75rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item {
  position: relative;
  margin-bottom: 1.5rem;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -1.25rem;
  top: 0.25rem;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
}

.timeline-time {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.timeline-event {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.timeline-details {
  font-size: 0.875rem;
  color: #6b7280;
}

.postmortem {
  background: #f0f9ff;
  padding: 1.5rem;
  border-radius: 6px;
  border: 1px solid #0ea5e9;
}

.postmortem > div {
  margin-bottom: 1rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}
</style>
