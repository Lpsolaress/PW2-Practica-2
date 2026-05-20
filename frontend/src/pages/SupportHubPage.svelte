<script>
  import { onMount, onDestroy } from 'svelte';
  import { io } from 'socket.io-client';
  import { app, isAuthenticated, isAdmin, showToast, navigate } from '../state/app.svelte.js';

  let socket = $state(null);
  let conversations = $state([]);
  let activeConversation = $state(null);
  let newMessage = $state('');
  let fileInput = $state();
  let chatScroll = $state();
  let loading = $state(false);

  function connect() {
    socket = io('http://localhost:3000', {
      auth: { token: app.auth.token }
    });

    socket.on('connect', () => {
      console.log('Socket connected to server');
      if (isAdmin()) {
        socket.emit('get_conversations_list');
      } else {
        if (!activeConversation) {
          activeConversation = { messages: [] };
        }
      }
    });

    socket.on('message_history', (data) => {
      console.log('Received history:', data);
      if (isAdmin()) {
        // If it's an object with messages (admin route)
        if (data.messages && activeConversation && activeConversation.userId === data.userId) {
          activeConversation.messages = data.messages;
          scrollChat();
        } else if (Array.isArray(data)) {
          // If it's just an array (unexpected for admin now, but let's be safe)
          if (activeConversation) {
             activeConversation.messages = data;
             scrollChat();
          }
        }
      } else {
        // For users, if they receive history (though we disabled it in backend)
        activeConversation = { messages: Array.isArray(data) ? data : [] };
        scrollChat();
      }
    });

    socket.on('conversations_list', (list) => {
      conversations = list;
    });

    socket.on('chat_message', (msg) => {
      if (isAdmin()) {
        if (activeConversation && activeConversation.userId === msg.roomId) {
          activeConversation.messages = [...activeConversation.messages, msg];
          scrollChat();
        }
        socket.emit('get_conversations_list');
      } else {
        if (activeConversation) {
          activeConversation.messages = [...activeConversation.messages, msg];
          scrollChat();
        }
      }
    });

    socket.on('new_ticket_message', (msg) => {
      if (isAdmin()) {
        showToast(`Nuevo mensaje de ${msg.username}`, 'info');
        socket.emit('get_conversations_list');
      }
    });
  }

  function selectConversation(conv) {
    activeConversation = {
      userId: conv._id,
      username: conv.username,
      messages: []
    };
    socket.emit('get_conversation', conv._id);
  }

  async function sendMessage(e) {
    if (e) e.preventDefault();
    if (!newMessage.trim() && !loading) return;
    
    const data = { text: newMessage.trim() };
    if (isAdmin() && activeConversation) {
      data.targetUserId = activeConversation.userId;
    }
    
    socket.emit('chat_message', data);
    newMessage = '';
  }

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    loading = true;
    const formData = new FormData();
    formData.append('image', file);

    try {
      const resp = await fetch('http://localhost:3000/chat/upload', {
        method: 'POST',
        body: formData
      });
      const result = await resp.json();
      
      if (result.imageUrl) {
        const data = { imageUrl: result.imageUrl, text: '' };
        if (isAdmin() && activeConversation) {
          data.targetUserId = activeConversation.userId;
        }
        socket.emit('chat_message', data);
      }
    } catch (err) {
      showToast('Error al subir imagen', 'error');
    } finally {
      loading = false;
      fileInput.value = '';
    }
  }

  function scrollChat() {
    setTimeout(() => {
      if (chatScroll) {
        chatScroll.scrollTo({
          top: chatScroll.scrollHeight,
          behavior: 'smooth'
        });
      }
    }, 100);
  }

  onMount(() => {
    if (isAuthenticated()) {
      connect();
      // If already connected, request list immediately
      if (socket && socket.connected && isAdmin()) {
        socket.emit('get_conversations_list');
      }
    }
  });

  onDestroy(() => {
    if (socket) socket.disconnect();
  });
</script>

