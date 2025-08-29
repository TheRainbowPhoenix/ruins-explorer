<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();

    const commandGroups = {
        "Message": [
            { name: "Show Text", code: 101, params: ["", 0, 0, 2] },
            { name: "Show Choices", code: 102, params: [["Choice 1", "Choice 2"], -2, null] },
            { name: "Input Number", code: 103, params: [1, 3] },
            { name: "Name Input", code: 303, params: [1, 8] }
        ],
        "Flow Control": [
            { name: "If...", code: 111, params: [0, 1, 0] },
            { name: "When [Choice]", code: 402, params: [0], indent: true },
            { name: "When [Cancel]", code: 403, params: [], indent: true },
            { name: "Else", code: 411, params: [], indent: true },
            { name: "End If", code: 412, params: [], indent: true }
        ],
        "Game Data": [
            { name: "Control Switches", code: 121, params: [1, 1, 0] },
            { name: "Control Variables", code: 122, params: [1, 1, 0, 0, 0] },
            { name: "Control Self Switch", code: 123, params: [0, 0] },
            { name: "Control Timer", code: 124, params: [0, 60] }
        ],
        "Scene": [
            { name: "Transfer Player", code: 201, params: [0, 1, 0, 0] },
            { name: "Battle Processing", code: 301, params: [0, 1] },
            { name: "Shop Processing", code: 302, params: [0, 1, 0, 0, false] }
        ],
        "Map": [
            { name: "Set Event Graphic", code: 501, params: [0, 0, false] }
        ],
        "Advanced": [
            { name: "Plugin Command", code: 356, params: [""] }
        ]
    };

    function add(command) {
        dispatch('add', command);
        dispatch('close');
    }
</script>

<div class="dialog-overlay" on:click={() => dispatch('close')}>
    <div class="dialog dialog-large" on:click|stopPropagation>
        <div class="dialog-header">
            <span>Add Command</span>
            <button class="btn btn-secondary" on:click={() => dispatch('close')}>✕</button>
        </div>
        <div class="dialog-content" style="display: flex; gap: 16px; flex-wrap: wrap;">
            {#each Object.entries(commandGroups) as [groupName, commands]}
                <div class="form-group" style="min-width: 200px;">
                    <label class="form-label">{groupName}</label>
                    {#each commands as command}
                        <button class="btn btn-secondary" style="width: 100%; text-align: left; margin-bottom: 4px;" on:click={() => add(command)}>
                            {command.name}
                        </button>
                    {/each}
                </div>
            {/each}
        </div>
    </div>
</div>