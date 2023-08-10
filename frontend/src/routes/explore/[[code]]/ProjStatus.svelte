<script>
    import { AREA_BORDER, PROJ_COLORS, MUN_THR } from '$lib/config'
    import { t } from '$lib/translations'

    export let status
    export let zoom = 0

    let style=`
      --border: ${AREA_BORDER};
      --ready: ${PROJ_COLORS.READY};
      --mapping: ${PROJ_COLORS.MAPPING};
      --mapped: ${PROJ_COLORS.MAPPED};
      --validated: ${PROJ_COLORS.VALIDATED};
    `
  </script>
  
  <p class="legend-item" {style}>
    <span class={status.toLowerCase()}></span>
    {$t('explore.' + status, { gender: zoom >= MUN_THR ? 'male' : 'female' })}
  </p>
  
  <style>
    .legend-item span {
      display:inline-block;
      width: 1rem;
      height: 1rem;
      margin-right: 0.5rem;
      border-width: 1px;
      border-color: var(--border);
    }
    .legend-item span.ready {
      background-color: var(--ready);
    }
    .legend-item span.mapping {
      background-color: var(--mapping);
    }
    .legend-item span.mapped {
      background-color: var(--mapped);
    }
    .legend-item span.validated {
      background-color: var(--validated);
    }
    .legend-item {
      display: flex;
      align-items: center;
    }
  </style>