<script>
    import { 
        displayName, tilesetId, mapWidth, mapHeight, scrollType, 
        specifyBattleback, mapData, events, actions 
    } from '../../store.js';

    $: exportData = generateExportData();

    /**
     * A custom formatter to pretty-print a page object with special indentation for the command list.
     * @param {object} page The event page object.
     * @param {string} baseIndent The base indentation string for the page object.
     * @returns {string} A formatted string representation of the page.
     */
    function formatPageObject(page, baseIndent) {
        const lines = [];
        const innerIndent = `${baseIndent}    `;

        // Helper to format the 'conditions' object specifically for Python compatibility.
        const formatConditionsObject = (conds) => {
            if (!conds || typeof conds !== 'object') return '{}';
            const parts = Object.entries(conds).map(([key, value]) => {
                let valueStr;
                if (typeof value === 'boolean') {
                    valueStr = value ? 'True' : 'False';
                } else {
                    valueStr = JSON.stringify(value); // Handles numbers and strings correctly
                }
                return `"${key}": ${valueStr}`;
            });
            return `{${parts.join(', ')}}`;
        };

        // Handle all properties except 'list'
        const pageKeys = Object.keys(page).filter(k => k !== 'list');
        pageKeys.forEach(key => {
            const value = page[key];
            let valueStr;

            if (key === 'conditions') {
                valueStr = formatConditionsObject(value);
            } else if (typeof value === 'boolean') {
                valueStr = value ? 'True' : 'False';
            } else {
                valueStr = JSON.stringify(value);
            }
            lines.push(`${innerIndent}"${key}": ${valueStr}`);
        });

        // Handle the 'list' property with custom, nested indentation
        if (page.hasOwnProperty('list')) {
            const commandLines = [];
            const commandBaseIndent = `${innerIndent}    `;
            page.list.forEach(command => {
                const extraIndent = '    '.repeat(command.indent || 0);
                commandLines.push(`${commandBaseIndent}${extraIndent}${JSON.stringify(command)}`);
            });
            const commandBlock = `[\n${commandLines.join(',\n')}\n${innerIndent}]`;
            lines.push(`${innerIndent}"list": ${commandBlock}`);
        }

        return `${baseIndent}{\n${lines.join(',\n')}\n${baseIndent}}`;
    }

    function generateExportData() {
        let exportStr = 'HEADER = {\n';
        exportStr += '    \'description\': \'Map Data\',\n';
        exportStr += '    \'exports\': ["displayName", "tilesetId", "width", "height", "scrollType", "specifyBattleback", "data", "events"],\n';
        exportStr += '}\n\n';
        
        exportStr += `displayName = "${$displayName}"\n`;
        exportStr += `tilesetId = "${$tilesetId}" # Corresponds to the key in AssetManager\n`;
        exportStr += `width = ${$mapWidth}\n`;
        exportStr += `height = ${$mapHeight}\n`;
        exportStr += `scrollType = ${$scrollType}\n`;
        exportStr += `specifyBattleback = ${$specifyBattleback ? 'True' : 'False'}\n\n`;
        
        exportStr += 'data = [\n';
        for (let y = 0; y < $mapHeight; y++) {
            let rowStr = '    ';
            for (let x = 0; x < $mapWidth; x++) {
                const index = y * $mapWidth + x;
                rowStr += $mapData[index] ?? 0;
                if (x < $mapWidth - 1) {
                    rowStr += ', ';
                }
            }
            if (y < $mapHeight - 1) {
                rowStr += ',';
            }
            exportStr += rowStr + '\n';
        }
        exportStr += ']\n\n';
        
        exportStr += 'events = {\n';
        const eventKeys = Object.keys($events);
        eventKeys.forEach((posKey, index) => {
            const [x, y] = posKey.split(',').map(Number);
            const event = $events[posKey];
            exportStr += `    # Event at (x=${x}, y=${y})\n`;
            exportStr += `    (${x}, ${y}): { # Event ID ${event.id}\n`;
            exportStr += `        "id": ${event.id},\n`;
            exportStr += `        "name": "${event.name}",\n`;
            exportStr += `        "x": ${event.x}, "y": ${event.y},\n`;
            exportStr += `        "pages": [\n`;

            event.pages.forEach((page, pageIndex) => {
                exportStr += formatPageObject(page, '            '); // 12 spaces for base indent
                if (pageIndex < event.pages.length - 1) {
                    exportStr += ',\n';
                }
            });
            exportStr += `\n        ]\n`;
            exportStr += '    }';
            if (index < eventKeys.length - 1) {
                exportStr += ',\n';
            }
            exportStr += '\n';
        });
        exportStr += '}';
        
        return exportStr;
    }

    function copyMapData() {
        navigator.clipboard.writeText(exportData);
    }

    function saveProject() {
        const projectData = {
            displayName: $displayName,
            tilesetId: $tilesetId,
            width: $mapWidth,
            height: $mapHeight,
            scrollType: $scrollType,
            specifyBattleback: $specifyBattleback,
            data: $mapData,
            events: $events
        };
        
        const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${$displayName || 'project'}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function loadProject() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    try {
                        const projectData = JSON.parse(event.target.result);
                        actions.loadProject(projectData);
                    } catch (error) {
                        alert('Error loading project file: ' + error.message);
                    }
                };
                reader.readAsText(file);
            }
        };
        input.click();
    }
</script>

<div class="form-group">
    <label class="form-label">Map Data</label>
    <textarea class="form-textarea" readonly value={exportData}></textarea>
</div>

<div class="form-group">
    <button class="btn btn-primary" on:click={copyMapData}>Copy Map Data</button>
    <button class="btn btn-secondary" on:click={saveProject}>Save Project</button>
    <button class="btn btn-secondary" on:click={loadProject}>Load Project</button>
</div>