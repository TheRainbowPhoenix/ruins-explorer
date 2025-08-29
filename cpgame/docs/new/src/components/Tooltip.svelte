<script>
    import { tooltip } from '../store.js';
</script>

{#if $tooltip.visible}
    <div 
        class="tile-id-display" 
        style="transform: translate({$tooltip.x}px, {$tooltip.y}px);"
    >
        {@html $tooltip.content}
    </div>
{/if}

<style>
    .tile-id-display {
        position: fixed;
        left: 0;
        top: 0;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        pointer-events: none;
        z-index: 100;
        white-space: nowrap;
    }
</style>