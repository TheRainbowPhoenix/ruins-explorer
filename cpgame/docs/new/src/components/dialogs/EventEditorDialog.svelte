<script>
    import { onMount } from 'svelte';
    import { isEventEditorOpen, actions, tileSize } from '../../store.js';
    import CommandList from '../commands/CommandList.svelte';
    import EditCommandDialog from './EditCommandDialog.svelte';
    import AddCommandDialog from './AddCommandDialog.svelte';
    import EditTextBlockDialog from './EditTextBlockDialog.svelte';
    import EditConditionsDialog from './EditConditionsDialog.svelte';

    export let event;

    let localEvent = JSON.parse(JSON.stringify(event));
    let currentPageIndex = 0;
    let tileset = new Image();
    let tilesetLoaded = false;
    
    let commandToEditIndex = null;
    let textBlockEditIndex = null;
    let showAddCommand = false;
    let showConditionsEditor = false;
    let currentIndent = 0;
    
    $: conditionsSummary = formatConditions(localEvent.pages[currentPageIndex]?.conditions);

    onMount(() => {
        tileset.src = 'jrpg.png';
        tileset.onload = () => tilesetLoaded = true;
        if (!localEvent.pages[currentPageIndex].through) {
            localEvent.pages[currentPageIndex].through = false;
        }
    });

    function close() {
        isEventEditorOpen.set(false);
    }

    function saveAndClose() {
        actions.updateEvent(localEvent);
        close();
    }
    
    function addPage() {
        localEvent.pages.push({ conditions: {}, graphic: { tileId: 0 }, list: [] });
        currentPageIndex = localEvent.pages.length - 1;
        localEvent = localEvent; 
    }

    function deletePage() {
        if (localEvent.pages.length > 1) {
            localEvent.pages.splice(currentPageIndex, 1);
            currentPageIndex = Math.min(currentPageIndex, localEvent.pages.length - 1);
            localEvent = localEvent;
        }
    }
    
    function addCommand(code, parameters) {
        const commands = localEvent.pages[currentPageIndex].list;
        commands.push({ code, parameters });
        // Special case for Show Text, which adds a text line right after
        if (code === 101) {
             commands.push({ code: 401, parameters: [""] });
        }
        localEvent = localEvent; // Trigger reactivity
    }
    
    function handleEditCommand(event) {
        commandToEditIndex = event.detail;
    }

    function handleSaveCommand(event) {
        localEvent.pages[currentPageIndex].list[commandToEditIndex] = event.detail;
        commandToEditIndex = null;
        localEvent = localEvent;
    }

    
    function handleAddCommand(e) {
        const { code, params, indent } = e.detail;
        const commands = localEvent.pages[currentPageIndex].list;

        if (indent) {
            if ([402, 403, 411, 412].includes(code)) currentIndent = Math.max(0, currentIndent - 1);
        }

        const newCommand = { code, parameters: params, indent: currentIndent };
        commands.push(newCommand);

        if (code === 101) commands.push({ code: 401, parameters: [""], indent: currentIndent });
        if ([111, 402, 403, 411].includes(code)) currentIndent++;
        
        localEvent = localEvent;
    }

    function handleEditRequest(e) {
        const index = e.detail;
        const command = localEvent.pages[currentPageIndex].list[index];
        if (command.code === 101 || command.code === 401) {
            textBlockEditIndex = index;
        } else {
            commandToEditIndex = index;
        }
    }
    
    function formatConditions(conds) {
        if (!conds) return "None";
        const parts = [];
        if (conds.switch1Valid) parts.push(`S[${conds.switch1Id}] ON`);
        if (conds.switch2Valid) parts.push(`S[${conds.switch2Id}] ON`);
        if (conds.variableValid) parts.push(`V[${conds.variableId}] >= ${conds.variableValue}`);
        if (conds.selfSwitchValid) parts.push(`Self-S[${conds.selfSwitchCh}] ON`);
        return parts.length > 0 ? parts.join(', ') : "None";
    }

    function handleSaveTextBlock(e) {
        const newCommands = e.detail;
        const list = localEvent.pages[currentPageIndex].list;
        
        // Find start and end of the old block to replace it
        let blockStartIndex = textBlockEditIndex;
        if (list[textBlockEditIndex].code === 401) {
             for (let i = textBlockEditIndex - 1; i >= 0; i--) {
                if (list[i].code === 101) { blockStartIndex = i; break; }
            }
        }
        let blockEndIndex = blockStartIndex;
        for (let i = blockStartIndex + 1; i < list.length; i++) {
            if (list[i].code === 401) blockEndIndex = i; else break;
        }
        
        list.splice(blockStartIndex, blockEndIndex - blockStartIndex + 1, ...newCommands);
        textBlockEditIndex = null;
    }

    function handleDeleteCommand() {
        const list = localEvent.pages[currentPageIndex].list;
        const command = list[commandToEditIndex];
        
        if (command.code === 111) currentIndent = Math.max(0, currentIndent - 1);
        
        if (command.code === 101 && list[commandToEditIndex + 1]?.code === 401) {
             list.splice(commandToEditIndex, 2);
        } else {
             list.splice(commandToEditIndex, 1);
        }
        commandToEditIndex = null;
        localEvent = localEvent;
    }

