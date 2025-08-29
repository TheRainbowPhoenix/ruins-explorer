<script>
    import { createEventDispatcher, onMount } from 'svelte';
    export let conditions = {};

    const dispatch = createEventDispatcher();
    let localConditions = JSON.parse(JSON.stringify(conditions));

    let loaded = false;

    // Ensure all possible condition properties exist on the local object for reliable binding
    onMount(() => {
        localConditions.switch1Valid = localConditions.switch1Valid || false;
        localConditions.switch1Id = localConditions.switch1Id || 1;
        localConditions.switch2Valid = localConditions.switch2Valid || false;
        localConditions.switch2Id = localConditions.switch2Id || 1;
        localConditions.variableValid = localConditions.variableValid || false;
        localConditions.variableId = localConditions.variableId || 1;
        localConditions.variableValue = localConditions.variableValue || 0;
        localConditions.selfSwitchValid = localConditions.selfSwitchValid || false;
        localConditions.selfSwitchCh = localConditions.selfSwitchCh || 'A';
        loaded = true;
    });

    function save() {
        // Clean up unused properties before saving
        if (!localConditions.switch1Valid) delete localConditions.switch1Id;
        if (!localConditions.switch2Valid) delete localConditions.switch2Id;
        if (!localConditions.variableValid) {
            delete localConditions.variableId;
            delete localConditions.variableValue;
        }
        if (!localConditions.selfSwitchValid) delete localConditions.selfSwitchCh;
        dispatch('save', localConditions);
    }
</script>

<div class="dialog-overlay" on:click={() => dispatch('close')}>
    <div class="dialog" on:click|stopPropagation>
        <div class="dialog-header">
            <span>Edit Page Conditions</span>
            <button class="btn btn-secondary" on:click={() => dispatch('close')}>✕</button>
        </div>
        <div class="dialog-content">
            {#if loaded}
                <!-- Switch 1 -->
            <div class="form-group"><label style="display: flex; align-items: center; gap: 8px;"><input type="checkbox" bind:checked={localConditions.switch1Valid}> Switch 1</label>
                {#if localConditions.switch1Valid}
                    <div class="action-fields" style="margin-left: 20px;"><span>ID:</span><input type="number" class="form-input" bind:value={localConditions.switch1Id}><span>is ON</span></div>
                {/if}
            </div>
            <!-- Switch 2 -->
            <div class="form-group"><label style="display: flex; align-items: center; gap: 8px;"><input type="checkbox" bind:checked={localConditions.switch2Valid}> Switch 2</label>
                {#if localConditions.switch2Valid}
                    <div class="action-fields" style="margin-left: 20px;"><span>ID:</span><input type="number" class="form-input" bind:value={localConditions.switch2Id}><span>is ON</span></div>
                {/if}
            </div>
            <!-- Variable -->
            <div class="form-group"><label style="display: flex; align-items: center; gap: 8px;"><input type="checkbox" bind:checked={localConditions.variableValid}> Variable</label>
                {#if localConditions.variableValid}
                     <div class="action-fields" style="margin-left: 20px;"><span>ID:</span><input type="number" class="form-input" bind:value={localConditions.variableId}><span>is >=</span><input type="number" class="form-input" bind:value={localConditions.variableValue}></div>
                {/if}
            </div>
            <!-- Self Switch -->
            <div class="form-group"><label style="display: flex; align-items: center; gap: 8px;"><input type="checkbox" bind:checked={localConditions.selfSwitchValid}> Self Switch</label>
                {#if localConditions.selfSwitchValid}
                    <div class="action-fields" style="margin-left: 20px;"><select class="form-select" bind:value={localConditions.selfSwitchCh}><option>A</option><option>B</option><option>C</option><option>D</option></select><span>is ON</span></div>
                {/if}
            </div>
            {/if}
        </div>
        <div class="dialog-footer">
            <button class="btn btn-primary" on:click={save}>Save Conditions</button>
        </div>
    </div>
</div>