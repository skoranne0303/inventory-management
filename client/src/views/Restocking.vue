<template>
  <div class="restocking">
    <div class="page-header">
      <h2>Restocking Planner</h2>
      <p>Allocate your budget to restock high-demand items automatically.</p>
    </div>

    <div v-if="loading" class="loading">Loading demand forecasts...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Budget Slider Card -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">Available Budget</h3>
          <span class="budget-value">{{ formatCurrency(budget) }}</span>
        </div>
        <div class="slider-container">
          <input
            type="range"
            class="budget-slider"
            :min="1000"
            :max="200000"
            :step="1000"
            v-model.number="budget"
          />
          <div class="slider-labels">
            <span>$1,000</span>
            <span>$200,000</span>
          </div>
        </div>
      </div>

      <!-- Success Banner -->
      <div v-if="submittedOrder" class="success-banner">
        <div class="success-content">
          <strong>Order {{ submittedOrder.order_number }} placed successfully!</strong>
          Expected delivery in 7 days.
        </div>
        <button class="btn btn-outline" @click="resetOrder">Place Another Order</button>
      </div>

      <!-- Recommendations Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recommended Items ({{ recommendations.length }} items)</h3>
        </div>

        <div v-if="recommendations.length === 0" class="empty-state">
          No increasing-demand items can be accommodated within the current budget.
        </div>

        <div v-else class="table-container">
          <table class="recommendations-table">
            <thead>
              <tr>
                <th>Item Name</th>
                <th>SKU</th>
                <th class="col-number">Current Demand</th>
                <th class="col-number">Forecasted</th>
                <th class="col-number">Qty to Order</th>
                <th class="col-number">Unit Cost</th>
                <th class="col-number">Subtotal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations" :key="item.item_sku">
                <td class="item-name-cell">{{ item.item_name }}</td>
                <td class="sku-cell">{{ item.item_sku }}</td>
                <td class="col-number">{{ item.current_demand.toLocaleString() }}</td>
                <td class="col-number">
                  <span class="forecasted-value">{{ item.forecasted_demand.toLocaleString() }}</span>
                </td>
                <td class="col-number"><strong>{{ item.quantity_to_order.toLocaleString() }}</strong></td>
                <td class="col-number">{{ formatCurrency(item.unit_cost) }}</td>
                <td class="col-number"><strong>{{ formatCurrency(item.subtotal) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Budget Summary Bar -->
        <div class="budget-summary">
          <span class="summary-item">
            <span class="summary-label">Items selected</span>
            <span class="summary-value">{{ recommendations.length }}</span>
          </span>
          <span class="summary-divider"></span>
          <span class="summary-item">
            <span class="summary-label">Allocated</span>
            <span class="summary-value allocated">{{ formatCurrency(totalCost) }}</span>
          </span>
          <span class="summary-divider"></span>
          <span class="summary-item">
            <span class="summary-label">Remaining</span>
            <span class="summary-value" :class="remainingBudget < 0 ? 'over-budget' : 'remaining'">
              {{ formatCurrency(remainingBudget) }}
            </span>
          </span>
        </div>
      </div>

      <!-- Order Error -->
      <div v-if="orderError" class="error order-error">{{ orderError }}</div>

      <!-- Place Order Button -->
      <div v-if="!submittedOrder" class="action-row">
        <button
          class="btn btn-primary"
          :disabled="recommendations.length === 0 || placing"
          @click="placeOrder"
        >
          <span v-if="placing" class="spinner-text">Placing Order...</span>
          <span v-else>Place Order</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

export default {
  name: 'Restocking',
  setup() {
    const budget = ref(50000)
    const demandForecasts = ref([])
    const loading = ref(true)
    const error = ref(null)
    const placing = ref(false)
    const submittedOrder = ref(null)
    const orderError = ref(null)

    const recommendations = computed(() => {
      const increasing = demandForecasts.value.filter(f => f.trend === 'increasing')
      const scored = increasing.map(f => {
        const gap = f.forecasted_demand - f.current_demand
        return { ...f, quantity_to_order: gap, subtotal: gap * f.unit_cost }
      }).sort((a, b) => (b.forecasted_demand - b.current_demand) - (a.forecasted_demand - a.current_demand))

      let remaining = budget.value
      const result = []
      for (const item of scored) {
        if (remaining <= 0) break
        if (item.subtotal <= remaining) {
          result.push({ ...item })
          remaining -= item.subtotal
        } else {
          const qty = Math.floor(remaining / item.unit_cost)
          if (qty > 0) {
            result.push({ ...item, quantity_to_order: qty, subtotal: qty * item.unit_cost })
            remaining -= qty * item.unit_cost
          }
        }
      }
      return result
    })

    const totalCost = computed(() => recommendations.value.reduce((sum, r) => sum + r.subtotal, 0))
    const remainingBudget = computed(() => budget.value - totalCost.value)

    const formatCurrency = (value) => {
      return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
    }

    const placeOrder = async () => {
      placing.value = true
      orderError.value = null
      try {
        const result = await api.submitRestockingOrder({
          items: recommendations.value.map(r => ({
            sku: r.item_sku,
            name: r.item_name,
            quantity: r.quantity_to_order,
            unit_cost: r.unit_cost
          })),
          total_cost: totalCost.value
        })
        submittedOrder.value = result
      } catch (err) {
        orderError.value = 'Failed to place order. Please try again.'
      } finally {
        placing.value = false
      }
    }

    const resetOrder = () => {
      submittedOrder.value = null
      orderError.value = null
    }

    onMounted(async () => {
      loading.value = true
      error.value = null
      try {
        demandForecasts.value = await api.getDemandForecasts()
      } catch (err) {
        error.value = 'Failed to load demand forecasts.'
        console.error(err)
      } finally {
        loading.value = false
      }
    })

    return {
      budget,
      demandForecasts,
      loading,
      error,
      placing,
      submittedOrder,
      orderError,
      recommendations,
      totalCost,
      remainingBudget,
      formatCurrency,
      placeOrder,
      resetOrder
    }
  }
}
</script>

<style scoped>
.restocking {
  padding: 0;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
}

.page-header p {
  color: #64748b;
  margin: 0;
  font-size: 0.9375rem;
}

/* Budget Card */
.budget-card .card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.budget-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2563eb;
  font-variant-numeric: tabular-nums;
}

.slider-container {
  padding: 0.5rem 0 0.25rem;
}

.budget-slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  accent-color: #2563eb;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.8125rem;
  color: #64748b;
}

