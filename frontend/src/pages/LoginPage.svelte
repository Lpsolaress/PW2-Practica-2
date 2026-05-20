<script>
  import { login, registro } from '../services/auth.js';
  import { setAuth, navigate, showToast } from '../state/app.svelte.js';

  let form = $state({
    email: '',
    password: ''
  });

  let submitting = $state(false);
  let error = $state('');
  let keepSignedIn = $state(true);
  let mode = $state('login');
  let modeInit = $state(false);

  $effect(() => {
    if (modeInit) return;
    modeInit = true;
    const saved = sessionStorage.getItem('loginMode');
    if (saved === 'login' || saved === 'register') {
      mode = saved;
    }
    sessionStorage.removeItem('loginMode');
  });

  function switchMode(next) {
    if (submitting) return;
    error = '';
    mode = next;
  }

  async function submit(e) {
    e.preventDefault();
    error = '';
    submitting = true;

    try {
      const email = form.email.trim();
      const password = form.password;

      const data =
        mode === 'register'
          ? await registro({
              username: (email.split('@')[0] || 'usuario').slice(0, 20),
              email,
              password,
              role: 'usuario'
            })
          : await login({ email, password });
      setAuth({ token: data.token, user: data.usuario });
      showToast(mode === 'register' ? 'Cuenta creada' : 'Sesión iniciada', 'success');
      navigate('/productos');
    } catch (err) {
      error = err?.message || (mode === 'register' ? 'No se pudo crear la cuenta' : 'No se pudo iniciar sesión');
      showToast(error, 'error');
    } finally {
      submitting = false;
    }
  }
</script>

