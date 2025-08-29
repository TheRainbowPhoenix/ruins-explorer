<script>
    import { zoomLevel } from '../store.js';

    function zoomIn() {
        zoomLevel.update(level => level < 4 ? level * 2 : level);
    }

    function zoomOut() {
        zoomLevel.update(level => level > 1 ? level / 2 : level);
    }

    function zoomReset() {
        zoomLevel.set(1);
    }
</script>

<div class="zoom-controls">
    <button class="zoom-btn" id="zoom-in" on:click={zoomIn}>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
    </button>
    <button class="zoom-btn" id="zoom-out" on:click={zoomOut}>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
    </button>
    <button class="zoom-btn" id="zoom-reset" on:click={zoomReset}>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="1 4 1 10 7 10"></polyline>
            <polyline points="23 20 23 14 17 14"></polyline>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
        </svg>
    </button>
</div>