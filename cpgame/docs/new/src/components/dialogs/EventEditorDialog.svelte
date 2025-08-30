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
    let copyStatus = '';
    
    $: conditionsSummary = formatConditions(localEvent.pages[currentPageIndex]?.conditions);
    $: currentPage = localEvent.pages[currentPageIndex];

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
        localEvent.pages.push({ conditions: {}, graphic: { tileId: 0 }, list: [], through: false });
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
        showConditionsEditor = false;
        recalculateIndents();
    }

    function recalculateIndents() {
        let indentLevel = 0;
        const list = currentPage.list;
        for (const command of list) {
            // A command that closes a block is indented one level less than the block's content.
            if ([403, 411, 412].includes(command.code)) {
                indentLevel = Math.max(0, indentLevel - 1);
            }
            command.indent = indentLevel;
            // A command that opens a block increases the indent for subsequent commands.
            if ([111, 402, 403, 411].includes(command.code)) {
                indentLevel++;
            }
        }
        localEvent = localEvent; // Trigger reactivity
    }

    
    function handleAddCommand(e) {
        const { code, params } = e.detail.command;
        const { index } = e.detail.extra;
        
        const commands = currentPage.list;
        
        // Indentation will be fixed by recalculateIndents, so we add with a temp indent of 0.
        const primaryCommand = { code, parameters: params, indent: 0 };
        commands.splice(index, 0, primaryCommand);

        // --- Auto-add closing or related commands ---
        if (code === 101) {
            // Add the accompanying text line
            commands.splice(index + 1, 0, { code: 401, parameters: [""], indent: 0 });
        } else if ([111, 402, 403].includes(code)) {
            // For If and When blocks, automatically add the "End If"
            commands.splice(index + 1, 0, { code: 412, parameters: [], indent: 0 });
        }
        
        
        recalculateIndents();
    }

    // New handler for direct deletion from the list
    function handleDeleteRequest(e) {
        const index = e.detail;
        const list = currentPage.list;
        const command = list[index];

        if (command.code === 101 && list[index + 1]?.code === 401) {
             list.splice(index, 2);
        } else {
             list.splice(index, 1);
        }
        
        recalculateIndents();
    }

    function handleAddCommandHere(e) {
        showAddCommand = { index: e.detail.index, indent: e.detail.indent };
    }

    function handleEditRequest(e) {
        const index = e.detail;
        const command = currentPage.list[index];
        if (command.code === 101 || command.code === 401) {
            textBlockEditIndex = index;
        } else {
            commandToEditIndex = index;
        }
    }
    
    function formatConditions(conds) {
        if (!conds || Object.keys(conds).length === 0) return "None";
        const parts = [];
        if (conds.switch1Valid) parts.push(`S[${conds.switch1Id}] ON`);
        if (conds.switch2Valid) parts.push(`S[${conds.switch2Id}] ON`);
        if (conds.variableValid) parts.push(`V[${conds.variableId}] >= ${conds.variableValue}`);
        if (conds.selfSwitchValid) parts.push(`Self-S[${conds.selfSwitchCh}] ON`);
        return parts.length > 0 ? parts.join(', ') : "None";
    }

    async function copyPage() {
        try {
            const pageJson = JSON.stringify(currentPage);
            await navigator.clipboard.writeText(pageJson);
            copyStatus = 'Copied!';
        } catch (err) {
            copyStatus = 'Failed to copy!';
        }
        setTimeout(() => copyStatus = '', 2000);
    }

    async function pastePage() {
        try {
            const clipboardText = await navigator.clipboard.readText();
            const newPageData = JSON.parse(clipboardText);
            
            // Basic validation
            if (newPageData && typeof newPageData.graphic === 'object' && Array.isArray(newPageData.list)) {
                localEvent.pages[currentPageIndex] = newPageData;
                copyStatus = 'Pasted!';
            } else {
                throw new Error("Invalid page data in clipboard.");
            }
        } catch (err) {
            copyStatus = 'Paste failed!';
            console.error(err);
        }
         setTimeout(() => copyStatus = '', 2000);
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
        
        recalculateIndents();
        
        list.splice(blockStartIndex, blockEndIndex - blockStartIndex + 1, ...newCommands);
        textBlockEditIndex = null;
    }

    

    function handleDeleteCommand() {
        const list = currentPage.list;
        const command = list[commandToEditIndex];
        
        if (command.code === 101 && list[commandToEditIndex + 1]?.code === 401) {
             list.splice(commandToEditIndex, 2);
        } else {
             list.splice(commandToEditIndex, 1);
        }
        
        recalculateIndents();
        commandToEditIndex = null;
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
                    <div class="page-actions">
                        {#if copyStatus}<div class="copy-feedback">{copyStatus}</div>{/if}
                        <select class="form-select" bind:value={currentPageIndex} style="flex:1;">
                        {#each localEvent.pages as _, i}
                            <option value={i}>Page {i + 1}</option>
                        {/each}
                        </select>
                        <button class="btn btn-secondary" on:click={addPage}>+</button>
                        <button class="btn btn-danger" on:click={deletePage}>-</button>
                        <!-- <button class="btn btn-secondary" on:click={copyPage}>Copy</button> -->
                        <!-- <button class="btn btn-secondary" on:click={pastePage}>Paste</button> -->
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
                    <CommandList commands={localEvent.pages[currentPageIndex].list} on:edit={handleEditRequest} on:add-here={handleAddCommandHere}  on:delete={handleDeleteRequest}/>
                </div>
                <button class="btn btn-primary" style="min-height: 32px;" on:click={() => handleAddCommandHere({ detail: { index: localEvent.pages[currentPageIndex].list.length, indent: 0 }})}>+ Add Command...</button>
                <div style="min-height: 24px;"></div>
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
        on:add={(e) => handleAddCommand({ detail: { command: e.detail, extra:showAddCommand }})}
    />
{/if}

{#if showConditionsEditor}
    <EditConditionsDialog
        conditions={localEvent.pages[currentPageIndex].conditions}
        on:close={() => showConditionsEditor = false}
        on:save={handleSaveCommand}
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
        on:save={handleSaveCommand}
        on:delete={handleDeleteCommand}
        on:close={() => commandToEditIndex = null}
    />
{/if}
