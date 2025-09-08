<script>
    import { onMount, afterUpdate } from 'svelte';
    import { currentTool, selectedTile, actions, tileSize, tilesetId } from '../../store.js';

    let tileset = new Image();
    let tilesetLoaded = false;
    let previewCanvas;

    onMount(() => {
        tileset.src = $tilesetId + ".png";
        tileset.onload = () => {
            tilesetLoaded = true;
            drawPreview();
        };
    });

    afterUpdate(() => {
        if (tilesetLoaded) {
            drawPreview();
        }
    });

    function drawPreview() {
        if (!previewCanvas) return;
        const ctx = previewCanvas.getContext('2d');
        const tile = $selectedTile;
        
        const tilesPerRow = Math.floor(tileset.width / $tileSize);
        const srcX = (tile % tilesPerRow) * $tileSize;
        const srcY = Math.floor(tile / tilesPerRow) * $tileSize;

        ctx.clearRect(0, 0, 64, 64);
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(
            tileset,
            srcX, srcY, $tileSize, $tileSize,
            0, 0, 64, 64
        );
    }

    function selectMode(mode) {
        currentTool.set(mode);
    }

    function selectTile(tileId) {
        selectedTile.set(tileId);
    }

    function fillMap() {
        actions.fillMap($selectedTile);
    }
</script>

<div class="form-group">
    <label class="form-label">Drawing Mode</label>
    <div class="mode-selector">
        <div class="mode-btn" class:active={$currentTool === 'place'} on:click={() => selectMode('place')}>
            Place
        </div>
        <div class="mode-btn" class:active={$currentTool === 'brush'} on:click={() => selectMode('brush')}>
            Brush
        </div>
        <div class="mode-btn" class:active={$currentTool === 'area'} on:click={() => selectMode('area')}>
            Area
        </div>
    </div>
</div>

<div class="form-group">
    <label class="form-label">Selected Tile</label>
    <div id="selected-tile-preview" style="width: 64px; height: 64px; border: 2px solid var(--border-primary); background: var(--bg-tertiary); image-rendering: pixelated;">
        {#if tilesetLoaded}
            <canvas bind:this={previewCanvas} width="64" height="64"></canvas>
        {/if}
    </div>
</div>

<div class="form-group">
    <label class="form-label">Tiles</label>
    <div class="tile-palette">
        {#if tilesetLoaded}
            {#each Array(
                Math.floor(tileset.width / $tileSize) * Math.floor(tileset.height / $tileSize)
            ) as _, i}
                {@const tilesPerRow = Math.floor(tileset.width / $tileSize)}
                {@const srcX = (i % tilesPerRow) * $tileSize}
                {@const srcY = Math.floor(i / tilesPerRow) * $tileSize}
                <div 
                    class="tile-item" 
                    class:selected={$selectedTile === i}
                    data-id={i}
                    style="
                        background-image: url('{tileset.src}');
                        background-position: -{srcX * 2}px -{srcY * 2}px;
                        background-size: {tileset.width * 2}px {tileset.height * 2}px;
                        width: {$tileSize*2}px;
                        height: {$tileSize*2}px;
                    "
                    on:click={() => selectTile(i)}
                ></div>
            {/each}
        {/if}
    </div>
</div>

<div class="form-group">
    <button class="btn btn-primary" on:click={fillMap}>Fill Map</button>
</div>