<main class="login">
  <section class="left" aria-label="Formulario de inicio de sesión">
    <div class="left__inner">
      <header class="top">
        <div class="logo" aria-hidden="true">
          <div class="wordmark wordmark--small">
            <span class="wordmark__text">Nuba</span>
            <span class="wordmark__line"></span>
          </div>
        </div>
        <button class="icon-btn" type="button" aria-label="Cerrar" tabindex="-1">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
            <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
          </svg>
        </button>
      </header>

      <h1 class="title">
        {#if mode === 'login'}
          TU CUENTA PARA
          <br />
          TODO LO <span class="title__brand">Nuba</span>
        {:else}
          CREA TU
          <br />
          CUENTA <span class="title__brand">Nuba</span>
        {/if}
      </h1>

      <form class="form" onsubmit={submit}>
        <input
          class="input"
          type="email"
          bind:value={form.email}
          autocomplete="email"
          placeholder="Correo electrónico"
          required
          disabled={submitting}
          aria-label="Correo electrónico"
        />

        <input
          class="input"
          type="password"
          bind:value={form.password}
          autocomplete="current-password"
          placeholder="Contraseña"
          required
          disabled={submitting}
          aria-label="Contraseña"
        />

        <div class="row">
          <label class="checkbox">
            <input type="checkbox" bind:checked={keepSignedIn} disabled={submitting} />
            <span>Mantener sesión iniciada</span>
          </label>
        </div>

        {#if error}
          <div class="error" role="alert">{error}</div>
        {/if}

        <div class="legal">
          Al iniciar sesión, aceptas la <button class="link link--inline" type="button" disabled={submitting}>Política de Privacidad</button> y los
          <button class="link link--inline" type="button" disabled={submitting}>Términos de Uso</button> de Nuba.
        </div>

        <button class="submit" type="submit" disabled={submitting}>
          {mode === 'login' ? (submitting ? 'INICIANDO SESIÓN…' : 'INICIAR SESIÓN') : submitting ? 'CREANDO…' : 'ÚNETE A NOSOTROS'}
        </button>
      </form>

      <div class="bottom">
        {#if mode === 'login'}
          <span class="muted">¿No eres miembro?</span>
          <button class="link" type="button" disabled={submitting} onclick={() => switchMode('register')}>
            <strong>Únete a nosotros.</strong>
          </button>
{:else}
          <span class="muted">¿Ya eres miembro?</span>
          <button class="link" type="button" disabled={submitting} onclick={() => switchMode('login')}>
            <strong>Inicia sesión.</strong>
          </button>
        {/if}
      </div>
    </div>
  </section>

  <section class="right" aria-label="Logo de Nuba">
    <div class="right__inner">
      <div class="wordmark" aria-hidden="true">
        <span class="wordmark__text">Nuba</span>
        <span class="wordmark__line"></span>
      </div>
    </div>
  </section>
</main>

<style>
  .login {
    --red: #ff0028;
    min-height: 100svh;
    display: grid;
    grid-template-columns: minmax(360px, 480px) 1fr;
  }

  .left {
    position: relative;
    display: grid;
    align-items: center;
    padding: 34px 28px;
    background: radial-gradient(120% 100% at 0% 0%, rgba(255, 0, 40, 0.18) 0%, rgba(0, 0, 0, 0) 56%),
      radial-gradient(110% 100% at 0% 100%, rgba(124, 92, 255, 0.12) 0%, rgba(0, 0, 0, 0) 55%),
      linear-gradient(180deg, rgba(18, 0, 6, 0.92), rgba(10, 0, 3, 0.92));
  }

  .left__inner {
    width: min(380px, 100%);
    margin: 0 auto;
  }

  .top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.9);
  }

  .wordmark {
    display: grid;
    gap: 18px;
    justify-items: start;
  }

  .wordmark__text {
    font-weight: 280;
    letter-spacing: -0.4px;
    font-size: clamp(64px, 6.8vw, 110px);
    line-height: 0.9;
    color: color-mix(in oklab, var(--red) 92%, white);
    animation: textAppear 1s cubic-bezier(0.25, 1, 0.5, 1) forwards, glowPulse 4s ease-in-out infinite 1.2s alternate;
  }

  .wordmark__line {
    height: 2px;
    width: min(480px, 62%);
    background: rgba(255, 255, 255, 0.82);
    animation: lineGrow 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    transform-origin: left;
  }

  @keyframes textAppear {
    from { opacity: 0; transform: translateY(20px); filter: blur(6px); }
    to { opacity: 1; transform: translateY(0); filter: blur(0); }
  }

  @keyframes glowPulse {
    from { text-shadow: 0 0 10px rgba(255, 0, 40, 0); }
    to { text-shadow: 0 0 25px rgba(255, 0, 40, 0.4), 0 0 5px rgba(255, 255, 255, 0.15); }
  }

  @keyframes lineGrow {
    from { transform: scaleX(0); opacity: 0; }
    to { transform: scaleX(1); opacity: 1; }
  }

  .wordmark--small {
    gap: 8px;
  }

  .wordmark--small .wordmark__text {
    font-weight: 520;
    font-size: 18px;
    letter-spacing: 0.2px;
    color: rgba(255, 255, 255, 0.9);
  }

  .wordmark--small .wordmark__line {
    width: 70px;
    height: 2px;
    background: rgba(255, 255, 255, 0.74);
  }

  .icon-btn {
    appearance: none;
    border: 0;
    background: transparent;
    color: rgba(255, 255, 255, 0.72);
    padding: 6px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
  }

  .title {
    margin: 0 0 18px;
    font-size: 22px;
    line-height: 1.05;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.92);
  }

  .title__brand {
    opacity: 0.9;
  }

  .form {
    display: grid;
    gap: 12px;
  }

  .input {
    appearance: none;
    width: 100%;
    padding: 13px 14px;
    border-radius: 0;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.92);
    font-size: 14px;
    outline: none;
  }

  .input::placeholder {
    color: rgba(255, 255, 255, 0.46);
  }

  .input:focus {
    border-color: rgba(255, 255, 255, 0.32);
    background: rgba(255, 255, 255, 0.08);
  }

  .row {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 12px;
    margin-top: 2px;
  }

  .checkbox {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.62);
    user-select: none;
  }

  .checkbox input {
    width: 14px;
    height: 14px;
    accent-color: rgba(255, 255, 255, 0.9);
  }

  .link {
    appearance: none;
    border: 0;
    background: transparent;
    padding: 0;
    color: rgba(255, 255, 255, 0.72);
    font-size: 12px;
    cursor: pointer;
  }

  .link:hover:enabled {
    text-decoration: underline;
  }

  .link:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .link--inline {
    display: inline;
    font: inherit;
  }

  .error {
    font-size: 12px;
    color: rgba(255, 140, 160, 0.95);
  }

  .legal {
    margin-top: 2px;
    font-size: 11px;
    line-height: 1.35;
    color: rgba(255, 255, 255, 0.45);
  }

  .submit {
    width: 100%;
    border: 0;
    border-radius: 4px;
    padding: 13px 14px;
    background: var(--red);
    color: white;
    font-weight: 900;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    cursor: pointer;
    margin-top: 6px;
  }

  .submit:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  .bottom {
    margin-top: 18px;
    display: flex;
    justify-content: center;
    gap: 6px;
    align-items: baseline;
    font-size: 12px;
  }

  .muted {
    color: rgba(255, 255, 255, 0.55);
  }

  .right {
    position: relative;
    min-height: 100svh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(90% 120% at 0% 0%, rgba(255, 0, 40, 0.22) 0%, rgba(0, 0, 0, 0) 58%),
      radial-gradient(90% 120% at 100% 100%, rgba(124, 92, 255, 0.16) 0%, rgba(0, 0, 0, 0) 58%),
      linear-gradient(135deg, rgba(12, 12, 14, 0.98), rgba(0, 0, 0, 0.92));
  }

  .right__inner {
    width: min(720px, 92%);
    padding: 42px 36px;
  }

  @media (max-width: 920px) {
    .login {
      grid-template-columns: 1fr;
    }

    .right {
      display: none;
    }

    .left {
      padding: 28px 18px;
    }
  }
</style>
