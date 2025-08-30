<script>
    import { createEventDispatcher, onMount } from 'svelte';
    let dialogElement;

    function handleKeydown(e) {
        if (e.key === 'Escape') {
            e.stopPropagation();
            dispatch('close');
        }
    }
    export let command;
    
    let localCommand = JSON.parse(JSON.stringify(command));
    const dispatch = createEventDispatcher();

    // Temporary state for the choices textarea
    let choicesText = '';

    const variableOps = [
        { value: 0, label: 'Set' }, { value: 1, label: 'Add' },
        { value: 2, label: 'Subtract' }, { value: 3, label: 'Multiply' },
        { value: 4, label: 'Divide' }, { value: 5, label: 'Modulo' }
    ];

    const ifConditionOps = [
        { value: 0, label: '== Equal to' }, { value: 1, label: '>= Greater or Equal' },
        { value: 2, label: '<= Less or Equal' }, { value: 3, label: '> Greater than' },
        { value: 4, label: '< Less than' }, { value: 5, label: '!= Not Equal to' }
    ];

    let loaded = false;

    onMount(() => {
        
        dialogElement?.focus();

        const defaults = {
            101: ['', 0],
            102: [[], -2, null],
            103: [1, 3],
            111: [0, 1, 0, 0, 0, 0], // type, id, val, operand_type, op
            121: [1, 1, 0],
            122: [1, 1, 0, 0, 0], // start, end, op, operand_type, val
            123: ["A", 0],
            124: [0, 60],
            125: [0, 0, 0],
            126: [1, 0, 0, 1],
            127: [1, 0, 0, 1],
            128: [1, 0, 0, 1],
            201: [0, 1, 0, 0],
            301: [0, 1, true, false, 10], 
            303: [1, 8], 
            356: [''],
            401: [''],
            402: [0],
            501: [0, 0, false],
        };
        
        const defaultParams = defaults[localCommand.code];

        if (defaultParams) {
            if (!localCommand.parameters || !Array.isArray(localCommand.parameters)) {
                localCommand.parameters = [];
            }
            for (let i = 0; i < defaultParams.length; i++) {
                if (localCommand.parameters[i] === undefined || localCommand.parameters[i] === null) {
                    localCommand.parameters[i] = defaultParams[i];
                }
            }
        }
        // Special handling for choices textarea
        if (localCommand.code === 102) {
            choicesText = (localCommand.parameters[0] || []).join('\n');
        }
        loaded = true;
    });

    function save() {
        // Special handling for choices textarea
        if (localCommand.code === 102) {
            localCommand.parameters[0] = choicesText.split('\n').filter(line => line.trim() !== '');
        }
        dispatch('save', localCommand);
    }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="dialog-overlay" on:dblclick|self={() => dispatch('close')} on:keydown={handleKeydown}>
    <div class="dialog" bind:this={dialogElement} tabindex="-1" on:click|stopPropagation>
        <div class="dialog-header">
            <span>Edit Command</span>
            <button class="btn btn-secondary" on:click={() => dispatch('close')}>✕</button>
        </div>
        <div class="dialog-content">
        {#if loaded}
            {#if localCommand.code === 101}
                <div class="form-group">
					<label class="form-label" for="101_0">Face Name</label>
                    <input type="text" class="form-input" name="101_0" bind:value={localCommand.parameters[0]}></div>
                <div class="form-group">
					<label class="form-label" for="101_1">Face Index</label>
                    <input type="number" class="form-input" name="101_1" bind:value={localCommand.parameters[1]}></div>
            {:else if localCommand.code === 102}
                <div class="form-group">
                    <label>Choices (one per line)</label>
                    <textarea class="form-textarea" rows="4" bind:value={choicesText}></textarea>
                </div>

                <div class="form-group">
                    <label>Cancel Type</label>
                    <select class="form-select" bind:value={localCommand.parameters[1]}>
                        <option value={-2}>Disallow</option>
                        <option value={-1}>Branch</option>
                        <option value={0}>Choice 1</option>
                        <option value={1}>Choice 2</option>
                        <option value={2}>Choice 3</option>
                        <option value={3}>Choice 4</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Store Choice in Variable (Optional)</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[2]}>
                </div>
            {:else if localCommand.code === 103}
                <div class="form-group">
                    <label>Store Result in Variable ID</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[0]}>
                </div>

                <div class="form-group">
                    <label>Number of Digits</label>
                    <input type="number" class="form-input" min="1" max="16" bind:value={localCommand.parameters[1]}>
                </div>
            {:else if localCommand.code === 111}
                <div class="form-group">
					<label class="form-label">Condition Type</label>
                    <select class="form-select" bind:value={localCommand.parameters[0]}>
                        <option value={0}>Switch</option>
                        <option value={1}>Variable</option>
                    </select>
                </div>
                {#if localCommand.parameters[0] === 0}
                    <div class="form-group">
                        <label class="form-label">Switch</label>
                        <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                    </div>
                    <div class="form-group">
					    <label class="form-label">Is</label>
                        <select class="form-select" bind:value={localCommand.parameters[2]}>
                            <option value={0}>ON</option>
                            <option value={1}>OFF</option>
                        </select>
                    </div>
                {/if}
                {#if localCommand.parameters[0] === 1}
                    <div class="form-group">
					    <label class="form-label">Variable</label>
                        <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                    </div>

                    <div class="form-group">
					    <label class="form-label">Operator</label>
                        <select class="form-select" bind:value={localCommand.parameters[4]}>
                            {#each ifConditionOps as op}
                            <option value={op.value}>{op.label}</option>
                            {/each}
                        </select>
                    </div>
                    
                    <div class="form-group">
					    <label class="form-label">Operand</label>
                        <select class="form-select" bind:value={localCommand.parameters[2]}>
                            <option value={0}>Constant</option>
                            <option value={1}>Variable</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
					    <label class="form-label">Value</label>
                        <input type="number" class="form-input" bind:value={localCommand.parameters[3]}>
                    </div>
                {/if}
            {:else if localCommand.code === 121}
                 <div class="form-group">
					<label class="form-label">Switch Range</label>
                    
                    <div class="action-fields">
                        <input type="number" class="form-input" bind:value={localCommand.parameters[0]}>
                        <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                    </div>
                </div>

                <div class="form-group">
					<label class="form-label">Operation</label>
                    <select class="form-select" bind:value={localCommand.parameters[2]}>
                        <option value={0}>ON</option>
                        <option value={1}>OFF</option>
                    </select>
                </div>
            {:else if localCommand.code === 122}
                <div class="form-group">
					<label class="form-label">Variable Range</label>
                    <div class="action-fields">
                        <input type="number" class="form-input" bind:value={localCommand.parameters[0]}>
                        <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                    </div>
                </div>

                <div class="form-group">
					<label class="form-label">Operation</label>
                    <select class="form-select" bind:value={localCommand.parameters[2]}>
                        {#each variableOps as op}
                        <option value={op.value}>{op.label}</option>
                        {/each}
                    </select>
                </div>

                <div class="form-group">
					<label class="form-label">Operand</label>
                    <select class="form-select" bind:value={localCommand.parameters[3]}>
                        <option value={0}>Constant</option>
                        <option value={1}>Variable</option>
                    </select>
                </div>

                <div class="form-group">
					<label class="form-label">Value</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[4]}>
                </div>
            {:else if localCommand.code === 123}
                <div class="form-group">
					<label class="form-label">Self Switch</label>
                    <select class="form-select" bind:value={localCommand.parameters[0]}>
                        <option value={"A"}>A</option>
                        <option value={"B"}>B</option>
                        <option value={"C"}>C</option>
                        <option value={"D"}>D</option>
                        <option value={"E"}>E</option>
                        <option value={"F"}>F</option>
                    </select>
                </div>

                <div class="form-group">
					<label class="form-label">Operation</label>
                    <select class="form-select" bind:value={localCommand.parameters[1]}>
                        <option value={0}>ON</option>
                        <option value={1}>OFF</option>
                    </select>
                </div>
            {:else if localCommand.code === 124}
                <div class="form-group">
					<label class="form-label">Operation</label>
                    <select class="form-select" bind:value={localCommand.parameters[0]}>
                        <option value={0}>Start</option>
                        <option value={1}>Stop</option>
                    </select>
                </div>

                {#if localCommand.parameters[0] === 0}
                    <div class="form-group">
                        <label class="form-label">Seconds</label>
                        <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                    </div>
                {/if}
            {:else if localCommand.code === 125}
                <div class="form-group">
                    <label>Operation</label>
                    <select class="form-select" bind:value={localCommand.parameters[0]}>
                        <option value={0}>Increase</option>
                        <option value={1}>Decrease</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Operand</label>
                    <select class="form-select" bind:value={localCommand.parameters[1]}>
                        <option value={0}>Constant</option>
                        <option value={1}>Variable</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>{localCommand.parameters[1] === 0 ? 'Amount' : 'Variable ID'}</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[2]}>
                </div>
            {:else if [126, 127, 128].includes(localCommand.code)}
                {@const itemType = {126: 'Item', 127: 'Weapon', 128: 'Armor'}[localCommand.code]}
                
                <div class="form-group">
                    <label>{itemType} ID</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[0]}>
                </div>
                
                <div class="form-group">
                    <label>Operation</label>
                    <select class="form-select" bind:value={localCommand.parameters[1]}>
                        <option value={0}>Increase</option>
                        <option value={1}>Decrease</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Operand</label>
                    <select class="form-select" bind:value={localCommand.parameters[2]}>
                        <option value={0}>Constant</option>
                        <option value={1}>Variable</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>{localCommand.parameters[2] === 0 ? 'Amount' : 'Variable ID'}</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[3]}>
                </div>
            {:else if localCommand.code === 201}
                <div class="form-group">
					<label class="form-label">Map ID</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                </div>
                
                <div class="form-group">
					<label class="form-label">Position</label>
                    
                    <div class="action-fields">
                        <input type="number" class="form-input" placeholder="X" bind:value={localCommand.parameters[2]}>
                        <input type="number" class="form-input" placeholder="Y" bind:value={localCommand.parameters[3]}>
                    </div>
                </div>
            {:else if localCommand.code === 301}
                <div class="form-group">
                    <label>Troop Designation</label>
                    <select class="form-select" bind:value={localCommand.parameters[0]}>
                        <option value={0}>Direct</option>
                        <option value={1}>Variable</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>{localCommand.parameters[0] === 0 ? 'Troop ID' : 'Variable ID'}</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                </div>
                
                <div class="form-group">
                    <label style="display:flex; align-items:center; gap:8px;">
                        <input type="checkbox" bind:checked={localCommand.parameters[2]}> Can Escape
                    </label>
                </div>
                
                <div class="form-group">
                    <label style="display:flex; align-items:center; gap:8px;">
                        <input type="checkbox" bind:checked={localCommand.parameters[3]}> Can Lose
                    </label>
                </div>
                
                <div class="form-group">
                    <label>Store Result in Variable ID (0=None)</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[4]}>
                </div>
            {:else if localCommand.code === 303}
                <div class="form-group">
                    <label>Actor ID</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[0]}>
                </div>

                <div class="form-group">
                    <label>Max Characters</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                </div>
            {:else if localCommand.code === 356}
                <div class="form-group">
					<label class="form-label">Plugin Command</label>
                    <input type="text" class="form-input" bind:value={localCommand.parameters[0]}>
                </div>
            {:else if localCommand.code === 401}
                <div class="form-group">
					<label class="form-label">Text</label>
                    <input type="text" class="form-input" bind:value={localCommand.parameters[0]}>
                </div>
            {:else if localCommand.code === 402}
                 <div class="form-group">
                    <label>Handle Choice #</label>
                    <input type="number" class="form-input" min="1" step="1" on:input={(e) => localCommand.parameters[0] = e.target.value - 1} value={localCommand.parameters[0] + 1}>
                </div>
            {:else if localCommand.code === 501}
                <div class="form-group">
					<label class="form-label">Event ID (0 for this event)</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[0]}>
                </div>
                
                <div class="form-group">
					<label class="form-label">Tile ID</label>
                    <input type="number" class="form-input" bind:value={localCommand.parameters[1]}>
                </div>

                <div class="form-group">
					<label style="display: flex; align-items: center; gap: 8px;">
                        <input type="checkbox" bind:checked={localCommand.parameters[2]}> Use Variable
                    </label>
                </div>
            {:else}
                <p>This command has no editable parameters.</p>
            {/if}
        {:else}
            <p>Loading...</p>
        {/if}
        </div>
        <div class="dialog-footer">
            <button class="btn btn-danger" on:click={() => dispatch('delete')}>Delete</button>
            <button class="btn btn-primary" on:click={save}>Save</button>
        </div>
    </div>
</div>