/* Recommendations Table */
.recommendations-table {
  width: 100%;
  table-layout: auto;
}

.col-number {
  text-align: right;
}

.item-name-cell {
  font-weight: 500;
  color: #0f172a;
  min-width: 180px;
}

.sku-cell {
  font-size: 0.8125rem;
  color: #64748b;
  font-family: monospace;
}

.forecasted-value {
  color: #10b981;
  font-weight: 500;
}

/* Budget Summary Bar */
.budget-summary {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  margin-top: 0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.summary-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.summary-value {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  font-variant-numeric: tabular-nums;
}

.summary-value.allocated {
  color: #2563eb;
}

.summary-value.remaining {
  color: #10b981;
}

.summary-value.over-budget {
  color: #ef4444;
}

.summary-divider {
  width: 1px;
  height: 2rem;
  background: #e2e8f0;
  flex-shrink: 0;
}

/* Empty State */
.empty-state {
  padding: 2.5rem 1.25rem;
  text-align: center;
  color: #64748b;
  font-size: 0.9375rem;
}

/* Action Row */
.action-row {
  margin-top: 1.25rem;
  display: flex;
  justify-content: flex-end;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 6px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: background 0.15s, opacity 0.15s;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background: white;
  color: #0f172a;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
}

.btn-outline:hover {
  background: #f8fafc;
}

.spinner-text {
  opacity: 0.8;
}

/* Success Banner */
.success-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-left: 4px solid #10b981;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
  gap: 1rem;
}

.success-content {
  color: #065f46;
  font-size: 0.9375rem;
}

.success-content strong {
  display: block;
  margin-bottom: 0.125rem;
}

/* Order Error */
.order-error {
  margin-top: 0.75rem;
}
</style>
