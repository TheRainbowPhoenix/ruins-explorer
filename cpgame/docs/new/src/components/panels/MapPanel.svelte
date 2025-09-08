<script>
    import { displayName, mapWidth, mapHeight, tilesetId, actions, guidesEnabled, isGuideEditorOpen, tileSize } from '../../store.js';
    import GuideEditorDialog from '../dialogs/GuideEditorDialog.svelte';

    // let localDisplayName = $displayName;
    let localWidth = $mapWidth;
    let localHeight = $mapHeight;
    let localTilesetId = $tilesetId;

    function resizeMap() {
        if (localWidth > 0 && localHeight > 0) {
            actions.resizeMap(localWidth, localHeight);
            // displayName.set(localDisplayName);
            tilesetId.set(localTilesetId);
        }
    }
</script>

<div class="form-group">
    <label class="form-label">Display Name</label>
    <input type="text" class="form-input" bind:value={$displayName}>
</div>
<div class="form-group">
    <label class="form-label">Width</label>
    <input type="number" class="form-input" min="1" max="100" bind:value={localWidth}>
</div>
<div class="form-group">
    <label class="form-label">Height</label>
    <input type="number" class="form-input" min="1" max="100" bind:value={localHeight}>
</div>
<div class="form-group">
    <label class="form-label">Tileset ID</label>
    <input type="text" class="form-input" bind:value={localTilesetId}>
</div>
<div class="form-group">
    <button class="btn btn-primary" on:click={resizeMap}>Resize Map</button>
</div>

<!-- Advanced Settings Section -->
<details>
    <summary>Advanced Settings</summary>
    <div class="details-content">
        <div class="setting-row">
            <span>
                Enable Guides
                <button class="btn-text" on:click={() => isGuideEditorOpen.set(true)}>Edit</button>
            </span>
            <label class="switch">
                <input type="checkbox" bind:checked={$guidesEnabled}>
                <span class="slider"></span>
            </label>
        </div>
        <div class="form-group">
            <label class="form-label">Tile Size</label>
            <input type="number" class="form-input" min="1" max="100" bind:value={$tileSize}>
        </div>
    </div>
</details>



{#if $isGuideEditorOpen}
    <GuideEditorDialog on:close={() => isGuideEditorOpen.set(false)} />
{/if}