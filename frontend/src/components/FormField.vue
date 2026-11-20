<script setup>
import { useId } from 'vue'

defineProps({
  label: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  error: { type: String, default: '' },
  autocomplete: { type: String, default: 'off' },
  placeholder: { type: String, default: '' },
})
defineEmits(['update:modelValue'])

const id = useId()
</script>

<template>
  <div>
    <label :for="id" class="label">{{ label }}</label>
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :autocomplete="autocomplete"
      :placeholder="placeholder"
      :aria-invalid="!!error"
      :aria-describedby="error ? id + '-error' : undefined"
      class="input"
      :class="{ 'input-error': error }"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <p v-if="error" :id="id + '-error'" class="field-error" role="alert">{{ error }}</p>
  </div>
</template>