<main class="hub">
  <aside class="sidebar">
    <div class="sidebar__top">
      <div class="logo">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="#ff0028"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        <span>CENTRO DE SOPORTE</span>
      </div>
    </div>

    <div class="sidebar__content">
      {#if isAdmin()}
        <div class="section-title">
          MENSAJES NUEVOS
          <button class="refresh-btn" onclick={() => socket.emit('get_conversations_list')} aria-label="Actualizar">
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          </button>
        </div>
        <div class="conversations">
          {#each conversations.filter(c => c.unreadCount > 0) as conv}
            <button 
              class="conv-card conv-card--new" 
              class:active={activeConversation?.userId === conv._id}
              onclick={() => selectConversation(conv)}
            >
              <div class="avatar">{conv.username[0].toUpperCase()}</div>
              <div class="conv-info">
                <div class="conv-info__top">
                  <span class="name">{conv.username}</span>
                  <span class="time">{new Date(conv.lastTimestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <div class="last-msg">{conv.lastMessage || 'Imagen'}</div>
              </div>
              {#if conv.unreadCount > 0}
                <div class="unread-badge">{conv.unreadCount}</div>
              {/if}
            </button>
          {:else}
            <div class="empty-list">No hay mensajes nuevos</div>
          {/each}
        </div>

        <div class="section-title">HISTORIAL</div>
        <div class="conversations">
          {#each conversations.filter(c => !c.unreadCount || c.unreadCount === 0) as conv}
            <button 
              class="conv-card" 
              class:active={activeConversation?.userId === conv._id}
              onclick={() => selectConversation(conv)}
            >
              <div class="avatar">{conv.username[0].toUpperCase()}</div>
              <div class="conv-info">
                <div class="conv-info__top">
                  <span class="name">{conv.username}</span>
                  <span class="time">{new Date(conv.lastTimestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <div class="last-msg">{conv.lastMessage || 'Imagen'}</div>
              </div>
            </button>
          {:else}
            <div class="empty-list">Sin historial previo</div>
          {/each}
        </div>
      {/if}

      <div class="section-title">NAVEGACIÓN</div>
      <nav class="side-nav">
        <button onclick={() => navigate('/productos')}>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
          Inicio
        </button>
        <button onclick={() => navigate('/perfil')}>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          Mi Perfil
        </button>
      </nav>
    </div>

    <button class="new-chat">
      <span>+</span> NUEVA CONVERSACIÓN
    </button>
  </aside>

  <section class="main-chat">
    {#if activeConversation || !isAdmin()}
      <header class="chat-header">
        <div class="user-meta">
          <div class="avatar avatar--lg">{isAdmin() ? activeConversation?.username[0].toUpperCase() : 'S'}</div>
          <div class="user-info">
            <div class="title">{isAdmin() ? activeConversation?.username : 'Soporte Activo: Asistente Nuba'}</div>
            <div class="status">
              <span class="dot"></span> 
              conectado con un agente
            </div>
          </div>
        </div>
        <div class="actions">
           <button class="icon-toggle" aria-label="Toggle Info"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><circle cx="12" cy="12" r="3"/><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/></svg></button>
           <button class="icon-toggle" aria-label="More Options"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg></button>
        </div>
      </header>

      <div class="chat-viewport" bind:this={chatScroll}>
        <div class="date-sep">HOY</div>
        
        {#if activeConversation}
          {#each activeConversation.messages as msg}
            <div class="msg-row" class:msg-row--me={msg.userId === app.auth.user?._id}>
              {#if msg.userId !== app.auth.user?._id}
                <div class="avatar avatar--sm">{msg.username[0].toUpperCase()}</div>
              {/if}
              <div class="bubble-wrap">
                <div class="bubble">
                  {#if msg.imageUrl}
                    <img src={msg.imageUrl} alt="Chat upload" class="bubble-img" />
                  {/if}
                  {#if msg.text}
                    <p>{msg.text}</p>
                  {/if}
                </div>
                <div class="meta">{msg.username} • {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
              </div>
            </div>
          {/each}
        {/if}
      </div>

      <footer class="chat-footer">
        <div class="input-area">
          <button class="attach" onclick={() => fileInput.click()} aria-label="Adjuntar imagen">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
          </button>
          <input type="file" hidden bind:this={fileInput} onchange={handleFileUpload} accept="image/*" />
          <input 
            type="text" 
            placeholder="Escribe tu mensaje aquí..." 
            bind:value={newMessage} 
            onkeydown={e => e.key === 'Enter' && sendMessage()}
          />
          <button class="emoji" aria-label="Emojis">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
          </button>
        </div>
        <button class="send-btn" onclick={sendMessage} disabled={loading} aria-label="Enviar mensaje">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="white"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </footer>
      <div class="footer-meta">
        <span>⚡ SOPORTE PRIORITARIO</span>
        <span>🛡️ CANAL SEGURO</span>
      </div>
    {:else}
      <div class="chat-placeholder">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="rgba(255,255,255,0.1)"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 1 1-7.6-11.7 8.38 8.38 0 0 1 3.8.9L21 3z"></path></svg>
        <p>Selecciona una conversación para comenzar</p>
      </div>
    {/if}
  </section>
</main>

<style>
  .hub {
    position: fixed;
    top: 58px;
    left: 0;
    right: 0;
    bottom: 0;
    background: #0c0b0f;
    display: flex;
    color: #fff;
    font-family: 'Inter', sans-serif;
  }

  /* Sidebar */
  .sidebar {
    width: 280px;
    background: #0f0e13;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
  }

  .sidebar__top {
    padding: 24px;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 1px;
  }

  .sidebar__content {
    flex: 1;
    overflow-y: auto;
    padding: 0 12px;
  }

  .section-title {
    font-size: 11px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.3);
    padding: 24px 12px 12px;
    letter-spacing: 0.5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .refresh-btn {
    background: transparent;
    border: 0;
    color: rgba(255, 255, 255, 0.2);
    cursor: pointer;
    padding: 4px;
    display: flex;
    transition: color 0.2s;
  }

  .refresh-btn:hover {
    color: #ff0028;
  }

  .conversations {
    display: flex;
    flex-direction: column;
    gap: 1px;
  }

  .conv-card {
    appearance: none;
    border: 0;
    background: transparent;
    padding: 12px;
    display: flex;
    gap: 12px;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    color: #fff;
    transition: background 0.2s;
  }

  .conv-card:hover {
    background: rgba(255, 255, 255, 0.03);
  }

  .conv-card.active {
    background: rgba(255, 0, 40, 0.1);
    box-shadow: inset 3px 0 0 #ff0028;
  }

  .conv-card--new .name {
    color: #ff0028;
  }

  .unread-badge {
    background: #ff0028;
    color: white;
    font-size: 10px;
    font-weight: 800;
    min-width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 4px;
    align-self: center;
  }

  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #2a2830;
    display: grid;
    place-items: center;
    font-weight: 700;
    font-size: 14px;
    flex-shrink: 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .avatar--lg { width: 44px; height: 44px; }
  .avatar--sm { width: 32px; height: 32px; font-size: 12px; }

  .conv-info {
    flex: 1;
    min-width: 0;
  }

  .conv-info__top {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
  }

  .name { font-weight: 700; font-size: 13px; }
  .time { font-size: 10px; opacity: 0.5; }
  .last-msg { font-size: 11px; opacity: 0.5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .side-nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .side-nav button {
    appearance: none;
    border: 0;
    background: transparent;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: rgba(255, 255, 255, 0.6);
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .side-nav button:hover {
    background: rgba(255, 255, 255, 0.03);
    color: #fff;
  }

  .new-chat {
    margin: 20px;
    background: #ff0028;
    border: 0;
    color: #fff;
    padding: 14px;
    border-radius: 8px;
    font-weight: 800;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  /* Main Chat */
  .main-chat {
    flex: 1;
    background: #0c0b0f;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .chat-header {
    padding: 16px 32px;
    background: rgba(255, 255, 255, 0.01);
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .user-meta {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .user-info .title { font-weight: 800; font-size: 15px; margin-bottom: 2px; }
  .user-info .status { font-size: 11px; opacity: 0.5; display: flex; align-items: center; gap: 6px; }
  .dot { width: 6px; height: 6px; background: #00ff88; border-radius: 50%; box-shadow: 0 0 8px #00ff88; }

  .actions { display: flex; gap: 12px; }
  .icon-toggle { background: transparent; border: 0; color: rgba(255, 255, 255, 0.4); cursor: pointer; padding: 8px; transition: color 0.2s; }
  .icon-toggle:hover { color: #fff; }

  .chat-viewport {
    flex: 1;
    overflow-y: auto;
    padding: 32px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .date-sep {
    align-self: center;
    background: rgba(255, 255, 255, 0.05);
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.3);
    margin-bottom: 8px;
  }

  .msg-row {
    display: flex;
    gap: 16px;
    max-width: 80%;
  }

  .msg-row--me {
    align-self: flex-end;
    flex-direction: row-reverse;
  }

  .bubble-wrap { display: flex; flex-direction: column; gap: 8px; }

  .bubble {
    padding: 16px 20px;
    background: #1a1920;
    border-radius: 12px;
    border-top-left-radius: 2px;
    font-size: 14px;
    line-height: 1.6;
    color: #eee;
  }

  .msg-row--me .bubble {
    background: #2a1114;
    border-top-left-radius: 12px;
    border-top-right-radius: 2px;
    border: 1px solid rgba(255, 0, 40, 0.2);
  }

  .bubble-img {
    max-width: 300px;
    border-radius: 8px;
    margin-bottom: 8px;
    display: block;
  }

  .meta { font-size: 10px; opacity: 0.3; font-weight: 700; letter-spacing: 0.5px; }
  .msg-row--me .meta { text-align: right; }

  .chat-footer {
    padding: 24px 32px;
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .input-area {
    flex: 1;
    background: #151419;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    display: flex;
    align-items: center;
    padding: 4px 8px;
  }

  .input-area input {
    flex: 1;
    background: transparent;
    border: 0;
    padding: 12px;
    color: #fff;
    font-size: 14px;
    outline: none;
  }

  .attach, .emoji {
    background: transparent;
    border: 0;
    color: rgba(255, 255, 255, 0.3);
    cursor: pointer;
    padding: 8px;
    transition: color 0.2s;
  }
  .attach:hover, .emoji:hover { color: #fff; }

  .send-btn {
    width: 48px;
    height: 48px;
    background: #ff0028;
    border-radius: 8px;
    border: 0;
    cursor: pointer;
    display: grid;
    place-items: center;
    transition: transform 0.2s;
  }

  .send-btn:hover { transform: scale(1.05); }

  .footer-meta {
    padding: 0 32px 24px;
    display: flex;
    justify-content: center;
    gap: 24px;
    font-size: 10px;
    font-weight: 800;
    opacity: 0.3;
  }

  .chat-placeholder {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    color: rgba(255, 255, 255, 0.2);
  }

  .empty-list {
    padding: 24px 12px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.2);
    text-align: center;
  }
</style>
