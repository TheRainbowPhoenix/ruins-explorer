<script>
    import { createEventDispatcher, onMount } from 'svelte';

    export let commandList = [];
    export let startIndex = 0;

    const dispatch = createEventDispatcher();
    
    let faceName = "";
    let faceIndex = 0;
    let textContent = "";

    // This block finds the start of the text block (the 101 command)
    // and gathers all subsequent 401 commands into a single string.
    onMount(() => {
        let blockStartIndex = startIndex;
        if (commandList[startIndex].code === 401) {
            for (let i = startIndex - 1; i >= 0; i--) {
                if (commandList[i].code === 101) {
                    blockStartIndex = i;
                    break;
                }
            }
        }
        
        const command101 = commandList[blockStartIndex];
        faceName = command101.parameters[0] || "";
        faceIndex = command101.parameters[1] || 0;

        let lines = [];
        for (let i = blockStartIndex + 1; i < commandList.length; i++) {
            if (commandList[i].code === 401) {
                lines.push(commandList[i].parameters[0]);
            } else {
                break;
            }
        }
        textContent = lines.join('\n');
    });

    function save() {
        // Reconstruct the command block from the form data
        const newCommands = [];
        
        // The main 101 command
        newCommands.push({
            ...commandList[startIndex], // Preserve indent and other properties
            code: 101,
            parameters: [faceName, faceIndex, 0, 2] // Assuming default background/position
        });

        // The chained 401 commands
        const lines = textContent.split('\n');
        for (const line of lines) {
            newCommands.push({
                ...commandList[startIndex],
                code: 401,
                parameters: [line]
            });
        }
        
        dispatch('save', newCommands);
    }

</script>

<div class="dialog-overlay" on:click={() => dispatch('close')}>
    <div class="dialog" on:click|stopPropagation>
        <div class="dialog-header">
            <span>Edit Text Block</span>
            <button class="btn btn-secondary" on:click={() => dispatch('close')}>✕</button>
        </div>
        <div class="dialog-content">
            <div class="form-group">
                <label class="form-label">Face Graphic</label>
                <div class="action-fields">
                    <input type="text" class="form-input" placeholder="Face Name" bind:value={faceName}>
                    <input type="number" class="form-input" placeholder="Face Index" bind:value={faceIndex}>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Text</label>
                <textarea class="form-textarea" rows="5" bind:value={textContent}></textarea>
            </div>
        </div>
        <div class="dialog-footer">
            <button class="btn btn-primary" on:click={save}>Save</button>
        </div>
    </div>
</div>