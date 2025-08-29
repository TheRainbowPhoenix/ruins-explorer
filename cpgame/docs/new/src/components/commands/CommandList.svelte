<script>
    import { createEventDispatcher } from 'svelte';
    export let commands = [];

    const dispatch = createEventDispatcher();

    function formatCommand(command) {
        const _p = (idx) => {
            if (command.parameters && command.parameters.length < idx) {
                return command.parameters[idx];
            } 
            return `<${idx}>`
        }
        switch (command.code) {
            case 101: return `Show Text: Face "${_p(0)}", Index ${_p(1)}`;
            case 102: return `Show Choices: [${_p(0).join(', ')}]`;
            case 103: return `Input Number: V[${_p(0)}] (${_p(1)} digits)`;
            case 111: 
                if (_p(0) === 0) return `◆ If: Switch [${_p(1)}] is ${_p(2) === 0 ? 'ON' : 'OFF'}`;
                if (_p(0) === 1) return `◆ If: Variable [${_p(1)}] ...`;
                return '◆ If: ...';
            case 121: return `Control Switches: [${_p(0)}-${_p(1)}] = ${_p(2) === 0 ? 'ON' : 'OFF'}`;
            case 122: return `Control Variables: V[${_p(0)}-${_p(1)}] ...`;
            case 123: return `Control Self Switch: ${String.fromCharCode(65 + _p(0))} = ${_p(1) === 0 ? 'ON' : 'OFF'}`;
            case 124: return `Control Timer: ${_p(0) === 0 ? 'Start' : 'Stop'} (${_p(1)}s)`;
            case 201: return `Transfer Player: Map ${_p(1)}, (${_p(2)}, ${_p(3)})`;
            case 301: return `Battle Processing: Enemy ID ${_p(1)}`;
            case 302: return `Shop Processing`;
            case 303: return `Name Input: Actor ${_p(0)} (${_p(1)} chars)`;
            case 356: return `Plugin Command: ${_p(0)}`;
            case 401: return `<span style="opacity:0.7; padding-left: 10px;">└ Text: ${_p(0)}</span>`;
            case 411: return '◆ Else';
            case 412: return '◆ End If';
            default: return `Unknown Command (${command.code})`;
        }
    }
</script>

<div class="command-list">
    {#each commands as command, index}
        <div class="command-item" on:click={() => dispatch('edit', index)}>
            <span style="display: inline-block; width: 20px; opacity: 0.5;">{@html '&nbsp;'.repeat(command.indent || 0)}</span>
            {@html formatCommand(command)}
        </div>
    {:else}
        <div class="command-item-empty">No commands.</div>
    {/each}
</div>

<style>
    .command-item {
        user-select: none;
    }
    .command-item-empty {
        padding: 8px 12px;
        color: var(--text-muted);
        font-style: italic;
    }
</style>