<script>
  import { app, clearToast } from '../state/app.svelte.js';

  let lastToastId = $state(null);

  $effect(() => {
    const toast = app.ui.toast;
    if (!toast) return;
    lastToastId = toast.id;
    const id = toast.id;
    const timeout = setTimeout(() => clearToast(id), 3500);
    return () => clearTimeout(timeout);
  });
</script>

{#if app.ui.toast}
  <div class="toast" data-type={app.ui.toast.type} role="status" aria-live="polite">
    <div class="toast__message">{app.ui.toast.message}</div>
    <button class="toast__close" type="button" onclick={() => clearToast(lastToastId)}>×</button>
  </div>
{/if}

<style>
  .toast {
    position: fixed;
    inset: auto 16px 16px auto;
    max-width: min(420px, calc(100vw - 32px));
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text);
    border-radius: 12px;
    padding: 12px 12px 12px 14px;
    box-shadow: var(--shadow);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
    align-items: start;
    z-index: 50;
  }

  .toast[data-type='success'] {
    border-color: color-mix(in oklab, var(--success) 70%, var(--border));
  }

  .toast[data-type='error'] {
    border-color: color-mix(in oklab, var(--danger) 70%, var(--border));
  }

  .toast__message {
    font-size: 14px;
    line-height: 1.35;
  }

  .toast__close {
    appearance: none;
    border: 0;
    background: transparent;
    color: inherit;
    font-size: 18px;
    line-height: 1;
    padding: 0 4px;
    cursor: pointer;
    opacity: 0.75;
  }

  .toast__close:hover {
    opacity: 1;
  }
</style>
