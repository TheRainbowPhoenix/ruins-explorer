<script>
    import { onMount } from 'svelte';
    import { 
        mapData, mapWidth, mapHeight, tileSize, zoomLevel, canvasSize,
        selectedTile, currentTool, currentPanel, selectedPosition, 
        isDrawing, areaStart, areaEnd, hoveredTile, lastHoveredTile, 
        lastSelectedPosition, events, selectedEvent, actions 
    } from '../store.js';
    import StatusBar from './StatusBar.svelte';
    import ZoomControls from './ZoomControls.svelte';

    let canvas;
    let ctx;
    let selectionOverlay;
    let tileset = new Image();
    
    onMount(() => {
        ctx = canvas.getContext('2d');
        tileset.src = 'jrpg.png';
        
        tileset.onload = () => {
            renderMap();
        };

        // Subscribe to reactive updates
        const unsubscribes = [
            canvasSize.subscribe(size => {
                if (canvas) {
                    canvas.width = size.width;
                    canvas.height = size.height;
                    renderMap();
                }
            }),
            mapData.subscribe(() => renderMap()),
            zoomLevel.subscribe(() => renderMap()),
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
            if ($currentPanel === 'tiles') {
                isDrawing.set(true);
                selectedPosition.set({ x, y });
                
                if ($currentTool === 'place') {
                    placeTile(x, y);
                } else if ($currentTool === 'area') {
                    areaStart.set({ x, y });
                    areaEnd.set({ x, y });
                }
            } else if ($currentPanel === 'events') {
                selectedPosition.set({ x, y });
                
                const posKey = `${x},${y}`;
                if ($events[posKey]) {
                    selectedEvent.set($events[posKey]);
                } else {
                    const newEvent = {
                        id: Object.keys($events).length + 1,
                        name: `Event ${Object.keys($events).length + 1}`,
                        x: x,
                        y: y,
                        pages: [{
                            graphic: { tileId: 0 },
                            list: []
                        }]
                    };
                    selectedEvent.set(newEvent);
                }
            }
        }
    }

    function handleMouseMove(e) {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / ($tileSize * $zoomLevel));
        const y = Math.floor((e.clientY - rect.top) / ($tileSize * $zoomLevel));
        
        if (x >= 0 && x < $mapWidth && y >= 0 && y < $mapHeight) {
            if ($currentPanel === 'tiles' || $currentPanel === 'events') {
                if ($isDrawing && $currentPanel === 'tiles') {
                    if ($currentTool === 'brush') {
                        selectedPosition.set({ x, y });
                        placeTile(x, y);
                    } else if ($currentTool === 'area') {
                        areaEnd.set({ x, y });
                    }
                } else {
                    hoveredTile.set({ x, y });
                    
                    if ($lastHoveredTile?.x !== x || $lastHoveredTile?.y !== y || 
                        $lastSelectedPosition.x !== $selectedPosition.x || 
                        $lastSelectedPosition.y !== $selectedPosition.y) {
                        
                        lastHoveredTile.set({ x, y });
                        lastSelectedPosition.set({ ...$selectedPosition });
                    }
                }
            }
        }
    }

    function handleMouseLeave() {
        hoveredTile.set(null);
        lastHoveredTile.set(null);
    }

    function handleMouseUp() {
        if ($isDrawing && $currentTool === 'area' && $areaStart) {
            // Fill the area
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

    function placeTile(x, y) {
        mapData.update(data => {
            const newData = [...data];
            const index = y * $mapWidth + x;
            newData[index] = $selectedTile;
            return newData;
        });
    }

    function renderMap() {
        if (!ctx || !tileset.complete) return;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw map tiles
        for (let y = 0; y < $mapHeight; y++) {
            for (let x = 0; x < $mapWidth; x++) {
                const tileId = $mapData[y * $mapWidth + x];
                drawTile(x, y, tileId);
            }
        }
        
        // Draw events
        Object.keys($events).forEach(posKey => {
            const [x, y] = posKey.split(',').map(Number);
            const event = $events[posKey];
            drawEvent(x, y, event.pages[0].graphic.tileId);
        });
    }

    function drawTile(x, y, tileId) {
        if (!ctx || !tileset.complete) return;

        const tilesPerRow = Math.floor(tileset.width / $tileSize);
        const srcX = (tileId % tilesPerRow) * $tileSize;
        const srcY = Math.floor(tileId / tilesPerRow) * $tileSize;
        
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(
            tileset,
            srcX, srcY, $tileSize, $tileSize,
            x * $tileSize * $zoomLevel, y * $tileSize * $zoomLevel,
            $tileSize * $zoomLevel, $tileSize * $zoomLevel
        );
    }

    function drawEvent(x, y, tileId) {
        const tilesPerRow = Math.floor(tileset.width / $tileSize);
        const srcX = (tileId % tilesPerRow) * $tileSize;
        const srcY = Math.floor(tileId / tilesPerRow) * $tileSize;
        
        // Draw semi-transparent black background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(
            x * $tileSize * $zoomLevel,
            y * $tileSize * $zoomLevel,
            $tileSize * $zoomLevel,
            $tileSize * $zoomLevel
        );
        
        // Draw event graphic
        ctx.save();
        ctx.globalAlpha = 0.8;
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(
            tileset,
            srcX, srcY, $tileSize, $tileSize,
            x * $tileSize * $zoomLevel, y * $tileSize * $zoomLevel,
            $tileSize * $zoomLevel, $tileSize * $zoomLevel
        );
        ctx.restore();
    }

    function updateSelectionOverlay() {
        if (!selectionOverlay) return;
        
        // Clear previous overlay
        selectionOverlay.innerHTML = '';
        
        // Add area selection if active
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
        
        // Add selected position highlight
        if ($selectedPosition.x >= 0 && $selectedPosition.y >= 0) {
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
                width={$canvasSize.width} 
                height={$canvasSize.height}
                on:mousedown={handleMouseDown}
                on:mousemove={handleMouseMove}
                on:mouseleave={handleMouseLeave}
                on:mouseup={handleMouseUp}
            ></canvas>
            <div class="selection-overlay" bind:this={selectionOverlay}></div>
        </div>
    </div>
    <StatusBar />
    <ZoomControls />
</div>