<script>
  import { onMount, onDestroy } from 'svelte';
  import { io } from 'socket.io-client';
  import { app, isAuthenticated, isAdmin, showToast, navigate } from '../state/app.svelte.js';

  let open = $state(false);
  let socket = $state(null);
  let messages = $state([]);
  let newMessage = $state('');
  let scrollElement = $state();

  $effect(() => {
    if (isAuthenticated() && !socket) {
      connect();
    } else if (!isAuthenticated() && socket) {
      disconnect();
    }
  });

  function connect() {
    socket = io('http://localhost:3000', {
      auth: { token: app.auth.token }
    });

    socket.on('connect', () => {
      console.log('Chat conectado');
    });

    socket.on('message_history', (history) => {
      messages = history;
      if (history.length > 0) app.ui.hasChatHistory = true;
      scrollToBottom();
    });

    socket.on('chat_message', (msg) => {
      messages = [...messages, msg];
      app.ui.hasChatHistory = true;
      scrollToBottom();
      if (!open) {
        showToast('Nuevo mensaje de soporte', 'info');
      }
    });

    socket.on('error', (err) => {
      console.error('Error de chat:', err);
    });
  }

  function disconnect() {
    if (socket) {
      socket.disconnect();
      socket = null;
      messages = [];
    }
  }

  function sendMessage(e) {
    if (e) e.preventDefault();
    if (!newMessage.trim() || !socket) return;

    socket.emit('chat_message', { text: newMessage.trim() });
    newMessage = '';
  }

  function toggle() {
    open = !open;
    if (open) scrollToBottom();
  }

  function scrollToBottom() {
    setTimeout(() => {
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }, 50);
  }

  onMount(() => {
    if (isAuthenticated()) connect();
  });

  onDestroy(() => {
    disconnect();
  });
</script>

{#if isAuthenticated() && !isAdmin()}
  <div class="chat-widget" class:open>
    {#if open}
      <div class="window">
        <header class="window__header">
          <button class="window__title-btn" onclick={() => { open = false; navigate('/soporte'); }}>
            Soporte Nuba <span class="external">↗</span>
          </button>
          <button class="icon-btn" onclick={toggle}>×</button>
        </header>
        
        <div class="window__messages" bind:this={scrollElement}>
          {#each messages as msg}
            <div class="msg" class:msg--me={msg.userId === app.auth.user?._id}>
              <div class="msg__bubble">{msg.text}</div>
              <div class="msg__meta">
                {msg.username} • {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          {/each}
          {#if messages.length === 0}
            <div class="empty">¿En qué podemos ayudarte?</div>
          {/if}
        </div>

        <form class="window__input" onsubmit={sendMessage}>
          <input type="text" placeholder="Escribe un mensaje..." bind:value={newMessage} />
          <button type="submit" aria-label="Enviar mensaje">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </form>
      </div>
    {/if}

    <button class="trigger" onclick={toggle} aria-label="Abrir chat de soporte">
      {#if !open}
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 1 1-7.6-11.7 8.38 8.38 0 0 1 3.8.9L21 3z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      {:else}
         <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      {/if}
    </button>
  </div>
{/if}

<style>
  .chat-widget {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 100;
  }
  .window__title-btn {
    background: transparent;
    border: none;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .window__title-btn:hover {
    color: #ff0028;
  }

  .external {
    font-size: 10px;
    opacity: 0.6;
  }

  .trigger {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #ff0028;
    color: white;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(255, 0, 40, 0.4);
    display: grid;
    place-items: center;
    transition: transform 0.2s;
  }

  .trigger:hover {
    transform: scale(1.05);
  }

  .window {
    position: absolute;
    bottom: 72px;
    right: 0;
    width: 320px;
    height: 420px;
    background: #0c0b0f;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
    overflow: hidden;
  }

  .window__header {
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }


  .icon-btn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    font-size: 20px;
    cursor: pointer;
  }

  .window__messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .empty {
    text-align: center;
    color: rgba(255, 255, 255, 0.4);
    font-size: 13px;
    margin-top: 20px;
  }

  .msg {
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-width: 85%;
    align-self: flex-start;
  }

  .msg--me {
    align-self: flex-end;
  }

  .msg__bubble {
    padding: 8px 12px;
    border-radius: 14px;
    font-size: 13px;
    background: rgba(255, 255, 255, 0.1);
    color: #eee;
    line-height: 1.4;
  }

  .msg--me .msg__bubble {
    background: #ff0028;
    color: white;
  }

  .msg__meta {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.4);
  }

  .msg--me .msg__meta {
    text-align: right;
  }

  .window__input {
    padding: 12px;
    background: rgba(255, 255, 255, 0.05);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    gap: 8px;
  }

  .window__input input {
    flex: 1;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 8px 12px;
    color: white;
    font-size: 13px;
    outline: none;
  }

  .window__input button {
    background: #ff0028;
    color: white;
    border: none;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: grid;
    place-items: center;
    cursor: pointer;
  }
</style>
