<template>
  <div class="page">
    <header class="page-head">
      <h1>Umbrales SPATI</h1>
      <p>Escalafón operacional de izaje (km/h en altura de pluma)</p>
    </header>
    <table class="tbl">
      <thead>
        <tr>
          <th>Nivel</th>
          <th>Ráfaga</th>
          <th>F / F_límite</th>
          <th>Acción</th>
        </tr>
      </thead>
      <tbody>
        <tr class="n0">
          <td>0 VERDE</td>
          <td>&lt; 26 km/h</td>
          <td>&lt; 40%</td>
          <td>Operación permitida</td>
        </tr>
        <tr class="n1">
          <td>1 AMARILLO</td>
          <td>26 – 29 km/h</td>
          <td>40 – 55%</td>
          <td>Pre-alerta · verificar anemómetro</td>
        </tr>
        <tr class="n2">
          <td>2 NARANJA</td>
          <td>30 – 34 km/h</td>
          <td>55 – 80%</td>
          <td>Restricción de cargas A·Cd elevado</td>
        </tr>
        <tr class="n3">
          <td>3 ROJO</td>
          <td>≥ 35 km/h (flag 36)</td>
          <td>&gt; 80%</td>
          <td>Parada obligatoria · asegurar pluma</td>
        </tr>
      </tbody>
    </table>
    <p class="nota">
      Flag secundario: probabilidad de rayos &gt; 30% o precipitación &gt; 2 mm/h eleva al menos a
      Naranja. Física: F = ½ ρ v² A Cd con ρ = p / (R_d T).
    </p>
  </div>
</template>

<style scoped>
.page { max-width: 800px; margin: 0 auto; padding: 1.25rem; }
.page-head h1 { margin: 0 0 0.35rem; }
.page-head p { margin: 0 0 1rem; color: var(--color-muted); }
.tbl { width: 100%; border-collapse: collapse; border: 1px solid var(--color-border); border-radius: var(--radius-md); overflow: hidden; }
.tbl th, .tbl td { padding: 0.65rem 0.75rem; text-align: left; border-bottom: 1px solid var(--color-border); font-size: 0.9rem; }
.tbl th { background: var(--color-surface); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-muted); }
.n0 td:first-child { color: #86efac; font-weight: 600; }
.n1 td:first-child { color: #fde68a; font-weight: 600; }
.n2 td:first-child { color: #fdba74; font-weight: 600; }
.n3 td:first-child { color: #fca5a5; font-weight: 600; }
.nota { margin-top: 1rem; color: var(--color-muted); font-size: 0.9rem; line-height: 1.5; }
</style>
