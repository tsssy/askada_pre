<template>
  <main class="page">
    <div class="glow"></div>
    <section class="card">
      <p class="eyebrow">thanks for your attention</p>
      <h1>coming soon…</h1>
      <p class="subtext">
        {{ statusText }}
      </p>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue';

const statusText = ref('We are building something fresh.');

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);
  const subreddit = params.get('subreddit') || 'unknown';
  const source =
    params.get('source') || params.get('utm_source') || params.get('ref') || '';

  try {
    const res = await fetch('/api/visit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subreddit, source, page_url: window.location.href })
    });

    if (!res.ok) {
      throw new Error('visit request failed');
    }

    await res.json();
  } catch (err) {
    statusText.value = 'We could not log this visit, but the launch is still on.';
  }
});
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=Space+Grotesk:wght@400;500&display=swap');

:root {
  --bg-1: #f6f2e9;
  --bg-2: #f2e0c8;
  --accent: #d86a4a;
  --ink: #1f1a17;
  --muted: #5a4c44;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Space Grotesk', system-ui, sans-serif;
  color: var(--ink);
  background: radial-gradient(circle at top left, #fff8ee 0%, var(--bg-1) 35%, var(--bg-2) 100%);
  min-height: 100vh;
}

.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 48px 20px;
  position: relative;
  overflow: hidden;
}

.glow {
  position: absolute;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(216, 106, 74, 0.35), transparent 70%);
  top: -140px;
  right: -120px;
  filter: blur(6px);
  animation: float 10s ease-in-out infinite;
}

.card {
  position: relative;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(216, 106, 74, 0.2);
  box-shadow: 0 30px 80px rgba(31, 26, 23, 0.12);
  padding: 56px 52px;
  max-width: 560px;
  width: 100%;
  text-align: left;
  border-radius: 28px;
  backdrop-filter: blur(6px);
  animation: rise 0.9s ease-out forwards;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.35em;
  font-size: 0.72rem;
  color: var(--accent);
  margin: 0 0 18px;
}

h1 {
  margin: 0 0 16px;
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.4rem, 6vw, 4rem);
  font-weight: 600;
}

.subtext {
  font-size: 1.05rem;
  color: var(--muted);
  margin: 0 0 22px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pill {
  padding: 8px 14px;
  background: rgba(216, 106, 74, 0.1);
  border: 1px solid rgba(216, 106, 74, 0.2);
  border-radius: 999px;
  font-size: 0.9rem;
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(18px);
  }
}

@media (max-width: 600px) {
  .card {
    padding: 42px 28px;
  }

  .eyebrow {
    letter-spacing: 0.2em;
  }
}
</style>
