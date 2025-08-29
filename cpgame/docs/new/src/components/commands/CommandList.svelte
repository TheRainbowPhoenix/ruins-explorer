<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    export let commands = [];

    const dispatch = createEventDispatcher();

    const ifConditionOps = [
        { value: 0, label: '==' }, { value: 1, label: '>=' },
        { value: 2, label: '<=' }, { value: 3, label: '>' },
        { value: 4, label: '<' }, { value: 5, label: '!=' }
    ];

    function formatCommand(command) {
        // Safe parameter accessor: p(index, fallbackValue)
        const p = (idx, fallback: string|number|any = '') => {
            if (!command.parameters || command.parameters[idx] === undefined || command.parameters[idx] === null) {
                return fallback;
            }
            return command.parameters[idx];
        };

        const code = command.code;
        switch (code) {
            case 101: return `Show Text: Face "${p(0, '')}", Index ${p(1, 0)}`;
            case 102: return `Show Choices: [${(p(0, [])).join(', ')}]`;
            case 103: return `Input Number: V[${p(0, 1)}] (${p(1, 3)} digits)`;
            case 111: 
                if (p(0, 0) === 0) return `◆ If: Switch [${p(1, 1)}] is ${p(2, 0) === 0 ? 'ON' : 'OFF'}`;
                if (p(0, 0) === 1) {
                    const opLabel = ifConditionOps.find(op => op.value === p(4, 0))?.label || '??';
                    const operand = p(2,0) === 1 ? `Variable [${p(3,0)}]` : `Constant ${p(3,0)}`;
                    return `◆ If: Variable [${p(1, 1)}] ${opLabel} ${operand}`;
                }
                return '◆ If: ...';
            case 121: return `Control Switches: [${p(0, 1)}-${p(1, 1)}] = ${p(2, 0) === 0 ? 'ON' : 'OFF'}`;
            case 122: return `Control Variables: V[${p(0, 1)}-${p(1, 1)}] ...`;
            case 123: return `Control Self Switch: ${String.fromCharCode(65 + p(0, 0))} = ${p(1, 0) === 0 ? 'ON' : 'OFF'}`;
            case 124: return `Control Timer: ${p(0, 0) === 0 ? 'Start' : 'Stop'} (${p(1, 60)}s)`;
            case 201: return `Transfer Player: Map ${p(1, 1)}, (${p(2, 0)}, ${p(3, 0)})`;
            case 301: return `Battle Processing: Enemy ID ${p(1, 1)}`;
            case 302: return `Shop Processing`;
            case 303: return `Name Input: Actor ${p(0, 1)} (${p(1, 8)} chars)`;
            case 356: return `Plugin Command: ${p(0, '')}`;
            case 401: return `<span style="opacity:0.7; padding-left: 10px;">└ Text: ${p(0, '')}</span>`;
            case 402: return `◆ When [${p(0, 'Choice')}]`;
            case 403: return `◆ When [Cancel]`;
            case 411: return '◆ Else';
            case 412: return '◆ End If';
            case 501: return `Set Tile: Event ${p(0, 0)}, Tile ${p(1, 0)}`;
            default: return `Unknown Command (${code})`;
        }
    }
</script>

<div class="command-list">
    {#each commands as command, index}
        <div class="command-item" on:dblclick={() => dispatch('edit', index)}>
            <div class="indent-lines">
                {#each Array(command.indent || 0) as _}<span class="indent-line"></span>{/each}
            </div>
            <div class="command-content">
                {@html formatCommand(command)}
            </div>
            <!-- <span style="display: inline-block; width: 20px; opacity: 0.5;">{@html '&nbsp;'.repeat(command.indent || 0)}</span> -->
        </div>
    {:else}
        <div class="command-item-empty">No commands.</div>
    {/each}
</div>

<style>
    .command-item-empty {
        padding: 8px 12px;
        color: var(--text-muted);
        font-style: italic;
    }
</style>