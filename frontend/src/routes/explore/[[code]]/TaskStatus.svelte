<script>
    import { NoSymbol } from 'svelte-heros-v2'
    import { AREA_BORDER, TASK_COLORS } from '$lib/config'
    import { t } from '$lib/translations'

    export let status

    let style=`
      --border: ${AREA_BORDER};
      --ready: ${TASK_COLORS.READY};
      --mapped: ${TASK_COLORS.MAPPED};
      --invalidated: ${TASK_COLORS.INVALIDATED};
      --validated: ${TASK_COLORS.VALIDATED};
      --update: ${TASK_COLORS.NEED_UPDATE};
    `
  </script>
  
  <p class="legend-item" {style}>
    {#if status === 'MIXED'}
      <span class="stripe"></span> {$t('explore.mixed')}
    {:else if status === 'LOCKED'}
      <NoSymbol size="18" color="red" strokeWidth="4" class="mr-2"/> {$t('explore.locked')}
    {:else}
      <span class={status.toLowerCase()}></span> {$t('explore.' + status)}
    {/if}
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
    .legend-item span.mapped {
      background-color: var(--mapped);
    }
    .legend-item span.invalidated {
      background-color: var(--invalidated);
    }
    .legend-item span.validated {
      background-color: var(--validated);
    }
    .legend-item span.need_update {
      background-color: var(--update);
    }
    .legend-item span.stripe {
      background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxMCcgaGVpZ2h0PScxMCc+CiAgPHJlY3Qgd2lkdGg9JzEwJyBoZWlnaHQ9JzEwJyBmaWxsPSd3aGl0ZScvPgogIDxwYXRoIGQ9J00tMSwxIGwyLC0yCiAgICAgICAgICAgTTAsMTAgbDEwLC0xMAogICAgICAgICAgIE05LDExIGwyLC0yJyBzdHJva2U9JyMxRTkwRkY5OScgc3Ryb2tlLXdpZHRoPSczJy8+Cjwvc3ZnPgo=");
      background-repeat: repeat;
      color: var(--mapped);
    } 
    .legend-item {
      display: flex;
      align-items: center;
    }
  </style>