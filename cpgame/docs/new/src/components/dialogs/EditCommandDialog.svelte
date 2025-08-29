<script>
    import { createEventDispatcher } from 'svelte';
    export let command;
    
    let localCommand = JSON.parse(JSON.stringify(command));
    const dispatch = createEventDispatcher();
</script>

<div class="dialog-overlay" on:click={() => dispatch('close')}>
    <div class="dialog" on:click|stopPropagation>
        <div class="dialog-header">
            <h3>Edit Command</h3>
            <button class="btn btn-secondary" on:click={() => dispatch('close')}>✕</button>
        </div>
        <div class="dialog-content">
            {#if localCommand.code === 101}
                <div class="form-group"><label class="form-label">Face Name</label><input type="text" class="form-input" bind:value={localCommand.parameters[0]}></div>
                <div class="form-group"><label class="form-label">Face Index</label><input type="number" class="form-input" bind:value={localCommand.parameters[1]}></div>
            {:else if localCommand.code === 401}
                <div class="form-group"><label class="form-label">Text</label><input type="text" class="form-input" bind:value={localCommand.parameters[0]}></div>
            {:else if localCommand.code === 121}
                 <div class="form-group"><label class="form-label">Switch Range</label><div class="action-fields"><input type="number" class="form-input" bind:value={localCommand.parameters[0]}><input type="number" class="form-input" bind:value={localCommand.parameters[1]}></div></div>
                <div class="form-group"><label class="form-label">Operation</label><select class="form-select" bind:value={localCommand.parameters[2]}><option value={0}>ON</option><option value={1}>OFF</option></select></div>
            {:else if localCommand.code === 123}
                <div class="form-group"><label class="form-label">Self Switch</label><select class="form-select" bind:value={localCommand.parameters[0]}><option value={0}>A</option><option value={1}>B</option><option value={2}>C</option><option value={3}>D</option></select></div>
                <div class="form-group"><label class="form-label">Operation</label><select class="form-select" bind:value={localCommand.parameters[1]}><option value={0}>ON</option><option value={1}>OFF</option></select></div>
            {:else if localCommand.code === 201}
                <div class="form-group"><label class="form-label">Map ID</label><input type="number" class="form-input" bind:value={localCommand.parameters[1]}></div>
                <div class="form-group"><label class="form-label">Position</label><div class="action-fields"><input type="number" class="form-input" placeholder="X" bind:value={localCommand.parameters[2]}><input type="number" class="form-input" placeholder="Y" bind:value={localCommand.parameters[3]}></div></div>
            {:else if localCommand.code === 356}
                <div class="form-group"><label class="form-label">Plugin Command</label><input type="text" class="form-input" bind:value={localCommand.parameters[0]}></div>
            {:else if localCommand.code === 501}
                <div class="form-group"><label class="form-label">Event ID (0 for this event)</label><input type="number" class="form-input" bind:value={localCommand.parameters[0]}></div>
                <div class="form-group"><label class="form-label">Tile ID</label><input type="number" class="form-input" bind:value={localCommand.parameters[1]}></div>
                 <div class="form-group"><input type="checkbox" bind:checked={localCommand.parameters[2]}> Use Variable</div>
            {:else}
                <p>This command has no editable parameters.</p>
            {/if}
        </div>
        <div class="dialog-footer">
            <button class="btn btn-danger" on:click={() => dispatch('delete')}>Delete</button>
            <button class="btn btn-primary" on:click={() => dispatch('save', localCommand)}>Save</button>
        </div>
    </div>
</div>