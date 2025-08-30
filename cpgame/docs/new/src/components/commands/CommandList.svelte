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
            case 123: return `Control Self Switch: ${p(0, 0)} = ${p(1, 0) === 0 ? 'ON' : 'OFF'}`;
            case 124: return `Control Timer: ${p(0, 0) === 0 ? 'Start' : 'Stop'} (${p(1, 60)}s)`;
            case 125: return `Change Gold: ${p(0, 0) === 0 ? 'Increase' : 'Decrease'} by ${p(1, 0) === 1 ? `V[${p(2,0)}]` : p(2,0)}`;
            case 126: return `Change Items: [ID ${p(0,1)}] ${p(1, 0) === 0 ? 'Increase' : 'Decrease'} by ${p(2, 0) === 1 ? `V[${p(3,0)}]` : p(3,0)}`;
            case 127: return `Change Weapons: [ID ${p(0,1)}] ${p(1, 0) === 0 ? 'Increase' : 'Decrease'} by ${p(2, 0) === 1 ? `V[${p(3,0)}]` : p(3,0)}`;
            case 128: return `Change Armors: [ID ${p(0,1)}] ${p(1, 0) === 0 ? 'Increase' : 'Decrease'} by ${p(2, 0) === 1 ? `V[${p(3,0)}]` : p(3,0)}`;
            case 201: return `Transfer Player: Map ${p(1, 1)}, (${p(2, 0)}, ${p(3, 0)})`;
            case 301: {
                const designation = p(0, 0) === 0 ? `Troop ID ${p(1, 1)}` : `Variable V[${p(1, 1)}]`;
                const flags = [];
                if (p(2, true)) flags.push('Can Escape');
                if (p(3, false)) flags.push('Can Lose');
                return `◆ Battle: ${designation}${flags.length > 0 ? ` (${flags.join(', ')})` : ''}`;
            };
            case 302: return `Shop Processing`;
            case 303: return `Name Input: Actor ${p(0, 1)} (${p(1, 8)} chars)`;
            case 356: return `Plugin Command: ${p(0, '')}`;
            case 401: return `<span style="opacity:0.7; padding-left: 10px;">└ Text: ${p(0, '')}</span>`;
            case 402: return `◆ When [Choice #${p(0, 0) + 1}]`;
            case 403: return `◆ When [Cancel]`;
            case 411: return '◆ Else';
            case 412: return '◆ End If';
            case 501: return `Set Tile: Event ${p(0, 0)}, Tile ${p(1, 0)}`;
            default: return `Unknown Command (${code})`;
        }
    }
</script>

<div class="command-list">
    <!-- Insert bar for the very first item -->
    <div class="command-item">
        <div class="insert-bar" on:click={() => dispatch('add-here', { index: 0 })}></div>
    </div>

    {#each commands as command, index}
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="command-item" on:dblclick={() => dispatch('edit', index)}>
            {#if ![401].includes(command.code)}
                <div class="insert-bar" on:click={() => dispatch('add-here', { index })}></div>
            {/if}
            <div class="indent-lines">
                {#each Array(command.indent || 0) as _}<span class="indent-line"></span>{/each}
            </div>
            <div class="command-content">
                {@html formatCommand(command)}
            </div>
            <div class="command-item-actions">
                <!-- svelte-ignore a11y_consider_explicit_label -->
                <button title="Edit Command" class="command-action-btn" on:click={() => dispatch('edit', index)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                </button>
                <!-- svelte-ignore a11y_consider_explicit_label -->
                <button title="Delete Command" class="command-action-btn" on:click={() => dispatch('delete', index)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                </button>
            </div>
        </div>

        <!-- Logic to render "Add Command Here" placeholders -->
        {@const currentIndent = command.indent || 0}
        {@const nextIndent = commands[index + 1]?.indent ?? -1} 
        {@const isBlockOpener = [111, 402, 403, 411].includes(command.code)}
        {@const isLastItem = index === commands.length - 1}

        <!-- Case 1: The very last command opens a block, so the block is empty -->
        {#if isBlockOpener && nextIndent !== currentIndent + 1}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div class="command-item-add" on:click={
                () => dispatch('add-here', {
                    index: index + 1,
                    indent: currentIndent + 1
                    })
            }>
                <div class="indent-lines">{#each Array(currentIndent + 1) as _}<span class="indent-line"></span>{/each}</div>
                <div class="command-content-add">+</div>
            </div>
        {/if}
        
        <!-- Case 2: The next command has a lower indent, meaning one or more blocks are closing -->
        {#if nextIndent < currentIndent}
            {#each Array(currentIndent - Math.max(0, nextIndent)) as _, j}
                {@const placeholderIndent = currentIndent - j}
                <div class="command-item-add" on:click={() => dispatch('add-here', { index: index + 1, indent: placeholderIndent })}>
                    <div class="indent-lines">{#each Array(placeholderIndent) as _}<span class="indent-line"></span>{/each}</div>
                    <div class="command-content-add">+</div>
                </div>
            {/each}
        {/if}
            <!-- <span style="display: inline-block; width: 20px; opacity: 0.5;">{@html '&nbsp;'.repeat(command.indent || 0)}</span> -->
        
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