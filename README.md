```svg
<svg width="1200" height="280" viewBox="0 0 1200 280" xmlns="http://www.w3.org/2000/svg">

  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0D1117"/>
      <stop offset="100%" stop-color="#161B22"/>
    </linearGradient>

    <linearGradient id="text" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#58A6FF"/>
      <stop offset="50%" stop-color="#7C5CFC"/>
      <stop offset="100%" stop-color="#00E5FF"/>
    </linearGradient>

    <filter id="glow">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect width="1200" height="280" rx="20" fill="url(#bg)"/>

  <!-- Decorative lines -->
  <g opacity="0.18" stroke="#58A6FF">
    <line x1="60" y1="60" x2="250" y2="60"/>
    <line x1="950" y1="220" x2="1140" y2="220"/>
    <line x1="120" y1="210" x2="300" y2="210"/>
    <line x1="900" y1="70" x2="1080" y2="70"/>
  </g>

  <!-- AI Nodes -->
  <g fill="#58A6FF" opacity="0.45">
    <circle cx="90" cy="60" r="4"/>
    <circle cx="180" cy="110" r="4"/>
    <circle cx="130" cy="170" r="4"/>
    <circle cx="1110" cy="60" r="4"/>
    <circle cx="1030" cy="150" r="4"/>
    <circle cx="1080" cy="220" r="4"/>
  </g>

  <g stroke="#58A6FF" opacity="0.3">
    <line x1="90" y1="60" x2="180" y2="110"/>
    <line x1="180" y1="110" x2="130" y2="170"/>
    <line x1="1110" y1="60" x2="1030" y2="150"/>
    <line x1="1030" y1="150" x2="1080" y2="220"/>
  </g>

  <!-- Main Title -->
  <text
      x="600"
      y="135"
      text-anchor="middle"
      font-family="Orbitron, Rajdhani, Exo, Arial, sans-serif"
      font-size="86"
      font-weight="900"
      fill="url(#text)"
      filter="url(#glow)"
      letter-spacing="8">
      YOOSUF
  </text>

  <!-- Subtitle -->
  <text
      x="600"
      y="190"
      text-anchor="middle"
      font-family="JetBrains Mono, Fira Code, monospace"
      font-size="22"
      fill="#8B949E"
      letter-spacing="3">
      AI ENGINEER • DATA SCIENCE • LLMs • RAG • AGENTS
  </text>

</svg>
```
