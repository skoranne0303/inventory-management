<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'create' ? 'Create Purchase Order' : 'Purchase Order Details' }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <!-- Item context header -->
            <div class="item-context">
              <div class="item-context-info">
                <div class="item-name">{{ backlogItem.item_name }}</div>
                <div class="item-sku">SKU: {{ backlogItem.item_sku }}</div>
              </div>
              <span class="priority-badge" :class="backlogItem.priority">
                {{ backlogItem.priority }} Priority
              </span>
            </div>

            <!-- Create mode: form -->
            <form v-if="mode === 'create'" @submit.prevent="submitForm" class="po-form">
              <div class="form-group">
                <label class="form-label" for="supplier-name">Supplier Name</label>
                <input
                  id="supplier-name"
                  v-model="form.supplier_name"
                  type="text"
                  class="form-input"
                  placeholder="Enter supplier name"
                  required
                  :disabled="submitting"
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="quantity">Quantity to Order</label>
                <input
                  id="quantity"
                  v-model.number="form.quantity"
                  type="number"
                  class="form-input"
                  :min="1"
                  required
                  :disabled="submitting"
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="unit-cost">Unit Cost ($)</label>
                <input
                  id="unit-cost"
                  v-model.number="form.unit_cost"
                  type="number"
                  class="form-input"
                  step="0.01"
                  min="0.01"
                  placeholder="0.00"
                  required
                  :disabled="submitting"
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="delivery-date">Expected Delivery Date</label>
                <input
                  id="delivery-date"
                  v-model="form.expected_delivery_date"
                  type="date"
                  class="form-input"
                  required
                  :disabled="submitting"
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="notes">Notes <span class="optional">(optional)</span></label>
                <textarea
                  id="notes"
                  v-model="form.notes"
                  class="form-textarea"
                  rows="3"
                  placeholder="Any additional notes..."
                  :disabled="submitting"
                ></textarea>
              </div>

              <div v-if="submitError" class="error-message">{{ submitError }}</div>
            </form>

            <!-- View mode: read-only info grid -->
            <div v-else class="info-grid">
              <div class="info-item">
                <div class="info-label">Supplier Name</div>
                <div class="info-value">{{ viewPO.supplier_name || 'N/A' }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">Quantity</div>
                <div class="info-value">{{ viewPO.quantity != null ? viewPO.quantity + ' units' : 'N/A' }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">Unit Cost</div>
                <div class="info-value">{{ formatCurrency(viewPO.unit_cost) }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">Total Cost</div>
                <div class="info-value">{{ formatCurrency(totalCost) }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">Expected Delivery</div>
                <div class="info-value">{{ formatDate(viewPO.expected_delivery_date) }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">Status</div>
                <div class="info-value">
                  <span class="status-badge" :class="(viewPO.status || 'pending').toLowerCase()">
                    {{ viewPO.status || 'Pending' }}
                  </span>
                </div>
              </div>

              <div v-if="viewPO.notes" class="info-item info-item-full">
                <div class="info-label">Notes</div>
                <div class="info-value">{{ viewPO.notes }}</div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="close" :disabled="submitting">Close</button>
            <button
              v-if="mode === 'create'"
              class="btn btn-primary"
              @click="submitForm"
              :disabled="submitting"
            >
              {{ submitting ? 'Creating...' : 'Create Purchase Order' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { api } from '../api'

export default {
  name: 'PurchaseOrderModal',

  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    backlogItem: {
      type: Object,
      default: null
    },
    mode: {
      type: String,
      default: 'create',
      validator: (value) => ['create', 'view'].includes(value)
    }
  },

  emits: ['close', 'po-created'],

  setup(props, { emit }) {
    const submitting = ref(false)
    const submitError = ref(null)

    const form = ref({
      supplier_name: '',
      quantity: 0,
      unit_cost: null,
      expected_delivery_date: '',
      notes: ''
    })

    // Reset form when modal opens in create mode
    watch(
      () => props.isOpen,
      (isOpen) => {
        if (isOpen && props.mode === 'create' && props.backlogItem) {
          const shortage = (props.backlogItem.quantity_needed || 0) - (props.backlogItem.quantity_available || 0)
          form.value = {
            supplier_name: '',
            quantity: Math.max(1, shortage),
            unit_cost: null,
            expected_delivery_date: '',
            notes: ''
          }
          submitError.value = null
          submitting.value = false
        }
      }
    )

    // Also reset when backlogItem changes while open
    watch(
      () => props.backlogItem,
      (item) => {
        if (props.isOpen && props.mode === 'create' && item) {
          const shortage = (item.quantity_needed || 0) - (item.quantity_available || 0)
          form.value.quantity = Math.max(1, shortage)
        }
      }
    )

    const viewPO = computed(() => {
      return (props.backlogItem && props.backlogItem.purchase_order) || {}
    })

    const totalCost = computed(() => {
      const po = viewPO.value
      if (po.quantity != null && po.unit_cost != null) {
        return po.quantity * po.unit_cost
      }
      return null
    })

    const close = () => {
      if (!submitting.value) {
        emit('close')
      }
    }

    const submitForm = async () => {
      if (submitting.value) return

      submitError.value = null
      submitting.value = true

      try {
        const payload = {
          backlog_item_id: props.backlogItem.id,
          supplier_name: form.value.supplier_name,
          quantity: form.value.quantity,
          unit_cost: form.value.unit_cost,
          expected_delivery_date: form.value.expected_delivery_date,
          notes: form.value.notes || ''
        }
        const result = await api.createPurchaseOrder(payload)
        emit('po-created', result)
        emit('close')
      } catch (err) {
        submitError.value =
          err?.response?.data?.detail || 'Failed to create purchase order. Please try again.'
        console.error('PurchaseOrderModal: create PO error', err)
      } finally {
        submitting.value = false
      }
    }

    const formatCurrency = (value) => {
      if (value == null) return 'N/A'
      return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return dateString
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    return {
      form,
      submitting,
      submitError,
      viewPO,
      totalCost,
      close,
      submitForm,
      formatCurrency,
      formatDate
    }
  }
}
</script>

<style scoped>
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
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.item-context {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.item-name {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.item-sku {
  font-size: 0.813rem;
  color: #64748b;
  font-family: 'Monaco', 'Courier New', monospace;
}

.priority-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.priority-badge.high {
  background: #fecaca;
  color: #991b1b;
}

.priority-badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.priority-badge.low {
  background: #dbeafe;
  color: #1e40af;
}

/* Form styles */
.po-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.optional {
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
  color: #94a3b8;
  font-size: 0.75rem;
}

.form-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: white;
  transition: border-color 0.15s ease;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input:disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}

.form-textarea {
  padding: 0.625rem 0.875rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: white;
  transition: border-color 0.15s ease;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-textarea:disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}

.error-message {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
}

/* View mode info grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item-full {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.approved {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.shipped {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.delivered {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.cancelled {
  background: #f1f5f9;
  color: #64748b;
}

/* Footer */
.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-shrink: 0;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
  border: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #334155;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