</script>

<div class="dialog-overlay">
    <div class="dialog dialog-large">
        <div class="dialog-header">
            <span>Edit Event: {localEvent.name}</span>
            <button class="btn btn-secondary" on:click={close}>✕</button>
        </div>
        <div class="dialog-content-split">
            <!-- LEFT COLUMN -->
            <div class="dialog-column-left">
                <div class="form-group">
                    <label class="form-label">Event Name</label>
                    <input type="text" class="form-input" bind:value={localEvent.name}>
                </div>
                <div class="form-group">
                    <label class="form-label">Page</label>
                    <div class="action-fields" style="display: flex; gap: 8px;">
                        <select class="form-select" bind:value={currentPageIndex} style="flex:1;">
                        {#each localEvent.pages as _, i}
                            <option value={i}>Page {i + 1}</option>
                        {/each}
                        </select>
                        <button class="btn btn-secondary" on:click={addPage}>+</button>
                        <button class="btn btn-danger" on:click={deletePage}>-</button>
                    </div>
                </div>
                <div class="form-group">
                    <label>Conditions: <small>{conditionsSummary}</small></label>
                    <button class="btn btn-secondary" on:click={() => showConditionsEditor = true}>Edit Conditions</button>
                </div>
                <div class="form-group">
                    <label style="display: flex; align-items: center; gap: 8px;">
                        <input type="checkbox" bind:checked={localEvent.pages[currentPageIndex].through}> Through
                    </label>
                </div>
                <div class="form-group">
                    <label class="form-label">Graphic</label>
                    <div class="graphic-picker">
                        {#if tilesetLoaded}
                            {#each Array(160) as _, i}
                                <div
                                    class="graphic-item"
                                    class:selected={localEvent.pages[currentPageIndex].graphic.tileId === i}
                                    style="background-image: url('{tileset.src}'); background-position: -{(i % 16) * $tileSize * 2}px -{Math.floor(i / 16) * $tileSize * 2}px; background-size: {tileset.width * 2}px {tileset.height * 2}px;"
                                    on:click={() => localEvent.pages[currentPageIndex].graphic.tileId = i}
                                ></div>
                            {/each}
                        {/if}
                    </div>
                </div>
            </div>
            <!-- RIGHT COLUMN -->
            <div class="dialog-column-right">
                <div class="form-group">
                    <label class="form-label">Commands</label>
                    <CommandList commands={localEvent.pages[currentPageIndex].list} on:edit={handleEditRequest}/>
                </div>
                <button class="btn btn-primary" on:click={() => showAddCommand = true}>+ Add Command...</button>
            </div>
        </div>
        <div class="dialog-footer">
            <button class="btn btn-primary" on:click={saveAndClose}>Save & Close</button>
        </div>
    </div>
</div>

{#if showAddCommand}
    <AddCommandDialog
        on:close={() => showAddCommand = false}
        on:add={handleAddCommand}
    />
{/if}

{#if showConditionsEditor}
    <EditConditionsDialog
        conditions={localEvent.pages[currentPageIndex].conditions}
        on:close={() => showConditionsEditor = false}
        on:save={(e) => { localEvent.pages[currentPageIndex].conditions = e.detail; showConditionsEditor = false}}
    />
{/if}

{#if textBlockEditIndex !== null}
    <EditTextBlockDialog
        commandList={localEvent.pages[currentPageIndex].list}
        startIndex={textBlockEditIndex}
        on:close={() => textBlockEditIndex = null}
        on:save={handleSaveTextBlock}
    />
{/if}

{#if commandToEditIndex !== null}
    <EditCommandDialog 
        command={localEvent.pages[currentPageIndex].list[commandToEditIndex]}
        on:save={(e) => { localEvent.pages[currentPageIndex].list[commandToEditIndex] = e.detail; commandToEditIndex = null; }}
        on:delete={handleDeleteCommand}
        on:close={() => commandToEditIndex = null}
    />
{/if}
