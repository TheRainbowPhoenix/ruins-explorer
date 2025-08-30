<script lang='ts'>
    import { onMount } from 'svelte';
    import { 
        mapData, mapWidth, mapHeight, tileSize, zoomLevel, canvasSize,
        selectedTile, currentTool, currentPanel, selectedPosition, 
        isDrawing, areaStart, areaEnd, hoveredTile, events, 
        selectedEvent, actions, tooltip,
        guidesEnabled, guidePageWidth, guidePageHeight
    } from '../store.js';
    import StatusBar from './StatusBar.svelte';
    import ZoomControls from './ZoomControls.svelte';

    let canvas: HTMLCanvasElement;
    let ctx;
    let selectionOverlay;
    let tileset = new Image();

    // Reactive variables to calculate the number of guides needed
    $: numVerticalGuides = $guidesEnabled && $mapWidth > $guidePageWidth 
        ? Math.floor(($mapWidth - 1) / $guidePageWidth) 
        : 0;
    $: numHorizontalGuides = $guidesEnabled && $mapHeight > $guidePageHeight 
        ? Math.floor(($mapHeight - 1) / $guidePageHeight) 
        : 0;


    // ensure renderMap() is called with the latest data after Svelte's update cycle.
    $: if (canvas) renderMap($canvasSize, $mapData, $events);

    onMount(() => {
        ctx = canvas.getContext('2d');
        tileset.src = 'jrpg.png';
        
        tileset.onload = () => {
            renderMap($canvasSize, $mapData, $events);
        };

        // Subscribe to reactive updates
        const unsubscribes = [
            canvasSize.subscribe(updateSelectionOverlay),
            hoveredTile.subscribe(updateSelectionOverlay),
            selectedPosition.subscribe(updateSelectionOverlay),
            areaStart.subscribe(updateSelectionOverlay),
            areaEnd.subscribe(updateSelectionOverlay)

        ];

        return () => {
            unsubscribes.forEach(unsub => unsub());
        };
    });

    // Canvas event handlers
    function handleMouseDown(e) {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / ($tileSize * $zoomLevel));
        const y = Math.floor((e.clientY - rect.top) / ($tileSize * $zoomLevel));
        
        if (x >= 0 && x < $mapWidth && y >= 0 && y < $mapHeight) {
            selectedPosition.set({ x, y });
            if ($currentPanel === 'tiles') {
                isDrawing.set(true);
                
                if ($currentTool === 'place') {
                    // Place tile immediately on mousedown
                    actions.placeTile(x, y, $selectedTile);
                } else if ($currentTool === 'brush') {
                    actions.placeTile(x, y, $selectedTile);
                } else if ($currentTool === 'area') {
                    areaStart.set({ x, y });
                    areaEnd.set({ x, y });
                }
            } else if ($currentPanel === 'events') {
                const posKey = `${x},${y}`;
                selectedEvent.set($events[posKey] || null);
            }
        }
    }

    function handleMouseMove(e) {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / ($tileSize * $zoomLevel));
        const y = Math.floor((e.clientY - rect.top) / ($tileSize * $zoomLevel));
        
        if (x >= 0 && x < $mapWidth && y >= 0 && y < $mapHeight) {
            hoveredTile.set({ x, y });
            if ($currentPanel === 'tiles' && $isDrawing) {
                if ($currentTool === 'brush') {
                    actions.placeTile(x, y, $selectedTile);
                } else if ($currentTool === 'area') {
                    areaEnd.set({ x, y });
                }
            }
            
            // Tooltip Logic
            let displayText = '';
            let visible = false;
            /* if ($currentPanel === 'tiles') {
                const tileId = $mapData[y * $mapWidth + x];
                displayText = `ID: ${tileId}`;
            } else */
            if ($currentPanel === 'events') {
                const posKey = `${x},${y}`;
                if ($events[posKey]) {
                    displayText = $events[posKey].name || `(${x}, ${y})`;
                    visible = true;
                }
            }
            
            tooltip.set({
                visible,
                content: displayText,
                x: e.clientX + 15,
                y: e.clientY
            });

        } else {
            hoveredTile.set(null);
            tooltip.set({ visible: false, content: '', x: 0, y: 0 });
        }
    }

    function handleMouseLeave() {
        hoveredTile.set(null);
        tooltip.set({ visible: false, content: '', x: 0, y: 0 });
    }

    function handleMouseUp() {
        if ($isDrawing && $currentTool === 'area' && $areaStart && $areaEnd) {
            const startX = Math.min($areaStart.x, $areaEnd.x);
            const endX = Math.max($areaStart.x, $areaEnd.x);
            const startY = Math.min($areaStart.y, $areaEnd.y);
            const endY = Math.max($areaStart.y, $areaEnd.y);
            
            mapData.update(data => {
                const newData = [...data];
                for (let y = startY; y <= endY; y++) {
                    for (let x = startX; x <= endX; x++) {
                        const index = y * $mapWidth + x;
                        newData[index] = $selectedTile;
                    }
                }
                return newData;
            });
            
            areaStart.set(null);
            areaEnd.set(null);
        }
        isDrawing.set(false);
    }

    function renderMap(size, data, evts) {
        if (!ctx || !tileset.complete || !canvas || !size || !data || !evts) return;
        
        canvas.width = size.width;
        canvas.height = size.height;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let y = 0; y < $mapHeight; y++) {
            for (let x = 0; x < $mapWidth; x++) {
                const tileId = data[y * $mapWidth + x];
                if (tileId !== undefined) drawTile(x, y, tileId);
            }
        }
        
        Object.values(evts).forEach(event => {
            if (event?.pages?.length > 0) {
                 drawEvent(event.x, event.y, event.pages[0].graphic.tileId);
            }
        });
    }

    function drawTile(x, y, tileId) {
        if (tileId < 0) return;
        const tilesPerRow = Math.floor(tileset.width / $tileSize);
        const srcX = (tileId % tilesPerRow) * $tileSize;
        const srcY = Math.floor(tileId / tilesPerRow) * $tileSize;
        
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(
            tileset, srcX, srcY, $tileSize, $tileSize,
            x * $tileSize * $zoomLevel, y * $tileSize * $zoomLevel,
            $tileSize * $zoomLevel, $tileSize * $zoomLevel
        );
    }

    function drawEvent(x, y, tileId) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.fillRect(
            x * $tileSize * $zoomLevel,
            y * $tileSize * $zoomLevel,
            $tileSize * $zoomLevel,
            $tileSize * $zoomLevel
        );
        // Draw the event graphic on top of the overlay
        const originalAlpha = ctx.globalAlpha;
        ctx.globalAlpha = 0.8;
        drawTile(x, y, tileId);
        ctx.globalAlpha = originalAlpha;
    }

    function updateSelectionOverlay() {
        if (!selectionOverlay) return;
        
        selectionOverlay.innerHTML = '';
        
        if ($areaStart && $areaEnd) {
            const startX = Math.min($areaStart.x, $areaEnd.x);
            const endX = Math.max($areaStart.x, $areaEnd.x);
            const startY = Math.min($areaStart.y, $areaEnd.y);
            const endY = Math.max($areaStart.y, $areaEnd.y);
            
            const areaRect = document.createElement('div');
            areaRect.className = 'area-rect';
            areaRect.style.left = `${startX * $tileSize * $zoomLevel}px`;
            areaRect.style.top = `${startY * $tileSize * $zoomLevel}px`;
            areaRect.style.width = `${(endX - startX + 1) * $tileSize * $zoomLevel}px`;
            areaRect.style.height = `${(endY - startY + 1) * $tileSize * $zoomLevel}px`;
            selectionOverlay.appendChild(areaRect);
        }
        
        if ($selectedPosition?.x >= 0 && $selectedPosition?.y >= 0) {
            const { x, y } = $selectedPosition;
            const selectedRect = document.createElement('div');
            selectedRect.className = 'selection-rect';
            selectedRect.style.left = `${x * $tileSize * $zoomLevel}px`;
            selectedRect.style.top = `${y * $tileSize * $zoomLevel}px`;
            selectedRect.style.width = `${$tileSize * $zoomLevel}px`;
            selectedRect.style.height = `${$tileSize * $zoomLevel}px`;
            selectionOverlay.appendChild(selectedRect);
        }
        
        // Add hovered tile highlight
        if ($hoveredTile) {
            const { x, y } = $hoveredTile;
            const hoverRect = document.createElement('div');
            hoverRect.className = 'hover-rect';
            hoverRect.style.left = `${x * $tileSize * $zoomLevel}px`;
            hoverRect.style.top = `${y * $tileSize * $zoomLevel}px`;
            hoverRect.style.width = `${$tileSize * $zoomLevel}px`;
            hoverRect.style.height = `${$tileSize * $zoomLevel}px`;
            selectionOverlay.appendChild(hoverRect);
        }
    }
</script>

<div class="main-content">
    <div class="canvas-container">
        <div class="canvas-wrapper">
            <canvas 
                bind:this={canvas}
                id="tilemap-canvas" 
                on:mousedown={handleMouseDown}
                on:mousemove={handleMouseMove}
                on:mouseleave={handleMouseLeave}
                on:mouseup={handleMouseUp}
            ></canvas>
            <div class="selection-overlay" bind:this={selectionOverlay}></div>
            {#if $guidesEnabled}
            <div class="guide-overlay">
                <!-- Render Vertical Guide Lines -->
                {#each Array(numVerticalGuides) as _, i}
                    <div 
                        class="guide-line vertical"
                        style="left: {(i + 1) * $guidePageWidth * $tileSize * $zoomLevel}px;"
                    ></div>
                {/each}

                <!-- Render Horizontal Guide Lines -->
                {#each Array(numHorizontalGuides) as _, i}
                     <div 
                        class="guide-line horizontal"
                        style="top: {(i + 1) * $guidePageHeight * $tileSize * $zoomLevel}px;"
                    ></div>
                {/each}
            </div>
            {/if}
        </div>
    </div>
    <StatusBar />
    <ZoomControls />
</div>