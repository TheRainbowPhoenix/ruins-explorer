<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { guidePageWidth, guidePageHeight } from '../../store.js';

    const dispatch = createEventDispatcher();
    let dialogElement;
    let localWidth = $guidePageWidth;
    let localHeight = $guidePageHeight;

    onMount(() => {
        dialogElement?.focus();
    });

    function handleKeydown(e) {
        if (e.key === 'Escape') {
            e.stopPropagation();
            dispatch('close');
        }
    }

    function save() {
        guidePageWidth.set(localWidth);
        guidePageHeight.set(localHeight);
        dispatch('close');
    }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="dialog-overlay" on:dblclick|self={() => dispatch('close')} on:keydown={handleKeydown}>
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <div class="dialog" bind:this={dialogElement} tabindex="-1" on:click|stopPropagation>
        <div class="dialog-header">
            <span>Edit Guide Dimensions</span>
            <button class="btn btn-secondary" on:click={() => dispatch('close')}>✕</button>
        </div>
        <div class="dialog-content">
            <p style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: 0;">
                Set the page size (in tiles) for the visual guides.
            </p>
            <div class="form-group">
                <label class="form-label">Page Width (Tiles)</label>
                <input type="number" class="form-input" min="1" max="100" bind:value={localWidth}>
            </div>
            <div class="form-group">
                <label class="form-label">Page Height (Tiles)</label>
                <input type="number" class="form-input" min="1" max="100" bind:value={localHeight}>
            </div>
        </div>
        <div class="dialog-footer">
            <button class="btn btn-primary" on:click={save}>Save</button>
        </div>
    </div>
</div>