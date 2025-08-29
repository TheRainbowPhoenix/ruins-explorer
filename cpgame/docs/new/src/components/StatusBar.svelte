<script>
    import { selectedPosition, zoomLevel, editorMode, hoveredTile } from '../store.js';

    $: cursorPosition = $hoveredTile ? 
        `${$hoveredTile.x}, ${$hoveredTile.y}` : 
        `${$selectedPosition.x}, ${$selectedPosition.y}`;
</script>

<div class="status-bar">
    <div class="status-item">Position: <span id="cursor-position">{cursorPosition}</span></div>
    <div class="status-item">Zoom: <span id="zoom-level">{$zoomLevel}x</span></div>
    <div class="status-item">Mode: <span id="editor-mode">{$editorMode}</span></div>
</div>