<script>
    import { currentPanel, displayName, mapWidth, mapHeight, tilesetId, 
             selectedTile, currentTool, events, selectedEvent, actions } from '../store.js';
    import MapPanel from './panels/MapPanel.svelte';
    import TilesPanel from './panels/TilesPanel.svelte';
    import EventsPanel from './panels/EventsPanel.svelte';
    import ExportPanel from './panels/ExportPanel.svelte';

    const panelTitles = {
        'map': 'Map Settings',
        'tiles': 'Tiles',
        'events': 'Events',
        'export': 'Export'
    };
</script>

<div class="sidebar" id="sidebar">
    <div class="sidebar-header">
        <span id="sidebar-title">{panelTitles[$currentPanel]}</span>
    </div>
    <div class="sidebar-content" id="sidebar-content">
        {#if $currentPanel === 'map'}
            <MapPanel />
        {:else if $currentPanel === 'tiles'}
            <TilesPanel />
        {:else if $currentPanel === 'events'}
            <EventsPanel />
        {:else if $currentPanel === 'export'}
            <ExportPanel />
        {/if}
    </div>
</div>