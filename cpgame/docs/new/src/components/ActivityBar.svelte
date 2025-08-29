<script>
    import { currentPanel } from '../store.js';

    const panels = [
        {
            id: 'map',
            title: 'Map Settings',
            icon: `<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>`
        },
        {
            id: 'tiles',
            title: 'Tiles',
            icon: `<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="3" y1="9" x2="21" y2="9"></line>
                  <line x1="9" y1="21" x2="9" y2="9"></line>`
        },
        {
            id: 'events',
            title: 'Events',
            icon: `<circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>`
        },
        {
            id: 'export',
            title: 'Export',
            icon: `<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>`
        }
    ];

    function selectPanel(panelId) {
        currentPanel.set(panelId);
    }
</script>

<div class="activity-bar">
    <!-- Activity Bar Logo -->
    <div class="activity-logo-header" title="Tilemap Editor">
        <svg class="activity-logo" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="4" width="24" height="24" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
            <rect x="8" y="8" width="4" height="4" fill="currentColor"/>
            <rect x="14" y="8" width="4" height="4" fill="currentColor"/>
            <rect x="20" y="8" width="4" height="4" fill="currentColor"/>
            <rect x="8" y="14" width="4" height="4" fill="currentColor"/>
            <rect x="14" y="14" width="4" height="4" fill="currentColor"/>
            <rect x="20" y="14" width="4" height="4" fill="currentColor"/>
            <rect x="8" y="20" width="4" height="4" fill="currentColor"/>
            <rect x="14" y="20" width="4" height="4" fill="currentColor"/>
            <rect x="20" y="20" width="4" height="4" fill="currentColor"/>
        </svg>
    </div>
    
    <div class="activity-separator"></div>
    
    <!-- Activity Items -->
    {#each panels as panel}
        <div 
            class="activity-item" 
            class:active={$currentPanel === panel.id}
            title={panel.title}
            on:click={() => selectPanel(panel.id)}
        >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                {@html panel.icon}
            </svg>
        </div>
    {/each}
</div>
